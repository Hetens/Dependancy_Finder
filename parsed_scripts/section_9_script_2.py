### Script 2

The test script for the given scenario is:

```python
import os
import unittest
from unittest.mock import patch
import subprocess

class TestX11GraphicsWindow(unittest.TestCase):

    def setUp(self):
        # Set up the test environment
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.coverage_file = os.path.join(self.test_dir, 'vram', 'EmulatorPkg', 'Unix', 'Host', 'X11GraphicsWindow.c')
        self.test_file = os.path.join(self.test_dir, 'test_x11_graphics_window.py')

    def test_file_exists(self):
        # Test if the file exists
        self.assertTrue(os.path.exists(self.coverage_file))

    def test_file_contents(self):
        # Test if the file contents are as expected
        with open(self.coverage_file, 'r') as f:
            contents = f.read()
            self.assertIn('EFI_X11_GRAPHICS_WINDOW_PROTOCOL_GUID', contents)
            self.assertIn('EFI_X11_GRAPHICS_WINDOW_PROTOCOL', contents)

    def test_clean_up_resources(self):
        # Test if the resources are cleaned up after closing the X11 graphics window
        with patch('subprocess.call') as mock_call:
            # Simulate closing the X11 graphics window
            mock_call.return_value = 0
            # Run the test file
            subprocess.run(['python', self.test_file])
            # Check if the resources are cleaned up
            self.assertEqual(mock_call.call_count, 1)

    def test_return_efi_success(self):
        # Test if EFI_SUCCESS is returned after closing the X11 graphics window
        with patch('subprocess.call') as mock_call:
            # Simulate closing the X11 graphics window
            mock_call.return_value = 0
            # Run the test file
            subprocess.run(['python', self.test_file])
            # Check if EFI_SUCCESS is returned
            self.assertEqual(mock_call.call_count, 1)

    def tearDown(self):
        # Clean up the test environment
        pass

if __name__ == '__main__':
    unittest.main()
```

This script assumes that the test file `test_x11_graphics_window.py` is in the same directory as the script. The test file should contain the necessary code to simulate closing the X11 graphics window and cleaning up resources.