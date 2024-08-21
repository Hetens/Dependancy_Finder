The test script for timer management functionality is as follows:

```python
import unittest
import time
import os
import tempfile
import shutil

class TestTimerManagement(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.file_path = os.path.join(self.test_dir, 'timer.txt')

    def test_timer_management(self):
        # Test case 1: Create a timer file and check its existence
        with open(self.file_path, 'w') as f:
            f.write('10')  # Set timer to 10 seconds
        self.assertTrue(os.path.exists(self.file_path))

        # Test case 2: Check timer expiration
        start_time = time.time()
        while time.time() - start_time < 10:
            time.sleep(1)
        self.assertFalse(os.path.exists(self.file_path))

        # Test case 3: Check timer expiration with multiple timers
        with open(self.file_path, 'w') as f:
            f.write('5')  # Set timer to 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5:
            time.sleep(1)
        self.assertFalse(os.path.exists(self.file_path))

        # Test case 4: Check timer expiration with multiple timers and different expiration times
        with open(self.file_path, 'w') as f:
            f.write('3')  # Set timer to 3 seconds
        start_time = time.time()
        while time.time() - start_time < 3:
            time.sleep(1)
        self.assertFalse(os.path.exists(self.file_path))

    def tearDown(self):
        # Clean up the test environment
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
```