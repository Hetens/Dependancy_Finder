#step 1 identify the build files

from dotenv import load_dotenv
import os
import re
import sys
import json
load_dotenv()   

def find_build_files(root_dir):
    build_files = []
    
    build_patterns = [
        r'(?i)makefile$',
        r'(?i)CMakeLists\.txt$',
        r'(?i)build\.gradle$',
        r'(?i)pom\.xml$',
        r'(?i)package\.json$',
        r'(?i)build\.xml$',
        r'(?i)\.csproj$',
        r'(?i)\.sln$',
        r'(?i)setup\.py$',
        r'(?i)requirements\.txt$',
    ]
    
    compiled_patterns = [re.compile(pattern) for pattern in build_patterns]
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            dirpath = dirpath.split('/')[-1]
            file_path = os.path.join(dirpath, filename)
            for pattern in compiled_patterns:
                if pattern.search(filename):
                    file_path = file_path.replace('\\', '/')
                    file_path  = file_path.split('/')[1:]
                    file_path = '/'.join(file_path)
                    build_files.append(file_path)
                    break
    
    return build_files

def display_tree(startpath):
    for root, dirs, files in os.walk(startpath):
        with open('output.txt', 'a',encoding='utf-8') as k:
            level = root.replace(startpath, '').count(os.sep)
            indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
            k.write(f'{indent}{os.path.basename(root)}/\n')
            subindent = '│   ' * level + '├── '
            for f in files:
                k.write(f'{subindent}{f}\n')

def parse_build_files(root_dir, build_files):
    required_files = set()
    
    for build_file in build_files:
        full_path = os.path.join(root_dir, build_file)
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                if build_file.endswith('Makefile'):
                    required_files.update(re.findall(r'\w+\.\w+', content))
                elif build_file.endswith('CMakeLists.txt'):
                    required_files.update(re.findall(r'add_executable\((.*?)\)', content))
                elif build_file.endswith('package.json'):
                    try:
                        data = json.loads(content)
                        required_files.update(data.get('dependencies', {}).keys())
                        required_files.update(data.get('devDependencies', {}).keys())
                    except json.JSONDecodeError:
                        print(f"Error: Unable to parse {build_file} as JSON. Skipping this file.")
                elif build_file.endswith('requirements.txt'):
                    required_files.update(re.findall(r'^(\w+)', content, re.MULTILINE))
                # Add more parsing logic for other build file types as needed
        except IOError:
            print(f"Error: Unable to read {build_file}. Skipping this file.")
        except Exception as e:
            print(f"Unexpected error occurred while processing {build_file}: {str(e)}")
    
    return list(required_files)

def main():
    repository_path = os.getenv('CODEBASE')
    print("\nRepository structure:")
    display_tree(repository_path)
    
    build_files = find_build_files(repository_path)
    
    if build_files:
        print("\nFound the following build files:")
        for file in build_files:
            with open('output.txt', 'a',encoding='utf-8') as k:
                k.write(file+'\n')

        required_files = parse_build_files(repository_path, build_files)
        
        print("\nFiles required by build files:")
        for file in required_files:
            with open('output.txt', 'a',encoding='utf-8') as k:
                k.write(file+'\n')
    else:
        print("\nNo build files found in the repository.")

main()

