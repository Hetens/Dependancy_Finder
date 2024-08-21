from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pandas as pd
import os
import re
from tenacity import retry, wait_exponential, stop_after_attempt
from langchain_groq import ChatGroq
import httpx
from tqdm import tqdm

os.environ["GROQ_API_KEY"] =str(os.getenv("GROQ_API_KEY"))
# Your existing setup code
http_client = httpx.Client(verify=False)
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0.3,
    http_client=http_client,
    max_tokens=None,
)
data_file = "./output_dir/output.txt"
output_file = './output_dir/summarized_output.csv'

# Your existing parse_output_file function
def parse_output_file(filepath):
    text = ''
    paths, contents = [], []
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    matches = re.finditer(r'C:/.*', text)
    matches1 = [match for match in matches]
    for match in matches1:
        match = match.group(0)
        match = match.split('/')[-1]
        paths.append(match)
    for match, match_next in zip(matches1[:-1], matches1[1:]):
        ending_index = match.span()[1]
        starting_index = match_next.span()[0]
        contents.append(text[ending_index:starting_index])
    return paths, contents

# Function to summarize text using Groq LLM
@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(3))
def summarize_chunk(chunk):
    prompt = PromptTemplate.from_template(
        """Summarize the following code snippet in one line, focusing on the main function or purpose.
        If it is a useless Chunk which servers no major purpose then just put 'N/A'\\\\n\\\\n{chunk}"""
    )
    summary = llm.invoke(prompt.format(chunk=chunk)).content
    return summary.strip()

# Function to write results to CSV
def write_to_csv(results, mode='a'):
    df = pd.DataFrame(results)
    df.to_csv(output_file, mode=mode, header=not os.path.exists(output_file), index=False)

# Main processing function
def process_data():
    paths, contents = parse_output_file(data_file)
    start_content = paths.index("vram\\UefiCpuPkg\\Library\\CpuExceptionHandlerLib\\LoongArch\\ExceptionCommon.c")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4096,
        chunk_overlap=200,
        length_function=len,
    )
    
    results = []
    total_chunks = sum(len(text_splitter.split_text(content)) for content in contents[start_content:]) #at the moment we have done 845 chunks+2680 chunks
    # Remove the output file if it exists
    # did 845 - 1451
    if os.path.exists(output_file):
        os.remove(output_file)
    
    with tqdm(total=total_chunks, desc="Processing chunks") as pbar:
        for path, content in zip(paths[start_content:], contents[start_content:]):
            chunks = text_splitter.split_text(content)
            start_line = 1
            for i, chunk in enumerate(chunks, 1):
                summary = summarize_chunk(chunk)
                end_line = start_line + chunk.count('\\\\n')
                results.append({
                    'line_numbers': f"{start_line}-{end_line}",
                    'path': path,
                    'main_function_inferred': summary
                })
                start_line = end_line + 1
                pbar.update(1)
                
                # Write to CSV after every 10 processings or if it's the last chunk
                if i % 10 == 0 or i == len(chunks):
                    write_to_csv(results)
                    results = []  # Clear the results list after writing
    
    print(f"\\\\nCSV file '{output_file}' has been created and updated incrementally.")

if __name__ == "__main__":
    process_data()