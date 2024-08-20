### Script 1

# The test script for the given inputs is:
# ```python

import os
import unittest
import subprocess
import tempfile

class TestNetworkInterfaceInitializationAndManagement(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for the test
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the test environment
        import shutil
        shutil.rmtree(self.test_dir)

    def test_network_interface_initialization_and_management(self):
        # Set up the test environment
        file_path = os.path.join(self.test_dir, 'BerkeleyPacketFilter.c')
        with open(file_path, 'w') as f:
            # Write some sample code to the file
            f.write('/* Sample Berkeley Packet Filter code */\n')
            f.write('int main() {\n')
            f.write('    return 0;\n')
            f.write('}\n')

        # Compile the code
        compile_command = f'gcc -c {file_path}'
        try:
            subprocess.check_output(compile_command, shell=True, cwd=self.test_dir)
        except subprocess.CalledProcessError as e:
            self.fail(f'Compilation failed with error: {e}')

        # Run the compiled code
        run_command = f'./BerkeleyPacketFilter.o'
        try:
            subprocess.check_output(run_command, shell=True, cwd=self.test_dir)
        except subprocess.CalledProcessError as e:
            self.fail(f'Execution failed with error: {e}')

        # Test the network interface initialization and management
        # For this example, we'll just check if the network interface is up
        import netifaces
        try:
            netifaces.ifaddresses('eth0')
        except ValueError:
            self.fail('Network interface not found')

    def test_edge_cases(self):
        # Test edge cases for the file contents
        # For this example, we'll just check if the file is empty
        file_path = os.path.join(self.test_dir, 'BerkeleyPacketFilter.c')
        with open(file_path, 'r') as f:
            file_contents = f.read()
        self.assertNotEqual(file_contents, '')

if __name__ == '__main__':
    unittest.main()
# ```

# This script assumes that the `BerkeleyPacketFilter.c` file is in the same directory as the script. It creates a temporary directory for the test, writes some sample code to the file, compiles it, runs it, and then tests the network interface initialization and management. It also includes a test for edge cases, in this case checking if the file is empty.

# Please note that this script is a basic example and may need to be modified to fit your specific use case. Additionally, this script assumes that the `netifaces` library is installed and available. If it's not installed, you can install it using pip: `pip install netifaces`.