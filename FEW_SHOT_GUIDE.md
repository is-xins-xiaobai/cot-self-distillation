# Few-Shot Learning with Different CoT Strategies

## 🎯 核心概念

**同样的3个数学问题，但每个CoT策略用不同的推理方式展示！**

这样模型可以学习到：
- ✅ 同一问题可以有多种正确推理路径
- ✅ 不同策略的推理模式
- ✅ 如何在保持正确性的前提下增加多样性

---

## 📚 Few-Shot示例结构

### 3个共享的问题

所有策略都使用这3个相同的问题作为示例：

1. **代数问题**: "If 3x + 5 = 20, what is the value of x?"
2. **几何问题**: "A rectangle has length 12 cm and width 8 cm. What is its perimeter?"
3. **百分比问题**: "What is 25% of 80?"

### 5种不同的推理策略

每个策略对这3个问题有不同的推理方式：

| 策略 | 特点 | 示例开头 |
|------|------|---------|
| **Forward** | 从已知到未知，逐步推导 | "Step 1: Identify the given information" |
| **Backward** | 从目标倒推，确定需要什么 | "Step 1: Identify the goal" |
| **Analogy** | 识别问题类型，应用模式 | "Step 1: Recognize the problem type" |
| **Cases** | 分情况讨论，分步骤处理 | "Step 1: Consider the equation structure" |
| **Verify** | 边做边验证，每步检查 | "Step 1: Set up and check understanding" |

---

## 💡 示例对比

### 问题：If 3x + 5 = 20, what is x?

#### Forward Strategy（前向推导）
```
Step 1: Identify the given information
We have the equation: 3x + 5 = 20

Step 2: Isolate the variable term
Subtract 5 from both sides:
3x = 15

Step 3: Solve for the variable
Divide both sides by 3:
x = 5

Step 4: Verify the solution
Substitute x = 5 back: 3(5) + 5 = 20 ✓
```

#### Backward Strategy（目标倒推）
```
Step 1: Identify the goal
We need to find: x

Step 2: Work backwards - what leads to the goal?
To find x, we need to isolate it
To isolate 3x, we need to remove the +5

Step 3: Apply the reverse operations
Undo the +5: 20 - 5 = 15, so 3x = 15
Undo the ×3: 15 ÷ 3 = 5, so x = 5

Step 4: Confirm by working forward
3(5) + 5 = 20 ✓
```

#### Analogy Strategy（类比推理）
```
Step 1: Recognize the problem type
This is a linear equation of the form ax + b = c
Similar to problems like 2x + 3 = 11

Step 2: Recall the standard approach
- Move constant to right (subtraction)
- Divide by coefficient of x

Step 3: Apply the method
Subtract 5: 3x = 15
Divide by 3: x = 5

Step 4: Verify like we do for all linear equations
3(5) + 5 = 20 ✓
```

**同样的问题，3种完全不同的推理路径，但都得到正确答案！**

---

## 🚀 使用方法

### 方法1：使用Python API

```python
from few_shot_examples import format_few_shot_prompt, get_few_shot_examples

# 获取特定策略的3个示例
forward_examples = get_few_shot_examples("forward")
print(f"Strategy has {len(forward_examples)} examples")

# 为新问题生成few-shot提示
new_problem = "If 5y - 3 = 22, what is y?"
prompt = format_few_shot_prompt("forward", new_problem)

# 使用模型生成
from model_wrapper import create_model
model = create_model(backend="openai", model_name="gpt-4")
response = model.generate(prompt)
```

### 方法2：使用命令行脚本

```bash
# 使用few-shot生成CoT数据
python3 generate_with_fewshot.py \
  --input data/example_math.json \
  --output data/cot_fewshot.json \
  --backend openai \
  --model gpt-4 \
  --samples-per-strategy 2
```

---

## 📊 完整的Few-Shot提示示例

当你为一个新问题生成few-shot提示时，格式如下：

```
Solve the following math problems step by step using forward reasoning.

Example 1:
Problem: If 3x + 5 = 20, what is the value of x?

Solution:
[完整的forward策略推理过程]

Answer: 5

============================================================

Example 2:
Problem: A rectangle has length 12 cm and width 8 cm. What is its perimeter?

Solution:
[完整的forward策略推理过程]

Answer: 40

============================================================

Example 3:
Problem: What is 25% of 80?

Solution:
[完整的forward策略推理过程]

Answer: 20

============================================================

Now solve this problem:
Problem: [你的新问题]

Solution:
```

