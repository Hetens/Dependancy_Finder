from dotenv import load_dotenv
import os
import re
import sys
import json
from collections import defaultdict

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
                    file_path = file_path.split('/')[1:]
                    file_path = '/'.join(file_path)
                    build_files.append(file_path)
                    break
    
    return build_files

def display_tree(startpath):
    for root, dirs, files in os.walk(startpath):
        with open('output.txt', 'a', encoding='utf-8') as k:
            level = root.replace(startpath, '').count(os.sep)
            indent = '│   ' * (level - 1) + '├── ' if level > 0 else ''
            k.write(f'{indent}{os.path.basename(root)}/\n')
            subindent = '│   ' * level + '├── '
            for f in files:
                k.write(f'{subindent}{f}\n')

def parse_build_files(root_dir, build_files):
    dependency_graph = defaultdict(set)
    
    for build_file in build_files:
        full_path = os.path.join(root_dir, build_file)
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                if build_file.lower().endswith('makefile'):
                    parse_makefile(content, dependency_graph)
                elif build_file.lower().endswith('cmakelists.txt'):
                    parse_cmake(content, dependency_graph)
                elif build_file.lower().endswith('package.json'):
                    parse_package_json(content, build_file, dependency_graph)
                elif build_file.lower().endswith('requirements.txt'):
                    parse_requirements(content, build_file, dependency_graph)
                elif build_file.lower().endswith('.gradle'):
                    parse_gradle(content, dependency_graph)
                elif build_file.lower().endswith('pom.xml'):
                    parse_pom_xml(content, dependency_graph)
                elif build_file.lower().endswith('.sln'):
                    parse_sln(content, dependency_graph)
                elif build_file.lower().endswith('.csproj'):
                    parse_csproj(content, dependency_graph)
                elif build_file.lower().endswith('setup.py'):
                    parse_setup_py(content, dependency_graph)
                
        except IOError:
            print(f"Error: Unable to read {build_file}. Skipping this file.")
        except Exception as e:
            print(f"Unexpected error occurred while processing {build_file}: {str(e)}")
    
    return dependency_graph

def parse_makefile(content, graph):
    # Improved Makefile parsing
    targets = re.findall(r'^([^#\s:]+)\s*:(.*)$', content, re.MULTILINE)
    for target, deps in targets:
        graph[target].update(re.findall(r'\S+', deps))
    
    # Find all file inclusions
    includes = re.findall(r'include\s+(.+)', content)
    for inc in includes:
        graph['Makefile'].add(inc.strip())
    
    # Find all file references in commands
    commands = re.findall(r'^\t(.+)$', content, re.MULTILINE)
    for cmd in commands:
        graph['Makefile'].update(re.findall(r'\S+\.\w+', cmd))

def parse_cmake(content, graph):
    # Find all add_executable and add_library commands
    targets = re.findall(r'add_(?:executable|library)\s*\(([^)]+)\)', content)
    for target in targets:
        parts = target.split()
        if len(parts) > 1:
            graph[parts[0]].update(parts[1:])
    
    # Find all include_directories
    includes = re.findall(r'include_directories\s*\(([^)]+)\)', content)
    for inc in includes:
        graph['CMakeLists'].update(inc.split())
    
    # Find all file() commands
    file_commands = re.findall(r'file\s*\(([^)]+)\)', content)
    for cmd in file_commands:
        graph['CMakeLists'].update(re.findall(r'\S+\.\w+', cmd))

def parse_package_json(content, build_file, graph):
    try:
        data = json.loads(content)
        for dep_type in ['dependencies', 'devDependencies']:
            for dep in data.get(dep_type, {}):
                graph[build_file].add(dep)
        
        # Parse scripts for file references
        for script in data.get('scripts', {}).values():
            graph[build_file].update(re.findall(r'\S+\.\w+', script))
    except json.JSONDecodeError:
        print(f"Error: Unable to parse {build_file} as JSON. Skipping this file.")

def parse_requirements(content, build_file, graph):
    deps = re.findall(r'^([^#\s=<>]+)', content, re.MULTILINE)
    graph[build_file].update(deps)

def parse_gradle(content, graph):
    # Find all dependencies
    dependencies = re.findall(r'(implementation|api|testImplementation|compile)\s+[\'"](.*?)[\'"]', content)
    for _, dep in dependencies:
        graph['Gradle'].add(dep)
    
    # Find all applied plugins
    plugins = re.findall(r'apply\s+plugin:\s+[\'"](.+?)[\'"]', content)
    graph['Gradle'].update(plugins)

def parse_pom_xml(content, graph):
    # Find all dependencies
    dependencies = re.findall(r'<dependency>.*?<artifactId>(.*?)</artifactId>.*?</dependency>', content, re.DOTALL)
    graph['Maven'].update(dependencies)
    
    # Find all plugins
    plugins = re.findall(r'<plugin>.*?<artifactId>(.*?)</artifactId>.*?</plugin>', content, re.DOTALL)
    graph['Maven'].update(plugins)

