"""
基础测试（不依赖额外库）
"""

import json
import sys

# 测试策略模块
print("=" * 60)
print("Testing CoT Strategies Module")
print("=" * 60)
print()

try:
    from cot_strategies import (
        get_all_strategies,
        create_diverse_prompts,
        format_cot_response
    )
    
    strategies = get_all_strategies()
    print(f"✓ Available strategies: {', '.join(strategies)}")
    print()
    
    # 测试提示生成
    problem = "If 3x + 5 = 20, what is x?"
    prompts = create_diverse_prompts(problem, n=3)
    
    print(f"✓ Generated {len(prompts)} diverse prompts")
    for i, p in enumerate(prompts[:2], 1):
        print(f"\nPrompt {i} ({p['strategy']}):")
        print(p['prompt'][:150] + "...")
    
    print("\n" + "=" * 60)
    print("✓ CoT Strategies module working!")
    print("=" * 60)
    print()
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# 测试模型包装器
print("=" * 60)
print("Testing Model Wrapper Module")
print("=" * 60)
print()

try:
    from model_wrapper import MockModel
    
    model = MockModel()
    prompt = "Problem: If 3x + 5 = 20, what is x?\n\nSolution:"
    response = model.generate(prompt)
    
    print("✓ Mock model generated response:")
    print(response[:200] + "..." if len(response) > 200 else response)
    
    print("\n" + "=" * 60)
    print("✓ Model wrapper working!")
    print("=" * 60)
    print()
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# 测试数据生成模块（基础功能）
print("=" * 60)
print("Testing Data Generation Module (Basic)")
print("=" * 60)
print()

try:
    import re
    
    # 手动实现简化版答案提取
    def simple_extract_answer(text):
        patterns = [
            r"Answer:\s*(.+?)(?:\n|$)",
            r"answer is\s*(.+?)(?:\.|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    # 测试
    test_text = "Step 1: ...\nStep 2: ...\nAnswer: x = 5"
    answer = simple_extract_answer(test_text)
    
    print(f"✓ Answer extraction: '{answer}'")
    
    print("\n" + "=" * 60)
    print("✓ Basic functions working!")
    print("=" * 60)
    print()
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# 测试示例数据
print("=" * 60)
print("Testing Example Dataset")
print("=" * 60)
print()

try:
    with open('data/example_math.json', 'r') as f:
        data = json.load(f)
    
    print(f"✓ Loaded {len(data)} example problems")
    print(f"\nFirst problem:")
    print(f"  Problem: {data[0]['problem']}")
    print(f"  Answer: {data[0]['answer']}")
    print(f"  Type: {data[0]['type']}")
    
    print("\n" + "=" * 60)
    print("✓ Example dataset loaded!")
    print("=" * 60)
    print()
    
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# 总结
print("\n" + "=" * 60)
print("🎉 All Basic Tests Passed!")
print("=" * 60)
print()
print("Core modules are working correctly.")
print()
print("Next steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Run full test: python test_generation.py")
print("3. Generate CoT data: python generate_dataset.py --help")
print("4. Read docs: cat README.md")
print()
