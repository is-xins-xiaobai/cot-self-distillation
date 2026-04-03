"""
使用Few-Shot示例生成CoT数据
每个策略使用相同的3个问题作为示例，但推理方式不同
"""

import argparse
import json
from typing import List, Dict
from tqdm import tqdm

from model_wrapper import create_model
from few_shot_examples import format_few_shot_prompt, get_few_shot_examples
from data_generation import (
    extract_answer,
    answers_match,
    score_reasoning_quality
)


def generate_cot_with_fewshot(
    problem: str,
    ground_truth_answer: str,
    model,
    strategy: str = "forward"
) -> Dict:
    """
    使用few-shot示例生成单个CoT
    
    Args:
        problem: 问题
        ground_truth_answer: 标准答案
        model: 模型
        strategy: CoT策略
    
    Returns:
        CoT数据字典或None
    """
    # 生成few-shot提示
    prompt = format_few_shot_prompt(strategy, problem)
    
    try:
        # 生成响应
        response = model.generate(
            prompt,
            temperature=0.7,
            max_tokens=512,
            top_p=0.9
        )
        
        # 提取答案
        answer = extract_answer(response)
        
        # 验证答案
        if answer and answers_match(answer, ground_truth_answer):
            # 评估质量
            quality = score_reasoning_quality(response)
            
            return {
                "problem": problem,
                "strategy": strategy,
                "cot": response,
                "answer": answer,
                "quality_score": quality,
                "method": "few-shot"
            }
    
    except Exception as e:
        print(f"Error generating CoT: {e}")
    
    return None


def generate_dataset_with_fewshot(
    problems: List[Dict],
    model,
    output_path: str,
    strategies: List[str] = None,
    samples_per_strategy: int = 2,
    quality_threshold: float = 0.5
):
    """
    为数据集生成few-shot CoT数据
    
    Args:
        problems: 问题列表
        model: 模型
        output_path: 输出路径
        strategies: 使用的策略列表
        samples_per_strategy: 每个策略生成的样本数
        quality_threshold: 质量阈值
    """
    if strategies is None:
        strategies = ["forward", "backward", "analogy", "cases", "verify"]
    
    all_data = []
    skipped = 0
    
    for item in tqdm(problems, desc="Generating few-shot CoT data"):
        problem = item["problem"]
        answer = item["answer"]
        
        problem_cots = []
        
        # 为每个策略生成样本
        for strategy in strategies:
            for _ in range(samples_per_strategy):
                cot_data = generate_cot_with_fewshot(
                    problem=problem,
                    ground_truth_answer=answer,
                    model=model,
                    strategy=strategy
                )
                
                if cot_data and cot_data["quality_score"] >= quality_threshold:
                    problem_cots.append(cot_data)
        
        # 检查是否有足够的高质量CoT
        if len(problem_cots) < 3:
            skipped += 1
            print(f"Skipping (only {len(problem_cots)} valid): {problem[:50]}...")
            continue
        
        # 按质量排序并选择最好的
        problem_cots.sort(key=lambda x: x["quality_score"], reverse=True)
        selected = problem_cots[:5]  # 保留top-5
        
        all_data.extend(selected)
    
    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Generation Complete ===")
    print(f"Total problems: {len(problems)}")
    print(f"Problems skipped: {skipped}")
    print(f"Total CoT samples: {len(all_data)}")
    print(f"Average per problem: {len(all_data) / (len(problems) - skipped):.2f}")
    print(f"Strategy distribution:")
    
    from collections import Counter
    strategy_counts = Counter(item["strategy"] for item in all_data)
    for strategy, count in strategy_counts.items():
        print(f"  {strategy}: {count}")
    
    print(f"\nSaved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate CoT data using few-shot examples"
    )
    
    parser.add_argument('--input', required=True, help='Input problems JSON')
    parser.add_argument('--output', required=True, help='Output CoT data JSON')
    parser.add_argument('--backend', default='openai', help='Model backend')
    parser.add_argument('--model', default=None, help='Model name')
    parser.add_argument('--strategies', nargs='+', default=None, help='CoT strategies')
    parser.add_argument('--samples-per-strategy', type=int, default=2, help='Samples per strategy')
    parser.add_argument('--quality-threshold', type=float, default=0.5, help='Quality threshold')
    parser.add_argument('--limit', type=int, default=None, help='Limit problems (for testing)')
    
    args = parser.parse_args()
    
    # 加载问题
    print(f"Loading problems from {args.input}...")
    with open(args.input, 'r') as f:
        problems = json.load(f)
    
    if args.limit:
        problems = problems[:args.limit]
    
    print(f"Loaded {len(problems)} problems")
    
    # 创建模型
    print(f"\nInitializing {args.backend} model...")
    model = create_model(backend=args.backend, model_name=args.model)
    
    # 显示示例
    print("\nFew-shot example for 'forward' strategy:")
    examples = get_few_shot_examples("forward")
    print(f"  Problem 1: {examples[0]['problem']}")
    print(f"  Problem 2: {examples[1]['problem']}")
    print(f"  Problem 3: {examples[2]['problem']}")
    
    # 生成数据
    print(f"\nGenerating CoT data...")
    generate_dataset_with_fewshot(
        problems=problems,
        model=model,
        output_path=args.output,
        strategies=args.strategies,
        samples_per_strategy=args.samples_per_strategy,
        quality_threshold=args.quality_threshold
    )
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
