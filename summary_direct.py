from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI, OpenAI
import httpx
from dotenv import load_dotenv
import os
from langchain.document_loaders.csv_loader import CSVLoader
import pandas as pd
load_dotenv()

# Load environment variables
api_key = os.getenv('API_KEY')
base_url = os.getenv('API_URL')

# Initialize HTTP client and LangChain LLM
http_client = httpx.Client(verify=False)
available_models = ["mixtral-8x7b-instruct-v01", "gemma-7b-it", "mistral-7b-instruct-v02", "llama-2-70b-chat", "phi-3-mini-128k-instruct", "llama-3-8b-instruct"]
model_selected = available_models[0]
langchain_llm = OpenAI(base_url=base_url, model=model_selected, http_client=http_client, api_key=api_key)

# Load and preprocess the CSV data
loader = CSVLoader(file_path="./output_dir/summarized_output_filtered.csv", encoding="utf-8", csv_args={'delimiter': ','})
data = loader.load()
df = pd.DataFrame(data)
line_numbers, paths = [], []
for row in df[2]:
    line_numbers.append(row[1].split("\n")[0].split(": ")[1].strip())
    paths.append(row[1].split("\n")[1].split(": ")[1].strip())

df['line_numbers'] = line_numbers
df['path'] = paths
df[['start_line', 'end_line']] = df['line_numbers'].str.split('-', expand=True)
df['start_line'] = df['start_line'].astype(int)
df['end_line'] = df['end_line'].astype(int)

# Extract code snippets
def get_code_snippet(path, start_line, end_line):
    path = path.replace("\\", "/")
    try:
        with open("./TestRepositories/" + path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            snippet = "".join(lines[start_line-1:end_line])
            return snippet
    except Exception as e:
        return None

df['code_snippet'] = df.apply(lambda row: get_code_snippet(row['path'], row['start_line'], row['end_line']), axis=1)
df = df.dropna(subset=['code_snippet'])

# Truncate the code snippets to avoid exceeding token limits
df['code_snippet'] = df['code_snippet'].apply(lambda x: x[:1000])  # Adjust length as needed

# Create and invoke the agent with the reduced DataFrame
agent = create_pandas_dataframe_agent(langchain_llm, df, verbose=True, allow_dangerous_code=True)
result = agent.invoke("What files will be useful for testing the project in its entirety?")
print(result)
