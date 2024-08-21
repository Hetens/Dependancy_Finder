The final test script is:

```python
import os
import unittest
import tempfile
import shutil
import fcntl
import time

class TestFileIO(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test_file.txt')
        with open(self.test_file, 'w') as f:
            f.write('This is a test file.')

    def test_block_io_operations(self):
        # Test that the file is not accessible while it's being written to
        with open(self.test_file, 'a') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                with open(self.test_file, 'r') as f2:
                    self.assertEqual(f2.read(), 'This is a test file.')
            except IOError:
                pass
            time.sleep(1)  # Wait for the lock to be acquired
            with self.assertRaises(IOError):
                with open(self.test_file, 'r') as f2:
                    f2.read()

    def test_file_contents(self):
        # Test that the file contents are correct
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), 'This is a test file.')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
```