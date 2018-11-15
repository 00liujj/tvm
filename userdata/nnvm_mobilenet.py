"""
.. _tutorial-nnvm-quick-start:

Quick Start Tutorial for Compiling Deep Learning Models
=======================================================
**Author**: `Yao Wang <https://github.com/kevinthesun>`_

This example shows how to build a neural network with NNVM python frontend and
generate runtime library for Nvidia GPU and Raspberry Pi with TVM.
To run this notebook, you need to install tvm and nnvm.
Notice that you need to build tvm with cuda and llvm.
"""

######################################################################
# Overview for Supported Hardware Backend of TVM
# ----------------------------------------------
# The image below shows hardware backend currently supported by TVM:
#
# .. image:: https://github.com/dmlc/web-data/raw/master/tvm/tutorial/tvm_support_list.png
#      :align: center
#      :scale: 100%
#
# In this tutorial, we'll choose cuda and llvm as target backends.
# To begin with, let's import NNVM and TVM.
import tvm
import nnvm.compiler
import nnvm.testing


######################################################################
# Define Neural Network in NNVM
# -----------------------------
# First, let's define a neural network with nnvm python frontend.
# For simplicity, we'll use pre-defined resnet-18 network in NNVM.
# Parameters are initialized with Xavier initializer.
# NNVM also supports other model formats such as MXNet, CoreML and ONNX.
#
# In this tutorial, we assume we will do inference on our device
# and the batch size is set to be 1. Input images are RGB color
# images of size 224 * 224. We can call the :any:`nnvm.symbol.debug_str`
# to show the network structure.

batch_size = 1
num_class = 1000
image_shape = (3, 224, 224)
data_shape = (batch_size,) + image_shape
out_shape = (batch_size, num_class)

net, params = nnvm.testing.mobilenet.get_workload(batch_size=batch_size, image_shape=image_shape)
#print(net.debug_str())

######################################################################
# Compilation
# -----------
# Next step is to compile the model using the NNVM/TVM pipeline.
# Users can specify the optimization level of the compilation.
# Currently this value can be 0 to 2, which corresponds to
# "SimplifyInference", "OpFusion" and "PrecomputePrune" respectively.
# In this example we set optimization level to be 0
# and use Raspberry Pi as compile target.
#
# :any:`nnvm.compiler.build` returns three components: the execution graph in
# json format, the TVM module library of compiled functions specifically
# for this graph on the target hardware, and the parameter blobs of
# the model. During the compilation, NNVM does the graph-level
# optimization while TVM does the tensor-level optimization, resulting
# in an optimized runtime module for model serving.
#
# We'll first compile for Nvidia GPU. Behind the scene, `nnvm.compiler.build`
# first does a number of graph-level optimizations, e.g. pruning, fusing, etc.,
# then registers the operators (i.e. the nodes of the optmized graphs) to
# TVM implementations to generate a `tvm.module`.
# To generate the module library, TVM will first transfer the HLO IR into the lower
# intrinsic IR of the specified target backend, which is CUDA in this example.
# Then the machine code will be generated as the module library.

import logging
#logging.basicConfig(level=logging.DEBUG) # to dump TVM IR after fusion

opt_level = 3
#target = tvm.target.cuda()
#target = 'llvm'
#target = tvm.target.create("llvm -device=arm_cpu -target=armv7a -mcpu=cortex-a53 -mattr=+neon")
#target = "llvm -target=arm -mattr=+neon -mfloat-abi=hard -mcpu=cortex-a9"
#target = tvm.target.rasp()
target = tvm.target.arm_cpu("mate10")
print('target for mate10', target)
target_host = "llvm -device=arm_cpu -target=arm64-linux-android -mattr=+neon"
target_host = None
target = tvm.target.mali('rk3399')
#target = "llvm -device=arm_cpu -target=arm64-linux-android -mattr=+neon"
target = tvm.target.arm_cpu('rasp3b')
target = "llvm -device=arm_cpu -target=arm-linux-gnueabihf -mattr=+neon"
#target = "llvm"
print('target', target, 'target_host', target_host)
with nnvm.compiler.build_config(opt_level=opt_level):
    graph, lib, params = nnvm.compiler.build(
        net, target, target_host=target_host, shape={"data": data_shape}, params=params)


import sys, os

dirname = 'export/'
if not os.path.exists(dirname):
    os.mkdir(dirname)
lib.save(dirname + "deploy_lib.o")
#lib.export_library(dirname + "libdeploy_lib.so")

#from tvm.contrib import ndk
#lib.export_library(dirname+"deploy_lib.so", ndk.create_shared)

with open(dirname + "deploy_graph.json", "w") as fo:
    fo.write(graph.json())
with open(dirname + "deploy_param.params", "wb") as fo:
    fo.write(nnvm.compiler.save_param_dict(params))



