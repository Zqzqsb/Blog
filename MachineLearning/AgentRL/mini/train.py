"""Grouped clipped policy gradient, with a table or local causal-LM policy.

The LM is normalized over six complete action strings, NOT free token decoding.
The table backend is the fast, tested CPU path. No package/model auto-downloads.
"""
import argparse
import copy
import json
import platform
import time
from pathlib import Path

import torch
from torch import nn

from environment import ACTIONS, HORIZON, Harness, verify


class TablePolicy(nn.Module):
    def __init__(self):
        super().__init__()
        self.logits = nn.Parameter(torch.zeros(HORIZON * 4, len(ACTIONS)))

    def log_probs(self, state):
        return self.logits[state[0]].log_softmax(dim=-1)


class LMPolicy(nn.Module):
    def __init__(self, model_path, device):
        super().__init__()
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path, local_files_only=True, trust_remote_code=False)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, local_files_only=True, trust_remote_code=False).to(device)
        if self.tokenizer.eos_token_id is None:
            raise ValueError("this demo requires an EOS token")
        self.model.eval()  # Dropout off even when computing gradients.

    def log_probs(self, state):
        device = next(self.model.parameters()).device
        prefix = self.tokenizer.encode(state[1], add_special_tokens=True)
        if not prefix:
            raise ValueError("empty prompt")
        scores = []
        for action in ACTIONS:
            suffix = self.tokenizer.encode(" " + action, add_special_tokens=False)
            suffix += [self.tokenizer.eos_token_id]
            ids = torch.tensor([prefix + suffix], device=device)
            logits = self.model(input_ids=ids, use_cache=False).logits
            # At position p-1 the model predicts the first candidate token.
            target_logits = logits[0, len(prefix)-1:-1].float().log_softmax(-1)
            targets = ids[0, len(prefix):]
            scores.append(target_logits.gather(1, targets[:, None]).sum())
        # Exact categorical policy over the complete, finite action catalog.
        return torch.stack(scores).log_softmax(0)


@torch.no_grad()
def rollout(policy, grader_seed, generator):
    env = Harness()
    steps = []
    while not env.done:
        state = (env.features(), env.prompt())
        lp = policy.log_probs(state)
        action = int(torch.multinomial(lp.exp().cpu(), 1, generator=generator))
        steps.append({"state": state, "action": action, "old_logp": float(lp[action])})
        env.step(ACTIONS[action])
    # Budget exhaustion is a failure under this explicitly chosen task contract.
    reward = verify(env.artifact(), grader_seed) if env.reason == "finished" else 0.0
    return {"steps": steps, "reward": reward, "reason": env.reason}


def advantages(rewards):
    r = torch.tensor(rewards, dtype=torch.float32)
    std = r.std(unbiased=False)
    if float(std) == 0:
        return torch.zeros_like(r)
    return (r - r.mean()) / std


def clipped_objective(ratio, advantage, clip):
    return torch.minimum(ratio * advantage,
                         ratio.clamp(1 - clip, 1 + clip) * advantage)


def update(policy, reference, optimizer, groups, epochs, clip, beta):
    # Cache frozen reference distributions; they are not model observations.
    for group in groups:
        adv = advantages([e["reward"] for e in group])
        for ep, a in zip(group, adv):
            ep["advantage"] = float(a)
            for step in ep["steps"]:
                with torch.no_grad():
                    step["ref_logp"] = reference.log_probs(step["state"]).detach()
    n = sum(len(group) for group in groups)
    result = {}
    for _ in range(epochs):
        optimizer.zero_grad()
        total_loss, total_kl, clipped, positions = 0.0, 0.0, 0, 0
        for group in groups:
            for ep in group:
                terms = []
                for step in ep["steps"]:
                    lp = policy.log_probs(step["state"])
                    ratio = (lp[step["action"]] - step["old_logp"]).exp()
                    objective = clipped_objective(ratio, ep["advantage"], clip)
                    ref_lp = step["ref_logp"].to(lp.device)
                    kl = (lp.exp() * (lp - ref_lp)).sum()  # Exact categorical KL.
                    terms.append(-objective + beta * kl)
                    total_kl += float(kl.detach())
                    clipped += int(abs(float(ratio.detach()) - 1) > clip)
                    positions += 1
                loss = torch.stack(terms).mean() / n
                loss.backward()
                total_loss += float(loss.detach())
        nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
        optimizer.step()
        result = {"loss": total_loss, "mean_kl": total_kl / positions,
                  "ratio_outside_clip_fraction": clipped / positions}
    return result


