#
# test descriptions
#
#  testname: [ shaderfolder, [ cli arg list ],
# NOTE: help test handled uniquely in test functions
#
pos_tests = {
    "test01": [ 'help', [ '-h', '-s', 'Vulkan'], "Verify Vulkan API help output"],
    "test02": [ 'computenbody',
                ['-s', 'Vulkan', '-c', 'gfx1100',
                 '--vert-glsl', 'particle.vert',
                 '--frag-glsl', 'particle.frag',
                 '--comp-glsl', 'particle.comp',
                 '-a', 'computenbody_analysis',
                 '-b', 'computenbody.bin',
                 '-v', '--keep'],
                "Verify vert, frag, and comp compilation using computenbody Vulkan shaders"]
    }

neg_tests = {
    "test01": [ 'help', [ '-h', '-s', 'bad_api'], "Verify correct handling of invalid API name"],
    "test02": [ 'cnbody_bad_folder',
                ['s', 'Vulkan', '-c', 'gfx1100',
                 '--vert-glsl', 'particle.vert',
                 '--frag-glsl', 'particle.frag',
                 '--comp-glsl', 'particle.comp',
                 '-a', 'computenbody_analysis',
                 '-b', 'computenbody.bin',
                 '-v', '--keep'],
                "Verify handling of invalid input file paths" ]
    }
