
cmake_minimum_required(VERSION 3.2)

if (ARM)
  set(CMAKE_TOOLCHAIN_FILE /data/public-space/toolchains/linux-gcc-4.9-arm-hard-toolchain.cmake)
elseif (ANDROID)
  set(ANDROID_NDK /opt/android-ndk-r14b/)
  #set(ANDROID_TOOLCHAIN_NAME arm-linux-androideabi-4.9)
  #set(ANDROID_ABI "armeabi-v7a with NEON")
  set(ANDROID_TOOLCHAIN_NAME aarch64-linux-android-4.9)
  set(ANDROID_ABI "arm64-v8a")
  set(ANDROID_NATIVE_API_LEVEL android-24)
  set(ANDROID_STL gnustl_static)
  set(ANDROID_APP_PIE TRUE)
  set(CMAKE_TOOLCHAIN_FILE ${CMAKE_CURRENT_LIST_DIR}/android.toolchain.cmake)
endif ()

project(tvmtest C CXX)

set(CMAKE_BUILD_TYPE Debug)

add_definitions(-std=c++11)

include_directories(../include/ ../3rdparty/dmlc-core/include/ ../3rdparty//dlpack/include/ Mali_OpenCL_SDK/include/)

add_library(deploy SHARED export/deploy_lib.o)

set_target_properties(deploy PROPERTIES
  LINKER_LANGUAGE C
)
target_link_libraries(deploy m)


set(OpenCL OpenCL)
add_subdirectory(Mali_OpenCL_SDK/lib)

add_executable(tvmtest infer.cpp)
target_link_libraries(tvmtest
  #${OpenCL}
  pthread dl)

add_subdirectory(Mali_OpenCL_SDK/common/)
add_executable(testsgemm Mali_OpenCL_SDK/samples/sgemm/sgemm.cpp)
target_include_directories(testsgemm PUBLIC Mali_OpenCL_SDK/common/ Mali_OpenCL_SDK/include/)
target_link_libraries(testsgemm ${OpenCL} Common)

