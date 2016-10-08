from ctypes import cdll, CFUNCTYPE, c_int, c_bool, c_char_p, c_void_p, create_string_buffer

# Load the ngspice shared library.
# TODO: Figure out the path intelligently
libngspice = cdll.LoadLibrary("/usr/local/lib/libngspice.so.0") 


# C structs that are required by the shared library



# Callback functions

@CFUNCTYPE(c_int, c_int, c_bool, c_bool, c_int, c_void_p)
def ControlledExit(exit_status, is_unload, is_quit, lib_id, ret_ptr):
    print(exit_status)
    print(is_unload)
    print(is_quit)
    print(lib_id)
    pass
    
@CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
def SendChar(output, lib_id, ret_ptr):
    print(output)
    print(lib_id)
    return 0

@CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
def SendStat(sim_stat, lib_id, ret_ptr):
    print(sim_stat)
    print(lib_id)
    return 0


# Initialize ngspice


# User functions
