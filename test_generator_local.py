
###################################################################################################################################################
# Loading Libraries 
###################################################################################################################################################



from langchain.agents.agent_types import AgentType
from langchain.agents.initialize import initialize_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
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
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_huggingface.llms import HuggingFacePipeline
import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


###################################################################################################################################################
# Loading the LLMS
###################################################################################################################################################
# Load the transformers pipeline
llm = HuggingFacePipeline.from_model_id(
    model_id="akjindal53244/Llama-3.1-Storm-8B",
    task="text-generation",
    device="cuda",
    model_kwargs={"torch_dtype": torch.bfloat16},
    pipeline_kwargs={"max_new_tokens": 1000, "do_sample": True, "temperature": 0.01, "top_k": 100, "top_p": 0.95}
)


###################################################################################################################################################
# FILE READING TOOL AND CSV
###################################################################################################################################################



# Load the CSV file
try:
    df = pd.read_csv('./output_dir/summarized_output_filtered.csv')
    df = df[105:]
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
###################################################################################################################################################
# Writing to markdown
###################################################################################################################################################



def write_markdown_section(identified_nodes, test_scripts, output_file="output2.md", append=False, section = 1):
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
        
        # Create test_scripts directory if it doesn't exist
        os.makedirs("test_scripts", exist_ok=True)
        
        for i, script in enumerate(test_scripts, 1):
            script_filename = f"section_{section}_script_{i}.py"
            log_filename = f"section_{section}_script_{i}.log"
            
            # Write script to file
            script_path = os.path.join("test_scripts", script_filename)
            with open(script_path, "w") as script_file:
                script_file.write(script)
            
            # Write coverage to log file
            log_path = os.path.join("test_scripts", log_filename)
            with open(log_path, "w") as log_file:
                log_file.write(f"Coverage for {script_filename}:\n")
                for node in identified_nodes:
                    log_file.write(f"Coverage_files: {node['coverage_files']}\n")
                    log_file.write(f"Relevant Paths: {node['path']}\n")
                    log_file.write(f"line_numbers: {node['line_numbers']}\n")
                    log_file.write(f"  Task: {node['task']}\n")
        
            
            # Write reference to script and log in markdown
            f.write(f"### Script {i}\n\n")
            f.write(f"Script file: [{script_filename}](./test_scripts/{script_filename})\n")
            f.write(f"Coverage log: [{log_filename}](./test_scripts/{log_filename})\n")
            f.write("\n---\n\n")


###################################################################################################################################################
# TEST GENERATOR TOOL
###################################################################################################################################################



# Custom tool to generate test automation scripts
@retry(wait=wait_exponential(multiplier=1, min=4, max=6), stop=stop_after_attempt(3))
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
        - Task: {task}
        - File Contents: {file_contents}

        The script should:
        1. Set up the test environment.
        2. Provide detailed test cases for testing the file and its impact on a system level Testing the given functionality.
        3. Use the file contents to fulfill the Task Provided to generate the test cases.
        4. Clean up the test environment.
        If you are unable to provide code try and assert the file's existence.

        Please provide the complete Python script that can be executed directly(assume data if necessary).
        Write only PYTHON.
        """[:8192]
        prompt = PromptTemplate(
            input_variables=["coverage_files", "line_numbers", "task", "path", 'file_contents'],
            template=template
        )
        return llm.invoke(prompt.format(coverage_files = coverage_files,line_numbers = line_numbers,task = task, path=path, file_contents=file_contents)) # Truncate to 2000 characters
    except Exception as e:
        return f"Error generating test script: {e}"

test_generator_tool = Tool(
    name="TestGenerator",
    func=generate_test_script,
    description="Generates a test automation script given inputs in dictionary form with the keys 'coverage_files', 'line_numbers', 'task', and 'path'"
)
# Create the main agent
tools = [file_reader_tool, test_generator_tool]


###################################################################################################################################################
# INITIALIZE THE AGENT
###################################################################################################################################################



try:
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
        rate_limiter=rate_limiter
    )
except Exception as e:
    print(f"Error initializing agent: {e}")
    agent = None

#UTILITY FUNCTION TO EXTRACT DICTIONARIES FROM LLM OUTPUT
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


section_size = 5  # Reduced from 10 to 5
total_rows = len(df)
test_scripts = []
identified_nodes = []

start_time = time.time()
total_sections = (total_rows + section_size - 1) // section_size




###################################################################################################################################################
# MAIN LOOP
###################################################################################################################################################



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

        Select which values of files are most relevant for SYSTEM LEVEL test automation scripts.
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
                result = agent.invoke(f"""Use the TestGenerator tool to create a test script for: {script_input} 

                Read the files that you may need more information about to generate test scripts.
                You can use the file_reader tool to read the file contents. which takes the file_path and start_line and end_line as input in the form of a dictionary.
                """)
                print("The Script input for the following nodes are : ", script_input)
                print("-----------------------------------------------------------------------------------------------------------------")
                print("The result for the following nodes are : ", result)
                time.sleep(10)  # Increased delay between API calls
                test_scripts.append(result['output'])  # Truncate to 2000 characters
            else:
                print("Agent not initialized. Skipping test script generation.")

        write_markdown_section(identified_nodes, test_scripts, append=True, section = section)
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