import sys

import os

import pytest

import string

import numpy

module_path = os.path.dirname(os.path.curdir + os.path.sep)
sys.path.insert(0, os.path.abspath(module_path))

from ngspicepy import netlist as nt

import ngspicepy as ng

netlists_path = 'tests/netlists/'


class TestInit:
    def test__init__(self):
        net = nt.Netlist(netlists_path + 'dc_ac_check.net')
        assert isinstance(net, nt.Netlist)

        with open(netlists_path + 'dc_ac_check.net') as f:
            net_list = f.readlines()
        net = nt.Netlist(net_list)
        assert isinstance(net, nt.Netlist)

        with open(netlists_path + 'dc_ac_check.net') as f:
            net_list = f.readlines()
        net_list = '\n'.join(net_list)
        net = nt.Netlist(net_list)
        assert isinstance(net, nt.Netlist)

        net = nt.Netlist(netlists_path + 'dc_ac_control.net')
        assert isinstance(net, nt.Netlist)

        with pytest.raises(ValueError):
            nt.Netlist(netlists_path + 'ac_dc_check.net')

        with pytest.raises(TypeError):
            nt.Netlist(123)

        with pytest.raises(ValueError):
            nt.Netlist(netlists_path + 'dc_ac_dot.net')

        with pytest.raises(ValueError):
            nt.Netlist(netlists_path + 'dc_ac_1dot.net')


class TestSetupSim:
    def test_setup_sim(self):
        ng.reset()
        net1 = nt.Netlist(netlists_path + 'dc_ac_check.net')
        net1.setup_sim('op')
        assert net1.sim_type == 'op'
        assert net1.parsed_args == []

        net1.setup_sim('dc', 'v1 0 1 0.1')
        assert net1.sim_type == 'dc'
        assert net1.parsed_args == 'v1 0 1 0.1'.split()
        ng.reset()


class TestRun:
    def test_run(self):
        ng.reset()
        net1 = nt.Netlist(netlists_path + 'dc_ac_check.net')
        net1.setup_sim('op')
        net1.run()
        assert net1.get_plots() == ['op1', 'const']
        ng.reset()


class TestGetCurrentPlot:
    def test_get_current_plot(self):
        net = nt.Netlist(netlists_path + 'dc_ac_check.net')
        net.setup_sim('dc', 'v1 0 1 .3')
        net.run()
        val = net.get_current_plot()
        assert val == 'dc1'
        assert isinstance(val, str)
        ng.reset()


class TestGetPlots:
    def test_get_plots(self):
        ng.reset()
        net = nt.Netlist(netlists_path + 'dc_ac_check.net')
        net.setup_sim('dc', 'v1 0 1 .3')
        net.run()
        net.setup_sim('dc', 'v1 0 1 .3')
        net.run()
        net.setup_sim('dc', 'v1 0 1 .3')
        net.run()
        val = net.get_plots()
        assert len(val) == 4
        assert val == ['dc3', 'dc2', 'dc1', 'const']
        assert isinstance(val, list)
        ng.reset()


class TestGetVectorNames:
    def test_get_vector_names(self):
        ng.reset()
        net = nt.Netlist(netlists_path + 'dc_ac_check.net')
        net.setup_sim('dc', 'v1 0 1 .3')
        net.run()
        val = net.get_vector_names('dc1')
        assert len(val) == 5
        assert isinstance(val, list)
        assert val == ['v1#branch', 'v2#branch', 'V(2)', 'V(1)', 'v-sweep']
        ng.reset()


class TestGetVector:
    def test_get_vector(self):
        net = nt.Netlist(netlists_path + 'dc_ac_check.net')
        net.setup_sim('dc', 'v1 0 1 .3')
        net.run()
        val = net.get_vector('V(1)', 'dc1')
        assert isinstance(val, numpy.ndarray)
        assert len(val) == 4
        ng.reset()


class TestGetVectors:
    def test_get_vectors(self):
        net = nt.Netlist(netlists_path + 'dc_ac_check.net')
        net.setup_sim('dc', 'v1 0 1 .3')
        net.run()
        val = net.get_vectors('dc1')
        assert len(val) == 5
        assert isinstance(val, dict)
        ng.reset()


class TestStr:
    def test__str__(self):
        net = nt.Netlist(netlists_path + 'dc_ac_check.net')
        val = str(net)
        assert isinstance(val, str)
