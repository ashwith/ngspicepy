********
Overview
********

ngspicepy as a python library for ngspice. It provides python wrappers for
ngspice's C API along with other useful functions. This allows one to run SPICE
simulations and get the data as numpy as arrays directly from python instead of
having to use files to use the data in python. Python has better tools to
process data and plot relavent results. Thus ngspicepy gives a bridge between
ngspice's powerful simulator and python.


Features
--------

 - A set of functions that provide easy access to the ngspice simulator.
 - A Netlist class that encapsulates a netlist and provides methods to run
   simulations and get the output data.
