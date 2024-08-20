import os

def parse_and_write_files(md_file_path):
    with open(md_file_path, 'r') as md_file:
        content = md_file.read()

    # Split the content by sections
    sections = content.split("## Identified Chunks")
    section_count = 0

    for section in sections[1:]:  # Skipping the first part before the first "## Identified Chunks"
        section_count += 1
        identified_chunks, generated_scripts = section.split("## Generated Test Scripts")
        
        # Prepare file names
        identified_chunks_filename = f"section_{section_count}_identified_chunks_{section_count}.log"
        script_count = 0
        
        # Write the Identified Chunks to a file
        with open(identified_chunks_filename, 'w') as file:
            file.write("## Identified Chunks" + identified_chunks.strip())
        
        # Split the generated scripts section by each script
        scripts = generated_scripts.split("---")
        
        for script in scripts:
            script_count += 1
            script_filename = f"section_{section_count}_script_{script_count}.py"
            
            # Write each script to its own file
            with open(script_filename, 'w') as file:
                file.write(script.strip())

    print(f"Parsed and created {section_count} identified chunks and {script_count} scripts.")

# Path to your markdown file
md_file_path = '../output2.md'

# Ensure the directory exists
output_dir = "parsed_scripts"
os.makedirs(output_dir, exist_ok=True)

# Change the working directory to the output directory
os.chdir(output_dir)

# Parse and write the files
parse_and_write_files(md_file_path)
