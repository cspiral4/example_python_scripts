#!python
#
# This script runs tests of the Radeon GPU Analyzer CLI Vulkan support.
#
import sys
import os
import argparse
# TBD add logger support, replace print statements.
import re
import subprocess
import unittest

from vulkan_tests import vulkan_tests
from vulkan_tests import vulkan_target_gpu
from RgaVulkanHelp import help_vulkan
from RgaBadApiHelp import help_bad_api

SUCCESS = "SUCCESS"
FAIL = "FAIL"
global INPUT_FOLDER
global OUTPUT_FOLDER
global TEST_SUITE
TARGET_GPU = vulkan_target_gpu

class TestRgaCli(unittest.TestCase):
    def __init__(self):
        self.output_folder = None
        self.test_desc = None
        self.rga_cmd = None
        self.test = None
        self.logger = None
        self.vk_tests = {}

    def setUp(self):
        self.vk_tests = create_vulkan_tests(self, *args, **kwargs)

    def testHelp(self):
        # Verify rga -h -s Vulkan
        self.assertTrue(test_vulkan_help())

    def testHelpNeg(self):
        # Verify rga -h -s bad_api
        self.assertTrue(test_help_bad_api())

    def create_vulkan_tests(self, *args, **kwargs):
        test_keys = list(vulkan_tests)
        target_gpu = vulkan_target_gpu
        vulkan_tests = {}

        for test in test_keys:
            # Initialize variables.
            self.rga_cmd = ['rga']

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
                    self.rga_cmd.append(vulkan_tests[test][1])
                else:
                    # construct command line
                    # Input file paths are INPUT_FOLDER + folder_name + input_file_name.
                    # Folder_name is vulkan_tests[test][0].
                    # Input file names defined by --vert-*, --frag-*, --tesc-*, --tese-*, and --comp-*
                    # rga arguments.
                    make_file_path = False
                    add_api = False
                    add_target_gpu = False
                    self.output_folder = os.path.join(output_folder, vulkan_tests[test][0])
                    self.test_desc = vulkan_tests[test][3]
                    self.test = test
                    for option in vulkan_tests[test][1]:
                        # RGA options with argument values
                        if add_target_gpu is True:
                            # This option is the value of the Target GPU under test.
                            self.rga_cmd.append(option)
                            target_gpu = option
                            continue
                        if add_api is True:
                            # This option is the value of the API under test.
                            self.rga_cmd.append(option)
                            continue
                        if make_file_path is True:
                            # convert this option into a full file path to input file.
                            input_file_path = os.path.join(input_folder, vulkan_tests[test][0], option)
                            self.rga_cmd.append(input_file_path)
                            make_file_path = False
                            continue
                        if option == '-s':
                            # Used for negative test of -s values.
                            self.rga_cmd.append(option)
                            add_api = True
                            continue
                        if option == '-c':
                            # Used when test case wants to use a target GPU list other than the default.
                            self.rga_cmd.append(option)
                            add_target_gpu = True
                            continue
                        if '--vert' in option or '--frag' in option or '--tesc' in option or '--tese' in option or '--comp' in option:
                            make_file_path = True
                            self.rga_cmd.append(option)
                            continue
                        if option == '-a':
                            output_file_path = os.path.join(output_folder, vulkan_tests[test][0], target_gpu + '_analysis.txt')
                            self.rga_cmd.append(option)
                            self.rga_cmd.append(output_file_path)
                            continue
                        if option == '-b':
                            output_file_path = os.path.join(output_folder, vulkan_tests[test][0], target_gpu + '_binary.bin')
                            self.rga_cmd.append(option)
                            self.rga_cmd.append(output_file_path)
                            continue

                        # RGA standalone options
                        self.rga_cmd.append(option)

                # Make sure command line includes a target API and GPU specification
                if '-s' not in self.rga_cmd:
                    self.rga_cmd = ['-s', 'Vulkan'] + self.rga_cmd
                if '-c' not in self.rga_cmd:
                    self.rga_cmd = self.rga_cmd + ['-c', target_gpu]

                # debug
                print(self.rga_cmd)

                # Define a specific unittest for the test case described vulkan_tests[test].
                # Positive test cases.
                if 'POSITIVE' in vulkan_tests[test][2]:
                    def test_vulkan_pos(self, *args, **kwargs):
                        test_status = True
                        # Run command and capture output.
                        proc_complete = subprocess.run(cmd, capture_output=True)
                        if proc_complete.returncode != 0:
                            print('Command exited with failure status.\n')
                            test_status = False
                        # TBD create per test expected command output files to match.
                        if re.search('error', proc_complete.stdout, re.IGNORECASE):
                            print('Error message in stdout.\n')
                            test_status = False
                        # TBD compare the build output to the golden text.
                        if not verify_cmd_output(proc_complete.stdout):
                            print('Unexpected output for command.\n')
                            test_status = False
                        # TBD Verify creation of all output files.
                        if not verify_output_files(self.output_folder):
                            print('Unexpected file contents for command.\n')
                            test_status = False

                        return(test_status)
                    
                    vulkan_tests[test] = (vulkan_pos_test(self, *args, **kwargs))

                # Negative test cases.
                if 'NEGATIVE' in vulkan_tests[test][2]:
                    def test_vulkan_neg(self, *args, **kwargs):
                        test_status = True
                        # Run command and capture output.
                        proc_complete = subprocess.run(cmd, capture_output=True)
                        if proc_complete.returncode == 0:
                            print('Command exited with unexpected success status.\n')
                            test_status = False
                        # TBD create per test expected command output files to match.
                        if re.search('error', proc_complete.stdout, re.IGNORECASE):
                            print('No error message found in stdout.\n')
                            test_status = False
                        if re.search('error', proc_complete.stderr, re.IGNORECASE):
                            print('No error message found in stderr.\n')
                        # TBD compare the build output to the golden text.
                        if not verify_neg_cmd_output(proc_complete.stdout):
                            print('Unexpected output for command')
                            test_status = False
                        # TBD report status of expected file creation.
                        if not report_output_files(self.output_folder):
                            print('Unexpected file contents for command')
                            test_status = False

                        return(test_status)

                    vulkan_tests[test] = (vulkan_neg_test(self, *args, **kwargs))

        return(vulkan_tests)


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


def verify_cmd_output(cmd_stdout, stderr):
    pass

def verify_neg_cmd_output(cmd_stdout, stderr):
    pass

def report_output_files(output_folder):
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to test the RGA command line Vulkan API functionality')
    parser.add_argument('input_folder', help='Full path to test input folder')
    parser.add_argument('output_folder', help='Full path to test output folder')
    parser.add_argument('test_suite', help='Name of test suite to run')
    parser.add_argument('target_gpu', help='Target GPU to compile for, instead of the default GPU')
    parser.add_argument('unittest_args', nargs='*', help='Python unittest command line options, passed to the tests')
    args = parser.parse_args()

    # Set test script globals from CLI input.
    INPUT_FOLDER = args.input_folder
    OUTPUT_FOLDER = args.output_folder
    TEST_SUITE = args.test_suite
    TARGET_GPU = args.target_gpu

    # Set sys.argv to unittest_args (leaving sys.argv[0] alone) and run tests
    sys.argv[1:] = args.unittest_args

    # TBD Initialize test cases
    # run help tests and generated tests
    #unittest.main()
