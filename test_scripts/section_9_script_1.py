The test automation script for implementing block I/O protocol and memory allocation functions is as follows:

```python
import os
import unittest
import subprocess
import shutil

class TestWinBlockIo(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for the test environment
        self.test_dir = 'test_env'
        os.mkdir(self.test_dir)

        # Copy the source files to the test environment
        shutil.copy('WinBlockIo.c', self.test_dir)
        shutil.copy('WinMemoryAllocationLib.c', self.test_dir)

        # Compile the source files
        self.compile_command = f'gcc -c {self.test_dir}/WinBlockIo.c -o {self.test_dir}/WinBlockIo.o'
        self.compile_memory_command = f'gcc -c {self.test_dir}/WinMemoryAllocationLib.c -o {self.test_dir}/WinMemoryAllocationLib.o'
        subprocess.run(self.compile_command, shell=True)
        subprocess.run(self.compile_memory_command, shell=True)

        # Link the object files
        self.link_command = f'gcc {self.test_dir}/WinBlockIo.o {self.test_dir}/WinMemoryAllocationLib.o -o {self.test_dir}/test_program'
        subprocess.run(self.link_command, shell=True)

    def test_block_io_protocol(self):
        # Test the block I/O protocol
        self.test_program = f'{self.test_dir}/test_program'
        output = subprocess.run(self.test_program, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.assertEqual(output.returncode, 0)

    def test_memory_allocation(self):
        # Test the memory allocation functions
        self.test_program = f'{self.test_dir}/test_program'
        output = subprocess.run(self.test_program, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.assertEqual(output.returncode, 0)

    def tearDown(self):
        # Clean up the test environment
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
```

This script assumes that the source files `WinBlockIo.c` and `WinMemoryAllocationLib.c` are in the same directory as the script. It compiles the source files, links the object files, and runs the resulting program. The `test_block_io_protocol` and `test_memory_allocation` methods test the block I/O protocol and memory allocation functions, respectively. The `tearDown` method cleans up the test environment by removing the temporary directory.

Note: This script does not provide any assertions about the file contents, as the contents are not provided. It assumes that the source files are correct and will compile and run correctly.

Also, note that this script uses the `subprocess` module to run the compiler and linker commands. This is a simple way to run external commands from Python, but it can be insecure if you're not careful. In this case, we're using the `shell=True` argument to run the commands through the shell, which can be a security risk if you're not careful. However, in this case, we're only running simple compiler and linker commands, so it's safe.

To run this script, save it to a file (e.g. `test_winblockio.py`) and run it with `python test_winblockio.py`. Make sure that the source files `WinBlockIo.c` and `WinMemoryAllocationLib.c` are in the same directory as the script.