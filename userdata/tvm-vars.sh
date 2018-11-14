#set -ex

THIS_DIR=$(cd $(dirname $BASH_SOURCE) && pwd)

export TVM_HOME=$(cd ${THIS_DIR}/.. && pwd)
export PATH=$PATH:$TVM_HOME/build/install/lib
export PYTHONPATH=$PYTHONPATH:$TVM_HOME/python:$TVM_HOME/nnvm/python:$TVM_HOME/topi/python/

#set +ex