模型会看到3个同类型推理的示例，然后生成类似风格的推理。

---

## 🔬 为什么这样设计？

### 1. 一致性 + 多样性

- **一致的问题**: 所有策略都用相同的3个问题
  - 公平对比不同策略
  - 确保难度一致
  
- **多样的推理**: 每个策略有不同的推理方式
  - 避免模型只学会一种思路
  - 提升泛化能力

### 2. 训推对齐

训练时：
- 模型看到5种策略的few-shot示例
- 学会识别和应用不同推理模式

推理时：
- 可以随机选择策略，或使用自我一致性
- 多种推理路径投票得到最终答案

### 3. 避免过拟合

如果每个策略用不同的问题作为示例：
- ❌ 策略A只见过问题1，策略B只见过问题2
- ❌ 模型可能过拟合特定问题类型

使用相同的3个问题：
- ✅ 所有策略都见过所有示例问题
- ✅ 区别在于推理方式，不是问题本身
- ✅ 模型学到的是"如何思考"，不是"如何回答特定问题"

---

## 🎓 示例问题的选择

我们选择的3个问题覆盖了基础数学的核心领域：

1. **代数**（线性方程）
   - 最常见的数学问题类型
   - 需要逐步操作和验证

2. **几何**（周长计算）
   - 空间和图形问题
   - 需要公式应用

3. **百分比**（比例计算）
   - 实用性强
   - 多种解法

这3个问题：
- ✅ 难度适中（Level 1-2）
- ✅ 解法明确
- ✅ 覆盖不同领域
- ✅ 适合展示不同推理策略

---

## 📈 与Zero-Shot和标准Few-Shot的对比

| 方法 | 示例数量 | 推理多样性 | 效果 |
|------|---------|-----------|------|
| **Zero-Shot** | 0 | 低 | 基线 |
| **Few-Shot (单一策略)** | 3 | 中 | 好 |
| **Few-Shot (多策略)** | 3×5=15 | 高 | **最好** |

我们的方法：
- 每个策略有3个示例
- 5个策略共享相同的3个问题
- 总共展示15个不同的推理路径（3问题 × 5策略）

---

## 🔧 自定义Few-Shot示例

### 添加新问题

编辑 `few_shot_examples.py`:

```python
SHARED_PROBLEMS = [
    {
        "problem": "你的新问题1",
        "answer": "答案1"
    },
    {
        "problem": "你的新问题2",
        "answer": "答案2"
    },
    {
        "problem": "你的新问题3",
        "answer": "答案3"
    }
]

# 然后为每个策略编写对应的推理过程
FORWARD_EXAMPLES = [
    {
        "problem": "你的新问题1",
        "cot": "...",  # Forward策略的推理
        "answer": "答案1"
    },
    # ... 其他2个问题
]

# 为所有5个策略重复
```

### 添加新策略

```python
# 定义新策略的示例
MY_STRATEGY_EXAMPLES = [
    # 同样的3个问题，但用你的新策略推理
    ...
]

# 在get_few_shot_examples中添加
strategy_map["my_strategy"] = MY_STRATEGY_EXAMPLES
```

---

## 🧪 测试Few-Shot系统

```bash
# 查看所有策略的示例
python3 few_shot_examples.py

# 测试生成（使用Mock模型，无需API key）
python3 generate_with_fewshot.py \
  --input data/example_math.json \
  --output data/test_fewshot.json \
  --backend mock \
  --limit 2
```

---

## 📚 参考文献

- **Few-Shot Learning**: Brown et al., "Language Models are Few-Shot Learners" (GPT-3 paper)
- **Chain-of-Thought**: Wei et al., "Chain-of-Thought Prompting Elicits Reasoning"
- **Self-Consistency**: Wang et al., "Self-Consistency Improves Chain of Thought Reasoning"

---

## ✅ 总结

**核心优势**：
- ✨ 同样的3个问题，5种不同推理方式
- 🎯 学习"如何思考"而非"记住答案"
- 🔄 训练和推理保持一致
- 📈 比单一策略few-shot效果更好

**使用建议**：
- 对于小模型（<7B）：使用few-shot效果显著
- 对于大模型（70B+）：few-shot仍有提升空间
- 结合自我一致性：多策略生成+投票

**下一步**：
- 运行 `python3 few_shot_examples.py` 查看示例
- 使用 `generate_with_fewshot.py` 生成数据
- 阅读完整代码了解实现细节

🎉 **享受多样化的few-shot CoT推理！**
