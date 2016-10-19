import ngspicepy as ng

import numpy as np

import pytest


class TestGetData:

    def test_real(self):
        val = ng.get_data('e')

        assert type(val) == np.ndarray
        assert len(val) == 1
        assert val.dtype == 'float64'
        assert val[0] == pytest.approx(np.e)

    def test_cmplx(self):
        val = ng.get_data('i')
        assert type(val) == np.ndarray
        assert len(val) == 1
        assert val.dtype == 'complex128'
        assert val[0] == pytest.approx(1j)

    def test_2args(self):
        ng.load_netlist('./tests/netlists/dc_ac_check.net')
        ng.run_dc('v1 0 1 0.1')
        ng.run_dc('v1 0 1 0.2')

        val = ng.get_data('v-sweep', 'dc1')
        assert val.dtype == 'float64'
        assert len(val) == 11

    def test_1arg_no_plot(self):
        ng.load_netlist('./tests/netlists/dc_ac_check.net')
        ng.run_dc('v1 0 1 0.1')
        ng.run_dc('v1 0 1 0.2')

        val = ng.get_data('v-sweep')
        assert val.dtype == 'float64'
        assert len(val) == 6

    def test_1arg_plot(self):
        ng.load_netlist('./tests/netlists/dc_ac_check.net')
        ng.run_dc('v1 0 1 0.1')
        ng.run_dc('v1 0 1 0.2')

        val = ng.get_data('dc1.v-sweep')
        assert val.dtype == 'float64'
        assert len(val) == 11

    def test_invalid_vector_name(self):
        ng.load_netlist('./tests/netlists/dc_ac_check.net')
        ng.run_dc('v1 0 1 0.1')
        ng.run_dc('v1 0 1 0.2')

        with pytest.raises(ValueError):
            ng.get_data('dc1.v-swoop')


class TestCurrentPlot:

    def test_current_plot(self):
        val = ng.current_plot()
        assert isinstance(val, str)


class TestLoadNetlist:

    def test_filename(self):
        ng.load_netlist('./tests/netlists/dc_ac_check.net')

    def test_str_lst(self):
        pass

    def test_str(self):
        pass
