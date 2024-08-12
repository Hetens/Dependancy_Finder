from Attempt1.util_multi import list_files, get_file_extensions, match_file_extensions, writing_full_file_parallel
from dotenv import load_dotenv  
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# print(len(paths), len(contents))
def main():
    load_dotenv()   
    directory = os.getenv('CODEBASE')
    if not directory:
        logging.error("CODEBASE environment variable is not set.")
        return
    
    logging.info(f"Analyzing codebase in {directory}")
    codebase_structure = list_files(directory)
    file_extensions = get_file_extensions(codebase_structure)
    file_map = match_file_extensions(file_extensions, codebase_structure)
    relevant = ['c']
    file_map = {key: file_map[key] for key in relevant if key in file_map}

    file_to_path = {file: os.path.join(directory, file) for ext, files in file_map.items() for file in files}

    writing_full_file_parallel(file_to_path.values())



if __name__ == '__main__':
    main()