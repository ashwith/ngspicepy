ngspicepy
=========
[![Build Status](https://travis-ci.org/ashwith/ngspicepy.svg?branch=master)](https://travis-ci.org/ashwith/ngspicepy)[![Coverage Status](https://coveralls.io/repos/github/ashwith/ngspicepy/badge.svg?branch=master)](https://coveralls.io/github/ashwith/ngspicepy?branch=master)

ngspicepy is a python library for ngspice. ngspice is general purpose free and open source circuit simulator. While the simulator is quite powerful, processing data after the simulation isn't straightforward. The plot windows aren't very impressive either. This library's main aim is to provide a set of functions that allow one to run simulations on ngspice and get the data in numpy arrays.

Software Requirements
----------------------

1. A GNU/Linux based OS.
2. python 3.5
3. ngspice - Both the binary and the shared library. Instructions for installing the latter are given below.
4. numpy

Compiling the Shared Library
----------------------------
In order to use ngspicepy, you will need the ngspice library. Download the source code for ngspice from [http://ngspice.sourceforge.net/](http://ngspice.sourceforge.net/). Now run:

```bash
tar xvzf ngspice-26.tar.gz
cd ngspice-26
mkdir release
cd release
../configure --with-ngshared 
make
sudo make install
```

If all goes well, the shared library should be in /usr/local/lib/. If not, please check the installation instructions that come with ngspice (see file INSTALL).

Using ngspicepy
---------------
Here is a simple usage example.
```python
>>>> from ngspicepy import *
>>>> from matplotlib import pyplot as plt
>>>> load_netlist('tests/netlists/dc_ac_check.net')
>>>> run_dc('v1 0 1 .3')
>>>> get_vector_names('dc1')
['v1#branch', 'V(2)', 'V(1)', 'v-sweep']
>>>> data = get_all_data()
>>>> data
{'V(1)': array([ 0. ,  0.3,  0.6,  0.9]),
 'V(2)': array([ 0.  ,  0.15,  0.3 ,  0.45]),
 'v-sweep': array([ 0. ,  0.3,  0.6,  0.9]),
 'v1#branch': array([ 0.  , -0.15, -0.3 , -0.45])}
>>>> plt.plot(data['v-sweep'], data['V(1)'])
>>>> plt.plot(data['v-sweep'], data['V(2)'])
>>>> plt.show()
```

The library provides the following functions:

1. load_netlist - Allows one to load the SPICE netlist either from a file, as a string containing the netlist or as a list of strings (one line per string).
2. send_command - Send a command to the simulator.
3. run_op, run_dc, run_tran, run_ac - Run OP, DC, AC and TRAN simulations respectively.
4. current_plot - Get the name of the current plot (a plot is a set of vectors which contain the output of a simulation).
5. get_plot_names - Get the names of all the plots.
6. get_data - Get the vector specified as a numpy array.
7. get_all_data - Get all the vectors (in the current plot unless specified).
8. get_vector_names - Get a list of vector names.
9. set_options - Set simulator options.

See the documentation for each function for more help.
