"""The API wrapper for ngspice's shared library."""
import os
import string
from collections import OrderedDict
from ctypes import c_bool, c_char_p, c_double, c_int, c_short,\
    c_void_p, cast, cdll, CFUNCTYPE, create_string_buffer,\
    POINTER, Structure
from queue import Queue

import numpy as np

# Load the ngspice shared library.
# TODO: Figure out the path intelligently
libpath = "/usr/local/lib/libngspice.so.0"
if os.path.isfile(libpath):
    libngspice = cdll.LoadLibrary(libpath)
else:  # pragma: no cover
    raise SystemError('Shared library libngspice.so not found in ' + libpath)

send_char_queue = Queue()
send_stat_queue = Queue()
is_simulating = False


# enums for v_type.
# See src/include/ngspice/sim.h in the ngspice source.
class v_types:
    """Definition for the values for v_types."""

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


# enums for v_flags.
# See src/include/ngspice/dvec.h in the ngspice source.
class v_flags:
    """Bit fields for v_flags."""

    VF_REAL = (1 << 0)
    VF_COMPLEX = (1 << 1)
    VF_ACCUM = (1 << 2)
    VF_PLOT = (1 << 3)
    VF_PRINT = (1 << 4)
    VF_MINGIVEN = (1 << 5)
    VF_MAXGIVEN = (1 << 6)
    VF_PERMANENT = (1 << 7)

# ngspice scale factors
scale_factors = OrderedDict()
scale_factors['meg'] = 'e6'
scale_factors['t'] = 'e12'
scale_factors['g'] = 'e9'
scale_factors['k'] = 'e3'
scale_factors['m'] = 'e-3'
scale_factors['u'] = 'e-6'
scale_factors['n'] = 'e-9'
scale_factors['p'] = 'e-12'
scale_factors['f'] = 'e-15'


# C structs that are required by the shared library
class ngcomplex_t(Structure):
    """ctypes definition for struct ngcomplex_t."""

    _fields_ = [("cx_real", c_double),
                ("cx_imag", c_double)]


class vector_info(Structure):
    """ctypes definition for struct vector_info."""

    _fields_ = [("v_name", c_char_p),
                ("v_type", c_int),
                ("v_flags", c_short),
                ("v_realdata", POINTER(c_double)),
                ("v_compdata", POINTER(ngcomplex_t)),
                ("v_length", c_int)]


class vecinfo(Structure):
    """ctypes definition for struct vecinfo."""

    _fields_ = [("number", c_int),
                ("vecname", c_char_p),
                ("is_real", c_bool),
                ("pdvec", c_void_p),
                ("pdvecscale", c_void_p)]


class vecinfoall(Structure):
    """ctypes definition for struct vecinfoall."""

    _fields_ = [("name", c_char_p),
                ("title", c_char_p),
                ("date", c_char_p),
                ("type", c_char_p),
                ("veccount", c_int),
                ("vecs", POINTER(POINTER(vecinfo)))]


class vecvalues(Structure):
    """ctypes definition for struct vecvalues."""

    _fields_ = [("name", c_char_p),
                ("creal", c_double),
                ("cimag", c_double),
                ("is_scale", c_bool),
                ("is_complex", c_bool)]


class vecvaluesall(Structure):
    """ctypes definition for struct vecvaluesall."""

    _fields_ = [("veccount", c_int),
                ("vecindex", c_int),
                ("vecsa", POINTER(POINTER(vecvalues)))]


# Callback functions
@CFUNCTYPE(c_int, c_int, c_bool, c_bool, c_int, c_void_p)
def ControlledExit(exit_status, is_unload, is_quit,
                   lib_id, ret_ptr):  # pragma: no cover
    """Callback function called when one exits from ngspice."""
    if not exit_status == 0 or not is_quit:
        raise SystemError('Invalid command or netlist.')
    return 0


@CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
def SendChar(output, lib_id, ret_ptr):
    """Callback function that captures what's sent by ngspice to stdout."""
    global send_char_queue

    clean_output = "".join(output.decode().split('*'))
    if 'stdout' in clean_output:
        to_print = ' '.join(clean_output.split(' ')[1:]).strip()
        if "ngspice" in to_print and "done" in to_print:  # pragma: no cover
            send_char_queue.put("Quitting ngspice")
        elif "Note: 'quit' asks for detaching ngspice.dll"\
                in to_print:  # pragma: no cover
            pass
        elif to_print not in string.whitespace:
            send_char_queue.put(to_print)
    elif 'stderr' in clean_output:  # pragma: no cover
        raise SystemError(" ".join(clean_output.split(' ')[1:]))
    return 0


@CFUNCTYPE(c_int, c_char_p, c_int, c_void_p)
def SendStat(sim_stat, lib_id, ret_ptr):
    """Callback function that captures status messages."""
    send_stat_queue.put(sim_stat.decode())
    return 0


# Initialize ngspice
libngspice.ngSpice_Init(SendChar, SendStat, ControlledExit, None,
                        None, None)

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


# Utility functions
def xstr(string):
    """Like str(), except that None is converted to ''."""
    if string is None:
        return ''
    else:
        return str(string)


def to_num(ng_number):
    """Convert an ngspice number to a float.
    
    ng_number - a string containing a number that ngspice recognizes. This can
    either be a float or a number with the appropriate scale factor.
    
    Examples:

    to_num('1.3')
    to_num('1Meg')
    """
    num_text = ng_number.lower()
    for scale_factor in scale_factors:
        if scale_factor in num_text:
            num_text = num_text.replace(scale_factor,
                                        scale_factors[scale_factor])
            break
    try:
        num = float(num_text)
        return num
    except ValueError:
        raise ValueError('Invalid ngspice number: ' + ng_number)


def check_sim_param(start, stop, step=None):
    """Check if start < stop if step is positive and start > stop otherwise."""
    if step is None:
        step = 1
    if step == 0:
        return (False, "step size is zero")
    if step > 0 and stop < start:
        return (False, "step size > 0 but stop < start ")
    if step < 0 and stop > start:
        return (False, "step size < 0 but stop > start")
    return (True, "All good")


