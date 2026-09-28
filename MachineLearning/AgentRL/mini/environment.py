"""A finite-action teaching environment, NOT an arbitrary-code sandbox."""
from dataclasses import dataclass
import random


ACTIONS = ("read", "fix_low", "fix_high", "undo_low", "test", "finish")
HORIZON = 6


@dataclass(frozen=True)
class Artifact:
    low_fixed: bool
    high_fixed: bool


def search(artifact, values, target):
    """Execute only the fixed algorithm below; never exec model-generated code."""
    low, high = 0, len(values) - 1
    for _ in range(2 * len(values) + 4):
        if low > high:
            return -1
        mid = (low + high) // 2
        if values[mid] == target:
            return mid
        if values[mid] < target:
            low = mid + int(artifact.low_fixed)
        else:
            high = mid - int(artifact.high_fixed)
    return "iteration_limit"


def verify(artifact, seed):
    """Private final checks; seed and result are never part of tool observations."""
    rng = random.Random(seed)
    arrays = [[], [1], [1, 3], [-2, 0, 4]]
    arrays += [sorted(rng.sample(range(-40, 41), rng.randrange(1, 14)))
               for _ in range(12)]
    for values in arrays:
        for target in set(values + [-41, 41, 0]):
            expected = values.index(target) if target in values else -1
            if search(artifact, values, target) != expected:
                return 0.0
    return 1.0


class Harness:
    """No policy version, group, optimizer or private verifier in this interface."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.low_fixed = False
        self.high_fixed = False
        self.steps = 0
        self.done = False
        self.reason = None
        self.history = []
        return self.observation()

    def observation(self):
        low = "mid + 1" if self.low_fixed else "mid"
        high = "mid - 1" if self.high_fixed else "mid"
        return (f"step={self.steps}/{HORIZON}; low = {low}; high = {high}; "
                "patches are visible immediately")

    def features(self):
        # Table indexes observable code variants and remaining action budget.
        return self.steps * 4 + int(self.low_fixed) * 2 + int(self.high_fixed)

    def prompt(self):
        history = "\n".join(self.history)
        return ("Repair binary search on a sorted array. Equality returns mid. "
                "If a[mid] < target update low, otherwise update high. "
                "Allowed actions: read, fix_low, fix_high, undo_low, test, finish.\n"
                f"History:\n{history}\nCurrent code: {self.observation()}\nAction:")

    def step(self, action):
        if self.done:
            raise RuntimeError("episode has ended")
        if action not in ACTIONS:
            raise ValueError(action)
        if action == "fix_low":
            self.low_fixed = True
        elif action == "fix_high":
            self.high_fixed = True
        elif action == "undo_low":
            self.low_fixed = False
        self.steps += 1
        observation = self.observation()
        if action == "test":
            # A public smoke test deliberately does not establish correctness.
            passed = search(self.artifact(), [1, 3, 5], 3) == 1
            observation += f"; public smoke test: {'PASS' if passed else 'FAIL'}"
        if action == "finish":
            self.done, self.reason = True, "finished"
        elif self.steps == HORIZON:
            self.done, self.reason = True, "budget_exhausted"
        self.history.append(f"{action} -> {observation}")
        return observation, self.done

    def artifact(self):
        return Artifact(self.low_fixed, self.high_fixed)
