#include <dlpack/dlpack.h>
#include <tvm/runtime/module.h>
#include <tvm/runtime/registry.h>
#include <tvm/runtime/packed_func.h>

// g++ infer.cpp -I ../include/ -I ../dmlc-core/include/ -I ../dlpack/include/ -std=c++11 -pthread -ldl
#include "../apps/howto_deploy/tvm_runtime_pack.cc"

#include <fstream>
#include <iterator>
#include <algorithm>

int main(int argc, char* argv[])
{
    printf("enter main\n");
    // tvm module for compiled functions
    tvm::runtime::Module mod_syslib = tvm::runtime::Module::LoadFromFile("./libdeploy.so");

    // json graph
    std::ifstream json_in("deploy_graph.json", std::ios::in);
    std::string json_data((std::istreambuf_iterator<char>(json_in)), std::istreambuf_iterator<char>());
    json_in.close();

    // parameters in binary
    std::ifstream params_in("deploy_param.params", std::ios::binary);
    std::string params_data((std::istreambuf_iterator<char>(params_in)), std::istreambuf_iterator<char>());
    params_in.close();


    int dtype_code = kDLFloat;
    int dtype_bits = 32;
    int dtype_lanes = 1;
    //int device_type = kDLOpenCL;
    int device_type = kDLCPU;
    int device_id = 0;

    DLTensor* x;
    int in_ndim = 4;
    int64_t in_shape[4] = {1, 3, 224, 224};
    TVMArrayAlloc(in_shape, in_ndim, dtype_code, dtype_bits, dtype_lanes, device_type, device_id, &x);
    // load image data saved in binary
    std::ifstream data_fin("cat.bin", std::ios::binary);
    data_fin.read(static_cast<char*>(x->data), 3 * 224 * 224 * 4);

    if (1) {
        // call directly
        tvm::runtime::GraphRuntime grt;
        TVMContext ctx;
        ctx.device_id = device_id;
        ctx.device_type = (DLDeviceType)device_type;

        grt.Init(json_data, mod_syslib, {ctx});

        printf("grt init ok\n");

        int idx = grt.GetInputIndex("data");
        printf("the index for data is %d\n", idx);
        if (idx >= 0) {
            grt.SetInput(idx, x);
        }
        grt.LoadParams(params_data);

        printf("load params ok\n");

        for (int i=0; i<10; i++) {
            clock_t start = clock();
            grt.Run();
            printf("the infer time is %.2fms\n", 1e3*(clock()-start)/CLOCKS_PER_SEC);
        }

        return 0;
    }

    // get global function module for graph runtime
    tvm::runtime::Module mod = (*tvm::runtime::Registry::Get("tvm.graph_runtime.create"))(json_data, mod_syslib, device_type, device_id);

    printf("enter set_input\n");

    // get the function from the module(set input data)
    tvm::runtime::PackedFunc set_input = mod.GetFunction("set_input");
    set_input("data", x);

    printf("enter load_params\n");

    // get the function from the module(load patameters)
    // parameters need to be TVMByteArray type to indicate the binary data
    TVMByteArray params_arr;
    params_arr.data = params_data.c_str();
    params_arr.size = params_data.length();
    tvm::runtime::PackedFunc load_params = mod.GetFunction("load_params");
    load_params(params_arr);

    // get the function from the module(run it)
    tvm::runtime::PackedFunc run = mod.GetFunction("run");

    printf("enter run\n");

    for (int i=0; i<10; i++) {

        clock_t start = clock();
        run();
        printf("the infer time is %.2fms\n", 1e3*(clock()-start)/CLOCKS_PER_SEC);
    }

    return 0;
    DLTensor* y;
    int out_ndim = 1;
    int64_t out_shape[1] = {1000, };
    TVMArrayAlloc(out_shape, out_ndim, dtype_code, dtype_bits, dtype_lanes, device_type, device_id, &y);

    // get the function from the module(get output data)
    tvm::runtime::PackedFunc get_output = mod.GetFunction("get_output");
    get_output(0, y);

    // get the maximum position in output vector
    auto y_iter = static_cast<float*>(y->data);
    auto max_iter = std::max_element(y_iter, y_iter + 1000);
    auto max_index = std::distance(y_iter, max_iter);
    std::cout << "The maximum position in output vector is: " << max_index << std::endl;

    TVMArrayFree(x);
    TVMArrayFree(y);

    return 0;
}