set -ex

CXX=g++
CXX=/data/public-space/toolchains/gcc-linaro-4.9-2016.02-x86_64_arm-linux-gnueabihf/bin/arm-linux-gnueabihf-g++
CXX=/opt/android-ndk-r11b/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/bin/arm-linux-androideabi-g++

ARM_OPTS="-march=armv7-a -mfloat-abi=softfp -mfpu=neon"

$CXX -shared -fPIC deploy_lib.o -o deploy.so $ARM_OPTS

$CXX -O3 ../infer.cpp -I ../../include/ -I ../../dmlc-core/include/ -I ../../dlpack/include/ -std=c++11 -pthread -ldl $ARM_OPTS



