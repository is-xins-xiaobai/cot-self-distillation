"""
Synthetic Math Problem Generator
生成合成数学问题用于CoT训练和测试
"""

import random
import json
from typing import List, Dict, Tuple


class SyntheticMathGenerator:
    """合成数学问题生成器"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
    
    def generate_arithmetic_problem(self) -> Tuple[str, str, int]:
        """生成基础算术问题"""
        operations = [
            ("multiplication", lambda a, b: a * b, "×"),
            ("division", lambda a, b: a // b, "÷"),
            ("addition_large", lambda a, b: a + b, "+"),
        ]
        
        op_name, op_func, op_symbol = random.choice(operations)
        
        if op_name == "multiplication":
            a = random.randint(5, 20)
            b = random.randint(10, 50)
            answer = op_func(a, b)
            problem = f"A shop sells items in packs of {a}. If a customer orders {b} packs, how many items will they receive in total?"
        
        elif op_name == "division":
            b = random.randint(5, 12)
            answer = random.randint(15, 40)
            a = answer * b
            problem = f"A total of {a} candies need to be divided equally among {b} children. How many candies will each child get?"
        
        else:  # addition_large
            a = random.randint(100, 500)
            b = random.randint(100, 500)
            answer = op_func(a, b)
            problem = f"A library has {a} books on the first floor and {b} books on the second floor. How many books does the library have in total?"
        
        return problem, str(answer), 1
    
    def generate_algebra_problem(self) -> Tuple[str, str, int]:
        """生成代数问题"""
        problem_types = ["linear_equation", "consecutive_numbers", "age_problem"]
        p_type = random.choice(problem_types)
        
        if p_type == "linear_equation":
            # ax + b = c, solve for x
            a = random.randint(2, 10)
            b = random.randint(-20, 20)
            x = random.randint(1, 20)
            c = a * x + b
            
            if b >= 0:
                problem = f"Solve for x: {a}x + {b} = {c}"
            else:
                problem = f"Solve for x: {a}x - {abs(b)} = {c}"
            
            answer = str(x)
            level = 2
        
        elif p_type == "consecutive_numbers":
            # Three consecutive numbers sum to S
            middle = random.randint(10, 30)
            total = (middle - 1) + middle + (middle + 1)
            
            problem = f"The sum of three consecutive integers is {total}. What is the middle number?"
            answer = str(middle)
            level = 2
        
        else:  # age_problem
            current_age = random.randint(20, 50)
            years_ago = random.randint(5, 15)
            past_age = current_age - years_ago
            
            problem = f"John is currently {current_age} years old. {years_ago} years ago, he was how old?"
            answer = str(past_age)
            level = 1
        
        return problem, answer, level
    
    def generate_geometry_problem(self) -> Tuple[str, str, int]:
        """生成几何问题"""
        shapes = ["square", "rectangle", "circle"]
        shape = random.choice(shapes)
        
        if shape == "square":
            side = random.randint(8, 25)
            
            if random.random() < 0.5:
                # Area problem
                area = side * side
                problem = f"A square has sides of length {side} cm. What is its area in square centimeters?"
                answer = str(area)
            else:
                # Perimeter problem
                perimeter = 4 * side
                problem = f"A square has a perimeter of {perimeter} meters. What is the length of one side?"
                answer = str(side)
            
            level = 1
        
        elif shape == "rectangle":
            length = random.randint(10, 30)
            width = random.randint(5, 15)
            area = length * width
            
            problem = f"A rectangular field is {length} meters long and {width} meters wide. What is its area?"
            answer = str(area)
            level = 1
        
        else:  # circle (simplified)
            radius = random.randint(5, 15)
            # Using pi ≈ 3.14 for simplicity
            area = int(3.14 * radius * radius)
            
            problem = f"A circular garden has a radius of {radius} meters. Using π ≈ 3.14, what is the approximate area of the garden in square meters? (Round to the nearest integer)"
            answer = str(area)
            level = 2
        
        return problem, answer, level
    
    def generate_word_problem(self) -> Tuple[str, str, int]:
        """生成应用题"""
        contexts = ["work_rate", "mixture", "distance"]
        context = random.choice(contexts)
        
        if context == "work_rate":
            workers1 = random.randint(3, 8)
            days1 = random.randint(8, 20)
            workers2 = random.randint(workers1 + 1, 12)
            
            # Work = workers * days is constant
            days2 = (workers1 * days1) // workers2
            
            problem = f"If {workers1} workers can complete a task in {days1} days, how many days will it take {workers2} workers to complete the same task?"
            answer = str(days2)
            level = 2
        
        elif context == "mixture":
            total = random.randint(100, 300)
            fraction = random.choice([0.25, 0.3, 0.4, 0.5, 0.6, 0.75])
            component = int(total * fraction)
            
            problem = f"A solution contains {total} ml of liquid, of which {int(fraction * 100)}% is water. How many ml of water is in the solution?"
            answer = str(component)
            level = 2
        
        else:  # distance
            speed = random.randint(40, 80)
            time = random.randint(2, 6)
            distance = speed * time
            
            problem = f"A car travels at {speed} km/h for {time} hours. What is the total distance traveled?"
            answer = str(distance)
            level = 1
        
        return problem, answer, level
    
    def generate_percentage_problem(self) -> Tuple[str, str, int]:
        """生成百分比问题"""
        original = random.randint(50, 500)
        percent = random.choice([10, 15, 20, 25, 30, 40, 50])
        
        if random.random() < 0.5:
            # Calculate percentage
            result = (original * percent) // 100
            problem = f"What is {percent}% of {original}?"
            answer = str(result)
        else:
            # Find total after increase
            increase = (original * percent) // 100
            total = original + increase
            problem = f"A price of ${original} is increased by {percent}%. What is the new price?"
            answer = str(total)
        
        return problem, answer, 2
    
    def generate_sequence_problem(self) -> Tuple[str, str, int]:
        """生成数列问题"""
        seq_types = ["arithmetic", "geometric", "recursive"]
        seq_type = random.choice(seq_types)
        
        if seq_type == "arithmetic":
            first = random.randint(3, 20)
            diff = random.randint(2, 8)
            n = random.randint(5, 10)
            
            nth_term = first + (n - 1) * diff
            
            problem = f"In an arithmetic sequence, the first term is {first} and the common difference is {diff}. What is the {n}th term?"
            answer = str(nth_term)
            level = 2
        
        elif seq_type == "geometric":
            first = random.randint(2, 5)
            ratio = random.randint(2, 3)
            n = random.randint(4, 6)
            
            nth_term = first * (ratio ** (n - 1))
            
            problem = f"In a geometric sequence, the first term is {first} and the common ratio is {ratio}. What is the {n}th term?"
            answer = str(nth_term)
            level = 3
        
        else:  # recursive
            # Fibonacci-like
            a, b = random.randint(1, 5), random.randint(5, 10)
            n = random.randint(5, 7)
            
            sequence = [a, b]
            for _ in range(n - 2):
                sequence.append(sequence[-1] + sequence[-2])
            
            problem = f"A sequence starts with {a}, {b}, and each term is the sum of the previous two terms. What is the {n}th term?"
            answer = str(sequence[-1])
            level = 3
        
        return problem, answer, level
    
    def generate_set_theory_problem(self) -> Tuple[str, str, int]:
        """生成集合论问题"""
        total = random.randint(30, 60)
        a = random.randint(total // 3, total * 2 // 3)
        b = random.randint(total // 3, total * 2 // 3)
        both = random.randint(2, min(a, b) // 2)
        
        # Using inclusion-exclusion
        neither = total - (a + b - both)
        
        problem = f"In a group of {total} people, {a} like coffee and {b} like tea. If {both} people like both drinks, how many people like neither coffee nor tea?"
        answer = str(neither)
        
        return problem, answer, 2
    
    def generate_problem(self, problem_type: str = None) -> Dict:
        """
        生成单个问题
        
        Args:
            problem_type: 问题类型，None则随机选择
        
        Returns:
            包含problem, answer, level, type的字典
        """
        problem_generators = {
            "arithmetic": self.generate_arithmetic_problem,
            "algebra": self.generate_algebra_problem,
            "geometry": self.generate_geometry_problem,
            "word_problem": self.generate_word_problem,
            "percentage": self.generate_percentage_problem,
            "sequence": self.generate_sequence_problem,
            "set_theory": self.generate_set_theory_problem,
        }
        
        if problem_type is None:
            problem_type = random.choice(list(problem_generators.keys()))
        
        if problem_type not in problem_generators:
            raise ValueError(f"Unknown problem type: {problem_type}")
        
        problem, answer, level = problem_generators[problem_type]()
        
        return {
            "problem": problem,
            "answer": answer,
            "level": level,
            "type": problem_type,
            "source": "synthetic"
        }
    
    def generate_dataset(
        self,
        n_problems: int = 100,
        output_file: str = None
    ) -> List[Dict]:
        """
        生成完整数据集
        
        Args:
            n_problems: 问题数量
            output_file: 输出文件路径（可选）
        
        Returns:
            问题列表
        """
        dataset = []
        
        for _ in range(n_problems):
            problem = self.generate_problem()
            dataset.append(problem)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)
            print(f"✓ Generated {n_problems} problems → {output_file}")
        
        return dataset


if __name__ == "__main__":
    # 测试生成器
    generator = SyntheticMathGenerator(seed=42)
    
    print("=== Synthetic Math Problem Generator Test ===\n")
    
    # 生成每种类型的示例
    types = ["arithmetic", "algebra", "geometry", "word_problem", 
             "percentage", "sequence", "set_theory"]
    
    for ptype in types:
        problem_data = generator.generate_problem(ptype)
        print(f"【{ptype.upper()}】")
        print(f"Problem: {problem_data['problem']}")
        print(f"Answer: {problem_data['answer']}")
        print(f"Level: {problem_data['level']}")
        print()
    
    # 生成小型数据集
    print("Generating example dataset...")
    dataset = generator.generate_dataset(
        n_problems=10,
        output_file="data/synthetic_example.json"
    )
    print(f"\n✓ Generated {len(dataset)} synthetic problems")