def parse_sln(content, graph):
    # Find all project references
    projects = re.findall(r'Project\([^)]+\)\s*=\s*"[^"]+",\s*"([^"]+)"', content)
    graph['Solution'].update(projects)

def parse_csproj(content, graph):
    # Find all references
    references = re.findall(r'<Reference\s+Include="([^"]+)"', content)
    graph['CSharp Project'].update(references)
    
    # Find all source files
    sources = re.findall(r'<Compile\s+Include="([^"]+)"', content)
    graph['CSharp Project'].update(sources)

def parse_setup_py(content, graph):
    # Find all install_requires
    requires = re.findall(r'install_requires\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if requires:
        graph['Setup.py'].update(re.findall(r'[\'"](.+?)[\'"]', requires[0]))
    
    # Find all packages
    packages = re.findall(r'packages\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if packages:
        graph['Setup.py'].update(re.findall(r'[\'"](.+?)[\'"]', packages[0]))

def resolve_dependencies(dependency_graph, target, visited=None):
    if visited is None:
        visited = set()
    
    if target in visited:
        return set()
    
    visited.add(target)
    dependencies = dependency_graph[target]
    all_dependencies = set(dependencies)
    
    for dep in dependencies:
        all_dependencies.update(resolve_dependencies(dependency_graph, dep, visited))
    
    return all_dependencies

def create_reverse_dependency_map(dependency_graph):
    reverse_map = defaultdict(set)
    for target, deps in dependency_graph.items():
        for dep in deps:
            reverse_map[dep].add(target)
    return reverse_map

def find_code_files(root_dir, file_patterns):
    code_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if any(re.search(pattern, file) for pattern in file_patterns):
                code_files.append(os.path.join(root, file))
    return code_files

def match_dependencies_to_files(reverse_map, code_files):
    matched_dependencies = defaultdict(set)
    for file_path in code_files:
        file_name = os.path.basename(file_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Check for exact matches
        if file_name in reverse_map:
            matched_dependencies[file_path].update(reverse_map[file_name])
        
        # Check for matches without file extension
        if file_name_without_ext in reverse_map:
            matched_dependencies[file_path].update(reverse_map[file_name_without_ext])
        
        # Check for partial matches (e.g., "utils" in "string_utils.cpp")
        for dep in reverse_map:
            if dep in file_name_without_ext:
                matched_dependencies[file_path].add(dep)
    
    return matched_dependencies

def find_dependent_files(root_dir, dependency_graph):
    # Create reverse dependency map
    reverse_map = create_reverse_dependency_map(dependency_graph)
    
    # Define patterns for code files
    file_patterns = [
        r'\.c$', r'\.cpp$', r'\.h$', r'\.hpp$',  # C/C++
        r'\.py$',  # Python
        r'\.java$',  # Java
        r'\.js$', r'\.ts$',  # JavaScript/TypeScript
        r'\.cs$',  # C#
        r'\.go$',  # Go
        r'\.rb$',  # Ruby
        r'\.php$',  # PHP
        r'\.swift$',  # Swift
        r'\.rs$',  # Rust
        # Add more patterns as needed
    ]
    
    # Find all code files in the repository
    code_files = find_code_files(root_dir, file_patterns)
    
    # Match dependencies to files
    dependent_files = match_dependencies_to_files(reverse_map, code_files)
    
    return dependent_files

def main():
    repository_path = os.getenv('CODEBASE')
    print("\nRepository structure:")
    display_tree(repository_path)
    
    build_files = find_build_files(repository_path)
    
    if build_files:
        print("\nFound the following build files:")
        for file in build_files:
            with open('./output_dir/output.txt', 'a', encoding='utf-8') as k:
                k.write(file + '\n')

        dependency_graph = parse_build_files(repository_path, build_files)
        
        print("\nDependency graph:")
        for target, deps in dependency_graph.items():
            print(f"{target}: {', '.join(deps)}")
        
        print("\nRecursively resolved dependencies:")
        # Create a list of targets to avoid modifying the dictionary during iteration
        targets = list(dependency_graph.keys())
        for target in targets:
            all_deps = resolve_dependencies(dependency_graph, target)
            print(f"{target}: {', '.join(all_deps)}")
            with open('output.txt', 'a', encoding='utf-8') as k:
                k.write(f"{target}: {', '.join(all_deps)}\n")

        dependency_graph = parse_build_files(repository_path, find_build_files(repository_path))
    
    dependent_files = find_dependent_files(repository_path, dependency_graph)
    
    print("\nDependent code files:")
    for file_path, dependencies in dependent_files.items():
        print(f"{file_path}:")
        for dep in dependencies:
            print(f"  - {dep}")
        print()
    else:
        print("\nNo build files found in the repository.")

if __name__ == "__main__":
    main()