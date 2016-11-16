"""

ngspicepy
=========
A python wrapper for ngspice.

ngspicepy as a python library for ngspice. It provides python wrappers for
ngspice's C API along with other useful functions. This allows one to run SPICE
simulations and get the data as numpy as arrays directly from python instead of
having to use files to use the data in python. Python has better tools to
process data and plot relavent results. Thus ngspicepy gives a bridge between
ngspice's powerful simulator and python.


The library can be used in two ways.

1. Directly using the functions provided by ngspicepy.
2. Using the Netlist class.

"""
from .netlist import *
from .ngspicepy import clear_plots, current_plot, get_all_data, get_data,\
    get_plot_names, get_vector_names, libngspice, load_netlist, reset, run_ac,\
    run_dc, run_op, run_tran, send_command, set_options


del ngspicepy
del netlist

__all__ = ("send_command", "run_dc", "run_ac", "run_tran", "run_op",
           "get_plot_names", "current_plot", "get_vector_names", "get_data",
           "get_all_data", "set_options", "load_netlist", "Netlist",
           "clear_plots", "reset", "libngspice")
