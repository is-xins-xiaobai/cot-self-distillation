# CoT Self-Distillation for Math Reasoning

基于多样化CoT的自蒸馏框架，用于提升数学推理能力。

## 🎯 核心思想

1. **结构化多样性**：固定外层4步框架，内层采用5种不同推理策略
2. **质量过滤**：只保留正确且高质量的推理路径
3. **训推一致**：训练和推理使用相同的结构化提示
4. **自我一致性**：推理时多路径投票提升鲁棒性

## 📦 安装

```bash
pip install torch transformers vllm openai together tqdm
```

## 🚀 快速开始

### 1. 准备数据

MATH500数据集格式（JSON或JSONL）：
```json
[
  {
    "problem": "If 3x + 5 = 20, what is the value of x?",
    "answer": "5",
    "level": 1,
    "type": "algebra"
  },
  ...
]
```

### 2. 生成CoT数据

```bash
python generate_dataset.py \
  --input data/math500.json \
  --output data/cot_distill_data.json \
  --backend openai \
  --model gpt-4 \
  --samples-per-problem 5 \
  --min-valid-cots 3 \
  --quality-threshold 0.5
```

**参数说明**：
- `--input`: 输入数据集路径
- `--output`: 输出CoT数据路径
- `--backend`: 模型后端（openai/vllm/huggingface/together/mock）
- `--model`: 模型名称
- `--samples-per-problem`: 每个问题保留的CoT数量
- `--min-valid-cots`: 每个问题最少需要的有效CoT
- `--quality-threshold`: 质量分数阈值（0-1）

### 3. 训练模型

```bash
python train.py \
  --model meta-llama/Llama-2-7b-hf \
  --train-data data/cot_distill_data.json \
  --output-dir checkpoints/llama2-7b-cot \
  --epochs 3 \
  --batch-size 4 \
  --learning-rate 2e-5 \
  --max-length 1024
```

### 4. 推理测试

```python
from model_wrapper import create_model
from data_generation import self_consistency_verification

# 加载训练好的模型
model = create_model(
    backend="huggingface",
    model_name="checkpoints/llama2-7b-cot/final_model"
)

# 使用自我一致性推理
problem = "If 3x + 5 = 20, what is the value of x?"
answer, cots = self_consistency_verification(problem, model, n_samples=5)

print(f"Answer: {answer}")
```

## 🎨 CoT策略

框架提供5种推理策略：

### 1. Forward Reasoning（前向推导）
```
Step 1: Identify what we know
Step 2: Set up the equation
Step 3: Solve step by step
Step 4: Verify the answer
```

### 2. Backward Reasoning（目标倒推）
```
Step 1: What do we need to find?
Step 2: What information leads to that?
Step 3: Connect what we have
Step 4: Confirm the solution
```

### 3. Analogical Reasoning（类比推理）
```
Step 1: Recognize the problem type
Step 2: Recall the standard approach
Step 3: Apply to our specific case
Step 4: Check against similar problems
```

### 4. Case Analysis（分类讨论）
```
Step 1: Break into cases
Step 2: Solve Case 1
Step 3: Solve Case 2
Step 4: Combine all cases
```

### 5. Verify as You Go（边做边验证）
```
Step 1: Start with validation mindset
Step 2: First calculation (verified)
Step 3: Next step (verified)
Step 4: Final verification
```

## 📊 数据生成流程

```
输入问题
    ↓
为每个策略生成2个样本（共10个）
    ↓
提取答案并验证正确性
    ↓
计算推理质量分数
    ↓
过滤低质量样本（threshold=0.5）
    ↓
按质量排序，保留top-5
    ↓
输出蒸馏数据
```

## 🔧 高级配置

### 使用本地模型（vLLM）

```bash
python generate_dataset.py \
  --input data/math500.json \
  --output data/cot_distill_data.json \
  --backend vllm \
  --model /path/to/llama-2-70b \
  --samples-per-problem 5
```

### 自定义策略

编辑 `cot_strategies.py` 中的 `STRATEGY_TEMPLATES`：

```python
STRATEGY_TEMPLATES["custom"] = {
    "name": "My Custom Strategy",
    "step1": ["First step prompt..."],
    "step2": ["Second step prompt..."],
    "step3": ["Third step prompt..."],
    "step4": ["Fourth step prompt..."],
}
```

### 并行生成（提速）

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_generate(dataset, model, n_workers=4):
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = [
            executor.submit(generate_diverse_cots_for_problem, item, model)
            for item in dataset
        ]
        results = [f.result() for f in futures]
    return results
```

## 📈 训练建议

### 渐进式训练

**阶段1**：高温多样性学习（epoch 1-2）
```python
training_args = TrainingArguments(
    learning_rate=5e-5,
    warmup_ratio=0.1,
    ...
)
```

**阶段2**：低温一致性学习（epoch 3-5）
```python
training_args = TrainingArguments(
    learning_rate=1e-5,
    warmup_ratio=0.05,
    ...
)
```

### 数据增强

对同一问题的多条CoT进行对比学习：

```python
# 在训练循环中
for problem, cots in grouped_data.items():
    # 所有正确CoT应该指向同一答案
    consistency_loss = contrastive_loss(cots)
    total_loss += consistency_loss
```

## 🧪 评估

使用MATH500测试集评估：

```bash
python evaluate.py \
  --model checkpoints/llama2-7b-cot/final_model \
  --test-data data/math500_test.json \
  --use-self-consistency \
  --n-samples 5
```

## 💡 最佳实践

### 避免训推不一致

✅ **正确做法**：
- 训练和推理都用相同的4步结构
- 训练时用temperature=0.7采样
- 推理时也用temperature=0.7采样
- 使用自我一致性投票

❌ **错误做法**：
- 训练时用结构化提示，推理时用自由格式
- 训练时贪心解码，推理时采样
- 训练时单一路径，推理时多路径

### 质量控制

1. **答案验证**：只保留答案正确的CoT
2. **质量评分**：过滤低质量推理
3. **多样性检查**：确保策略分布均匀
4. **人工抽查**：定期检查生成质量

### 数据规模建议

| 基础模型 | 推荐数据量 | CoT/问题 |
|---------|-----------|---------|
| 7B | 5K-10K | 3-5 |
| 13B | 10K-20K | 4-6 |
| 70B | 20K-50K | 5-8 |

## 🐛 常见问题

### Q: 生成速度太慢？
A: 使用vLLM本地部署，或者使用Together API批量生成。

### Q: 答案匹配失败？
A: 检查 `extract_answer()` 和 `normalize_answer()` 函数，可能需要针对数据集调整。

### Q: 质量分数都很低？
A: 降低 `--quality-threshold` 或检查质量评分函数。

### Q: 显存不足？
A: 减小 `--batch-size`，增加 `--gradient-accumulation-steps`，或使用8-bit量化。

## 📚 参考

- [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171)
- [Large Language Models are Zero-Shot Reasoners](https://arxiv.org/abs/2205.11916)
- [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465)

## 📄 License

MIT License

## 🙋 支持

如有问题，请提Issue或联系作者。
