"""
主脚本：为MATH500等数据集生成CoT蒸馏数据
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict

from model_wrapper import create_model
from data_generation import generate_distillation_dataset
from cot_strategies import get_all_strategies


def load_math_dataset(file_path: str) -> List[Dict]:
    """
    加载MATH数据集
    
    支持格式:
    1. JSONL: 每行一个JSON对象
    2. JSON: 列表形式
    
    预期字段: problem, answer (必需), level, type (可选)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {file_path}")
    
    data = []
    
    # JSONL格式
    if file_path.suffix == '.jsonl':
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
    
    # JSON格式
    elif file_path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    # 验证必需字段
    for item in data:
        if 'problem' not in item or 'answer' not in item:
            raise ValueError("Dataset must contain 'problem' and 'answer' fields")
    
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Generate diverse CoT data for self-distillation"
    )
    
    # 数据集参数
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input dataset path (JSON or JSONL format)'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output path for generated CoT data'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of problems to process (for testing)'
    )
    
    # 模型参数
    parser.add_argument(
        '--backend',
        type=str,
        default='openai',
        choices=['openai', 'vllm', 'huggingface', 'together', 'mock'],
        help='Model backend'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Model name/path'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='API key (if needed)'
    )
    
    # 生成参数
    parser.add_argument(
        '--samples-per-problem',
        type=int,
        default=5,
        help='Number of CoT samples to keep per problem'
    )
    parser.add_argument(
        '--min-valid-cots',
        type=int,
        default=3,
        help='Minimum number of valid CoTs required per problem'
    )
    parser.add_argument(
        '--quality-threshold',
        type=float,
        default=0.5,
        help='Quality score threshold (0-1)'
    )
    parser.add_argument(
        '--strategies',
        type=str,
        nargs='+',
        default=None,
        help='CoT strategies to use (default: all)'
    )
    
    args = parser.parse_args()
    
    # 加载数据集
    print(f"Loading dataset from {args.input}...")
    dataset = load_math_dataset(args.input)
    print(f"Loaded {len(dataset)} problems")
    
    # 限制数量（用于测试）
    if args.limit:
        dataset = dataset[:args.limit]
        print(f"Limited to {len(dataset)} problems for testing")
    
    # 创建模型
    print(f"\nInitializing {args.backend} model...")
    model_kwargs = {}
    if args.api_key:
        model_kwargs['api_key'] = args.api_key
    
    model = create_model(
        backend=args.backend,
        model_name=args.model,
        **model_kwargs
    )
    print("Model ready!")
    
    # 显示策略
    strategies = args.strategies or get_all_strategies()
    print(f"\nUsing strategies: {', '.join(strategies)}")
    
    # 生成数据
    print(f"\nGenerating CoT distillation data...")
    print(f"- Samples per problem: {args.samples_per_problem}")
    print(f"- Min valid CoTs: {args.min_valid_cots}")
    print(f"- Quality threshold: {args.quality_threshold}")
    print()
    
    generate_distillation_dataset(
        math_dataset=dataset,
        model=model,
        output_path=args.output,
        samples_per_problem=args.samples_per_problem,
        min_valid_cots=args.min_valid_cots,
        quality_threshold=args.quality_threshold
    )
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
