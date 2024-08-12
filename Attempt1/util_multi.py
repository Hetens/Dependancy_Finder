import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import os
import csv
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def list_files(directory):
    """
    Recursively lists all files and directories in the given directory.
    """
    def recursive_list_files(root_path):
        structure = {'dir': {}, 'file': []}
        for root, dirs, files in os.walk(root_path):
            relative_path = os.path.relpath(root, directory)
            if relative_path == '.':
                current_dir = structure
            else:
                path_parts = relative_path.split(os.sep)
                current_dir = structure
                for part in path_parts:
                    current_dir = current_dir['dir'][part]
            
            for dir_name in dirs:
                current_dir['dir'][dir_name] = {'dir': {}, 'file': []}
            current_dir['file'].extend(files)

        return structure

    return recursive_list_files(directory)

def get_file_extensions(codebase_structure):
    """
    Get all the file extensions in the codebase.
    """
    file_extensions = set()

    def recursive_collect_files(structure):
        for file in structure['file']:
            extension = get_file_extension(file)
            file_extensions.add(extension)
        for subdir in structure['dir'].values():
            recursive_collect_files(subdir)

    recursive_collect_files(codebase_structure)
    return list(file_extensions)

def get_file_extension(filename):
    return os.path.splitext(filename)[1][1:].lower()

def match_file_extensions(file_extensions, codebase_structure):
    """
    Match the file extensions with the codebase structure.
    """
    file_map = {extension: [] for extension in file_extensions}

    def recursive_collect_files(structure, path=""):
        for file in structure['file']:
            extension = get_file_extension(file)
            file_map[extension].append(os.path.join(path, file))
        for subdir_name, subdir_structure in structure['dir'].items():
            recursive_collect_files(subdir_structure, os.path.join(path, subdir_name))

    recursive_collect_files(codebase_structure)
    return file_map

def read_file_with_fallback_encoding(filepath):
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'ascii']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    #raise ValueError(f"Unable to read file {filepath} with any of the attempted encodings.")

def analyze_file(filepath):
    """
    Analyzes a file for imports, class definitions, and function definitions
    using language-independent patterns.
    """
    try:
        file_content = read_file_with_fallback_encoding(filepath)
    except ValueError as e:
        logging.error(str(e))
        return {'imports': [], 'classes': [], 'functions': []}

    structure = {
        'imports': [],
        'classes': [],
        'functions': []
    }

    patterns = {
        'imports': r'^.*(?:import|package|require|include)\s.*$',
        'classes': r'\b(public|private|protected)*(\s)*(?:class|type|typedef|impl|struct|trait|use|sub)\s(\b|:|{).*(\s{|\:|\(\w+\))$',
        'functions':r'\b(?:fn|func|function|def|public|private|final|int|float|char|string|double|long|fun|sub)(?!.*\bclass\b)(\s.+)({|:|\))$'
    }

    for key, pattern in patterns.items():
        matches = re.findall(pattern, file_content, re.MULTILINE)
        structure[key] = [
            match.strip() if isinstance(match, str) else match[0].strip()
            for match in matches 
            if not (isinstance(match, str) and match.strip().startswith(('//', '*', '/*')) and match.strip()=='') 
        ]
        try:
            with open('output1.txt', 'a+') as f:
                if len(structure[key]) > 0:
                    parts = filepath.split("/Dependancy_Finder/")
                    trimmed_path = parts[1] if len(parts) > 1 else ""
                    f.write(f"{trimmed_path}:{key}-{str(structure[key])}\n")
        except Exception as e:
            logging.error(f"Error writing to output.txt: {str(e)}")
    return structure

def analyze_files_concurrent(file_list):
    results = {}
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_file = {executor.submit(analyze_file, filepath): filepath for filepath in file_list}
        for future in as_completed(future_to_file):
            filepath = future_to_file[future]
            try:
                results[filepath] = future.result()
            except Exception as exc:
                logging.error(f'{filepath} generated an exception: {exc}')
    return results

def write_results_to_csv(results, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['file_path', 'imports', 'functions', 'classes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for filepath, data in results.items():
            writer.writerow({
                'file_path': filepath,
                'imports': ';'.join(data['imports']),
                'functions': ';'.join(data['functions']),
                'classes': ';'.join(data['classes'])
            })

def process_single_file(filepath):
    try:
        file_content = read_file_with_fallback_encoding(filepath)
        if file_content is not None:
            return filepath, file_content
    except Exception as e:
        logging.error(f"Error processing file {filepath}: {str(e)}")
    return None

def writing_full_file_parallel(file_list, output_file='../output_dir/output2.txt', max_workers=None):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_single_file, filepath): filepath for filepath in file_list}
        
        with open(output_file, 'a+', encoding='utf-8') as f:
            for future in as_completed(future_to_file):
                result = future.result()
                if result:
                    filepath, file_content = result
                    try:
                        f.write(f"{filepath}\n{file_content}\n")
                    except Exception as e:
                        logging.error(f"Error writing to {output_file}: {str(e)}")
