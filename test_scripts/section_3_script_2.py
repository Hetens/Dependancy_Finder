The test script for the task 'Provide Emulation Layer for Windows on UEFI Firmware' with the given line numbers '140-304' is:

```python
import os
import unittest
from unittest.mock import patch
import tempfile
import shutil

class TestEmulationLayer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for the test environment
        self.test_dir = tempfile.mkdtemp()
        self.file_path = os.path.join(self.test_dir, 'emulation_layer.txt')

        # Create a sample file contents for the emulation layer
        self.file_contents = """# Emulation Layer for Windows on UEFI Firmware
# This file provides the necessary configuration for the emulation layer

# Configuration for the emulation layer
emulation_layer_config = {
    'firmware_type': 'UEFI',
    'os_type': 'Windows',
    'emulation_mode': 'virtual'
}

# Function to initialize the emulation layer
def init_emulation_layer():
    # Initialize the emulation layer configuration
    emulation_layer_config['firmware_type'] = 'UEFI'
    emulation_layer_config['os_type'] = 'Windows'
    emulation_layer_config['emulation_mode'] = 'virtual'

    # Return the initialized emulation layer configuration
    return emulation_layer_config

# Function to test the emulation layer
def test_emulation_layer():
    # Initialize the emulation layer
    emulation_layer_config = init_emulation_layer()

    # Test the emulation layer configuration
    self.assertEqual(emulation_layer_config['firmware_type'], 'UEFI')
    self.assertEqual(emulation_layer_config['os_type'], 'Windows')
    self.assertEqual(emulation_layer_config['emulation_mode'], 'virtual')

    # Return True if the test is successful
    return True"""

        # Write the file contents to the temporary file
        with open(self.file_path, 'w') as f:
            f.write(self.file_contents)

    def tearDown(self):
        # Clean up the test environment
        shutil.rmtree(self.test_dir)

    def test_file_exists(self):
        # Test if the file exists
        self.assertTrue(os.path.exists(self.file_path))

    def test_file_contents(self):
        # Test if the file contents match the expected contents
        with open(self.file_path, 'r') as f:
            file_contents = f.read()
            self.assertEqual(file_contents, self.file_contents)

    def test_emulation_layer_config(self):
        # Test the emulation layer configuration
        with open(self.file_path, 'r') as f:
            file_contents = f.read()
            emulation_layer_config = eval(file_contents.split('\n\n')[1])
            self.assertEqual(emulation_layer_config['firmware_type'], 'UEFI')
            self.assertEqual(emulation_layer_config['os_type'], 'Windows')
            self.assertEqual(emulation_layer_config['emulation_mode'], 'virtual')

    def test_init_emulation_layer(self):
        # Test the init_emulation_layer function
        with open(self.file_path, 'r') as f:
            file_contents = f.read()
            init_emulation_layer = eval(file_contents.split('\n\n')[2])
            emulation_layer_config = init_emulation_layer()
            self.assertEqual(emulation_layer_config['firmware_type'], 'UEFI')
            self.assertEqual(emulation_layer_config['os_type'], 'Windows')
            self.assertEqual(emulation_layer_config['emulation_mode'], 'virtual')

    def test_test_emulation_layer(self):
        # Test the test_emulation_layer function
        with open(self.file_path, 'r') as f:
            file_contents = f.read()
            test_emulation_layer = eval(file_contents.split('\n\n')[3])
            result = test_emulation_layer()
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
```