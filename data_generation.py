"""
CoT Data Generation for Self-Distillation
为MATH500等数据集生成多样化的CoT推理路径
"""

import json
import re
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm
import numpy as np
from cot_strategies import create_diverse_prompts, get_all_strategies

# ===== 答案提取 =====

def extract_answer(text: str) -> Optional[str]:
    """
    从CoT响应中提取最终答案
    
    支持多种格式:
    - Answer: xxx
    - The answer is xxx
    - \\boxed{xxx}
    - Final answer: xxx
    """
    # 尝试多种模式
    patterns = [
        r"Answer:\s*(.+?)(?:\n|$)",
        r"The answer is\s*(.+?)(?:\.|$)",
        r"\\boxed\{(.+?)\}",
        r"Final answer:\s*(.+?)(?:\n|$)",
        r"Therefore,\s*(.+?)(?:\.|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            answer = match.group(1).strip()
            # 清理答案
            answer = answer.rstrip('.')
            return answer
    
    # 如果都没匹配到，尝试提取最后一行
    lines = text.strip().split('\n')
    if lines:
        last_line = lines[-1].strip()
        if last_line:
            return last_line
    
    return None


def normalize_answer(answer: str) -> str:
    """
    归一化答案用于比较
    
    - 移除空格
    - 统一格式
    - 提取数值
    """
    if not answer:
        return ""
    
    # 移除空格
    answer = answer.replace(" ", "")
    
    # 提取数字（如果是纯数字答案）
    num_match = re.search(r'-?\d+\.?\d*', answer)
    if num_match:
        try:
            num = float(num_match.group())
            return str(num)
        except:
            pass
    
    return answer.lower().strip()


def answers_match(ans1: str, ans2: str, tolerance: float = 1e-6) -> bool:
    """
    判断两个答案是否匹配
    
    Args:
        ans1, ans2: 两个答案字符串
        tolerance: 数值比较的容差
    
    Returns:
        是否匹配
    """
    if not ans1 or not ans2:
        return False
    
    # 归一化
    ans1_norm = normalize_answer(ans1)
    ans2_norm = normalize_answer(ans2)
    
    # 字符串比较
    if ans1_norm == ans2_norm:
        return True
    
    # 数值比较
    try:
        num1 = float(ans1_norm)
        num2 = float(ans2_norm)
        return abs(num1 - num2) < tolerance
    except:
        return False


# ===== 推理质量评分 =====

def score_reasoning_quality(cot: str) -> float:
    """
    评估CoT推理的质量
    
    评分维度:
    1. 长度合理性（50-500词）
    2. 步骤清晰性（有明确的步骤标记）
    3. 计算准确性（有数学表达式）
    4. 完整性（有验证步骤）
    
    Returns:
        0-1之间的质量分数
    """
    score = 0.0
    
    # 1. 长度检查（0.2分）
    words = len(cot.split())
    if 50 <= words <= 500:
        score += 0.2
    elif 30 <= words < 50 or 500 < words <= 800:
        score += 0.1
    
    # 2. 步骤结构（0.3分）
    step_patterns = [
        r"Step \d+",
        r"\d+\.",
        r"First,|Second,|Third,|Finally,",
    ]
    step_count = sum(len(re.findall(p, cot, re.IGNORECASE)) for p in step_patterns)
    if step_count >= 4:
        score += 0.3
    elif step_count >= 2:
        score += 0.15
    
    # 3. 数学内容（0.3分）
    math_indicators = [
        r'\d+',  # 数字
        r'[+\-*/=]',  # 运算符
        r'\\frac|\\sqrt',  # LaTeX
        r'\$.*?\$',  # 数学公式
    ]
    math_count = sum(len(re.findall(p, cot)) for p in math_indicators)
    if math_count >= 10:
        score += 0.3
    elif math_count >= 5:
        score += 0.15
    
    # 4. 验证步骤（0.2分）
    verify_keywords = [
        "verify", "check", "confirm", "validation",
        "correct", "makes sense", "reasonable"
    ]
    if any(kw in cot.lower() for kw in verify_keywords):
        score += 0.2
    
    return score


# ===== 数据生成主函数 =====

def generate_diverse_cots_for_problem(
    problem: str,
    ground_truth_answer: str,
    model,
    n_samples: int = 10,
    strategies: List[str] = None
) -> List[Dict]:
    """
    为单个问题生成多条多样化的CoT推理路径
    
    Args:
        problem: 数学问题
        ground_truth_answer: 标准答案
        model: 生成模型（需要实现generate方法）
        n_samples: 每个策略生成的样本数
        strategies: 使用的策略列表
    
    Returns:
        有效的CoT列表，每个包含 {strategy, cot, answer, quality_score}
    """
    if strategies is None:
        strategies = get_all_strategies()
    
    valid_cots = []
    
    for strategy in strategies:
        # 为每个策略生成多个样本
        for sample_idx in range(n_samples):
            # 生成提示
            prompts = create_diverse_prompts(problem, n=len(strategies))
            prompt_data = [p for p in prompts if p['strategy'] == strategy][0]
            prompt = prompt_data['prompt']
            
            try:
                # 生成响应
                response = model.generate(
                    prompt,
                    temperature=0.7,  # 适度的温度保证多样性
                    max_tokens=512,
                    top_p=0.9
                )
                
                # 提取答案
                answer = extract_answer(response)
                
                # 验证答案正确性
                if answer and answers_match(answer, ground_truth_answer):
                    # 评估质量
                    quality = score_reasoning_quality(response)
                    
                    valid_cots.append({
                        "strategy": strategy,
                        "cot": response,
                        "answer": answer,
                        "quality_score": quality,
                        "sample_idx": sample_idx
                    })
                
            except Exception as e:
                print(f"Warning: Generation failed for strategy {strategy}: {e}")
                continue
    
    return valid_cots


def generate_distillation_dataset(
    math_dataset: List[Dict],
    model,
    output_path: str,
    samples_per_problem: int = 5,
    min_valid_cots: int = 3,
    quality_threshold: float = 0.5
):
    """
    为整个MATH数据集生成CoT蒸馏数据
    
    Args:
        math_dataset: 数学问题数据集
            格式: [{"problem": str, "answer": str, "level": int, "type": str}, ...]
        model: 生成模型
        output_path: 输出JSON路径
        samples_per_problem: 每个问题保留的样本数
        min_valid_cots: 每个问题至少需要的有效CoT数量
        quality_threshold: 质量分数阈值
    """
    distill_data = []
    skipped = 0
    
    for item in tqdm(math_dataset, desc="Generating CoT data"):
        problem = item["problem"]
        answer = item["answer"]
        
        # 生成多样化CoT
        cots = generate_diverse_cots_for_problem(
            problem=problem,
            ground_truth_answer=answer,
            model=model,
            n_samples=2  # 每个策略2个样本
        )
        
        # 过滤低质量CoT
        high_quality_cots = [
            cot for cot in cots 
            if cot["quality_score"] >= quality_threshold
        ]
        
        # 检查是否满足最小数量要求
        if len(high_quality_cots) < min_valid_cots:
            skipped += 1
            print(f"Skipping problem (only {len(high_quality_cots)} valid CoTs): {problem[:50]}...")
            continue
        
        # 按质量排序并选择top-k
        high_quality_cots.sort(key=lambda x: x["quality_score"], reverse=True)
        selected_cots = high_quality_cots[:samples_per_problem]
        
        # 保存
        for cot_data in selected_cots:
            distill_data.append({
                "problem": problem,
                "strategy": cot_data["strategy"],
                "cot": cot_data["cot"],
                "answer": cot_data["answer"],
                "quality_score": cot_data["quality_score"],
                "metadata": {
                    "level": item.get("level"),
                    "type": item.get("type"),
                    "original_answer": answer
                }
            })
    
    # 保存到文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(distill_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Generation Complete ===")
    print(f"Total problems processed: {len(math_dataset)}")
    print(f"Problems skipped: {skipped}")
    print(f"Total CoT samples generated: {len(distill_data)}")
    print(f"Average CoTs per problem: {len(distill_data) / (len(math_dataset) - skipped):.2f}")
    print(f"Saved to: {output_path}")


# ===== 自我一致性验证 =====

def self_consistency_verification(
    problem: str,
    model,
    n_samples: int = 5,
    threshold: float = 0.6
) -> Tuple[str, List[str]]:
    """
    使用自我一致性验证获取最可靠的答案
    
    Args:
        problem: 问题
        model: 模型
        n_samples: 采样数量
        threshold: 一致性阈值（多数投票占比）
    
    Returns:
        (consensus_answer, valid_cots): 共识答案和对应的CoT列表
    """
    # 生成多条推理路径
    cots = generate_diverse_cots_for_problem(
        problem=problem,
        ground_truth_answer="",  # 未知答案
        model=model,
        n_samples=n_samples
    )
    
    # 提取所有答案
    answers = [cot["answer"] for cot in cots]
    
    # 投票
    answer_counts = {}
    for ans in answers:
        norm_ans = normalize_answer(ans)
        answer_counts[norm_ans] = answer_counts.get(norm_ans, 0) + 1
    
    # 找到多数答案
    if not answer_counts:
        return None, []
    
    majority_answer = max(answer_counts, key=answer_counts.get)
    majority_count = answer_counts[majority_answer]
    
    # 检查是否达到阈值
    if majority_count / len(answers) < threshold:
        return None, []
    
    # 返回达成共识的答案和对应的CoT
    consensus_cots = [
        cot["cot"] for cot in cots
        if normalize_answer(cot["answer"]) == majority_answer
    ]
    
    return majority_answer, consensus_cots


if __name__ == "__main__":
    # 测试代码
    print("=== Testing Answer Extraction ===")
    test_texts = [
        "After calculation, the answer is 42.",
        "Therefore, x = 5\n\nFinal answer: 5",
        "We get $\\boxed{3.14}$",
    ]
    
    for text in test_texts:
        answer = extract_answer(text)
        print(f"Text: {text[:50]}...")
        print(f"Extracted: {answer}\n")
    
    print("\n=== Testing Quality Scoring ===")
    test_cot = """
Step 1: Given information
We have 3x + 5 = 20

Step 2: Solve for x
Subtract 5 from both sides: 3x = 15
Divide by 3: x = 5

Step 3: Verify
Check: 3(5) + 5 = 15 + 5 = 20 ✓

Answer: x = 5
"""
    score = score_reasoning_quality(test_cot)
    print(f"Quality score: {score:.2f}")