def __parse__(sim_cmd, *args, **kwargs):
    """Parse the arguments and check for correctness depending on the simulation chosen."""
    cmd_dc = OrderedDict()
    cmd_dc['src'] = ""
    cmd_dc['start'] = ""
    cmd_dc['stop'] = ""
    cmd_dc['step'] = ""
    cmd_dc['src2'] = ""
    cmd_dc['start2'] = ""
    cmd_dc['stop2'] = ""
    cmd_dc['step2'] = ""

    is_parametric = False

    pdc_keys = ['start', 'stop', 'step']
    cmd_ac = OrderedDict()
    cmd_ac['variation'] = ""
    cmd_ac['npoints'] = ""
    cmd_ac['fstart'] = ""
    cmd_ac['fstop'] = ""
    pac_keys = ['fstart', 'fstop', 'npoints']
    cmd_tran = OrderedDict()
    cmd_tran['tstep'] = ""
    cmd_tran['tstop'] = ""
    cmd_tran['tstart'] = "0"
    cmd_tran['tmax'] = ""
    ptran_keys = ['tstart', 'tstop', 'tstep']

    if sim_cmd == 'ac':
        cmd = cmd_ac
        p_keys = pac_keys
        required_args = set(['variation', 'npoints', 'fstart', 'fstop'])
    elif sim_cmd == 'dc':
        cmd = cmd_dc
        p_keys = pdc_keys
        required_args = set(['src', 'start', 'stop', 'step'])
    elif sim_cmd == 'tran':
        cmd = cmd_tran
        p_keys = ptran_keys
        required_args = set(['tstep', 'tstop'])

    # Parse arguments:
    #
    # Case 1:
    # -------
    # If just one arg is given, assume that the entire string is a
    # command. Separate it out and assign it to the cmd dictionary
    # for error checking.
    if len(args) == 1:
        clean_arg = ' '.join(args[0].split())
        for key, arg in zip(cmd.keys(), clean_arg.split(' ')):
            cmd[key] = xstr(arg)
    else:
        # Case 2:
        # -------
        # If the simulation args are given as comma separated values,
        # assign them to the dictionary for error checking.
        for key, value in zip(cmd.keys(), args):
            cmd[key] = xstr(value)

    # Case 3:
    # -------
    # Finally parse the keyword args. Overwrite any args that
    # were already given.
        for key in kwargs:
            if key not in cmd:
                raise KeyError('invalid keyword argument')
            else:
                cmd[key] = xstr(kwargs[key])

    # Check if the arguments were entered correctly:
    #
    # 1. Checks for first source
    # --------------------------
    # Check if any of the required arguments are empty.
    empty_args = set([key for key in cmd if cmd[key] == ""])
    keys = list(cmd.keys())
    if any(arg in empty_args for arg in required_args):
        missing_args =\
            empty_args.intersection(required_args)
        raise ValueError('Arguments missing: ' +
                         ' '.join(missing_args))

    # 2. Checks for the second source
    # -------------------------------
    #
    # 2a. Arguments of second source given, check if source is given.
    if sim_cmd == 'dc':
        required_args = set([keys[5], keys[6], keys[7]])
        if any(arg not in empty_args for arg in required_args) and\
                cmd['src2'] == "":
            raise ValueError('Second source not specified.')

    # 2b. Second source is specified, check if its required arguments
    # are empty.
        if cmd['src2'] != "":
            required_args = set([keys[5], keys[6], keys[7]])
            if any(arg in empty_args for arg in required_args):
                missing_args = empty_args.intersection(required_args)
                raise ValueError('Arguments missing: ' +
                                 ' '.join(missing_args))
            else:
                is_parametric = True

    # Check if the arguments are correct, i.e., is start < stop if
    # step is positive, is start > stop if step is negative, is
    # start != step?
    start = to_num(cmd[p_keys[0]])
    stop = to_num(cmd[p_keys[1]])
    step = to_num(cmd[p_keys[2]])
    is_good, msg = check_sim_param(start, stop, step)
    if not is_good:
        raise ValueError('Wrong values')
    # Do the same for the second source if it exists.

    if sim_cmd == 'dc':
        if is_parametric:
            start = to_num(cmd['start2'])
            stop = to_num(cmd['stop2'])
            step = to_num(cmd['step2'])
            is_good, msg = check_sim_param(start, stop, step)
            if not is_good:
                raise ValueError('Wrong Values')

    return [cmd[key] for key in cmd if cmd[key] != '']


# User functions
def send_command(command):
    """Send a command to ngspice.

    The argument `command` is string that contains a valid ngspice
    command. See the chapter 'Interactive Interpreter' of the ngspice
    manual: http://ngspice.sourceforge.net/docs/ngspice26-manual.pdf
    """
    while not send_stat_queue.empty():
        send_stat_queue.get_nowait()

    libngspice.ngSpice_Command(create_string_buffer(command.encode()))

    output = []

    while not send_char_queue.empty():
        output.append(send_char_queue.get_nowait())
    return output


def run_dc(*args, **kwargs):
    """Run a DC simulation on ngspice.

    The argument(s) are either:

    1. A single string containing the source(s) followed by their
       start, stop and step values.
    2. src, start, stop, step[, src2, start, stop, step]
    3. The arguments in 2. Specified as keyword arguments.

    src and src2 must be strings. start, stop and step can be either
    strings or floats. If they are strings, they must contain only a
    float and optionally one of ngspice's scale factors and no spaces.

    Examples:

        >>> run_dc('v1 0 1 0.1')
        >>> run_dc('v2 0 1 1m v2 0 1 0.3')
        >>> run_dc('v1', 0, '1meg', '1k')
        >>> run_dc(src='v1', start=0, stop=1, step=0.1\\
                   src2='v2', start2=0, step2=0.3, stop2=1)
    """
    parsed_args = __parse__('dc', *args, **kwargs)
    return send_command('dc ' + ' '.join(parsed_args))


