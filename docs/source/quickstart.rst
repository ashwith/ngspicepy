**********
Quickstart
**********

.. role:: python(code)
    :language: python

With ngspicepy installed, you can import it using

.. code:: python

    import ngspicepy as ng

The library gives you access to several functions. First, you need to load a
netlist. You can do so by specifying the filename that contains the netlist:

.. code:: python

    ng.load_netlist('circuit.net') 

The extension doesn't matter. Any text file containing a valid SPICE netlist
will work. The function also accepts other ways to import netlist. Consult the
documentation for more information.

Next you may want to run a simulation, say a DC simulation where the voltage of
source V1 is varied from 0V to 10V in steps of 0.1V.

.. code:: python

    ng.run_dc('v1 0 10 0.1')


Currently, there are functions for AC, DC, TRAN and OP analyses. The functions
provided check the input arguments for correctness since ngspice, at times,
crashes when given wrong commands. For other types of analyses, you can
directly run a valid ngspice command using,

.. code:: python

    ng.send_command('dc v1 0 10 0.1')


For the list of available commands, please consult the ngspice manual.

Next you can get the results. A simulation generates several vectors. You can
get a list of these vector names using,

.. code:: python

    vecs = ng.get_vector_names()

where :python:`vecs` contains a list of strings. Suppose you're interested in
the voltage at node '1'. The name of the corresponding vector is 'v(1)'. You
can get it's contents using,

.. code:: python

    vec_data = get_data('v(1)')

If you want to get all of the data,

.. code:: python

    vecs_data = get_all_data()
