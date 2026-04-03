"""
Few-Shot Examples for Different CoT Strategies
每个策略使用相同的3个问题，但推理方式不同
"""

# ===== 3个共享的问题 =====

SHARED_PROBLEMS = [
    {
        "problem": "If 3x + 5 = 20, what is the value of x?",
        "answer": "5"
    },
    {
        "problem": "A rectangle has length 12 cm and width 8 cm. What is its perimeter?",
        "answer": "40"
    },
    {
        "problem": "What is 25% of 80?",
        "answer": "20"
    }
]


# ===== 策略1: Forward Reasoning（前向推导）=====

FORWARD_EXAMPLES = [
    # Example 1
    {
        "problem": "If 3x + 5 = 20, what is the value of x?",
        "cot": """Step 1: Identify the given information
We have the equation: 3x + 5 = 20

Step 2: Isolate the variable term
Subtract 5 from both sides:
3x + 5 - 5 = 20 - 5
3x = 15

Step 3: Solve for the variable
Divide both sides by 3:
x = 15 ÷ 3
x = 5

Step 4: Verify the solution
Substitute x = 5 back into the original equation:
3(5) + 5 = 15 + 5 = 20 ✓

Answer: 5""",
        "answer": "5"
    },
    
    # Example 2
    {
        "problem": "A rectangle has length 12 cm and width 8 cm. What is its perimeter?",
        "cot": """Step 1: Identify what we know
Length = 12 cm
Width = 8 cm
We need to find: Perimeter

Step 2: Recall the formula
Perimeter of rectangle = 2 × (length + width)

Step 3: Substitute and calculate
Perimeter = 2 × (12 + 8)
Perimeter = 2 × 20
Perimeter = 40 cm

Step 4: Check if the answer makes sense
The perimeter should be larger than any single side.
40 > 12 and 40 > 8 ✓

Answer: 40""",
        "answer": "40"
    },
    
    # Example 3
    {
        "problem": "What is 25% of 80?",
        "cot": """Step 1: Understand what is being asked
We need to find 25% of 80
This means: (25/100) × 80

Step 2: Convert percentage to decimal
25% = 25/100 = 0.25

Step 3: Perform the multiplication
0.25 × 80 = 20

Step 4: Verify using an alternative method
25% is the same as 1/4
80 ÷ 4 = 20 ✓

Answer: 20""",
        "answer": "20"
    }
]


# ===== 策略2: Backward Reasoning（目标倒推）=====

BACKWARD_EXAMPLES = [
    # Example 1
    {
        "problem": "If 3x + 5 = 20, what is the value of x?",
        "cot": """Step 1: Identify the goal
We need to find: x
Target equation: 3x + 5 = 20

Step 2: Work backwards - what leads to the goal?
To find x, we need to isolate it
To isolate 3x, we need to remove the +5
To find x, we need to divide 3x by 3

Step 3: Apply the reverse operations
First, undo the +5: 20 - 5 = 15
So 3x = 15
Then, undo the ×3: 15 ÷ 3 = 5
So x = 5

Step 4: Confirm by working forward
3(5) + 5 = 15 + 5 = 20 ✓

Answer: 5""",
        "answer": "5"
    },
    
    # Example 2
    {
        "problem": "A rectangle has length 12 cm and width 8 cm. What is its perimeter?",
        "cot": """Step 1: What do we need to find?
Goal: Perimeter of the rectangle

Step 2: What formula gives us perimeter?
Perimeter = sum of all four sides
Or: Perimeter = 2 × (length + width)

Step 3: What do we have that leads to this?
We have: length = 12 cm, width = 8 cm
These are exactly what we need for the formula!

Step 4: Calculate the result
length + width = 12 + 8 = 20
Perimeter = 2 × 20 = 40 cm

Answer: 40""",
        "answer": "40"
    },
    
    # Example 3
    {
        "problem": "What is 25% of 80?",
        "cot": """Step 1: Define the target
We want: 25% of 80

Step 2: What operation gives us "percent of"?
"percent of" = multiplication
We need: (25/100) × 80

Step 3: Trace back to what we have
We have: 25 (the percentage) and 80 (the whole)
These are exactly what we need!

Step 4: Execute the calculation
25/100 = 0.25
0.25 × 80 = 20

Answer: 20""",
        "answer": "20"
    }
]


