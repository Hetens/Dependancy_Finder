import networkx as nx
from pyvis.network import Network
from collections import defaultdict
import hashlib

def generate_chunk_id(source, dependency):
    return hashlib.md5(f"{source}|{dependency}".encode()).hexdigest()

def process_mapreduce_output(input_file, output_file):
    dependencies = defaultdict(lambda: defaultdict(int))
    
    # Read the MapReduce output
    with open(input_file, 'r',encoding='UTF-16') as f:
        for line in f:
            count = int(line.split(']')[1])
            source = line.split(']')[0].split(',')[0].split('\\')[-1]
            dependency = line.split(']')[0].split(',')[1]
            #print(source, dependency, count)
            dependencies[source][dependency] += count
    
    # Create a NetworkX graph
    G = nx.DiGraph()
    
    for source, deps in dependencies.items():
        source_node = source.split('/')[-1].split('\\')[-1]  # Extract filename from path
        for dependency, count in deps.items():
            edge_label = f"Occurs {count} times"
            chunk_id = generate_chunk_id(source, dependency)
            G.add_edge(source_node, dependency, title=edge_label, weight=count, chunk_id=chunk_id)

    # Create a Pyvis network from the NetworkX graph
    k_value = 2  # Adjust this value to change node spacing
    pos = nx.spring_layout(G, k=k_value, iterations=50)


    net = Network(notebook=False, cdn_resources="remote", height="1200px", width="1200px")


    for node, (x, y) in pos.items():
        net.add_node(
            node,
            x=x * 200, 
            y=y * 200,
            physics=True,  
            **G.nodes[node] 
        )

    # Add edges to the Pyvis network
    for source, target, edge_attrs in G.edges(data=True):
        edge_data = edge_attrs.copy()
        edge_data['value'] = edge_data['weight']
        net.add_edge(
            source,
            target,
            **edge_data
        )
        # Generate the HTML file
        net.show(output_file)

if __name__ == "__main__":
    input_file = "output.txt"
    output_file = "dependency_graph.html"
    process_mapreduce_output(input_file, output_file)