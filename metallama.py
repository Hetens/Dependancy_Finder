import transformers
import torch

model_id = "akjindal53244/Llama-3.1-Storm-8B"
pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device_map="auto",
)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"}
]

outputs = pipeline(messages, max_new_tokens=128, do_sample=True, temperature=0.01, top_k=100, top_p=0.95)
print(outputs[0]["generated_text"][-1])  # Expected Output: {'role': 'assistant', 'content': '2 + 2 = 4'}
