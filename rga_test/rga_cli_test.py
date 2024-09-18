#!python

import sys
import os
import argparse
import subprocess
import unittest
import vulkan_tests
import RgaVulkanHelp
import RgaBadApiHelp

SUCCESS = "SUCCESS"
FAIL = "FAIL"

class TestRgaCli(unittest.TestCase):
    def setUp(self):
        self.input_folder = os.environ["INPUT_FOLDER"]
        self.output_folder = os.environ["OUTPUT_FOLDER"]
    
    def test_vulkan_pos(self):
        print(self.input_folder)
        print(self.output_folder)
        self.assertTrue(cli_test_pos(self.input_folder, self.output_folder))

    def test_vulkan_neg(self):
        self.assertTrue(cli_test_neg(self.input_folder, self.output_folder))

def cli_test_pos(input_folder, output_folder):
    status = True
    test_keys = list(vulkan_tests.pos_tests)
    for test in test_keys:
        rga_cmd = ['rga']
        if test == 'help':
            print("option list:")
            print(vulkan_tests.pos_tests[test][1])
            rga_cmd += vulkan_tests.pos_tests[test][1]
            # debug
            print(rga_cmd)
            # tbd - invoke command and catch output
            # Verify command status == 0
            # compare the vulkan help output to golden text
        else:
            input_path = os.path.join(input_folder, test)
            rga_args = []
            rga_output_files = []
            for rga_opt in vulkan_tests.pos_tests[test][1]:
                if rga_opt.find('vert') or rga_opt.find('frag') or rga_opt.find('comp'):
                    # add INPUT_FOLDER path to file name
                    input_file = os.path.join(input_path, rga_opt)
                    rga_args += [input_file]
                elif test in rga_opt:
                    # this is an output filename, add the output folder to the path
                    output_file = os.path.join(output_folder, test, rga_opt)
                    rga_args += [output_file]
                    rga_output_files += [output_file]
                else:
                    rga_args += rga_opt

            # debug
            print(rga_args)
            # TBD 
            # compare the build output to the golden text
            # Verify creation of all output files

    return(status)

def cli_test_neg(input_folder, output_folder):
    status = True
    test_keys = list(vulkan_tests.neg_tests)
    for test in test_keys:
        rga_cmd = ['rga']
        # debug
        print(rga_cmd)
        if test == 'help':
            rga_cmd += + vulkan_tests.neg_tests[test][1]
            # tbd - invoke command and catch output
            # Verify output matches bad API help output string
            # Verify exit status != 0
        else:
            input_path = os.path.join(input_folder, test)
            rga_args = []
            rga_output_files = []
            for rga_opt in vulkan_tests.pos_tests[test][1]:
                if rga_opt.find('vert') or rga_opt.find('frag') or rga_opt.find('comp'):
                    # add file name input path
                    input_file = os.path.join(input_path, rga_opt)
                    rga_args += [input_file]
                elif test in rga_opt:
                    # this is an output filename, add the output folder to the path
                    output_file = os.path.join(output_folder, test, rga_opt)
                    rga_args += [output_file]
                    rga_output_files += [output_file]
                else:
                    rga_args += rga_opt

            # debug
            print(rga_args)
            # TBD 
            # Verify exit status !=0
            # Verify error text matches expected error text

    return(status)

if __name__ == "__main__":
    
    unittest.main()
