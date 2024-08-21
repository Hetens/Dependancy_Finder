The test script for the 'Network Interface Management' task is:

```python
import os
import unittest
import subprocess
import shutil

class TestNetworkInterfaceManagement(unittest.TestCase):

    def setUp(self):
        # Set up the test environment
        self.test_dir = 'test_network_interface_management'
        self.file_name = 'network_interface_management.txt'
        self.file_path = os.path.join(self.test_dir, self.file_name)
        self.test_file_contents = """# Network Interface Management

# Create a new network interface
ip link add eth0 type ethernet

# Bring the interface up
ip link set eth0 up

# Set the IP address
ip addr add 192.168.1.1/24 dev eth0

# Set the netmask
ip addr add 255.255.255.0 dev eth0

# Set the gateway
ip route add default via 192.168.1.1 dev eth0

# Delete the network interface
ip link delete eth0"""

        # Create the test directory
        os.makedirs(self.test_dir, exist_ok=True)

        # Write the test file contents to the file
        with open(self.file_path, 'w') as f:
            f.write(self.test_file_contents)

    def test_network_interface_management(self):
        # Test case 1: Create a new network interface
        self.assertEqual(subprocess.run(['ip', 'link', 'add', 'eth0', 'type', 'ethernet'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode, 0)

        # Test case 2: Bring the interface up
        self.assertEqual(subprocess.run(['ip', 'link', 'set', 'eth0', 'up'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode, 0)

        # Test case 3: Set the IP address
        self.assertEqual(subprocess.run(['ip', 'addr', 'add', '192.168.1.1/24', 'dev', 'eth0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode, 0)

        # Test case 4: Set the netmask
        self.assertEqual(subprocess.run(['ip', 'addr', 'add', '255.255.255.0', 'dev', 'eth0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode, 0)

        # Test case 5: Set the gateway
        self.assertEqual(subprocess.run(['ip', 'route', 'add', 'default', 'via', '192.168.1.1', 'dev', 'eth0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode, 0)

        # Test case 6: Delete the network interface
        self.assertEqual(subprocess.run(['ip', 'link', 'delete', 'eth0'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode, 0)

    def tearDown(self):
        # Clean up the test environment
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
```

This script will create a test directory, write the test file contents to a file in that directory, run the test cases, and then clean up the test environment by deleting the test directory. The test cases cover the following scenarios:

1. Creating a new network interface
2. Bringing the interface up
3. Setting the IP address
4. Setting the netmask
5. Setting the gateway
6. Deleting the network interface

Each test case uses the `subprocess` module to run the corresponding command and checks the return code to ensure that the command was successful.

Note: This script assumes that the `ip` command is available on the system. If the `ip` command is not available, the script will fail.