import string
from ctypes import c_bool, c_char_p, c_double, c_int, c_short,\
        c_void_p, cdll, CFUNCTYPE, create_string_buffer,\
        POINTER, Structure
from queue import Queue

# Load the ngspice shared library.
# TODO: Figure out the path intelligently
libngspice = cdll.LoadLibrary("/usr/local/lib/libngspice.so.0")

send_char_queue = Queue()
send_stat_queue = Queue()
is_simulating = False


# enums for v_type
SV_NOTYPE         = 0
SV_TIME           = 1
SV_FREQUENCY      = 2
SV_VOLTAGE        = 3
SV_CURRENT        = 4
SV_OUTPUT_N_DENS  = 5
SV_OUTPUT_NOISE   = 6
SV_INPUT_N_DENS   = 7
SV_INPUT_NOISE    = 8
SV_POLE           = 9
SV_ZERO           = 10
SV_SPARAM         = 11
SV_TEMP           = 12
SV_RES            = 13
SV_IMPEDANCE      = 14
SV_ADMITTANCE     = 15
SV_POWER          = 16
SV_PHASE          = 17
SV_DB             = 18
SV_CAPACITANCE    = 19
SV_CHARGE         = 20


# C structs that are required by the shared library
class ngcomplex_t(Structure):
    _fields_ = [("cx_real", c_double),
                ("cx_imag", c_double)]


class vector_info(Structure):
    _fields_ = [("v_name", c_char_p),
                ("v_type", c_int),
                ("v_flags", c_short),
                ("v_realdata", POINTER(c_double)),
                ("v_compdata", POINTER(ngcomplex_t)),
                ("v_length", c_int)]


class vecinfo(Structure):
    _fields_ = [("number", c_int),
                ("vecname", c_char_p),
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
    global send_char_queue

    clean_output = "".join(output.decode().split('*'))
    if 'stdout' in clean_output:
        to_print = ' '.join(clean_output.split(' ')[1:]).strip()
        if "ngspice" in to_print and "done" in to_print:
            send_char_queue.put("Quitting ngspice")
        elif "Note: 'quit' asks for detaching ngspice.dll" in to_print:
            pass
        elif to_print not in string.whitespace:
            send_char_queue.put(to_print)
    elif 'stderr' in clean_output:
        raise SystemError(" ".join(clean_output.split(' ')[1:]))
    return 0


@CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
def SendStat(sim_stat, lib_id, ret_ptr):
    send_stat_queue.put(sim_stat.decode())
    return 0


# Initialize ngspice
libngspice.ngSpice_Init(SendChar, SendStat, ControlledExit, None, None, None)

# Specify API argument types and return types
libngspice.ngSpice_Command.argtypes = [c_char_p]
libngspice.ngGet_Vec_Info.argtypes  = [c_char_p]
libngspice.ngSpice_Circ.argtypes    = [POINTER(c_char_p)]
libngspice.ngSpice_AllVecs.argtypes = [c_char_p]

libngspice.ngSpice_Command.restype  = c_int
libngspice.ngSpice_running.restype  = c_int
libngspice.ngGet_Vec_Info.restype   = POINTER(vector_info)
libngspice.ngSpice_Circ.restype     = c_int
libngspice.ngSpice_CurPlot.restype  = c_char_p
libngspice.ngSpice_AllPlots.restype = POINTER(c_char_p)
libngspice.ngSpice_AllVecs.restype  = POINTER(c_char_p)


# User functions
def send_command(command):
    # Clear the status queue for new commands
    while not send_stat_queue.empty():
        send_stat_queue.get_nowait()

    libngspice.ngSpice_Command(create_string_buffer(command.encode()))

    output = []

    while not send_char_queue.empty():
        output.append(send_char_queue.get_nowait())
    return output
    
#Function to return current plot
def current_plot():
    plot_name=libngspice.ngSpice_CurPlot()
    return (plot_name.decode())
