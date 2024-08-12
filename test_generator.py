from langchain.agents.agent_types import AgentType
from langchain.agents.initialize import initialize_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
import pandas as pd
import os
import ast
import json
import re
import time
from dotenv import load_dotenv
load_dotenv()
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
import os
os.environ["GROQ_API_KEY"]  =str(os.getenv("GROQ_API_KEY"))
from langchain_groq import ChatGroq
import httpx
http_client = httpx.Client(verify=False)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.1,
    http_client=http_client,
    max_tokens=1000,
    timeout=30,
    max_retries=2,
    # other params...
)
logging.basicConfig(level=logging.INFO)

# Load the CSV file
try:
    df = pd.read_csv('./output_dir/summarized_output_filtered.csv')
    df[['start_line', 'end_line']] = df['line_numbers'].str.split('-', expand=True)
except Exception as e:
    print(f"Error loading CSV file: {e}")
    df = pd.DataFrame()  # Create an empty DataFrame if file loading fails

# Function to get a section of the CSV
def get_csv_section(df, start_row, end_row):
    try:
        return df.iloc[start_row:end_row].to_dict(orient='records')
    except Exception as e:
        print(f"Error getting CSV section: {e}")
        return []

# Custom tool to read file contents
def read_file_contents(inputs):
    print("The input for the file reader tool is : ", inputs)
    try:
        dictionary = ast.literal_eval(inputs)
        file_path = dictionary['file_path']
        start_line = dictionary['start_line']
        end_line = dictionary['end_line']
        file_path = file_path.strip("'\"")
        full_path = os.path.join(os.getcwd(), 'TestRepositories', file_path)
        full_path = os.path.normpath(full_path)
        
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
                logging.info(f"Reading file: {full_path}")
                lines = file.readlines()
                snippet = "".join(lines[start_line-1:end_line])
                return snippet   # Truncate to 5000 characters
        return f"File not found: {full_path}"
    except Exception as e:
        return f"Error reading file: {e}"

file_reader_tool = Tool(
    name="FileReader",
    func=read_file_contents,
    description="Reads the contents of a file given its 'file_path' ,'start_line' and 'end_line' line numbers in dictionary format"
)

def write_markdown_section(identified_nodes, test_scripts, output_file="output1.md", append=False):
    mode = "a" if append else "w"
    with open(output_file, mode) as f:
        if not append:
            f.write("# LangChain Test Automation Results\n\n")
        
        f.write("## Identified Chunks\n\n")
        for node in identified_nodes:
            f.write(f"- Coverage_files: {node['coverage_files']}\n")
            f.write(f"  Relevant Paths: {node['path']}\n")
            f.write(f"  line_numbers: {node['line_numbers']}\n")
            f.write(f"  Task: {node['task']}\n")
        
        f.write("## Generated Test Scripts\n\n")
        for i, script in enumerate(test_scripts, 1):
            f.write(f"### Script {i}\n\n")
            f.write("```python\n")
            try:
                f.write(json.dumps(script, indent=2))
            except TypeError as e:
                f.write(f"Error serializing script: {e}\n")
                f.write(str(script))  # Fallback to string representation
            f.write("\n```\n\n")
            f.write("---\n\n")
# Custom tool to generate test automation scripts
@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def generate_test_script(inputs):
    try:
        dictionary = ast.literal_eval(inputs)
        coverage_files = dictionary['coverage_files']
        line_numbers = dictionary['line_numbers']
        path = dictionary['path']
        task = dictionary['task']
        file_contents = dictionary.get('file_contents', 'File contents not provided') # Truncate to 2000 characters

        template = """
        Create a Python test automation script for the following scenario:
        - Coverage Files: {coverage_files}
        - line numbers: {line_numbers}
        - Task: {task}
        - Path: {path}
        - File Contents: {file_contents}

        Note: contextual proximity implies that while creating the graph they appeared in the same chunk of text.
        The script should:
        1. Set up the test environment.
        2. Read the file contents from the given path if you need more information.
        3. Provide detailed test cases for testing the file and its impact on a system level Testing the given functionality.
        4. Write comprehensive tests for the edge with respect to the file contents or assume data if necessary.
        5. Clean up the test environment.
        If you are unable to provide code try and assert the file's existence.

        Please provide the complete Python script (assume data if necessary).
        """
        prompt = PromptTemplate(
            input_variables=["coverage_files", "line_numbers", "task", "path", 'file_contents'],
            template=template
        )
        return llm.invoke(prompt.format(coverage_files = coverage_files,line_numbers = line_numbers,task = task, path=path, file_contents=file_contents))  # Truncate to 2000 characters
    except Exception as e:
        return f"Error generating test script: {e}"

