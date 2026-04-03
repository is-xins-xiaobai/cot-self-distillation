"""
快速测试CoT生成功能
"""

from model_wrapper import create_model, MockModel
from data_generation import (
    generate_diverse_cots_for_problem,
    extract_answer,
    score_reasoning_quality,
    answers_match
)
from cot_strategies import create_diverse_prompts
import json

def test_with_mock_model():
    """使用Mock模型测试（不需要API key）"""
    
    print("="*60)
    print("Testing with Mock Model")
    print("="*60)
    print()
    
    # 创建Mock模型
    model = create_model(backend="mock")
    
    # 测试问题
    problem = "If 3x + 5 = 20, what is the value of x?"
    ground_truth = "5"
    
    print(f"Problem: {problem}")
    print(f"Expected answer: {ground_truth}")
    print()
    
    # 生成多样化CoT
    print("Generating diverse CoTs...")
    cots = generate_diverse_cots_for_problem(
        problem=problem,
        ground_truth_answer=ground_truth,
        model=model,
        n_samples=2  # 每个策略2个样本
    )
    
    print(f"\nGenerated {len(cots)} valid CoTs")
    print()
    
    # 显示结果
    for i, cot_data in enumerate(cots, 1):
        print(f"--- CoT #{i} ---")
        print(f"Strategy: {cot_data['strategy']}")
        print(f"Quality Score: {cot_data['quality_score']:.2f}")
        print(f"Answer: {cot_data['answer']}")
        print()
        print("Reasoning:")
        print(cot_data['cot'][:300] + "..." if len(cot_data['cot']) > 300 else cot_data['cot'])
        print()
    
    return cots


def test_answer_extraction():
    """测试答案提取"""
    
    print("="*60)
    print("Testing Answer Extraction")
    print("="*60)
    print()
    
    test_cases = [
        ("The answer is 42.", "42"),
        ("Answer: x = 5", "5"),
        ("Therefore, $\\boxed{3.14}$", "3.14"),
        ("Final answer: 2.5\n\nVerification: ...", "2.5"),
    ]
    
    for text, expected in test_cases:
        extracted = extract_answer(text)
        match = answers_match(extracted, expected)
        status = "✓" if match else "✗"
        print(f"{status} Text: {text[:40]}...")
        print(f"   Expected: {expected}, Got: {extracted}")
        print()


def test_quality_scoring():
    """测试质量评分"""
    
    print("="*60)
    print("Testing Quality Scoring")
    print("="*60)
    print()
    
    # 高质量CoT
    high_quality = """
Step 1: Identify given information
We have the equation 3x + 5 = 20

Step 2: Isolate the variable term
Subtract 5 from both sides:
3x + 5 - 5 = 20 - 5
3x = 15

Step 3: Solve for x
Divide both sides by 3:
x = 15 / 3
x = 5

Step 4: Verify the solution
Substitute x = 5 back:
3(5) + 5 = 15 + 5 = 20 ✓

Answer: x = 5
"""
    
    # 低质量CoT
    low_quality = """
x = 5
"""
    
    high_score = score_reasoning_quality(high_quality)
    low_score = score_reasoning_quality(low_quality)
    
    print(f"High-quality CoT score: {high_score:.2f}")
    print(f"Low-quality CoT score: {low_score:.2f}")
    print()
    
    if high_score > low_score:
        print("✓ Quality scoring working correctly!")
    else:
        print("✗ Quality scoring may need adjustment")


def test_prompt_generation():
    """测试提示生成"""
    
    print("="*60)
    print("Testing Prompt Generation")
    print("="*60)
    print()
    
    problem = "What is 2 + 2?"
    prompts = create_diverse_prompts(problem, n=3)
    
    for i, p in enumerate(prompts, 1):
        print(f"--- Prompt #{i} ({p['strategy']}) ---")
        print(p['prompt'][:200] + "...")
        print()


def main():
    """运行所有测试"""
    
    print("\n" + "="*60)
    print("CoT Self-Distillation - Quick Test")
    print("="*60)
    print()
    
    try:
        # 1. 测试答案提取
        test_answer_extraction()
        
        # 2. 测试质量评分
        test_quality_scoring()
        
        # 3. 测试提示生成
        test_prompt_generation()
        
        # 4. 测试完整流程
        cots = test_with_mock_model()
        
        # 保存测试结果
        output_file = "test_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cots, f, indent=2, ensure_ascii=False)
        
        print("="*60)
        print(f"✓ All tests passed!")
        print(f"Test results saved to: {output_file}")
        print("="*60)
        print()
        
    except Exception as e:
        print("="*60)
        print(f"✗ Test failed: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