def run_ac(*args, **kwargs):
    """Run an AC simulation on ngspice.
    
    An AC simulation requires one to specify the start (`fstart`) and stop
    (`fstop`) frequecies, the type of `variation` (dec/oct/lin) and the number of
    points (`npoints`; per decade or octave if dec or oct are used)

    The argument(s) are either:

    1. A single string of the form '<variation> <npoints> <fstart> <fstop>'
    2. variation, npoints, fstart, fstop
    3. The arguments in 2. Specified as keyword arguments.

    Examples:

        >>> run_ac('dec 10 1 10')
        >>> run_ac('dec 10 1k 10meg')
        >>> run_ac('dec', 10, '1k', '100k')
        >>> run_ac(variation='dec', npoints=0, fstart=1, fstop=10)
    """
    parsed_args = __parse__('ac', *args, **kwargs)
    return send_command('ac ' + ' '.join(parsed_args))


def run_tran(*args, **kwargs):
    """Run a TRAN simulation on ngspice.

    The argument(s) are either:

    1. A single string containing tstep, tstop, tstart, tmax and uic
       values. The values of tmax and uic are optional.
    2. tstep, tstop[, tstart, tmax, uic]
    3. The arguments in 2. Specified as keyword arguments.

    start, stop and step can be either strings or floats. If the are
    strings, they must contain only a float and optionally one of
    ngspice's scale factors and no spaces.

    Examples:

        >>> run_tran('1 10 0 11 ')
        >>> run_tran('1ns 10ns 0 11ns')
        >>> run_tran('1ns', 0, '10ns', '11ns')
        >>> run_tran(tstep=1, tstop=10, tstart=0, tmax=11)
    """
    parsed_args = __parse__('tran', *args, **kwargs)
    return send_command('tran ' + ' '.join(parsed_args))


def run_op():
    """Run operating point analysis."""
    op_result = send_command('op')
    return op_result


def clear_plots(*args):
    """Clear the specified plots names.

    The argument(s) are either:
    
    1. Empty, which will clear all plots.
    2. Multiple arguments, each containing the name of a plot (a string).
    3. A string containing comma separated names of the plots that need to be
       deleted.
    4. A list or tuple of strings contianing the plots that need to be deleted.

    Examples:

        >>> clear_plots()
        >>> clear_plots('dc dc2 dc3')
        >>> clear_plots(('dc1','dc2','dc3'))
        >>> clear_plots('dc1','dc2','dc3')
        >>> clear_plots(['dc1','dc2','dc3'])
    """
    if len(args) == 0:
        clear_cmd = 'all'
    elif len(args) == 1:
        if type(args[0]) == str:
            clear_cmd = args[0]
        elif type(args[0]) == list or type(args[0]) == tuple:
            clear_cmd = ' '.join(args[0])
        else:
            raise TypeError('Type must be string,list or tuple')
    else:
        clear_cmd = ' '.join(args)
    return send_command('destroy ' + clear_cmd)


def reset():
    """Same as calling clear_plots(). Resets the ngspice environment."""
    clear_plots()


def get_plot_names():
    """Return a list of plot names.

    A plot is the name for a group of vectors. Example: A DC
    simulation run right after ngspice is loaded creates a plot called
    dc1 which contains the vectors generated by the DC simulation.
    """
    plot_name_array = libngspice.ngSpice_AllPlots()
    names_list = []
    name = plot_name_array[0]
    i = 1
    while name is not None:
        names_list.append(name.decode())
        name = plot_name_array[i]
        i += 1

    return names_list


