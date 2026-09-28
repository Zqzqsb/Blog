"""Optional offline integration check using a tiny RANDOM LM, not a trained model."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import torch
from tokenizers import Tokenizer, models, pre_tokenizers
from transformers import GPT2Config, GPT2LMHeadModel, PreTrainedTokenizerFast

from environment import ACTIONS, Harness
from train import LMPolicy


def main():
    torch.set_num_threads(1)
    torch.manual_seed(123)
    with tempfile.TemporaryDirectory(prefix="agentrl-hf-") as folder:
        words = ["[PAD]", "[UNK]", "[EOS]", *ACTIONS,
                 "Repair", "binary", "search", "low", "high", "mid", "Action"]
        vocab = {word: i for i, word in enumerate(words)}
        tok = Tokenizer(models.WordLevel(vocab, unk_token="[UNK]"))
        tok.pre_tokenizer = pre_tokenizers.Whitespace()
        tokenizer = PreTrainedTokenizerFast(tokenizer_object=tok,
                    unk_token="[UNK]", pad_token="[PAD]", eos_token="[EOS]")
        tokenizer.save_pretrained(folder)
        model = GPT2LMHeadModel(GPT2Config(vocab_size=len(vocab), n_positions=512,
                   n_layer=1, n_head=2, n_embd=16, bos_token_id=2,
                   eos_token_id=2, pad_token_id=0))
        model.save_pretrained(folder)
        policy = LMPolicy(folder, "cpu")
        env = Harness()
        state = (env.features(), env.prompt())
        lp = policy.log_probs(state)
        assert torch.allclose(lp.exp().sum(), torch.tensor(1.), atol=1e-6)
        (-lp[0]).backward()
        assert any(p.grad is not None and p.grad.abs().sum() > 0
                   for p in policy.parameters())
        destination = Path(__file__).parent / "results" / "hf-smoke.json"
        subprocess.run([sys.executable, str(Path(__file__).with_name("train.py")),
                        "--backend", "hf", "--model", folder,
                        "--iterations", "1", "--groups", "1", "--group-size", "64",
                        "--epochs", "1", "--eval-episodes", "8",
                        "--output", str(destination)], check=True)
        report = json.loads(destination.read_text())
        assert report["history"][0]["mixed_groups"] == 1
        report["scope"] = "offline integration smoke test using a random tiny GPT-2; no pretrained-LM capability claim"
        destination.write_text(json.dumps(report, indent=2) + "\n")
    print("HF local loading, normalized actions, backward and training loop: PASS")


if __name__ == "__main__":
    main()
