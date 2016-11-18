************
Known Issues
************

The following is a list of known issues:

1. If, for some reason, the ngspice simulator is killed (by sending the command
   exit or due to an error in the netlist), the shared library cannot be
   reloaded. This is a problem with the ngspice shared library and cannot be
   addressed till in ngspicepy till it is fixed.
2. The Netlist class, doesn't do a thorough check while parsing the netlist.
   Given that ngspice does crash when there are errors in the netlist, this is
   a problem but will take a significant effort to code. A complete parser
   *may* be added in the future.
