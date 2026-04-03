"""
CoT Strategy Templates for Math Reasoning
支持多种推理策略的CoT模板设计
"""

import random
from typing import List, Dict

# ===== 策略定义 =====

# 固定的外层结构（保证训推一致性）
FIXED_STRUCTURE = """Problem: {problem}

Solution:
{step1_header}
{step1_content}

{step2_header}
{step2_content}

{step3_header}
{step3_content}

{step4_header}
{step4_content}

Answer: {answer}"""


# 内层策略变体（提供多样性）
STRATEGY_TEMPLATES = {
    "forward": {
        "name": "Forward Reasoning",
        "step1": [
            "Let's identify what we know:",
            "First, let's list the given information:",
            "What information does the problem provide?",
        ],
        "step2": [
            "Now, let's set up the equation:",
            "We can formulate this as:",
            "This translates mathematically to:",
        ],
        "step3": [
            "Solving step by step:",
            "Let's calculate:",
            "Working through the computation:",
        ],
        "step4": [
            "Let's verify our answer:",
            "Checking if this makes sense:",
            "Verification:",
        ]
    },
    
    "backward": {
        "name": "Backward Reasoning",
        "step1": [
            "What do we need to find?",
            "Let's identify the goal:",
            "The target is to determine:",
        ],
        "step2": [
            "What information leads to that goal?",
            "Working backwards, we need:",
            "To find that, we must first know:",
        ],
        "step3": [
            "Now connecting what we have:",
            "Using the given information:",
            "Applying what we know:",
        ],
        "step4": [
            "Does this answer make sense?",
            "Let's confirm:",
            "Sanity check:",
        ]
    },
    
    "analogy": {
        "name": "Analogical Reasoning",
        "step1": [
            "This problem is similar to [type]:",
            "I recognize this as a [pattern] problem:",
            "This follows the [method] approach:",
        ],
        "step2": [
            "In this type of problem, we typically:",
            "The standard approach is:",
            "Following the pattern, we should:",
        ],
        "step3": [
            "Applying the method to our specific case:",
            "Adapting to our problem:",
            "With our numbers:",
        ],
        "step4": [
            "Checking against similar problems:",
            "Does this align with the pattern?",
            "Comparing to known solutions:",
        ]
    },
    
    "cases": {
        "name": "Case Analysis",
        "step1": [
            "Let's break this into cases:",
            "We need to consider different scenarios:",
            "This problem has multiple possibilities:",
        ],
        "step2": [
            "Case 1:",
            "First scenario:",
            "When condition A holds:",
        ],
        "step3": [
            "Case 2:",
            "Alternative scenario:",
            "When condition B holds:",
        ],
        "step4": [
            "Combining all cases:",
            "The complete solution is:",
            "Considering all possibilities:",
        ]
    },
    
    "verify": {
        "name": "Verify as You Go",
        "step1": [
            "Let's solve and verify at each step:",
            "We'll check our work as we proceed:",
            "Step-by-step with validation:",
        ],
        "step2": [
            "First calculation (checking...):",
            "Initial step (verified):",
            "Starting with:",
        ],
        "step3": [
            "Next step (checking...):",
            "Continuing (verified):",
            "Then:",
        ],
        "step4": [
            "Final verification:",
            "Cross-checking the complete solution:",
            "Ultimate sanity check:",
        ]
    }
}


def get_strategy_prompt(strategy: str, step: int) -> str:
    """获取特定策略的特定步骤提示"""
    if strategy not in STRATEGY_TEMPLATES:
        strategy = "forward"  # 默认策略
    
    step_key = f"step{step}"
    return random.choice(STRATEGY_TEMPLATES[strategy][step_key])


def get_all_strategies() -> List[str]:
    """获取所有可用策略"""
    return list(STRATEGY_TEMPLATES.keys())


def create_diverse_prompts(problem: str, n: int = 5) -> List[str]:
    """
    为同一问题创建多个多样化的CoT提示
    
    Args:
        problem: 数学问题
        n: 生成的提示数量
    
    Returns:
        多个不同策略的提示列表
    """
    strategies = get_all_strategies()
    prompts = []
    
    for i in range(n):
        strategy = strategies[i % len(strategies)]
        
        prompt = f"""Problem: {problem}

Please solve this step-by-step using the following approach:

Step 1: {get_strategy_prompt(strategy, 1)}
Step 2: {get_strategy_prompt(strategy, 2)}
Step 3: {get_strategy_prompt(strategy, 3)}
Step 4: {get_strategy_prompt(strategy, 4)}

Solution:"""
        
        prompts.append({
            "strategy": strategy,
            "prompt": prompt
        })
    
    return prompts


def format_cot_response(
    problem: str,
    step1: str,
    step2: str,
    step3: str,
    step4: str,
    answer: str,
    strategy: str = "forward"
) -> str:
    """
    格式化CoT响应为固定结构
    
    Args:
        problem: 问题
        step1-4: 四个推理步骤的内容
        answer: 最终答案
        strategy: 使用的策略
    
    Returns:
        格式化的CoT响应
    """
    template = STRATEGY_TEMPLATES[strategy]
    
    return FIXED_STRUCTURE.format(
        problem=problem,
        step1_header=f"Step 1: {random.choice(template['step1'])}",
        step1_content=step1,
        step2_header=f"Step 2: {random.choice(template['step2'])}",
        step2_content=step2,
        step3_header=f"Step 3: {random.choice(template['step3'])}",
        step3_content=step3,
        step4_header=f"Step 4: {random.choice(template['step4'])}",
        step4_content=step4,
        answer=answer
    )


# ===== 简化版本：单一灵活提示 =====

def get_flexible_cot_prompt(problem: str, variation: int = 0) -> str:
    """
    生成灵活的CoT提示（不固定策略，只固定结构）
    
    Args:
        problem: 数学问题
        variation: 变体编号（用于增加多样性）
    
    Returns:
        CoT提示
    """
    variations = [
        "Let's solve this step by step:",
        "Let's break down this problem:",
        "Let's work through this carefully:",
        "Let's approach this systematically:",
        "Let's think through this problem:",
    ]
    
    intro = variations[variation % len(variations)]
    
    return f"""{intro}

Problem: {problem}

Solution:
"""


if __name__ == "__main__":
    # 测试
    problem = "If 3x + 5 = 20, what is the value of x?"
    
    print("=== 测试多样化提示生成 ===\n")
    prompts = create_diverse_prompts(problem, n=3)
    
    for i, p in enumerate(prompts):
        print(f"策略 {i+1}: {p['strategy']}")
        print(p['prompt'])
        print("\n" + "="*60 + "\n")
    
    print("=== 测试格式化响应 ===\n")
    formatted = format_cot_response(
        problem=problem,
        step1="Given: 3x + 5 = 20",
        step2="Subtract 5 from both sides: 3x = 15",
        step3="Divide both sides by 3: x = 5",
        step4="Check: 3(5) + 5 = 15 + 5 = 20 ✓",
        answer="x = 5",
        strategy="forward"
    )
    print(formatted)