# ===== 策略3: Analogical Reasoning（类比推理）=====

ANALOGY_EXAMPLES = [
    # Example 1
    {
        "problem": "If 3x + 5 = 20, what is the value of x?",
        "cot": """Step 1: Recognize the problem type
This is a linear equation of the form ax + b = c
Similar to problems like 2x + 3 = 11

Step 2: Recall the standard approach for linear equations
- Move constant to the right side (subtraction)
- Divide by the coefficient of x

Step 3: Apply the method to our problem
Subtract 5 from both sides: 3x = 20 - 5 = 15
Divide by 3: x = 15/3 = 5

Step 4: Verify like we do for all linear equations
Substitute back: 3(5) + 5 = 20 ✓

Answer: 5""",
        "answer": "5"
    },
    
    # Example 2
    {
        "problem": "A rectangle has length 12 cm and width 8 cm. What is its perimeter?",
        "cot": """Step 1: Identify the problem pattern
This is a "perimeter of rectangle" problem
Like asking: "A fence around a rectangular field"

Step 2: Use the standard perimeter formula
For rectangles: P = 2(l + w)
This is the same pattern we always use

Step 3: Apply the formula
P = 2(12 + 8)
P = 2(20)
P = 40

Step 4: Check reasonableness
Perimeter ≈ 2×longer side + 2×shorter side
≈ 24 + 16 = 40 ✓

Answer: 40""",
        "answer": "40"
    },
    
    # Example 3
    {
        "problem": "What is 25% of 80?",
        "cot": """Step 1: Recognize as a percentage problem
Pattern: "What is X% of Y?"
Similar to: "What is 10% of 50?" or "What is 50% of 100?"

Step 2: Use the standard percentage method
X% of Y = (X/100) × Y
This pattern works for all percentage problems

Step 3: Apply to our specific case
25% of 80 = (25/100) × 80
= 0.25 × 80
= 20

Step 4: Quick check using benchmarks
25% is 1/4, and 80/4 = 20 ✓

Answer: 20""",
        "answer": "20"
    }
]


# ===== 策略4: Case Analysis（分类讨论）=====

CASES_EXAMPLES = [
    # Example 1
    {
        "problem": "If 3x + 5 = 20, what is the value of x?",
        "cot": """Step 1: Consider the equation structure
3x + 5 = 20
The coefficient of x is positive (Case: standard linear equation)

Step 2: Solve using algebraic manipulation
Case A: Isolate the term with x
3x = 20 - 5 = 15

Step 3: Continue solving
Case B: Solve for x
x = 15/3 = 5

Step 4: Verify the solution
Check: Does 3(5) + 5 = 20?
15 + 5 = 20 ✓
The solution is valid.

Answer: 5""",
        "answer": "5"
    },
    
    # Example 2
    {
        "problem": "A rectangle has length 12 cm and width 8 cm. What is its perimeter?",
        "cot": """Step 1: Break down the perimeter
A rectangle has 4 sides to consider:
- Two sides of length 12 cm
- Two sides of length 8 cm

Step 2: Calculate each case
Case 1: Length sides
2 × 12 = 24 cm

Step 3: Calculate second case
Case 2: Width sides
2 × 8 = 16 cm

Step 4: Combine all cases
Total perimeter = 24 + 16 = 40 cm

Answer: 40""",
        "answer": "40"
    },
    
    # Example 3
    {
        "problem": "What is 25% of 80?",
        "cot": """Step 1: Consider different calculation approaches
We can solve this in multiple ways:

Step 2: Method 1 - Direct percentage
25% = 25/100 = 0.25
0.25 × 80 = 20

Step 3: Method 2 - Using fractions
25% = 1/4
80 ÷ 4 = 20

Step 4: Both methods agree
Case 1 (decimal): 20
Case 2 (fraction): 20
Both give the same answer ✓

Answer: 20""",
        "answer": "20"
    }
]


# ===== 策略5: Verify as You Go（边做边验证）=====

