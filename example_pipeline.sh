#!/bin/bash
# 完整的CoT自蒸馏Pipeline示例

set -e  # 遇到错误立即退出

echo "======================================="
echo "CoT Self-Distillation Pipeline"
echo "======================================="
echo ""

# ===== 配置 =====

# 数据路径
INPUT_DATA="data/math500.json"
COT_DATA="data/cot_distill_data.json"
TEST_DATA="data/math500_test.json"

# 模型配置
BACKEND="openai"  # 或 "vllm", "huggingface", "together"
TEACHER_MODEL="gpt-4"  # 用于生成CoT的教师模型
STUDENT_MODEL="meta-llama/Llama-2-7b-hf"  # 要训练的学生模型

# 生成参数
SAMPLES_PER_PROBLEM=5
MIN_VALID_COTS=3
QUALITY_THRESHOLD=0.5

# 训练参数
EPOCHS=3
BATCH_SIZE=4
LEARNING_RATE=2e-5
MAX_LENGTH=1024

# 输出目录
OUTPUT_DIR="checkpoints/llama2-7b-cot-distilled"

# ===== 步骤1: 准备数据 =====

echo "Step 1: Checking data..."
if [ ! -f "$INPUT_DATA" ]; then
    echo "Error: Input data $INPUT_DATA not found!"
    echo "Please prepare your MATH dataset in JSON format."
    echo ""
    echo "Expected format:"
    echo '['
    echo '  {'
    echo '    "problem": "If 3x + 5 = 20, what is x?",'
    echo '    "answer": "5",'
    echo '    "level": 1,'
    echo '    "type": "algebra"'
    echo '  },'
    echo '  ...'
    echo ']'
    exit 1
fi

echo "✓ Input data found: $INPUT_DATA"
echo ""

# ===== 步骤2: 生成CoT数据 =====

echo "Step 2: Generating diverse CoT data..."
echo "This may take a while depending on dataset size..."
echo ""

python generate_dataset.py \
    --input "$INPUT_DATA" \
    --output "$COT_DATA" \
    --backend "$BACKEND" \
    --model "$TEACHER_MODEL" \
    --samples-per-problem $SAMPLES_PER_PROBLEM \
    --min-valid-cots $MIN_VALID_COTS \
    --quality-threshold $QUALITY_THRESHOLD

echo ""
echo "✓ CoT data generated: $COT_DATA"
echo ""

# 检查生成的数据
echo "Checking generated data..."
python -c "
import json
with open('$COT_DATA', 'r') as f:
    data = json.load(f)
print(f'Total CoT samples: {len(data)}')
print(f'Unique problems: {len(set(item[\"problem\"] for item in data))}')
print(f'Strategies used: {set(item[\"strategy\"] for item in data)}')
"
echo ""

# ===== 步骤3: 训练模型 =====

echo "Step 3: Training student model..."
echo "Model: $STUDENT_MODEL"
echo "Output: $OUTPUT_DIR"
echo ""

python train.py \
    --model "$STUDENT_MODEL" \
    --train-data "$COT_DATA" \
    --output-dir "$OUTPUT_DIR" \
    --epochs $EPOCHS \
    --batch-size $BATCH_SIZE \
    --learning-rate $LEARNING_RATE \
    --max-length $MAX_LENGTH \
    --gradient-accumulation-steps 4 \
    --warmup-steps 100 \
    --save-steps 500

echo ""
echo "✓ Training complete!"
echo "Model saved to: $OUTPUT_DIR/final_model"
echo ""

# ===== 步骤4: 评估（可选） =====

if [ -f "$TEST_DATA" ]; then
    echo "Step 4: Evaluating model..."
    echo ""
    
    python evaluate.py \
        --model "$OUTPUT_DIR/final_model" \
        --test-data "$TEST_DATA" \
        --use-self-consistency \
        --n-samples 5
    
    echo ""
    echo "✓ Evaluation complete!"
else
    echo "Step 4: Skipping evaluation (test data not found)"
fi

echo ""
echo "======================================="
echo "Pipeline Complete! 🎉"
echo "======================================="
echo ""
echo "Next steps:"
echo "1. Test the model with your own problems"
echo "2. Deploy to production"
echo "3. Monitor performance on new data"
echo ""
echo "Model location: $OUTPUT_DIR/final_model"
echo ""
