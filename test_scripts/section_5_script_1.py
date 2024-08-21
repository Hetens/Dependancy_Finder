The test script for the 'Initialization' task is:

```python
import os
import unittest
from unittest.mock import patch
import tempfile
import shutil

class TestInitialization(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.file_path = os.path.join(self.test_dir, 'file.txt')
        self.file_contents = 'This is a test file.\nIt has multiple lines.'

    def test_file_creation(self):
        with open(self.file_path, 'w') as f:
            f.write(self.file_contents)

        self.assertTrue(os.path.exists(self.file_path))

    def test_file_contents(self):
        with open(self.file_path, 'r') as f:
            contents = f.read()

        self.assertEqual(contents, self.file_contents)

    def test_file_deletion(self):
        os.remove(self.file_path)
        self.assertFalse(os.path.exists(self.file_path))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
```

This script creates a temporary directory, creates a file in that directory, tests the file's existence and contents, and then deletes the file and the directory. The `setUp` method is called before each test, and the `tearDown` method is called after each test.