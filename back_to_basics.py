from mrjob.job import MRJob
from mrjob.step import MRStep
import re

class DependencyGraphMR(MRJob):

    def mapper(self, _, line):
        if line.startswith('C:'):
            # This is a file path
            line  = line.split('vram')[1]
            self.current_file = line.strip()
        elif hasattr(self, 'current_file'):
            # This is content of the file
            dependencies = self.extract_dependencies(line)
            for dep in dependencies:
                yield (self.current_file, dep), 1

    def reducer(self, key, values):
        # Sum up occurrences of each dependency
        yield key, sum(values)

    def extract_dependencies(self, code):
        dependencies = []

        # C/C++ patterns
        c_include_pattern = re.compile(r'#include\s+[<"](.+?)[>"]')
        dependencies.extend(c_include_pattern.findall(code))

        define_pattern = re.compile(r'#define\s+(\w+)')
        dependencies.extend(define_pattern.findall(code))

        # Python patterns
        python_import_pattern = re.compile(r'(?:from\s+(\S+)\s+)?import\s+(\S+)')
        for match in python_import_pattern.finditer(code):
            if match.group(1):  # from ... import ...
                dependencies.append(match.group(1))
            dependencies.append(match.group(2))

        # Java patterns
        java_import_pattern = re.compile(r'import\s+([\w.]+)(?:\.(?:\*|\w+))?;')
        dependencies.extend(java_import_pattern.findall(code))

        # JavaScript patterns (ES6+)
        js_import_pattern = re.compile(r'(?:import|export).*?(?:from\s+[\'"](.+?)[\'"]|[\'"](.+?)[\'"])')
        for match in js_import_pattern.finditer(code):
            dependencies.append(match.group(1) or match.group(2))

        # Generic function call pattern (simplified, may need refinement)
        function_pattern = re.compile(r'\b(\w+)\s*\(')
        dependencies.extend(function_pattern.findall(code))

        return list(set(dependencies))  # Remove duplicates

    def steps(self):
        return [
            MRStep(mapper=self.mapper,
                   reducer=self.reducer)
        ]

if __name__ == '__main__':
    DependencyGraphMR.run()