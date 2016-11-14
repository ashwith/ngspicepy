import sys

import os

import pytest

import string

import numpy

module_path = os.path.dirname(os.path.curdir + os.path.sep)
sys.path.insert(0, os.path.abspath(module_path))

from ngspicepy import netlist as nt

netlists_path = 'tests/netlists/'


class TestInit:
    def test__init__(self):
        a = nt.Netlist(netlists_path + 'dc_ac_check.net')
        assert isinstance(a, nt.Netlist)

        with open(netlists_path + 'dc_ac_check.net') as f:
            netlist = f.readlines()
        a = nt.Netlist(netlists_path + 'dc_ac_check.net')
        assert isinstance(a, nt.Netlist)

        with open(netlists_path + 'dc_ac_check.net') as f:
            netlist = f.readlines()
        netlist = '\n'.join(netlist)
        out = nt.Netlist(netlists_path + 'dc_ac_check.net')
        assert isinstance(out, nt.Netlist)
        with pytest.raises(ValueError):
            nt.Netlist(netlists_path + ' ' + 'ac_dc_check.net')

        with pytest.raises(TypeError):
            nt.Netlist(123)


class TestSetupSim:
    def test_setup_sim(self):
        pass


class TestRun:
    def test_run(self):
        pass


class TestGetCurrentPlot:
    def test_get_current_plot(self):
        a = nt.Netlist(netlists_path + 'dc_ac_check.net')
        a.setup_sim('dc', 'v1 0 1 .3')
        a.run()
        val = a.get_current_plot()
        assert val == 'dc1'
        assert isinstance(val, str)


class TestGetPlots:
    def test_get_plots(self):
        a = nt.Netlist(netlists_path + 'dc_ac_check.net')
        a.setup_sim('dc', 'v1 0 1 .3')
        a.run()
        a.setup_sim('dc', 'v1 0 1 .3')
        a.run()
        a.setup_sim('dc', 'v1 0 1 .3')
        a.run()
        val = a.get_plots()
        assert len(val) == 5
        assert val == ['dc4', 'dc3', 'dc2', 'dc1', 'const']
        assert isinstance(val, list)


class TestGetVectorNames:
    def test_get_vector_names(self):
        a = nt.Netlist(netlists_path + 'dc_ac_check.net')
        a.setup_sim('dc', 'v1 0 1 .3')
        a.run()
        val = a.get_vector_names('dc1')
        assert len(val) == 5
        assert isinstance(val, list)
        assert val == ['v1#branch', 'v2#branch', 'V(2)', 'V(1)', 'v-sweep']


class TestGetVector:
    def test_get_vector(self):
        a = nt.Netlist(netlists_path + 'dc_ac_check.net')
        a.setup_sim('dc', 'v1 0 1 .3')
        a.run()
        val = a.get_vector('V(1)', 'dc1')
        assert isinstance(val, numpy.ndarray)
        assert len(val) == 4


class TestGetVectors:
    def test_get_vectors(self):
        a = nt.Netlist(netlists_path + 'dc_ac_check.net')
        a.setup_sim('dc', 'v1 0 1 .3')
        a.run()
        val = a.get_vectors('dc1')
        assert len(val) == 5
        assert isinstance(val, dict)


class TestCheckNetlist:
    def test__checkNetlist__(self):
        pass


class TestStr:
    def test__str__(self):
        pass
