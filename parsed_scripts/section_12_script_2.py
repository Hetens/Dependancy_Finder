### Script 2

Here's a Python test automation script that meets the requirements:

```python
import os
import unittest
from unittest.mock import patch
import subprocess

class TestFileDescriptorMapping(unittest.TestCase):

    def setUp(self):
        # Set up the test environment
        self.test_dir = os.path.dirname(__file__)
        self.host_file_path = os.path.join(self.test_dir, 'Host.c')
        self.test_binary_path = os.path.join(self.test_dir, 'test_binary')

    def test_file_exists(self):
        # Test if the file exists
        self.assertTrue(os.path.exists(self.host_file_path))

    def test_file_contents(self):
        # Read the file contents from the given path
        with open(self.host_file_path, 'r') as file:
            file_contents = file.read()
        self.assertGreater(len(file_contents), 0)

    def test_compile_binary(self):
        # Compile the Host.c file into a binary
        compile_command = f"gcc -o {self.test_binary_path} {self.host_file_path}"
        subprocess.run(compile_command, shell=True, check=True)

    def test_map_file_descriptor(self):
        # Test mapping file descriptor to a memory region
        # Assuming the binary is compiled and the file is mapped correctly
        # This test case can be modified based on the actual implementation
        map_command = f"./{self.test_binary_path}"
        subprocess.run(map_command, shell=True, check=True)

    def test_edge_cases(self):
        # Test edge cases with respect to the file contents
        # Assuming the file contents are not empty
        with open(self.host_file_path, 'r') as file:
            file_contents = file.read()
        if not file_contents:
            self.fail("File contents are empty")

    def tearDown(self):
        # Clean up the test environment
        if os.path.exists(self.test_binary_path):
            os.remove(self.test_binary_path)

if __name__ == '__main__':
    unittest.main()
```

This script assumes that the `Host.c` file is in the same directory as the script and that the `gcc` compiler is installed and available. The script also assumes that the binary is compiled correctly and the file is mapped correctly.

Note that this script is a basic example and may need to be modified based on the actual implementation and requirements. Additionally, this script does not handle any potential errors that may occur during the compilation or execution of the binary.