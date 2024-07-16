import re
import os

def parse_output_file(filepath, heirarchy = 4):
    text =''
    paths,contents = [],[]
    with open(filepath, 'r',encoding='utf-8') as f:
        text = f.read()
    matches = re.finditer(r'C:/.*',text)
    matches1 = [match for match in matches]# make this the last section of the codebase
    for match in matches1:
        paths.append(match.group(0))
    for match, match_next in zip(matches1[:-1],matches1[1:]):
        ending_index = match.span()[1]
        starting_index = match_next.span()[0]
        contents.append(text[ending_index:starting_index])
  
    #appending the last file
    unique_dirs = set()
    contents.append(text[matches1[-1].span()[1]:])
    for path in paths:
        path = path.replace('/','\\')
        dir = path.split('\\')  
        dir = dir[-heirarchy]
        unique_dirs.add(dir)
    
    dir_contents = {}
    for dir in unique_dirs:
        dir_contents[dir] = []
    file_names = {}
    for path, content in zip(paths, contents):
        path = path.replace('/', '\\')
        dir = path.split('\\')[-heirarchy]
        dir_contents[dir]+=''+(content)
        file_names[dir] = path.split('\\')[-1]
    
    return file_names, dir_contents, unique_dirs


# file_names,dir_contents,unique_dirs =parse_output_file("output2.txt",3)


import nest_asyncio

nest_asyncio.apply()

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    ServiceContext,
)
codebase = os.getenv('CODEBASE')
required_exts = ['.h','.c']
reader = SimpleDirectoryReader(codebase,required_ext =required_exts, recursive = True)
documents = reader.load_data()
print(documents)
