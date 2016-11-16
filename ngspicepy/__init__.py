from .ngspicepy import send_command, run_dc, run_ac, run_tran, run_op,\
get_plot_names, current_plot, get_vector_names, get_data, get_all_data,\
set_options, load_netlist, clear_plots, reset, libngspice

from .netlist import *

del ngspicepy
del netlist

__all__ = ["send_command", "run_dc", "run_ac", "run_tran", "run_op",
           "get_plot_names", "current_plot", "get_vector_names", "get_data",
           "get_all_data", "set_options", "load_netlist", "Netlist",
           "clear_plots", "reset", "libngspice"]
