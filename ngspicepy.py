from ctypes import cdll, CFUNCTYPE, c_int, c_bool, c_char_p, c_void_p,\
        c_double, create_string_buffer, Structure

# Load the ngspice shared library.
# TODO: Figure out the path intelligently
libngspice = cdll.LoadLibrary("/usr/local/lib/libngspice.so.0") 


# C structs that are required by the shared library

class vecinfoall(Structure):
    _fields_ = [("name", c_char_p),
            ("title", c_char_p),
            ("date", c_char_p),
            ("type", c_char_p),
            ("veccount", c_int),
            ("vecs", POINTER(POINTER(vecinfo)))]


class vecvalues(Structure):
    _fields_ = [("name", c_char_p),
            ("creal", c_double),
            ("cimag", c_double),
            ("is_scale", c_bool),
            ("is_complex", c_bool)]

class vecvaluesall(Structure):
    _fields_ = [("veccount", c_int),
            ("vecindex", c_int),
            ("vecsa", POINTER(POINTER(vecvalues))]



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