def current_plot():
    """Return the name of the current plot."""
    plot_name = libngspice.ngSpice_CurPlot()
    return (plot_name.decode())


def get_vector_names(plot_name=None):
    """Return a list of the names of the vectors in the given plot.

    `plot_name` specifies the plot whose vectors need to be returned. If
    it unspecified, the vector names from the current plot are
    returned.
    """
    if plot_name is None:
        plot_name = current_plot()

    if plot_name not in get_plot_names():
        raise ValueError("Given plot name doesn't exist")
    else:
        vector_names = libngspice.ngSpice_AllVecs(
            create_string_buffer(plot_name.encode()))
    names_list = []
    name = vector_names[0]
    i = 1
    while name is not None:
        names_list.append(name.decode())
        name = vector_names[i]
        i = i + 1

    return names_list


def get_data(vector_arg, plot_arg=None):
    """Get the data in a vector as a numpy array.

    `vector_arg` denotes the vector name
    plot_agr denotes the plot name
    """
    if '.' in vector_arg:
        plot_name, vector_name = vector_arg.split('.')
        if vector_name not in get_vector_names(plot_name):
            raise ValueError("Incorrect vector name")
    else:
        if vector_arg not in get_vector_names(plot_arg):
            raise ValueError("Incorrect vector name")
        if plot_arg is not None:
            vector_arg = ".".join([plot_arg, vector_arg])

    info = libngspice.ngGet_Vec_Info(
        create_string_buffer(vector_arg.encode()))
    if info.contents.v_flags & v_flags.VF_REAL != 0:
        data = np.ctypeslib.as_array(info.contents.v_realdata,
                                     shape=(info.contents.v_length,))
    elif info.contents.v_flags & v_flags.VF_COMPLEX != 0:
        data = np.ctypeslib.as_array(
            info.contents.v_compdata,
            shape=(info.contents.v_length,)).view('complex128')
    return data


def get_all_data(plot_name=None):
    """Return a dictionary of all vectors in the specified plot."""
    vector_names = get_vector_names(plot_name)

    vector_data = {}
    for vector_name in vector_names:
        vector_data[vector_name] = get_data(vector_name)

    return vector_data


def set_options(*args, **kwargs):
    """Pass simulator options to ngspice.

    Options may either be entered as a string or keyword arguments.
    
    Examples:

        >>> set_options(trtol=1, temp=300)
        >>> set_options('trtol=1')
    """
    for option in args:
        return send_command('option ' + str(option))
    for option in kwargs:
        return send_command('option ' + option + '=' +
                            str(kwargs[option]))


def load_netlist(netlist):
    """Load ngspice with the specified netlist.

    The argument netlist can be one of the following:

    1. The path to a file that contains the netlist.
    2. A list of strings where each string is one line of the netlist.
    3. A string containing the entire netlist with each line separated
       by a newline character.

    The function does not check if the netlist is valid. An invalid
    netlist may cause ngspice to crash.
    """
    if type(netlist) == str:
        if os.path.isfile(netlist):
            return send_command('source ' + netlist)
        elif '\n' in netlist:
            netlist_list = netlist.split('\n')
        else:
            raise ValueError('Invalid netlist file or string')
    elif type(netlist) == list:
        netlist_list = netlist
    else:
        raise TypeError('Netlist format unsupported.\
                Must be a string or list')

    c_char_p_array = c_char_p * (len(netlist_list) + 1)
    netlist_str = c_char_p_array()

    for i, line in enumerate(netlist_list):
        netlist_str[i] = cast(create_string_buffer(line.encode()), c_char_p)
    netlist_str[len(netlist_list)] = None

    libngspice.ngSpice_Circ(netlist_str)

    output = []

    while not send_char_queue.empty():
        output.append(send_char_queue.get_nowait())
    return output
