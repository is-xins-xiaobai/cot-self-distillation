"""
训练脚本：使用生成的CoT数据进行自蒸馏
"""

import json
import torch
import argparse
from pathlib import Path
from typing import List, Dict
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from tqdm import tqdm


class CoTDataset(Dataset):
    """CoT蒸馏数据集"""
    
    def __init__(
        self,
        data_path: str,
        tokenizer,
        max_length: int = 1024,
        format_template: str = "default"
    ):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.format_template = format_template
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # 格式化输入
        if self.format_template == "alpaca":
            text = f"""### Instruction:
Solve the following math problem step by step.

### Input:
{item['problem']}

### Response:
{item['cot']}"""
        
        elif self.format_template == "chat":
            text = f"""<|user|>
{item['problem']}

<|assistant|>
{item['cot']}"""
        
        else:  # default
            text = f"""Problem: {item['problem']}

Solution:
{item['cot']}"""
        
        # Tokenize
        tokenized = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        
        return {
            "input_ids": tokenized["input_ids"].squeeze(),
            "attention_mask": tokenized["attention_mask"].squeeze(),
            "labels": tokenized["input_ids"].squeeze()
        }


class CoTTrainer:
    """CoT自蒸馏训练器"""
    
    def __init__(
        self,
        model_name: str,
        train_data_path: str,
        output_dir: str,
        **kwargs
    ):
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载模型和tokenizer
        print(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # 设置pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        # 加载数据
        print(f"Loading training data: {train_data_path}")
        self.train_dataset = CoTDataset(
            train_data_path,
            self.tokenizer,
            max_length=kwargs.get("max_length", 1024),
            format_template=kwargs.get("format_template", "default")
        )
        
        print(f"Dataset size: {len(self.train_dataset)}")
    
    def train(
        self,
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-5,
        warmup_steps: int = 100,
        save_steps: int = 500,
        **kwargs
    ):
        """训练模型"""
        
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=kwargs.get("gradient_accumulation_steps", 4),
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            save_steps=save_steps,
            save_total_limit=3,
            logging_steps=10,
            fp16=True,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            **kwargs.get("extra_training_args", {})
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            data_collator=data_collator,
        )
        
        # 训练
        print("\n" + "="*50)
        print("Starting training...")
        print("="*50 + "\n")
        
        trainer.train()
        
        # 保存最终模型
        final_model_path = self.output_dir / "final_model"
        trainer.save_model(str(final_model_path))
        self.tokenizer.save_pretrained(str(final_model_path))
        
        print(f"\n✅ Training complete! Model saved to {final_model_path}")
        
        return trainer


def main():
    parser = argparse.ArgumentParser(
        description="Train model with CoT self-distillation"
    )
    
    # 模型参数
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Base model name or path'
    )
    parser.add_argument(
        '--train-data',
        type=str,
        required=True,
        help='Path to generated CoT training data (JSON)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='Output directory for checkpoints'
    )
    
    # 训练参数
    parser.add_argument(
        '--epochs',
        type=int,
        default=3,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=4,
        help='Batch size per device'
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=2e-5,
        help='Learning rate'
    )
    parser.add_argument(
        '--max-length',
        type=int,
        default=1024,
        help='Maximum sequence length'
    )
    parser.add_argument(
        '--gradient-accumulation-steps',
        type=int,
        default=4,
        help='Gradient accumulation steps'
    )
    parser.add_argument(
        '--warmup-steps',
        type=int,
        default=100,
        help='Number of warmup steps'
    )
    parser.add_argument(
        '--save-steps',
        type=int,
        default=500,
        help='Save checkpoint every N steps'
    )
    parser.add_argument(
        '--format-template',
        type=str,
        default='default',
        choices=['default', 'alpaca', 'chat'],
        help='Prompt format template'
    )
    
    args = parser.parse_args()
    
    # 创建训练器
    trainer_obj = CoTTrainer(
        model_name=args.model,
        train_data_path=args.train_data,
        output_dir=args.output_dir,
        max_length=args.max_length,
        format_template=args.format_template
    )
    
    # 训练
    trainer_obj.train(
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        warmup_steps=args.warmup_steps,
        save_steps=args.save_steps,
        gradient_accumulation_steps=args.gradient_accumulation_steps
    )


if __name__ == "__main__":
    main()
