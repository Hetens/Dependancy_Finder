The test script for the function 'FatAccessCache' is:

```python
import os
import unittest
import tempfile
import shutil
import subprocess

class TestFatAccessCache(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.test_dir, 'DiskCache.c')
        self.executable_file = os.path.join(self.test_dir, 'DiskCache')

        # Create a sample file contents
        with open(self.cache_file, 'w') as f:
            f.write('#include <stdio.h>\n')
            f.write('#include <stdlib.h>\n')
            f.write('#include <string.h>\n')
            f.write('#include <sys/stat.h>\n')
            f.write('#include <fcntl.h>\n')
            f.write('#include <unistd.h>\n')
            f.write('\n')
            f.write('int main() {\n')
            f.write('    // Create a cache file\n')
            f.write('    int fd = open("cache.txt", O_RDWR | O_CREAT, 0644);\n')
            f.write('    if (fd == -1) {\n')
            f.write('        perror("open");\n')
            f.write('        return 1;\n')
            f.write('    }\n')
            f.write('    // Write data to the cache file\n')
            f.write('    char *data = "Hello, World!";\n')
            f.write('    write(fd, data, strlen(data));\n')
            f.write('    // Close the cache file\n')
            f.write('    close(fd);\n')
            f.write('    return 0;\n')
            f.write('}\n')

    def test_compile(self):
        # Compile the C file
        try:
            subprocess.check_output(['gcc', '-o', self.executable_file, self.cache_file])
        except subprocess.CalledProcessError as e:
            self.fail(f"Compilation failed with error: {e}")

    def test_execute(self):
        # Execute the compiled executable
        try:
            subprocess.check_output([self.executable_file])
        except subprocess.CalledProcessError as e:
            self.fail(f"Execution failed with error: {e}")

    def test_cache_file_exists(self):
        # Check if the cache file exists
        cache_path = os.path.join(self.test_dir, 'cache.txt')
        self.assertTrue(os.path.exists(cache_path))

    def test_cache_file_contents(self):
        # Check if the cache file contains the expected data
        cache_path = os.path.join(self.test_dir, 'cache.txt')
        with open(cache_path, 'r') as f:
            contents = f.read()
            self.assertEqual(contents, 'Hello, World!')

    def tearDown(self):
        # Clean up the test environment
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
```

This script will create a temporary directory, write a sample C file to it, compile the C file, execute the compiled executable, and then check if the cache file exists and contains the expected data. Finally, it will clean up the test environment by removing the temporary directory.

Note: This script assumes that the `gcc` compiler is installed and available on the system. If you are using a different compiler, you may need to modify the script accordingly.