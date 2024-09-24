#!python
#
# This script runs tests of the Radeon GPU Analyzer CLI Vulkan support.
#
import sys
import os
import argparse
import subprocess
import unittest
from vulkan_tests import vulkan_tests
from vulkan_tests import vulkan_target_gpus
from RgaVulkanHelp import help_vulkan
from RgaBadApiHelp import help_bad_api
import re

SUCCESS = "SUCCESS"
FAIL = "FAIL"
global INPUT_FOLDER
global OUTPUT_FOLDER

class TestRgaCli(unittest.TestCase):

    def testHelp(self):
        # Verify rga -h -s Vulkan
        self.assertTrue(test_vulkan_help())

    def testHelpNeg(self):
        # Verify rga -h -s bad_api
        self.assertTrue(test_vulkan_help_neg())
        
    def testVulkanCmd(self):
        # Data driven test of RGA CLI Vulkan API
        print(INPUT_FOLDER)
        print(OUTPUT_FOLDER)
        print(TEST_SUITE)
        self.assertTrue(testVulkanCli(INPUT_FOLDER, OUTPUT_FOLDER, TEST_SUITE))

def test_vulkan_help():
    status = True
    rga_cmd = ['rga', '-h', '-s', 'Vulkan']
    # Run help command for Vulkan API and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    if proc_complete.returncode != 0:
        status = False
        fail_message = 'Command exited with failure status\n'
    if not re.match(help_vulkan, proc_complete.stdout):
        status = False
        fail_message += 'Error message in stdout\n'

    if not status:
        print(fail_message)

    return(status)
    
def test_help_bad_api():
    status = True
    rga_cmd = ['rga', '-h', '-s', 'bad_api']
    # Run help command for Vulkan API and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    if proc_complete.returncode == 0:
        status = False
        fail_message = 'Command exited with incorrect success status\n'
    if not re.match(help_bad_api, proc_complete.stdout):
        status = False
        fail_message += 'Expected error message not found in stdout\nOutput:\n' + help_bad_api + '\n'

    if not status:
        print(fail_message)

    return(status)

def test_vulkan_cli(input_folder, output_folder, suite):
    status = True
    test_keys = list(vulkan_tests)
    target_gpu = 'gfx1100'

    for test in test_keys:
        # Initialize variables.
        rga_cmd = ['rga']
        test_status = True

        # Filter tests by suites list.
        run_test = False
        if suite in vulkan_tests[test][2]:
            run_test = True
        if run_test is True:
            # debug
            print("test case rga option list:")
            print(vulkan_tests[test][1])
            # Handle help test differently, no folder path to use
            if test == 'help':
                rga_cmd.append(vulkan_tests[test][1])
            else:
                # construct command line
                # Input file paths are INPUT_FOLDER + folder_name + input_file_name.
                # Folder_name is vulkan_tests[test][0].
                # Input file names defined by --vert-*, --frag-*, --tesc-*, --tese-*, and --comp-*
                # rga arguments.
                make_file_path = False
                add_api = False
                add_target_gpu = False
                for option in vulkan_tests[test][1]:
                    # RGA options with argument values
                    if add_target_gpu is True:
                        # This option is the value of the Target GPU under test.
                        rga_cmd.append(option)
                        target_gpu = option
                        continue
                    if add_api is True:
                        # This option is the value of the API under test.
                        rga_cmd.append(option)
                        continue
                    if make_file_path is True:
                        # convert this option into a full file path to input file.
                        input_file_path = os.path.join(input_folder, vulkan_tests[test][0], option)
                        rga_cmd.append(input_file_path)
                        make_file_path = False
                        continue
                    if option == '-s':
                        # Used for negative test of -s values.
                        rga_cmd.append(option)
                        add_api = True
                        continue
                    if option == '-c':
                        # Used when test case wants to use a target GPU list other than the default.
                        rga_cmd.append(option)
                        add_target_gpu = True
                        continue
                    if '--vert' in option or '--frag' in option or '--tesc' in option or '--tese' in option or '--comp' in option:
                        make_file_path = True
                        rga_cmd.append(option)
                        continue
                    if option == '-a':
                        output_file_path = os.path.join(output_folder, vulkan_tests[test][0], target_gpu + '_analysis.txt')
                        rga_cmd.append(option)
                        rga_cmd.append(output_file_path)
                        continue
                    if option == '-b':
                        output_file_path = os.path.join(output_folder, vulkan_tests[test][0], target_gpu + '_binary.bin')
                        rga_cmd.append(option)
                        rga_cmd.append(output_file_path)
                        continue

                    # RGA standalone options
                    rga_cmd.append(option)

            # Make sure command line includes a target API and GPU specification
            if '-s' not in rga_cmd:
                rga_cmd = ['-s', vulkan_target_gpus] + rga_cmd
            if '-c' not in rga_cmd:
                rga_cmd = rga_cmd + ['-c', 'Vulkan']

            # debug
            print(rga_cmd)

            # Run test and verify results.
            if 'POSITIVE' in vulkan_tests[test][2]:
                test_status = pos_test_run(rga_cmd, test, vulkan_tests[test][3])
            if 'NEGATIVE' in vulkan_tests[test][2]:
                test_status = neg_test_run(rga_cmd, test, vulkan_tests[test][3])

            if test_status is False:
                # If any one test fails, return failing status.
                # to be considered: set a threshold for number of failing test cases before test is a failure.
                status = False

    return(status)


def pos_test_run(cmd):
    status = True
    fail_message = None
    # TBD run command and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    if proc_complete.returncode != 0:
        status = False
        fail_message = 'Command exited with failure status\n'
    if re.search('error', proc_complete.stdout, re.IGNORECASE):
        status = False
        fail_message += 'Error message in stdout\n'
    # compare the build output to the golden text.
    # Verify creation of all output files.

    if status is False:
        print(fail_message)

    return(status)

def neg_test_run(cmd):
    status = True
    # TBD run command and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    if proc_complete.returncode == 0:
        status = False
        fail_message = 'Command exited with a success status\n'
    if not re.search('error', proc_complete.stdout, re.IGNORECASE):
        status = False
        fail_message = 'Expected error message not displayed\n'
    # compare the build output to the golden text.
    # Verify failure to create output.

    if status is False:
        print(fail_message)

    return(status)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_folder', help='Full path to test input folder')
    parser.add_argument('output_folder', help='Full path to test output folder')
    parser.add_argument('test_suite', help='Name of test suite to run')
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()

    # Set test script globals from CLI input.
    INPUT_FOLDER = args.input_folder
    OUTPUT_FOLDER = args.output_folder
    TEST_SUITE = args.test_suite

    # Set sys.argv to unittest_args (leaving sys.argv[0] alone) and run tests
    sys.argv[1:] = args.unittest_args
    unittest.main()
