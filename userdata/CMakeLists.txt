
cmake_minimum_required(VERSION 3.2)

if (NOT CMAKE_TOOLCHAIN_FILE)
  set(ANDROID_NDK /opt/android-ndk-r14b/)
  #set(ANDROID_TOOLCHAIN_NAME arm-linux-androideabi-4.9)
  #set(ANDROID_ABI "armeabi-v7a with NEON")
  set(ANDROID_TOOLCHAIN_NAME aarch64-linux-android-4.9)
  set(ANDROID_ABI "arm64-v8a")
  set(ANDROID_NATIVE_API_LEVEL android-24)
  set(ANDROID_STL gnustl_static)
  set(ANDROID_APP_PIE TRUE)
  set(CMAKE_TOOLCHAIN_FILE /data/public-space/toolchains/android.toolchain.cmake)
endif ()

project(tvmtest C CXX)

add_definitions(-std=c++11)

include_directories(../include/ ../3rdparty/dmlc-core/include/ ../3rdparty//dlpack/include/)

add_library(deploy SHARED export/deploy_lib.o)

set_target_properties(deploy PROPERTIES
  LINKER_LANGUAGE C
)
target_link_libraries(deploy m)

add_executable(tvmtest infer.cpp)




