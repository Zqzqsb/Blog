# Agent RL 最小训练实验

配套文章：[第七篇：跑通一个可验证的训练闭环](../Agent%20RL（七）：跑通一个可验证的训练闭环.md)。

这个示例实际更新策略参数。默认使用 CPU 上的有限状态参数表，也支持对本地因果语言模型的六个候选动作重新归一化后训练。它不是自由文本 LLM GRPO 框架，也不执行任意生成代码。

## 运行

在本目录执行；默认路径需要 Python 和 PyTorch，HF 路径还需要 Transformers。已验证环境为 Python 3.12.4、PyTorch 2.12.0+cu130、Transformers 5.12.0，所有记录均来自 CPU。

```bash
python3 -m unittest -v test_demo.py
python3 train.py --seed 7 --output results/local-grpo-7.json
python3 train.py --method rs-sft --seed 7 --output results/local-sft-7.json
```

需要安装依赖时，在自己的虚拟环境内安装 PyTorch；本地 LM 后端额外安装 Transformers。脚本不安装包、不下载 checkpoint。

默认每轮 4 组、每组 8 条轨迹，共 100 轮；每批更新 2 次。可用 `python3 train.py --help` 查看配置。改变随机种子为 19、42 可以复现另外两组实验。

## 本地模型接口

```bash
python3 train.py --backend hf --model /absolute/path/to/local-model \
  --device cpu --iterations 1 --groups 1 --group-size 8 \
  --epochs 1 --eval-episodes 8 --lr 1e-6 \
  --output results/local-hf.json
```

实现加载并训练全部模型参数，还复制一份冻结参考模型，内存需求包括权重、梯度、优化器状态与激活。请选择适合机器的小模型。输入为普通文本 prompt；六个候选动作包含 EOS，通过候选序列得分的 softmax 定义动作分布，不是模型的自由解码分布。

没有 checkpoint 时可执行离线接口检查：

```bash
python3 smoke_hf.py
```

脚本在临时目录创建随机微型 GPT-2，验证本地加载、分布归一化、非零反向梯度与训练循环，不需要网络。该结果不代表预训练模型能力。

## 文件与结果

- `environment.py`：六动作 harness、有限候选算法、公开 smoke test 与终局验证函数。
- `train.py`：表格 / 本地 LM 策略、组内裁剪更新、成功轨迹 SFT、评估与日志。
- `test_demo.py`：7 个训练契约测试。
- `smoke_hf.py`：可选的本地 LM 接口检查。
- `results/seed-{7,19,42}.json`：组内裁剪更新的原始记录。
- `results/rs-sft-{7,19,42}.json`：迭代式成功轨迹 SFT 对照。
- `results/hf-smoke.json`：随机微型语言模型的接口检查记录。

JSON 保存配置、运行时、训练指标与训练前后评估。示例不保存可部署 checkpoint，重新运行会从初始策略开始。结果文件名相同会覆盖，个人实验建议使用 `local-` 前缀。

## 实验范围

训练与评估是同一个修复任务，评估使用另外的验证输入；不能据此声称未见任务泛化或 RL 优于 SFT。环境状态由当前代码变体和步数构成，修复操作是预定义动作，属于人工缩小的任务。

harness 与验证器在代码职责上分离，但处于同一进程。这不是容器隔离，也不是可以安全执行任意不可信 Python 或 shell 的环境。
