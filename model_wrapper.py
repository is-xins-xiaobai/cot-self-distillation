"""
Model Wrapper for CoT Generation
支持OpenAI API, vLLM, HuggingFace等多种后端
"""

import os
from typing import Optional, List
from abc import ABC, abstractmethod

# ===== 抽象基类 =====

class ModelWrapper(ABC):
    """模型包装器抽象类"""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> str:
        """生成响应"""
        pass


# ===== OpenAI API =====

class OpenAIModel(ModelWrapper):
    """OpenAI API包装器"""
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop
        )
        return response.choices[0].message.content


# ===== vLLM =====

class VLLMModel(ModelWrapper):
    """vLLM包装器（适用于本地部署的大模型）"""
    
    def __init__(
        self,
        model_path: str,
        tensor_parallel_size: int = 1,
        gpu_memory_utilization: float = 0.9
    ):
        try:
            from vllm import LLM, SamplingParams
        except ImportError:
            raise ImportError("Please install vllm: pip install vllm")
        
        self.llm = LLM(
            model=model_path,
            tensor_parallel_size=tensor_parallel_size,
            gpu_memory_utilization=gpu_memory_utilization
        )
        self.SamplingParams = SamplingParams
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> str:
        sampling_params = self.SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop
        )
        
        outputs = self.llm.generate([prompt], sampling_params)
        return outputs[0].outputs[0].text


# ===== HuggingFace Transformers =====

class HuggingFaceModel(ModelWrapper):
    """HuggingFace Transformers包装器"""
    
    def __init__(
        self,
        model_name: str,
        device: str = "cuda",
        load_in_8bit: bool = False
    ):
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
        except ImportError:
            raise ImportError("Please install transformers: pip install transformers torch")
        
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        if load_in_8bit:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                load_in_8bit=True,
                device_map="auto"
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16
            ).to(device)
        
        self.model.eval()
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> str:
        import torch
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )
        
        # 处理stop tokens
        if stop:
            for stop_token in stop:
                if stop_token in generated_text:
                    generated_text = generated_text.split(stop_token)[0]
        
        return generated_text


# ===== Together API =====

class TogetherModel(ModelWrapper):
    """Together API包装器（支持多种开源模型）"""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        try:
            import together
        except ImportError:
            raise ImportError("Please install together: pip install together")
        
        together.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        self.model_name = model_name
        self.together = together
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> str:
        response = self.together.Complete.create(
            prompt=prompt,
            model=self.model_name,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop=stop
        )
        return response['output']['choices'][0]['text']


# ===== Mock Model for Testing =====

class MockModel(ModelWrapper):
    """测试用的Mock模型"""
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> str:
        # 简单的测试响应
        if "3x + 5 = 20" in prompt:
            return """Step 1: Given information
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
Substitute x = 5 back into the original equation:
3(5) + 5 = 15 + 5 = 20 ✓
The solution is correct.

Answer: x = 5"""
        
        return "Mock response for testing"


# ===== Factory Function =====

def create_model(
    backend: str = "openai",
    model_name: Optional[str] = None,
    **kwargs
) -> ModelWrapper:
    """
    创建模型包装器
    
    Args:
        backend: 后端类型 ("openai", "vllm", "huggingface", "together", "mock")
        model_name: 模型名称
        **kwargs: 其他参数
    
    Returns:
        ModelWrapper实例
    """
    if backend == "openai":
        model_name = model_name or "gpt-4"
        return OpenAIModel(model_name=model_name, **kwargs)
    
    elif backend == "vllm":
        if not model_name:
            raise ValueError("model_name required for vllm backend")
        return VLLMModel(model_path=model_name, **kwargs)
    
    elif backend == "huggingface":
        if not model_name:
            raise ValueError("model_name required for huggingface backend")
        return HuggingFaceModel(model_name=model_name, **kwargs)
    
    elif backend == "together":
        model_name = model_name or "meta-llama/Llama-2-70b-chat-hf"
        return TogetherModel(model_name=model_name, **kwargs)
    
    elif backend == "mock":
        return MockModel()
    
    else:
        raise ValueError(f"Unknown backend: {backend}")


if __name__ == "__main__":
    # 测试
    print("=== Testing Mock Model ===")
    model = create_model(backend="mock")
    
    prompt = """Problem: If 3x + 5 = 20, what is the value of x?

Solution:"""
    
    response = model.generate(prompt, temperature=0.7)
    print(response)
