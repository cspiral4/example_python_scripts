#!python
#
# run_vulkan_test [--suite SUITE | --test TESTNAME]
# Default behavior: run SMOKE tests
#
# Based on PyTest test module, since this is functional tests of
# a C++ application.  Unit testing should be done using a different framework.
# The pytest marks are used to define suites
#
import os
import sys
import argparse
import logger
import re
import subprocess

from vulkan_tests import vulkan_tests
from vulkan_tests import vulkan_test_gpu
from RgaVulkanHelp import help_vulkan
from RgaBadApiHelp import help_bad_api

#
# Test Routines
#
@pytest.mark.smoke
def test_vulkan_smoke():
    '''Run RGA smoke tests of the Vulkan API'''
    vk_tests = {}
    vk_test_names = list(vulkan_tests)
    for test in vk_test_names:
        if 'SMOKE' in vulkan_tests[test][2]:
            vk_tests[test] = vulkan_tests[test]
    assert run_tests(vk_tests)

@pytest.mark.smoke
@pytest.mark.regression
def test_vk_help():
    '''positive help tests of RGA Vulkan API'''
    rga_cmd = ['rga', '-h', '-s', 'Vulkan']
    test_status = True
    # Run help command for Vulkan API and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    if proc_complete.returncode != 0:
        test_status = False
    if not re.match(help_vulkan, proc_complete.stdout):
        test_status = False
    assert test_status

@pytest.mark.regression
def test_rga_help_bad_api():
    '''negative help test of the RGA CLI'''
    rga_cmd = ['rga', '-h', '-s', 'bad_api']
    test_status = True
    # Run help command for Vulkan API and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    if proc_complete.returncode == 0:
        test_status = False
    if not re.match(help_bad_api, proc_complete.stdout):
        test_status = False
    assert test_status


@pytest.mark.regression
def test_vk_regression():
    '''Run RGA regression tests of the Vulkan API'''
    vk_tests = {}
    vk_test_names = list(vulkan_tests)
    for test in vk_test_names:
        if 'REGRESSION' in vulkan_tests[test][2]:
            vk_tests[test] = vulkan_tests[test]
    assert run_tests(vk_tests)

@pytest.mark.build
def test_vk_build():
    '''Run RGA build tests of the Vulkan API'''
    k_tests = {}
    vk_test_names = list(vulkan_tests)
    for test in vk_test_names:
        if 'BUILD' in vulkan_tests[test][2]:
            vk_tests[test] = vulkan_tests[test]
    assert run_tests(vk_tests)


#
# convenience routines
#
def vk_pos_test(test_name, cmd, test_desc):
    '''Run RGA positive regression test of the Vulkan API'''
    test_status = True
    # Run command and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    if proc_complete.returncode != 0:
        test_status = False
    # TBD create per test expected command output files to match.
    if re.search('error', proc_complete.stdout, re.IGNORECASE) is not None:
        test_status = False
    if proc_complete.stderr is not None:
        test_status = False
    # TBD compare the build output to the golden text.
    if not verify_cmd_output(proc_complete.stdout, proc_complete.stderr):
        test_status = False
    # TBD Verify creation of all output files.
    if not verify_output_files(output_folder):
        test_status = False

    return(test_status)
        

def vk_neg_test(test_name, cmd, test_desc):
    '''Run negative test cases'''
    proc_complete = subprocess.run(cmd, capture_output=True)
    report_output_files()
    if proc_complete.returncode == 0:
        test_status = False
    # create per test expected command output files to match
    if re.search('error', proc_complete.stdout, re.IGNORECASE) is None:
        test_status = False
    if re.search('error', proc_complete.stderr, re.IGNORECASE) is None:
        test_status = False
    # TBD compare build output to expected failure output.
    if not verify_neg_cmd_output(proc_complete.stdout, proc_complete.stderr):
        test_status = False

    return(test_status)

def construct_cmd(rga_options, sample_name):
    '''Construct the RGA CLI command line to test'''
    # TBD construct list of expected output files (full paths).
    # Initialize variables.
    rga_cmd = ['rga']
    script_root = sys.path[0]

    # construct command line
    # Input file paths are INPUT_FOLDER + folder_name + input_file_name.
    # Folder_name is vulkan_tests[test][0].
    # Input file names defined by --vert-*, --frag-*, --tesc-*, --tese-*, and --comp-*
    # rga arguments.
    make_file_path = False
    add_api = False
    add_target_gpu = False
    # TBD set output folder path relative to test script root folder
    # output folder name to include date/timestamp info for uniqueness
    # Use test input folder name as for output folder construction.
    output_folder = os.path.join(script_root, 'test_output', sample_name)
    # TBD set input folder path relative to test script root folder
    # use sample_name as sample folder name.
    input_folder = os.path.join(script_root, 'test_input', sample_name)
    for option in vulkan_tests[test][1]:
        # RGA options with argument values
        if add_target_gpu is True:
            # This option is the value of the Target GPU under test.
            rga_cmd.append(option)
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
            make_file_path = True
            rga_cmd.append(option)
            continue
        if option == '-a':
            output_file_path = os.path.join(output_folder, vulkan_test_gpu + '_analysis.txt')
            rga_cmd.append(option)
            rga_cmd.append(output_file_path)
            continue
        if option == '-b':
            output_file_path = os.path.join(output_folder, vulkan_test_gpu + '_binary.bin')
            rga_cmd.append(option)
            rga_cmd.append(output_file_path)
            continue

        # RGA standalone options
        rga_cmd.append(option)

    # Make sure command line includes a target API and GPU specification
    if '-s' not in rga_cmd:
        rga_cmd = ['-s', 'Vulkan'] + rga_cmd
    if '-c' not in rga_cmd:
        rga_cmd = rga_cmd + ['-c', vulkan_test_gpu]

    # debug
    print(rga_cmd)
    return(rga_cmd)

def run_tests(tests)
    '''Run tests using a filtered list.'''
    test_names = list(tests)
    suite_status = True
    for test in tests:
        rga_cmd = construct_cmd(tests[test][1], tests[test][0])
        if 'POSITIVE' in tests[test][2]:
            if not vk_pos_test(test, rga_cmd, tests[test][3]):
                suite_status = False
        elif 'NEGATIVE' in tests[test][2]:
            if not vk_neg_test(test, rga_cmd, tests[test][3]):
                suite_status = False
        else:
            print('WARNING: test %s not marked as POSITIVE or NEGATIVE'%test)
            print('WARNING: Please update the test suite list in vulkan_tests.py')

    return(suite_status)


def verify_cmd_output(test_name, output):
    '''Compare test output with expected positive output.'''
    pass

def verify_neg_cmd_output(test_name, output):
    '''Compare test output with expected negative output.'''
    pass

def verify_output_files(output_folder, expected_files):
    '''Verify expected files created
       Compare file contents with golden file contents.
     output_folder: folder containing files generated by the test run.
     expected_files: list of files expected to be generated by the test run.
       Verify the files exist and match the golden files '''
    pass

def report_output_files(output_folder):
    '''For negative RGA tests, output files and file
       contents are expected to be invalid.
       Report files created and metadata (size, permissions, type).'''
    pass
