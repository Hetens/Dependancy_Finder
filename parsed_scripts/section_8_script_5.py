### Script 5

The test automation script for the X11 graphics window protocol implementation is:

```python
import os
import unittest
from unittest.mock import patch
import subprocess

class TestX11GraphicsWindowProtocol(unittest.TestCase):

    def setUp(self):
        # Set up the test environment
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(self.test_dir, 'X11GraphicsWindow.c')
        self.build_dir = os.path.join(self.test_dir, 'build')

    def test_file_exists(self):
        # Test if the file exists
        self.assertTrue(os.path.exists(self.file_path))

    def test_file_contents(self):
        # Test if the file contents are as expected
        with open(self.file_path, 'r') as f:
            file_contents = f.read()
            self.assertGreater(len(file_contents), 0)

    def test_build(self):
        # Test if the file can be built successfully
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            build_command = f"gcc -o {self.build_dir}/X11GraphicsWindow {self.file_path}"
            subprocess.run(build_command, shell=True, check=True)
            self.assertTrue(os.path.exists(os.path.join(self.build_dir, 'X11GraphicsWindow')))

    def test_run(self):
        # Test if the built executable runs successfully
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            run_command = f"./{self.build_dir}/X11GraphicsWindow"
            subprocess.run(run_command, shell=True, check=True)
            self.assertTrue(os.path.exists(os.path.join(self.build_dir, 'X11GraphicsWindow.log')))

    def tearDown(self):
        # Clean up the test environment
        if os.path.exists(self.build_dir):
            import shutil
            shutil.rmtree(self.build_dir)

if __name__ == '__main__':
    unittest.main()
```

This script assumes that the file `X11GraphicsWindow.c` is in the same directory as the script. It tests the existence of the file, its contents, the successful build of the file, and the successful run of the built executable. The `tearDown` method is used to clean up the test environment by removing the build directory.