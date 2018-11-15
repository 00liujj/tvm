project(opencl)

if (NOT OpenCL)
set(OpenCL OpenCL)
endif ()


add_library(${OpenCL} SHARED opencl_stubs.c)
target_include_directories(${OpenCL} PUBLIC ../include)