test_generator_tool = Tool(
    name="TestGenerator",
    func=generate_test_script,
    description="Generates a test automation script given inputs in dictionary form with the keys 'coverage_files', 'line_numbers', 'task', and 'path'"
)
# Create the main agent
tools = [file_reader_tool, test_generator_tool]

try:
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True
    )
except Exception as e:
    print(f"Error initializing agent: {e}")
    agent = None

# Function to extract list of dictionaries from LLM output
def extract_dicts_from_llm_output(output):
    try:
        dict_pattern = r'\{[^{}]*\}'
        dict_strings = re.findall(dict_pattern, output)
        
        dicts = []
        for d_str in dict_strings:
            try:
                d = ast.literal_eval(d_str)
                if isinstance(d, dict) and all(key in d for key in ['coverage_files', 'line_numbers', 'task', 'path']):
                    dicts.append(d)
            except:
                pass
        
        return dicts
    except Exception as e:
        print(f"Error extracting dictionaries from LLM output: {e}")
        return []

# Process the CSV in sections
section_size = 5  # Reduced from 10 to 5
total_rows = len(df)
test_scripts = []
identified_nodes = []

start_time = time.time()
total_sections = (total_rows + section_size - 1) // section_size

for section, start_row in enumerate(range(0, total_rows, section_size), 1):
    section_start_time = time.time()
    try:
        end_row = min(start_row + section_size, total_rows)
        csv_section = get_csv_section(df, start_row, end_row)

        elapsed_time = time.time() - start_time
        estimated_total_time = (elapsed_time / section) * total_sections
        estimated_time_left = estimated_total_time - elapsed_time

        print(f"\nProcessing rows {start_row} to {end_row - 1} (Section {section}/{total_sections}):")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(f"Estimated time left: {estimated_time_left:.2f} seconds")

        llm_context = f"""
        Here is a section of the CSV file (rows {start_row} to {end_row - 1}):

        {csv_section}

        Select which values of nodes, edges, paths are most relevant for SYSTEM LEVEL test automation scripts. Do not repeat nodes and edges.
        Assign them high or low priority for testing.
        Write them in dictionary format with keys: 'coverage_files', 'line_numbers', 'task', 'path'.
        Provide your selections as a list of dictionaries.
        """  # Truncate to 2000 characters

        llm_plan = llm.invoke(llm_context)
        time.sleep(10)  # Increased delay between API calls

        plan_list = extract_dicts_from_llm_output(llm_plan.content)

        for item in plan_list:
            coverage_files = item.get('coverage_files', 'Coverage files not provided')
            line_numbers = item.get('line_numbers', 'Line numbers not provided')
            task = item.get('task', 'Task not provided')
            path = item.get('path', 'Path not provided')
            
            identified_nodes.append({
                'coverage_files': coverage_files,
                'line_numbers': line_numbers,
                'task': task,
                'path': path

            })
            if r'\\\\' in path:
                path = path.replace(r'\\\\', '/')
            script_input = str({
                'coverage_files': coverage_files,
                'line_numbers': line_numbers,
                'task': task,
                'path': path
            })  # Truncate to 2000 characters
            if agent:
                result = agent.invoke(f"Use the TestGenerator tool to create a test script for: {script_input}")
                print("The Script input for the following nodes are : ", script_input)
                print("-----------------------------------------------------------------------------------------------------------------")
                print("The result for the following nodes are : ", result)
                time.sleep(10)  # Increased delay between API calls
                test_scripts.append(result)  # Truncate to 2000 characters
            else:
                print("Agent not initialized. Skipping test script generation.")

        write_markdown_section(identified_nodes, test_scripts, append=(section > 1))
        print(identified_nodes, test_scripts)
        identified_nodes = []
        test_scripts = []
        
        print("##############################################################################################################")
        section_time = time.time() - section_start_time
        print(f"Time taken for this section: {section_time:.2f} seconds")
        time.sleep(10)  # Increased delay between sections

    except Exception as e:
        print(f"Error processing rows {start_row} to {end_row - 1}: {e}")

total_time = time.time() - start_time
print(f"\nTotal processing time: {total_time:.2f} seconds")
print("Results have been written to output.md")