def sft_update(policy, optimizer, groups, epochs):
    successes = [ep for group in groups for ep in group if ep["reward"] == 1]
    if not successes:
        return {"loss": 0.0, "retained_episodes": 0, "optimizer_steps": 0}
    total_loss = 0.0
    for _ in range(epochs):
        optimizer.zero_grad()
        total_loss = 0.0
        for ep in successes:
            loss = -torch.stack([policy.log_probs(s["state"])[s["action"]]
                                 for s in ep["steps"]]).mean() / len(successes)
            loss.backward()
            total_loss += float(loss.detach())
        nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
        optimizer.step()
    return {"loss": total_loss, "retained_episodes": len(successes),
            "optimizer_steps": epochs}


@torch.no_grad()
def evaluate(policy, count, seed):
    generator = torch.Generator().manual_seed(seed)
    episodes = [rollout(policy, 900000 + i, generator) for i in range(count)]
    wins = sum(e["reward"] for e in episodes)
    return {"episodes": count, "successes": int(wins), "success_rate": wins / count,
            "mean_actions": sum(len(e["steps"]) for e in episodes) / count}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--backend", choices=["table", "hf"], default="table")
    p.add_argument("--method", choices=["grpo", "rs-sft"], default="grpo")
    p.add_argument("--model", help="local causal-LM checkpoint; required for hf")
    p.add_argument("--device", default="cpu")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--iterations", type=int, default=100)
    p.add_argument("--groups", type=int, default=4)
    p.add_argument("--group-size", type=int, default=8)
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--clip", type=float, default=0.2)
    p.add_argument("--beta", type=float, default=0.02)
    p.add_argument("--eval-episodes", type=int, default=500)
    p.add_argument("--output", type=Path, default=Path("run.json"))
    args = p.parse_args()
    if min(args.iterations, args.groups, args.epochs, args.eval_episodes) < 1:
        p.error("counts must be positive")
    if args.group_size < 2:
        p.error("group-size must be at least two")
    if args.backend == "hf" and not args.model:
        p.error("--backend hf requires --model")
    if not 0 < args.clip < 1 or args.beta < 0:
        p.error("require 0 < clip < 1 and beta >= 0")
    torch.set_num_threads(1)
    torch.manual_seed(args.seed)
    policy = (TablePolicy() if args.backend == "table"
              else LMPolicy(args.model, args.device))
    reference = copy.deepcopy(policy).requires_grad_(False)
    learning_rate = args.lr if args.lr is not None else (0.08 if args.backend == "table" else 1e-6)
    optimizer = torch.optim.Adam(policy.parameters(), lr=learning_rate)
    generator = torch.Generator().manual_seed(args.seed + 1000)
    before = evaluate(policy, args.eval_episodes, args.seed + 2000)
    started = time.perf_counter()
    history = []
    for iteration in range(args.iterations):
        groups = []
        for group_id in range(args.groups):
            grader_seed = iteration * args.groups + group_id
            group = [rollout(policy, grader_seed, generator) for _ in range(args.group_size)]
            for ep in group:
                ep["policy_version"] = iteration
            groups.append(group)
        if args.method == "grpo":
            metrics = update(policy, reference, optimizer, groups, args.epochs, args.clip, args.beta)
            metrics["optimizer_steps"] = args.epochs
        else:
            metrics = sft_update(policy, optimizer, groups, args.epochs)
        metrics["iteration"] = iteration
        metrics["train_success_rate"] = sum(e["reward"] for g in groups for e in g) / (args.groups * args.group_size)
        metrics["mixed_groups"] = sum(len({e["reward"] for e in g}) > 1 for g in groups)
        history.append(metrics)
        if iteration % 20 == 0 or iteration + 1 == args.iterations:
            print(json.dumps(metrics), flush=True)
    after = evaluate(policy, args.eval_episodes, args.seed + 2000)
    config = {**vars(args), "output": str(args.output), "effective_lr": learning_rate}
    report = {"config": config, "runtime": {"python": platform.python_version(),
              "torch": torch.__version__, "platform": platform.platform()},
              "before": before, "after": after,
              "train_and_final_eval_seconds": time.perf_counter() - started,
              "history": history,
              "scope": "same repair task, fresh verifier inputs; not unseen-task generalization"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"before": before, "after": after, "output": str(args.output)}))


if __name__ == "__main__":
    main()