VERIFY_EXAMPLES = [
    # Example 1
    {
        "problem": "If 3x + 5 = 20, what is the value of x?",
        "cot": """Step 1: Set up and check understanding
Equation: 3x + 5 = 20
Check: This is asking for x ✓

Step 2: First operation (subtract 5)
3x + 5 - 5 = 20 - 5
3x = 15
Check: 3x + 5 would give 20 if x is correct ✓

Step 3: Second operation (divide by 3)
x = 15 ÷ 3
x = 5
Check: 5 is a reasonable value for x ✓

Step 4: Final verification
Substitute x = 5: 3(5) + 5 = 15 + 5 = 20
Check: This matches the original equation ✓

Answer: 5""",
        "answer": "5"
    },
    
    # Example 2
    {
        "problem": "A rectangle has length 12 cm and width 8 cm. What is its perimeter?",
        "cot": """Step 1: Identify given values and verify
Length = 12 cm ✓
Width = 8 cm ✓
Check: Both values are positive ✓

Step 2: Calculate sum of length and width
12 + 8 = 20
Check: 20 is reasonable for (l + w) ✓

Step 3: Apply perimeter formula
Perimeter = 2 × 20 = 40 cm
Check: 40 > 12 and 40 > 8 ✓

Step 4: Cross-check by adding all sides
12 + 12 + 8 + 8 = 40 cm
Check: Same result ✓

Answer: 40""",
        "answer": "40"
    },
    
    # Example 3
    {
        "problem": "What is 25% of 80?",
        "cot": """Step 1: Convert percentage to decimal
25% = 25/100 = 0.25
Check: 0.25 is between 0 and 1 ✓

Step 2: Set up multiplication
0.25 × 80
Check: Result should be less than 80 ✓

Step 3: Calculate
0.25 × 80 = 20
Check: 20 < 80 ✓

Step 4: Verify using fraction method
25% = 1/4, so 80/4 = 20
Check: Both methods give 20 ✓

Answer: 20""",
        "answer": "20"
    }
]


# ===== 获取Few-Shot示例的函数 =====

def get_few_shot_examples(strategy: str) -> list:
    """
    获取指定策略的few-shot示例
    
    Args:
        strategy: CoT策略名称
    
    Returns:
        包含3个示例的列表
    """
    strategy_map = {
        "forward": FORWARD_EXAMPLES,
        "backward": BACKWARD_EXAMPLES,
        "analogy": ANALOGY_EXAMPLES,
        "cases": CASES_EXAMPLES,
        "verify": VERIFY_EXAMPLES
    }
    
    if strategy not in strategy_map:
        raise ValueError(f"Unknown strategy: {strategy}. Available: {list(strategy_map.keys())}")
    
    return strategy_map[strategy]


def format_few_shot_prompt(strategy: str, new_problem: str) -> str:
    """
    生成包含few-shot示例的完整提示
    
    Args:
        strategy: CoT策略
        new_problem: 新问题
    
    Returns:
        完整的few-shot提示
    """
    examples = get_few_shot_examples(strategy)
    
    prompt = f"Solve the following math problems step by step using {strategy} reasoning.\n\n"
    
    # 添加3个示例
    for i, example in enumerate(examples, 1):
        prompt += f"Example {i}:\n"
        prompt += f"Problem: {example['problem']}\n\n"
        prompt += f"Solution:\n{example['cot']}\n"
        prompt += "\n" + "="*60 + "\n\n"
    
    # 添加新问题
    prompt += f"Now solve this problem:\n"
    prompt += f"Problem: {new_problem}\n\n"
    prompt += f"Solution:"
    
    return prompt


if __name__ == "__main__":
    # 测试
    print("=== Few-Shot Examples Test ===\n")
    
    # 展示同一个问题在不同策略下的示例
    test_problem = "If 3x + 5 = 20, what is the value of x?"
    
    strategies = ["forward", "backward", "analogy", "cases", "verify"]
    
    for strategy in strategies:
        examples = get_few_shot_examples(strategy)
        example1 = examples[0]  # 第一个示例
        
        print(f"{'='*60}")
        print(f"Strategy: {strategy.upper()}")
        print(f"{'='*60}")
        print(f"Problem: {example1['problem']}\n")
        print("Solution:")
        print(example1['cot'][:200] + "...")
        print("\n")
    
    # 测试生成完整提示
    print("\n" + "="*60)
    print("Full Few-Shot Prompt Example (Forward Strategy)")
    print("="*60 + "\n")
    
    new_problem = "If 5y - 3 = 22, what is y?"
    prompt = format_few_shot_prompt("forward", new_problem)
    print(prompt[:500] + "...\n")
