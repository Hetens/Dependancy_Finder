import sys
import os
import re
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from multiprocessing import Pool, cpu_count
import logging
from util_multi import list_files, get_file_extensions, match_file_extensions, analyze_files_concurrent, write_results_to_csv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_import_name(import_statement):
    """
    Extracts the name of the imported module or entity from an import statement.
    Handles 'import', 'require', and 'include' statements.
    """
    patterns = [
        r'^\s*import\s+.*\s+from\s+[\'"](.+)[\'"]\s*;',
        r'^\s*import\s+[\'"](.+)[\'"]\s*;',
        r'^\s*require\s*\(\s*[\'"](.+)[\'"]\s*\)\s*;',
        r'^\s*include\s*[\'"](.+)[\'"]\s*;',
        r'^\s*#include\s*[<"](.+)[>"]\s*'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, import_statement)
        if match:
            return match.group(1)
    return None

def process_file(file_data):
    file, filepath, analysis_results = file_data
    graph_entry = set()
    file_dir = os.path.dirname(filepath)
    for import_statement in analysis_results[filepath]['imports']:
        imported_module = extract_import_name(import_statement)
        if imported_module:
            if imported_module.startswith('.'):
                imported_module = os.path.normpath(os.path.join(file_dir, imported_module))
            
            for other_file, other_deps in analysis_results.items():
                if (
                    imported_module in other_file or
                    any(imported_module in dep for dep in other_deps['classes']) or
                    any(imported_module in dep for dep in other_deps['functions'])
                ):
                    graph_entry.add(other_file)
    return file, graph_entry

def build_dependency_graph(file_map, directory):
    """
    Builds a dependency graph of files based on their imports and definitions.
    """
    file_to_path = {file: os.path.join(directory, file) for ext, files in file_map.items() for file in files}
    analysis_results = analyze_files_concurrent(file_to_path.values())
    try:
        if sys.argv[1] == '-w':
            logging.info("generating csv file for all outputs")
            write_results_to_csv(analysis_results, 'analysis_results.csv')
    except IndexError:
        pass
    
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_file, [(file, filepath, analysis_results) for file, filepath in file_to_path.items()])
    
    return dict(results)

def visualize_dependency_graph(graph):
    G = nx.DiGraph()
    
    for file, dependencies in graph.items():
        file = os.path.basename(file)
        G.add_node(file)
        for dep in dependencies:
            dep = os.path.basename(dep)
            G.add_edge(file, dep)
    
    plt.figure(figsize=(20, 20))
    pos = nx.spring_layout(G, k=0.9, iterations=50)
    
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=300, alpha=0.8)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, alpha=0.5, connectionstyle="arc3,rad=0.1")
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
    
    plt.title("File Dependency Graph", fontsize=20)
    plt.axis('off')
    plt.tight_layout()
    plt.margins(0.1)
    
    plt.savefig('dependency_graph.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    load_dotenv()
    directory = os.getenv('CODEBASE')
    if not directory:
        logging.error("CODEBASE environment variable not set")
        return

    logging.info("Analyzing codebase structure...")
    codebase_structure = list_files(directory)
    file_extensions = get_file_extensions(codebase_structure)
    file_map = match_file_extensions(file_extensions, codebase_structure)

    # Filter file extensions based on relevance
    # relevant = ['h', 'c']
    # file_map = {key: file_map[key] for key in relevant if key in file_map}

    logging.info("Building dependency graph...")
    dependency_graph = build_dependency_graph(file_map, directory)

    logging.info("Visualizing dependency graph...")
    visualize_dependency_graph(dependency_graph)

    logging.info("Writing dependency graph to file...")
    with open('dependency_graph1.txt', 'w') as f:
        for file, dependencies in dependency_graph.items():
            if dependencies:
                f.write(f"File: {file}\n")
                f.write("Dependencies:\n")
                for dep in dependencies:
                    f.write(f"  - {dep.split('/Dependancy_Finder/')[1]}\n")
                f.write("\n")
            else: 
                continue

    logging.info("Process completed successfully.")

if __name__ == "__main__":
    main()