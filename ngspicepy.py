from ctypes import cdll, CFUNCTYPE, c_int, c_bool, c_char_p, c_void_p, c_short,\
        c_double, create_string_buffer, POINTER, Structure

from queue import Queue, Empty
import string

# Constants
TIMEOUT = 0.5

# Load the ngspice shared library.
# TODO: Figure out the path intelligently
libngspice = cdll.LoadLibrary("/usr/local/lib/libngspice.so.0") 

send_char_dat = Queue()
send_stat_dat = Queue()
is_simulating = False

# C structs that are required by the shared library



class ngcomplex_t(Structure):
    _fields_=[("cx_real",c_double),
                ("cx_imag",c_double)]
class vector_info(Structure):
    _fields_ = [("v_name", c_char_p),
            ("v_type", c_int),
            ("v_flags", c_short),
            ("v_realdata",POINTER(c_double)),
            ("v_compdata",POINTER(ngcomplex_t)),
            ("v_length",c_int)]

class vecinfo(Structure):     
  _fields_ = [("number", c_int),
            ("vecname",c_char_p),
            ("is_real", c_bool),
            ("pdvec", c_void_p),
            ("pdvecscale", c_void_p)]
       
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
            ("vecsa", POINTER(POINTER(vecvalues)))]


# Callback functions

@CFUNCTYPE(c_int, c_int, c_bool, c_bool, c_int, c_void_p)
def ControlledExit(exit_status, is_unload, is_quit, lib_id, ret_ptr):
    print(exit_status)
    print(is_unload)
    print(is_quit)
    return 0
    
@CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
def SendChar(output, lib_id, ret_ptr):
    global send_char_dat

    clean_output = "".join(output.decode().split('*'))
    #print(clean_output)
    if 'stdout' in clean_output:
        to_print = ' '.join(clean_output.split(' ')[1:]).strip()
        if "ngspice" in to_print and "done" in to_print:
            send_char_dat.put("Quitting ngspice")
        elif "Note: 'quit' asks for detaching ngspice.dll" in to_print:
            pass
        elif to_print not in string.whitespace:
            send_char_dat.put(to_print)
    elif 'stderr' in clean_output:
        raise SystemError(" ".join(clean_output.split(' ')[1:]))
    return 0

@CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
def SendStat(sim_stat, lib_id, ret_ptr):
    send_stat_dat.put(sim_stat.decode())
    return 0


# Initialize ngspice
libngspice.ngSpice_Init(SendChar, SendStat, ControlledExit, None, None, None)

# User functions
def send_command(command):
    # Clear the status queue for new commands
    while not send_stat_dat.empty():
        send_stat_dat.get_nowait()

    libngspice.ngSpice_Command(create_string_buffer(command.encode()))
    
    output = []
    
    while not send_char_dat.empty():
        output.append(send_char_dat.get_nowait())
    return output

