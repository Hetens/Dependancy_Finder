### Script 3

The test script for the specified task is as follows:

```python
import os
import unittest
from unittest.mock import patch
import subprocess

class TestBerkeleyPacketFilter(unittest.TestCase):

    def setUp(self):
        # Set up the test environment
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(self.test_dir, 'BerkeleyPacketFilter.c')
        self.build_dir = os.path.join(self.test_dir, 'build')

    def test_file_exists(self):
        # Test if the file exists
        self.assertTrue(os.path.exists(self.file_path))

    def test_file_contents(self):
        # Read the file contents
        with open(self.file_path, 'r') as f:
            file_contents = f.read()
        self.assertGreater(len(file_contents), 0)

    def test_build(self):
        # Build the Berkeley Packet Filter
        build_command = f"gcc -c {self.file_path} -o {self.build_dir}/BerkeleyPacketFilter.o"
        subprocess.run(build_command, shell=True, check=True)

    def test_efi_interface_thunk(self):
        # Test the EFI interface thunk for EmuSnp protocol
        # Assume data if necessary
        test_data = b'\x00\x01\x02\x03'
        with patch('os.read', return_value=test_data):
            with patch('os.write', return_value=len(test_data)):
                # Simulate the EFI interface thunk
                efi_thunk = subprocess.Popen(['./build/BerkeleyPacketFilter.o'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = efi_thunk.communicate()
                self.assertEqual(efi_thunk.returncode, 0)
                self.assertEqual(output, test_data)

    def tearDown(self):
        # Clean up the test environment
        if os.path.exists(self.build_dir):
            import shutil
            shutil.rmtree(self.build_dir)

if __name__ == '__main__':
    unittest.main()
```

This script assumes that the `BerkeleyPacketFilter.c` file is in the same directory as the script, and that the `gcc` compiler is installed and available in the system's PATH. The script first sets up the test environment by defining the test directory, file path, and build directory. It then tests if the file exists, reads the file contents, builds the Berkeley Packet Filter, and tests the EFI interface thunk for EmuSnp protocol. The `test_efi_interface_thunk` method simulates the EFI interface thunk by running the built Berkeley Packet Filter executable and capturing its output. It assumes that the `os.read` and `os.write` functions are patched to return the test data. Finally, the script cleans up the test environment by removing the build directory.