import ngspicepy as ng

import os

import string


class Netlist(object):
    """
    A class that represents SPICE netlists.
    """

    def __init__(self, netlist):
        """
        Class constructor. Accepts any one of the following:

        - A string file (with path) of the netlist file.
        - A string containing the netlist with each line separated by a
          newline.
        - A list of strings, where each item is a line of the netlist.

        """

        if type(netlist) == str:
            if os.path.isfile(netlist):
                with open(netlist) as f:
                    netlist_list = f.readlines()
            elif '\n' in netlist:
                netlist_list = netlist.split('\n')
            else:
                raise ValueError('Invalid netlist file or string')
        elif type(netlist) == list:
            netlist_list = netlist
        else:
            raise TypeError('Netlist format unsupported.\
                    Must be a string or list')

        self.netlist = [item.strip()
                        for item in netlist_list
                        if item.strip() != '']

        self.__checkNetlist__()

    def setup_sim(self, sim_type, *args, **kwargs):
        """Sets up the simulation."""
        self.sim_type = sim_type
        if self.sim_type == 'op':
            self.parsed_args = []
        else:
            self.parsed_args = ng.parse(sim_type, *args, **kwargs)

    def run(self):
        """Runs the simulation"""
        ng.load_netlist(self.netlist)
        ng.send_command(self.sim_type + ' ' + ' '.join(self.parsed_args))

    def get_current_plot(self):
        return ng.current_plot()

    def get_plots(self):
        return ng.get_plot_names()

    def get_vector_names(self, plot_name):
        return ng.get_vector_names(plot_name)

    def get_vector(self, vector_name, plot_name):
        return ng.get_data(vector_name, plot_name)

    def get_vectors(self, plot_name):
        return ng.get_all_data(plot_name)

    def __checkNetlist__(self):
        """Checks if the netlist is valid. """
        # Check if the line has a valid component or is a valid command.
        # Ignore line 1 since its a title line

        valid_components = string.ascii_uppercase

        valid_commands = ['OPTIONS',  # Simulator variables
                          'NODESET',  # Specify initial node voltage guesses
                          'IC',       # Set initial conditions
                          'AC',       # Small signal AC analysis
                          'DC',       # DC transfer function
                          'DISTO',    # Distortion analysis
                          'NOISE',    # Noise analysis
                          'OP',       # Operating point analysis
                          'PZ',       # Pole-zero analysis
                          'SENS',     # DC or small-signal AC sensitivity
                                      # analysis
                          'TF',       # Transfer function analysis
                          'TRAN',     # Transient analysis
                          'PSS',      # Periodic steady state analysis
                          'MEAS',     # Measurements after AC, DC and
                          'MEASURE',  # transient analysis
                          'SAVE',     # Name vectors to be saved in raw file
                          'PRINT',    # Print vectors
                          'PLOT',     # Plot vectors
                          'FOUR',     # Fourier analysis of transient analysis
                                      # output
                          'PROBE',    # Same as SAVE
                          'WIDTH',    # Set print/plot width
                          'TITLE',    # Title of the netlist
                          'END',      # End of netlist
                          'MODEL',    # Component's model
                          'SUBCKT',   # Begingging of sub circuit definition
                          'ENDS',     # End of sub circuit definition
                          'GLOBAL',   # Global nodes
                          'INCLUDE',  # Include a file
                          'LIB',      # Include a library
                          'PARAM',    # Netlist parameters
                          'FUNC',     #
                          'CSPARAM',  #
                          'TEMP',     # Set temperature
                          'IF']       #

        ignore_first_chars = '*+'

        valid_first_chars = valid_components + ignore_first_chars

        inControl = False

        netlist = self.netlist[1:]
        for idx, line in enumerate(netlist, start=2):
            # Detect if we're in a control block
            command = line.split()[0].upper()
            if command == 'CONTROL':
                inControl = True
            elif command == 'ENDC':
                inControl = False

            if not inControl:
                # Check if line is a valid component.
                if line[0] != '.' and line[0].upper() not in valid_first_chars:
                    raise ValueError("Unable to parse line " + str(idx) +
                                     "unknown component '" + line[0] +
                                     "':\n" + line)
                # Check if it is a valid command
                elif line[0] == '.':
                    command  = line[1:].split()[0].upper()  # First word after
                                                            # the dot is the
                                                            # command
                    # Ensure the command is valid
                    if command not in valid_commands:
                        raise ValueError("Unable to parse line " + str(idx) +
                                         "unknown command '" + 
                                         command + "':\n" +
                                         line)

    def __str__(self):
        return '\n'.join(self.netlist)
