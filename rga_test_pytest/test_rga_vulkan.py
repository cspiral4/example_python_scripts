#!python
#
# run_vulkan_test [--suite SUITE | --test TESTNAME]
# Default behavior: run SMOKE tests
#
# Based on PyTest test module, since this is functional tests of
# a C++ application.  Unittesting should be done using a different framework.
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

@pytest.marker.smoke
def test_vulkan_smoke():
    '''Run RGA smoke tests of the Vulkan API'''
    vk_tests = {}
    vk_test_names = list(vulkan_tests)
    for test in vk_test_names:
        if 'SMOKE' in vulkan_tests[test][2]:
            vk_tests[test] = vulkan_tests[test]
    run_tests(vk_tests)

@pytest.marker.smoke
@pytest.marker.regression
def test_vk_help():
    '''Run positive and negative help tests of RGA CLI'''
    rga_cmd = ['rga', '-h', '-s', 'Vulkan']
    # Run help command for Vulkan API and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    assert proc_complete.returncode == 0
    assert re.match(help_vulkan, proc_complete.stdout)

@pytest.marker.regression
def test_rga_bad_api():
    rga_cmd = ['rga', '-h', '-s', 'bad_api']
    # Run help command for Vulkan API and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    assert proc_complete.returncode != 0
    assert re.match(help_bad_api, proc_complete.stdout)


@pytest.marker.regression
def test_vk_regression():
    '''Run RGA regression tests of the Vulkan API'''
    vk_tests = {}
    vk_test_names = list(vulkan_tests)
    for test in vk_test_names:
        if 'REGRESSION' in vulkan_tests[test][2]:
            vk_tests[test] = vulkan_tests[test]
    run_tests(vk_tests)

@pytest.marker.build
def test_vk_build():
    '''Run RGA build tests of the Vulkan API'''
    k_tests = {}
    vk_test_names = list(vulkan_tests)
    for test in vk_test_names:
        if 'BUILD' in vulkan_tests[test][2]:
            vk_tests[test] = vulkan_tests[test]
    run_tests(vk_tests)

def vk_pos_test(test_name, cmd, test_desc):
    '''Run RGA positive regression test of the Vulkan API'''
    # Run command and capture output.
    proc_complete = subprocess.run(cmd, capture_output=True)
    assert proc_complete.returncode == 0
    # TBD create per test expected command output files to match.
    assert re.search('error', proc_complete.stdout, re.IGNORECASE) is not None
    # TBD compare the build output to the golden text.
    assert verify_cmd_output(proc_complete.stdout)
    # TBD Verify creation of all output files.
    assert verify_output_files(output_folder)
        

def vk_neg_test(test_name, cmd, test_desc):
    '''Run negative test cases'''
    proc_complete = subprocess.run(cmd, capture_output=True)
    report_output_files()
    assert proc_complete.returncode != 0
    # TBD create per test expected command output files to match
    assert re.search('error', proc_complete.stdout, re.IGNORECASE) is not None
    assert re.search('error', proc_complete.stderr, re.IGNORECASE) is not None
    # TBD compare build output to expected failure output.
    assert verify_neg_cmd_output(proc_complete.stdout, proc_complete.stderr)
    

def construct_cmd(rga_options):
    '''Construct the RGA CLI command line to test'''
    # Initialize variables.
    rga_cmd = ['rga']

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
    output_folder = os.path.join(script_root, vulkan_tests[test][0])
    # TBD set input folder path relative to test script root folder
    # use test[testname][0] as sample folder name.
    input_folder = os.path.join(script_root, 'samples')
    test_desc = vulkan_tests[test][3]
    test = test
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
            output_file_path = os.path.join(output_folder, vulkan_tests[test][0], vulkan_test_gpu + '_analysis.txt')
            rga_cmd.append(option)
            rga_cmd.append(output_file_path)
            continue
        if option == '-b':
            output_file_path = os.path.join(output_folder, vulkan_tests[test][0], vulkan_test_gpu + '_binary.bin')
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
    '''Run tests using the filtered list.'''
    test_names = list(tests)
    for test in tests:
        rga_cmd = construct_cmd(tests[test][1])
        if 'POSITIVE' in tests[test][2]:
            assert vk_pos_test(test, rga_cmd, tests[test][3])

        if 'NEGATIVE' in tests[test][2]:
            assert vk_neg_test(test, rga_cmd, tests[test][3])
