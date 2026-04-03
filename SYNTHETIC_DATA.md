# Synthetic Math Problem Generation

## 🎯 Why Synthetic Data?

This project uses **synthetically generated math problems** instead of existing datasets like MATH500 for several important reasons:

### 1. Avoid Data Contamination
- ✅ No overlap with evaluation benchmarks (MATH, GSM8K, etc.)
- ✅ Prevents data leakage in research
- ✅ Ensures fair model evaluation

### 2. Privacy and Copyright
- ✅ No copyright concerns
- ✅ Freely shareable
- ✅ Commercial-use friendly

### 3. Unlimited Scalability
- ✅ Generate as many problems as needed
- ✅ Control difficulty distribution
- ✅ Customize problem types

### 4. Research Reproducibility
- ✅ Deterministic generation (with seed)
- ✅ Easy to recreate exact dataset
- ✅ Transparent data creation process

---

## 🏗️ Problem Generator Architecture

### Supported Problem Types

| Type | Examples | Difficulty |
|------|----------|-----------|
| **Arithmetic** | Multiplication, division, large sums | Level 1 |
| **Algebra** | Linear equations, consecutive numbers | Level 1-2 |
| **Geometry** | Area, perimeter (squares, rectangles, circles) | Level 1-2 |
| **Word Problems** | Work rate, distance, mixture | Level 1-2 |
| **Percentage** | Calculate %, price changes | Level 2 |
| **Sequences** | Arithmetic, geometric, recursive | Level 2-3 |
| **Set Theory** | Inclusion-exclusion, Venn diagrams | Level 2 |

### Design Principles

1. **Realistic Numbers** - Use practical ranges (not too small or too large)
2. **Integer Answers** - Avoid decimal complications for training
3. **Clear Wording** - Unambiguous problem statements
4. **Verifiable** - Easy to check correctness

---

## 📝 Usage Examples

### Basic Usage

```python
from synthetic_problem_generator import SyntheticMathGenerator

# Initialize generator with seed for reproducibility
generator = SyntheticMathGenerator(seed=42)

# Generate a single problem
problem = generator.generate_problem(problem_type="algebra")
print(problem)
```

**Output:**
```json
{
  "problem": "The sum of three consecutive integers is 45. What is the middle number?",
  "answer": "15",
  "level": 2,
  "type": "algebra",
  "source": "synthetic"
}
```

### Generate Specific Type

```python
# Arithmetic problem
arith = generator.generate_problem("arithmetic")

# Geometry problem
geom = generator.generate_problem("geometry")

# Random type
random = generator.generate_problem()
```

### Generate Full Dataset

```python
# Generate 1000 problems
dataset = generator.generate_dataset(
    n_problems=1000,
    output_file="data/synthetic_1000.json"
)

print(f"Generated {len(dataset)} problems")
```

### Command Line Generation

```bash
# Quick generation via Python command
python3 -c "
from synthetic_problem_generator import SyntheticMathGenerator
gen = SyntheticMathGenerator(seed=123)
gen.generate_dataset(500, 'data/my_dataset.json')
"
```

---

## 🔬 Example Problems

### Arithmetic
```
Problem: A bakery sells cupcakes in boxes of 6. If Sarah orders 17 boxes 
         for a party, how many cupcakes will she have in total?
Answer: 102
Level: 1
```

### Algebra
```
Problem: The sum of three consecutive even numbers is 54. What is the 
         largest of these three numbers?
Answer: 20
Level: 2
```

### Geometry
```
Problem: A square garden has a perimeter of 48 meters. What is the area 
         of this garden in square meters?
Answer: 144
Level: 1
```

### Word Problem
```
Problem: If 4 workers can complete a project in 12 days, how many days 
         will it take for 6 workers to complete the same project?
Answer: 8
Level: 2
```

### Percentage
```
Problem: A merchant buys goods for $800 and wants to make a 25% profit. 
         At what price should the merchant sell the goods?
Answer: 1000
Level: 2
```

