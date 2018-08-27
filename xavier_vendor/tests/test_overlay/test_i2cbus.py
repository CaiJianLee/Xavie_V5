__author__ = 'Mingcheng'

import mock
import pytest
import ee.overlay.i2cbus as I2CBus
from ee.bus.ci2c import CI2cBus

@mock.patch('ee.overlay.i2cbus.os.path')
@mock.patch('ee.overlay.i2cbus.os.environ')
def test_i2cbus(mock_environ, mock_path):
    with mock.patch.object(CI2cBus, "__init__", return_value=None) as mock_init_ci2cbus:
        mock_environ.get.return_value = '/opt/smartgiant/libsei2c.so'
        mock_path.isfile.return_value = True
        I2CBus.get_bus('/dev/i2c-1')
        mock_init_ci2cbus.assert_called_once_with('/dev/i2c-1')
            