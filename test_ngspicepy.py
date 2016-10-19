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

    @mock.patch('ngspicepy.libngspice.ngGet_Vec_Info',
                return_value=ret_val)
    def test_api_call(self, mock_get_info):
        ng.get_data('v-sweep')
        # mock_get_info.assert_called_once_with(create_string_buffer(b'v-sweep'))
        assert mock_get_info.called


class TestCurrentPlot:

    def test_current_plot(self):
        val = ng.current_plot()
        assert isinstance(val, str)

    @mock.patch('ngspicepy.libngspice.ngSpice_CurPlot',
                return_val=b'const')
    def test_api_call(self, mock_CurPlot):
        ng.current_plot()
        mock_CurPlot.assert_called_once_with()


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