### Sequence
```
Problem: A sequence starts with 5 and each subsequent term is obtained 
         by multiplying the previous term by 2 and subtracting 1. 
         What is the 4th term?
Answer: 39
Level: 3
```

### Set Theory
```
Problem: In a class of 30 students, 18 play basketball and 12 play soccer. 
         If 5 students play both sports, how many students play neither?
Answer: 5
Level: 2
```

---

## 🔄 Integration with CoT Pipeline

### Full Workflow

```bash
# Step 1: Generate synthetic problems
python3 -c "
from synthetic_problem_generator import SyntheticMathGenerator
SyntheticMathGenerator(seed=42).generate_dataset(
    n_problems=500,
    output_file='data/synthetic_500.json'
)
"

# Step 2: Generate CoT reasoning paths
python3 generate_dataset.py \
  --input data/synthetic_500.json \
  --output data/cot_synthetic_500.json \
  --backend openai \
  --model gpt-4 \
  --samples-per-problem 5

# Step 3: Train model
python3 train.py \
  --model meta-llama/Llama-2-7b-hf \
  --train-data data/cot_synthetic_500.json \
  --output-dir checkpoints/synthetic-trained \
  --epochs 3
```

---

## 🧪 Validation

All generated problems are:

- ✅ **Mathematically correct** - Answer verified during generation
- ✅ **Well-formed** - Clear problem statement
- ✅ **Difficulty-labeled** - Level 1-3 classification
- ✅ **Type-tagged** - Organized by topic
- ✅ **Source-marked** - "synthetic" tag for tracking

### Quality Checks

```python
from synthetic_problem_generator import SyntheticMathGenerator

generator = SyntheticMathGenerator()

# Generate and validate
for _ in range(100):
    problem = generator.generate_problem()
    
    # Check required fields
    assert "problem" in problem
    assert "answer" in problem
    assert "level" in problem
    assert "type" in problem
    assert problem["source"] == "synthetic"
    
    # Check answer is numeric
    assert problem["answer"].replace("-", "").isdigit()

print("✓ All checks passed!")
```

---

## 📊 Dataset Statistics

**Example dataset** (`data/example_math.json`):
- Total problems: 10
- All synthetic: ✓
- Difficulty distribution:
  - Level 1: 3 problems
  - Level 2: 5 problems
  - Level 3: 2 problems
- Problem types: 7 different types

**Scalability**:
- Can generate 10,000+ problems in minutes
- Fully deterministic with seed
- Balanced difficulty distribution

---

## 🎓 Educational Use

This generator is perfect for:

- **Research** - Clean training data without contamination
- **Teaching** - Generate practice problems for students
- **Benchmarking** - Create custom evaluation sets
- **Ablation studies** - Control for specific problem types

---

## 🔧 Customization

### Add New Problem Type

Edit `synthetic_problem_generator.py`:

```python
def generate_custom_problem(self) -> Tuple[str, str, int]:
    """Your custom problem type"""
    # Your generation logic
    problem = "..."
    answer = "..."
    level = 2
    return problem, answer, level

# Add to problem_generators dict
problem_generators["custom"] = self.generate_custom_problem
```

### Adjust Difficulty

Modify number ranges in generator methods:

```python
# Make harder
a = random.randint(100, 500)  # Instead of (5, 20)

# Make easier  
a = random.randint(2, 10)  # Instead of (20, 100)
```

---

## 📚 References

- **Integer Arithmetic**: All operations use integer arithmetic
- **Word Problems**: Based on classic problem templates
- **Geometric Formulas**: Standard area/perimeter formulas
- **Set Theory**: Inclusion-exclusion principle

---

## ✅ Summary

- ✨ **7 problem types** with balanced difficulty
- 🎲 **Deterministic generation** (seed-based)
- 🚀 **Unlimited scalability** 
- 🔒 **No data contamination**
- 📖 **Well-documented** and easy to use

**Use synthetic data to ensure clean, reproducible research!** 🎯
