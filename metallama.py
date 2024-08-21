

from langchain_huggingface.llms import HuggingFacePipeline
import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

llm = HuggingFacePipeline.from_model_id(
    model_id="akjindal53244/Llama-3.1-Storm-8B",
    task="text-generation",
    device=0,
    model_kwargs={"torch_dtype": torch.bfloat16},
    pipeline_kwargs={"max_new_tokens": 20}
)
from langchain_core.prompts import ChatPromptTemplate

chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI bot. Your name is {name}."),
        ("human", "Hello, how are you doing?"),
        ("ai", "I'm doing well, thanks!"),
        ("human", "{user_input}"),
    ]
)

chain = chat_template|llm.bind(skip_prompt=True)
print(chain.invoke({'name': 'Llama', 'user_input': 'What is 2 + 2?'}))
# Expected Output: {'role': 'assistant', 'content': '2 + 2 = 4'}
