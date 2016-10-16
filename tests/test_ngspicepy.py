from importlib.machinery import SourceFileLoader
import pytest
import mock

import numpy as np

ng = SourceFileLoader("ngspicepy", "../ngspicepy.py").load_module()


class TestGetData:

    def test_real():
        val = ng.get_data('e')
        
        assert type(val) == np.ndarray
        assert len(val) == 1
        
        load_netlist('netlists/dc_ac_check.net')
        


    def test_cmplx():
        pass

    def test_2args():
        pass

    def test_1arg_no_plot():
        pass

    def test_1arg_plot():
        pass

    def test_invalid_vector_name():
        pass
