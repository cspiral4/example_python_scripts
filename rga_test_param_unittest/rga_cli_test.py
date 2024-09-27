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
from parameterized import parameterized

from vulkan_tests import vulkan_tests
from vulkan_tests import vulkan_target_gpu
from RgaVulkanHelp import help_vulkan
from RgaBadApiHelp import help_bad_api

SUCCESS = "SUCCESS"
FAIL = "FAIL"
global INPUT_FOLDER
global OUTPUT_FOLDER
global TEST_SUITE

class TestRgaCli(unittest.TestCase):
    def __init__(self):
        self.test_desc = None
        self.test = None
        self.logger = None
        self.test_params_pos = []
        self.test_params_neg = []

    def setUp(self):
        self.build_params_list(self)

    def test_help(self):
        # Verify rga -h -s Vulkan
        self.assertTrue(test_vulkan_help())

    def test_help_neg(self):
        # Verify rga -h -s bad_api
        self.assertTrue(test_help_bad_api())

    def build_params_list(self):
        # Convert vulkan_tests to input parameters for positive and negative tests
        test_names = list(vulkan_tests)
        test_params = [(None, None, None)]
        for test_name in test_names:
            if TEST_SUITE in vulkan_tests[test_name][2]:
                cmd_options = construct_cmd_opts(vulkan_tests[test_name][1], vulkan_tests[test_name][0])
                suites = vulkan_tests[test_name][2]
                test_folder = vulkan_tests[test_name][0]
                test_desc = vulkan_tests[test_name][3]
                if 'NEGATIVE' in vulkan_tests[test_name][2]:
                    self.test_params_neg += [(test_name, cmd_options, test_folder, test_desc)]
                else:
                    self.test_params_pos += [(test_name, cmd_options, test_folder, test_desc)]

    def construct_cmd_opts(self, opts_list, sample_name):
        # Add input folder path to input file arguments.
        # Add output folder path to output file arguments.
        target_gpu = vulkan_target_gpu
        rga_cmd = ['rga']
        # construct command line
        # Input file paths are INPUT_FOLDER + folder_name + input_file_name.
        # Folder_name is vulkan_tests[test][0].
        # Input file names defined by --vert-*, --frag-*, --tesc-*, --tese-*, and --comp-*
        # rga arguments.
        make_file_path = False
        add_api = False
        add_target_gpu = False
        output_folder = os.path.join(OUTPUT_FOLDER, sample_name)
        input_folder = os.path.join(INPUT_FOLDER, sample_name)
        for option in opts_list:
            # RGA options with argument values
            if add_target_gpu is True:
                # This option is the value of the Target GPU under test.
                rga_cmd.append(option)
                target_gpu = option
                add_target_gpu = False
                continue
            if add_api is True:
                # This option is the value of the API under test.
                rga_cmd.append(option)
                add_api = False
                continue
            if make_file_path is True:
                # convert this option into a full file path to input file.
                input_file_path = os.path.join(input_folder, option)
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
                # Input file specifier.
                make_file_path = True
                rga_cmd.append(option)
                continue
            if option == '-a':
                # Create analysis file from input files.
                output_file_path = os.path.join(output_folder, target_gpu + '_analysis.txt')
                rga_cmd.append(option)
                rga_cmd.append(output_file_path)
                continue
            if option == '-b':
                # Create a binary image from the input files.
                output_file_path = os.path.join(output_folder, target_gpu + '_binary.bin')
                rga_cmd.append(option)
                rga_cmd.append(output_file_path)
                continue
            # RGA standalone options
            rga_cmd.append(option)

        # Make sure command line includes a target API and GPU specification
        if '-s' not in rga_cmd:
            rga_cmd = ['-s', 'Vulkan'] + rga_cmd
        if '-c' not in rga_cmd:
            rga_cmd = rga_cmd + ['-c', target_gpu]

        return rga_cmd

    @parameterized.expand(self.test_params_pos)
    def test_rga_pos(self, test_name, rga_cmd, sample_name, test_desc):
        test_status = True
        # Run command and capture output.
        proc_complete = subprocess.run(rga_cmd, capture_output=True)
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


    @parameterized.expand(self.test_params_neg)
    def test_rga_neg(self, test_name, rga_cmd, sample_name, test_desc):
        test_status = True
        # Run command and capture output.
        proc_complete = subprocess.run(rga_cmd, capture_output=True)
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

    # run tests
    unittest.main()
