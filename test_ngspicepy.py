import ngspicepy as ng

import numpy as np

import pytest

from unittest import mock

from ctypes import c_bool, c_char_p, c_double, c_int, c_short,\
    c_void_p, cast, cdll, CFUNCTYPE, create_string_buffer,\
    POINTER, Structure, cast, pointer

ret_val = ng.vector_info()
ret_val.v_name = cast(create_string_buffer(b"v-sweep"), c_char_p)
ret_val.v_flags = 129
ret_val.v_realdata = np.ctypeslib.as_ctypes(np.linspace(1, 10, 10))
ret_val.v_length = 10
ret_val = pointer(ret_val)


class TestGetPlotNames:
    def test_get_plot_names(self):
        ng.load_netlist('./tests/netlists/dc_ac_check.net')
        ng.run_dc('v1 0 1 0.1')
        ng.run_dc('v1 0 1 0.2')
        ng.run_dc('v1 0 1 0.3')

        val = ng.get_plot_names()
        assert isinstance(val, list)
        assert val == ['dc3', 'dc2', 'dc1', 'const']
        assert len(val) == 4


class TestSendCommand:
    def test_send_command(self):
        val = ng.send_command(' dc v1 0 1 .1 ')
        assert isinstance(val, list)


class TestRunDc:
    def test_run_dc(self):
        val = ng.run_dc('v1 0 1 .1 v2 0 1 .1 ')
        assert isinstance(val, list)


class TestGetData:

    def test_real(self):
        val = ng.get_data('const.e')

        assert type(val) == np.ndarray
        assert len(val) == 1
        assert val.dtype == 'float64'
        assert val[0] == pytest.approx(np.e)

    def test_cmplx(self):
        val = ng.get_data('const.i')
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

    @mock.patch('ngspicepy.libngspice.ngGet_Vec_Info',
                return_value=ret_val)
    def test_api_call(self, mock_get_info):
        ng.get_data('v-sweep')
        # mock_get_info.assert_called_once_with(create_string_buffer(b'v-sweep'))
        assert mock_get_info.called


class TestGetAllData:
    def test_get_all_data(self):
        ng.load_netlist('./tests/netlists/dc_ac_check.net')
        ng.run_dc('v1 0 1 0.1')
        val = ng.get_all_data('dc1')
        for i in val:
            assert type(i) == str


class TestCurrentPlot:

    def test_current_plot(self):
        val = ng.current_plot()
        assert isinstance(val, str)

    @mock.patch('ngspicepy.libngspice.ngSpice_CurPlot',
                return_val=b'const')
    def test_api_call(self, mock_CurPlot):
        ng.current_plot()
        mock_CurPlot.assert_called_once_with()


class TestGetVectorNames:
    def test_get_vector_names(self):
        ng.load_netlist('./tests/netlists/dc_ac_check.net')
        ng.run_dc('v1 0 1 0.1')
        val = ng. get_vector_names('dc1')
        assert val == ['v1#branch', 'V(2)', 'V(1)', 'v-sweep']


class TestLoadNetlist:

    def test_filename(self):
        out = ng.load_netlist('./tests/netlists/dc_ac_check.net')
        assert isinstance(out, list)

    def test_str_lst(self):
        with open('tests/netlists/dc_ac_check.net') as f:
            netlist = f.readlines()
        out = ng.load_netlist(netlist)
        assert isinstance(out, list)

    def test_str(self):
        with open('tests/netlists/dc_ac_check.net') as f:
            netlist = f.readlines()
        netlist = '\n'.join(netlist)
        out = ng.load_netlist(netlist)
        assert isinstance(out, list)

    def test_invalid_filename(self):
        with pytest.raises(ValueError):
            ng.load_netlist('dummy.net')
