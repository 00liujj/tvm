import tvm
import numpy as np
from tvm.contrib import graph_runtime as runtime
import nnvm.symbol as sym
import nnvm.compiler
from nnvm.testing import utils


out_channels = 16
data = sym.Variable(name="data")
simple_net = sym.conv2d(data=data, kernel_size=(3,3), channels=out_channels, padding = (1, 1), use_bias=True)
simple_net = sym.batch_norm(data=simple_net)
simple_net = sym.relu(data=simple_net)

batch_size = 1
data_shape = (batch_size, 3, 224, 224)
net, params = utils.create_workload(simple_net, batch_size, data_shape[1:])

print(net, params)

import logging
logging.basicConfig(level=logging.DEBUG) # to dump TVM IR after fusion

target = "llvm -target=arm-linux-gnueabihf -mcpu=cortex-a53 -mattr=+neon"
#target = "cuda"
with nnvm.compiler.build_config():
  graph, lib, params = nnvm.compiler.build(
    net, target, shape={"data": data_shape}, params=params)

print(graph)

lib.save("xxxdeploy_lib.o")

#print(params)

