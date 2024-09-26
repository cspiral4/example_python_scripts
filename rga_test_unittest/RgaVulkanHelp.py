help_vulkan = """*** Vulkan mode options ***
===========================

Usage:
  rga.exe [options]

 Generic options:
  -l, --list-asics        List the known GPU codenames, architecture names
                          and variant names. To target a specific GPU, use its
                          codename as the argument to the "-c" command line
                          switch.
  -c, --asic arg          Which ASIC to target.  Repeatable.
      --version           Print version string.
  -h, --help              Produce this help message.
  -a, --analysis arg      Path to output analysis file.
  -b, --binary arg        Path to ELF binary output file.
      --isa arg           Path to output ISA disassembly file(s).
      --livereg arg       Path to live register analysis output file(s).
      --livereg-sgpr arg  Path to live register sgpr analysis output file(s).
      --cfg arg           Path to per-block control flow graph output
                          file(s).
      --cfg-i arg         Path to per-instruction control flow graph output
                          file(s).
  -s, --source-kind arg   Source platform: dx12 for DirectX 12, dxr for DXR,
                          dx11 for DirectX 11, vulkan for Vulkan, opengl for
                          OpenGL, opencl for OpenCL offline mode and amdil for
                          AMDIL.
  -u, --updates           Check for available updates.
  -v, --verbose           Print command line strings that RGA uses to launch
                          external processes.

 Macro and Include paths options:
  -D, --define arg       Define symbol or symbol=value. Repeatable.
  -I, --IncludePath arg  Additional include path required for compilation.
                         Repeatable.

 Input shader type options:
      --vert arg  Full path to vertex shader input file.
      --tesc arg  Full path to tessellation control shader input file.
      --tese arg  Full path to tessellation evaluation shader input file.
      --geom arg  Full path to geometry shader input file.
      --frag arg  Full path to fragment shader input file
      --comp arg  Full path to compute shader input file.

 By default, input files would be interpreted as SPIR-V binary files, unless the file extension is any of the following:
   .vert  --> GLSL source file.
   .frag  --> GLSL source file.
   .tesc  --> GLSL source file.
   .tese  --> GLSL source file.
   .geom  --> GLSL source file.
   .comp  --> GLSL source file.
   .glsl  --> GLSL source file.
   .vs    --> GLSL source file.
   .fs    --> GLSL source file.


Usage:
  rga.exe [options]

 Vulkan mode options:
      --stage-glsl arg       Full path to [stage] input file, while forcing
                             interpretation of input file as glsl source file
                             rather than SPIR-V binary. arg is the full path to
                             stage shader input file. stage can be one of:
                             "vert", "tesc", "tese", "geom", "frag", "comp". For
                             example, use "--vert-glsl shader.glsl" to
                             specify path to the vertex shader file and indicate
                             that it is a glsl source file (rather than a SPIR-V
                             binary).
      --stage-spvas arg      Full path to [stage] input file, while forcing
                             interpretation of input file as SPIR-V textual
                             source file rather than SPIR-V binary. arg is the
                             full path to stage shader input file. stage can be
                             one of: "vert", "tesc", "tese", "geom", "frag",
                             "comp". For example, use "--vert-spvas shader.txt"
                             to specify path to the vertex shader file and
                             indicate that it is a SPIR-V textual source file
                             (rather than a SPIR-V binary).
      --pso arg              Full path to .gpso (graphics) or .cpso (compute)
                             pipeline state JSON file. If no pipeline state
                             file is provided, a default pipeline state would
                             be used. In that case, if your shaders do not
                             match the default state, the compilation would fail.
      --icd arg              Full path to a Vulkan ICD. If given, RGA would
                             load the given ICD explicitly instead of the
                             Vulkan loader.
      --loader-debug arg     Value for the VK_LOADER_DEBUG environment
                             variable (all, error, info, warn, debug). Use this
                             option to log Vulkan loader messages to the console.
      --glslang-opt arg      Additional options to be passed to glslang for
                             Vulkan front-end compilation (for example,
                             "--target-env vulkan1.1 --suppress-warnings").It is
                             recommended to wrap the argument to this option with
                             '@' characters in the case where glslang and rga
                             options overlap, like -c or -w. For example,
                             --glslang-opt "@-c -w@".
      --disassemble-spv arg  Disassemble SPIR-V binary file. Accepts an
                             optional argument with the full path to the output
                             file where the disassembly would be saved. If not
                             specified, the disassembly would be printed to
                             stdout.
      --validation           Enable Vulkan validation layers and dump the
                             output of validation layers to stdout.
      --validation-file arg  Enable Vulkan validation layers and dump the
                             output of validation layers to the text file
                             specified by the option argument.

Alternative glslang compiler and SPIR-V tools.
RGA uses the glslang package that it ships with as the default front-end compiler for Vulkan.
Use this option to provide a custom glslang package

Usage:
  rga.exe [options]

      --compiler-bin arg  Path to alternative compiler's binaries folder. The
                          following executables are expectedto be in this
                          folder: glslangValidator, spirv-as, spirv-dis. If
                          given, this package would beused instead of the glslang
                          package that is bundled with RGA to compile GLSL to
                          SPIR-V,disassemble SPIR-V binaries, reassemble SPIR-V
                          binaries, etc.

"""