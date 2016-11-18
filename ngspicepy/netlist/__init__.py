"""
The Netlist Class
=================

The Netlist class encapsulates the ngspicepy library into a single data
structure. The netlist class can be used to perform the AC, DC, TRAN and OP
analysis.

There are three steps involved:

    1. Load the netlist file for the circuit.
    2. Set up the simulation type and the simulation parameters.
    3. Run the simulation
    4. Extract the data

Example
-------

    >>> amp = Netlist('CS-Amp.cir')
    >>> amp.setup_sim('tran', tstep='1u', tstop='10m')
    >>> amp.run()
    >>> t = amp.get_vector('time')
    >>> v_in = amp.get_vector('nin')
    >>> v_out = amp.get_vector('nout')
"""
from .netlist import Netlist
