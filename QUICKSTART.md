# 🚀 Quick Start Guide

## 最快上手方式（5分钟）

### 1. 安装依赖

```bash
cd ~/Projects/cot_self_distillation
pip install -r requirements.txt
```

### 2. 运行测试

```bash
python test_generation.py
```

这会运行所有组件测试，不需要API key。

### 3. 使用示例数据生成CoT

```bash
python generate_dataset.py \
  --input data/example_math.json \
  --output data/example_cot_output.json \
  --backend mock \
  --samples-per-problem 3
```

### 4. 检查输出

```bash
python -c "
import json
with open('data/example_cot_output.json', 'r') as f:
    data = json.load(f)
    print(f'Generated {len(data)} CoT samples')
    print(f'Sample:')
    print(json.dumps(data[0], indent=2))
"
```

## 使用真实模型（需要API key）

### OpenAI GPT-4

```bash
export OPENAI_API_KEY="your-api-key"

python generate_dataset.py \
  --input data/example_math.json \
  --output data/cot_gpt4.json \
  --backend openai \
  --model gpt-4 \
  --samples-per-problem 5
```

### 本地模型（vLLM）

```bash
python generate_dataset.py \
  --input data/example_math.json \
  --output data/cot_local.json \
  --backend vllm \
  --model /path/to/your/model \
  --samples-per-problem 5
```

## 训练示例

使用生成的数据训练模型：

```bash
python train.py \
  --model meta-llama/Llama-2-7b-hf \
  --train-data data/cot_gpt4.json \
  --output-dir checkpoints/test-run \
  --epochs 1 \
  --batch-size 2 \
  --max-length 512
```

## 完整Pipeline

运行完整的端到端流程：

```bash
chmod +x example_pipeline.sh
./example_pipeline.sh
```

（需要先配置脚本中的API key和模型路径）

## 常见问题

### Q: ModuleNotFoundError
A: 确保安装了所有依赖：`pip install -r requirements.txt`

### Q: CUDA out of memory
A: 减小batch size或使用8-bit量化

### Q: API rate limit
A: 添加重试逻辑或使用本地模型

## 下一步

1. 阅读完整文档：`README.md`
2. 尝试不同的CoT策略
3. 在MATH500上训练完整模型
4. 评估和调优

## 项目结构

```
cot_self_distillation/
├── cot_strategies.py         # CoT策略定义
├── data_generation.py         # 数据生成逻辑
├── model_wrapper.py           # 模型包装器
├── generate_dataset.py        # 数据生成脚本
├── train.py                   # 训练脚本
├── test_generation.py         # 测试脚本
├── example_pipeline.sh        # 完整Pipeline
├── data/
│   └── example_math.json      # 示例数据
├── requirements.txt           # 依赖
├── README.md                  # 完整文档
└── QUICKSTART.md             # 本文件
```

## 获取帮助

查看脚本帮助：

```bash
python generate_dataset.py --help
python train.py --help
```

祝使用愉快！🎉
