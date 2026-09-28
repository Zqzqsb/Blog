import unittest
import torch
from environment import Artifact, Harness, verify
from train import TablePolicy, advantages, clipped_objective, rollout, update, sft_update


class TrainingContractTests(unittest.TestCase):
    def test_private_verifier_rejects_partial_repairs(self):
        for low, high in [(False, False), (True, False), (False, True)]:
            self.assertEqual(verify(Artifact(low, high), 10), 0)
        self.assertEqual(verify(Artifact(True, True), 10), 1)

    def test_public_pass_does_not_imply_private_pass(self):
        env = Harness()
        observation, _ = env.step("test")
        self.assertIn("PASS", observation)
        self.assertEqual(verify(env.artifact(), 10), 0)

    def test_environment_isolation_and_terminal_contract(self):
        a, b = Harness(), Harness()
        a.step("fix_low")
        self.assertNotEqual(a.artifact(), b.artifact())
        for _ in range(6):
            b.step("read")
        self.assertEqual(b.reason, "budget_exhausted")
        with self.assertRaises(RuntimeError):
            b.step("finish")
        self.assertNotIn("reward", " ".join(b.history))
        self.assertNotIn("policy_version", b.prompt())

    def test_group_statistics(self):
        a = advantages([1, 1, 0, 0, 0, 1, 0, 0])
        self.assertAlmostEqual(float(a[0]), 1.2909944, places=5)
        self.assertAlmostEqual(float(a[2]), -0.7745967, places=5)
        self.assertTrue(torch.equal(advantages([0, 0]), torch.zeros(2)))

    def test_clip_stops_only_the_favorable_direction(self):
        for ratio, advantage, expected_grad in [(1.3, 1., 0.), (.7, 1., 1.),
                                                 (.7, -1., 0.), (1.3, -1., -1.)]:
            x = torch.tensor(ratio, requires_grad=True)
            clipped_objective(x, advantage, .2).backward()
            self.assertAlmostEqual(float(x.grad), expected_grad, places=5)

    def test_rollout_logprobs_reproduce_and_update_changes_policy(self):
        import copy
        policy = TablePolicy()
        reference = copy.deepcopy(policy).requires_grad_(False)
        generator = torch.Generator().manual_seed(7)
        group = [rollout(policy, 3, generator) for _ in range(64)]
        self.assertEqual({e["reward"] for e in group}, {0., 1.})
        for ep in group:
            for step in ep["steps"]:
                lp = policy.log_probs(step["state"])[step["action"]]
                self.assertAlmostEqual(float(lp.detach()), step["old_logp"], places=6)
        before = policy.logits.detach().clone()
        optimizer = torch.optim.Adam(policy.parameters(), lr=.08)
        update(policy, reference, optimizer, [group], 2, .2, .02)
        self.assertFalse(torch.equal(before, policy.logits.detach()))
        self.assertTrue(torch.equal(before, reference.logits.detach()))

    def test_sft_ignores_failures(self):
        policy = TablePolicy()
        optimizer = torch.optim.Adam(policy.parameters(), lr=.08)
        before = policy.logits.detach().clone()
        metrics = sft_update(policy, optimizer, [[{"reward": 0., "steps": []}]], 2)
        self.assertEqual(metrics["optimizer_steps"], 0)
        self.assertTrue(torch.equal(before, policy.logits.detach()))


if __name__ == "__main__":
    torch.set_num_threads(1)
    unittest.main()
