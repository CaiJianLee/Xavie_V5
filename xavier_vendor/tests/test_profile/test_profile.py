__author__ = 'Mingcheng'

import os
import json
import mock
import pytest

from ee.profile.profile import Profile
from ee.profile.parser import ProfileParser
from ee.profile.xobj import XObject
from ee.chip import *
from ee.board import *

@pytest.fixture
def jsonfile():
    return os.getcwd() + '/tests/test_profile/test.json'
    
power_profile={"partno": "Psu-001-001", "id": "power", 
        "digipot":{"partno": "AD5272","bus": "EEPROM_IIC", "switch_channel": "Power_DIGIPOT", "addr": "0x2C"},
        "eeprom": {"partno": "CAT24C08","id": "power", "bus": "EEPROM_IIC", "switch_channel": "Power_EEPROM", "addr": "0x53"}
    }

def test_read_profile(jsonfile):
    classes = globals()
    XObject.set_classes(classes)
    parser = ProfileParser()
    parser.read_profile(jsonfile)

    boards = Profile.get_boards()
    boards[power_profile['id']]=power_profile

    assert len(Profile.get_extendio()) == 1
    assert len(Profile.get_busswitch()) == 9
    assert len(Profile.get_eeprom()) == 8
    assert len(Profile.get_boards()) == 5
    assert len(Profile.get_buses()) == 8
    assert len(Profile.get_chips()) == 12

def test_get_extendio():
    extendioes = Profile.get_extendio()
    extendio = extendioes['instrument']
    extendio_2 = extendio['cp2']
    assert extendio_2['partno'] == 'CAT9555'
    assert extendio_2['bus'] == '/dev/i2c-0'
    assert extendio_2['addr'] == int('0x01',16)
    assert extendio_2['switch_channel'] == 'none'

    bit30 = extendio['bit30']
    assert bit30['pin'] == '14'
    assert bit30['chip'] == 'cp2'

def test_get_extendio_by_name():
    base_board_extendio = Profile.get_extendio_by_name('instrument')
    extendio_8 = base_board_extendio['cp8']
    assert extendio_8['partno'] == 'CAT9555'
    assert extendio_8['bus'] == '/dev/i2c-0'
    assert extendio_8['addr'] == int('0x07',16)
    assert extendio_8['switch_channel'] == 'none'

    bit128 = base_board_extendio['bit128']
    assert bit128['pin'] == '16'
    assert bit128['chip'] == 'cp8'

def test_get_extendio_chip_name():
    bit40_chipname = Profile.get_extendio_chip_name('bit40','instrument')
    assert bit40_chipname == 'cp3'

def test_get_busswitch_by_name():
    #test busswitch
    TB_channel = Profile.get_busswitch_by_name('TB')
    TB_chip = Profile.get_busswitch_by_name(TB_channel['chip'])
    assert TB_chip['partno'] == 'TCA9548'
    assert TB_chip['addr'] == int('0x71',16)
    assert TB_chip['bus'] == '/dev/AXI4_EEPROM_IIC'

    assert Profile.get_busswitch_by_name('TB')['channel'] == 0
    assert Profile.get_busswitch_by_name('DMM_1')['channel'] == 1
    assert Profile.get_busswitch_by_name('CODEC_1')['channel'] == 2
    assert Profile.get_busswitch_by_name('Datalogger_1')['channel'] == 3
    assert Profile.get_busswitch_by_name('BK')['channel'] == 4
    assert Profile.get_busswitch_by_name('Power_EEPROM')['channel'] == 5
    assert Profile.get_busswitch_by_name('DIGIPOT')['channel'] == 6
    assert Profile.get_busswitch_by_name('POWER_DIGIPOT')['channel'] == 7

def test_get_eeprom_by_name():
    #test eeprom
    base_board_eeprom = Profile.get_eeprom_by_name('TB_EEPROM')
    assert base_board_eeprom['bus'] == '/dev/AXI4_EEPROM_IIC'
    assert base_board_eeprom['addr'] == int('0x50',16)
    assert base_board_eeprom['partno'] == 'CAT24C08'
    assert base_board_eeprom['switch_channel'] == 'TB'
    
    datalogger_eeprom = Profile.get_eeprom_by_name('datalogger')
    assert datalogger_eeprom['bus'] == '/dev/AXI4_EEPROM_IIC'
    assert datalogger_eeprom['addr'] == int('0x53',16)
    assert datalogger_eeprom['partno'] == 'CAT24C08'
    assert datalogger_eeprom['switch_channel'] == 'Datalogger-1'

    eload_1_eeprom = Profile.get_eeprom_by_name('ELOAD1')
    assert eload_1_eeprom['bus'] == '/dev/AXI4_ELOAD_IIC'
    assert eload_1_eeprom['addr'] == int('0x53',16)
    assert eload_1_eeprom['partno'] == 'CAT24C08'
    assert eload_1_eeprom['switch_channel'] == "none"

    try:
        Profile.get_eeprom_by_name('SPAM')['bus']
    except KeyError:
        assert True
    else:
        assert False

def test_get_board_by_name():
    #test dmm board
    dmm_board = Profile.get_board_by_name('dmm')
    assert dmm_board['id'] == "dmm"
    assert dmm_board['partno'] == 'Dmm-001-001'
    assert dmm_board['adc']['partno'] == 'AD7175'
    assert dmm_board['adc']['path'] == '/dev/AXI4_DMM_AD7175'

    assert dmm_board['io']['BIT1'] == 'bit35'
    assert dmm_board['io']['BIT2'] == 'bit37'
    assert dmm_board['io']['BIT3'] == 'bit36'
    assert cmp(dmm_board['io']['profile']['bit35'], {"pin": '3', "chip": "cp3"}) == 0
    assert cmp(dmm_board['io']['profile']['bit37'], {"pin": '5', "chip": "cp3"}) == 0
    assert cmp(dmm_board['io']['profile']['bit36'], {"pin": '4', "chip": "cp3"}) == 0
    assert cmp(dmm_board['io']['profile']['cp3'], {"switch_channel":"none", "partno": "CAT9555", "bus": "/dev/i2c-0", "addr": int('0x02',16)}) == 0

    assert dmm_board['eeprom']['partno'] == 'CAT24C08'
    assert dmm_board['eeprom']['bus'] == 'EEPROM_IIC'
    assert dmm_board['eeprom']['switch_channel'] == 'DMM_1'
    assert dmm_board['eeprom']['addr'] == '0x51'

    #test datalogger board
    datalogger_board = Profile.get_board_by_name('datalogger')
    assert datalogger_board["id"] == "datalogger"
    assert datalogger_board['partno'] == 'Scope-002-001A'
    assert datalogger_board['adc']['partno'] == 'AD7177'
    assert datalogger_board['adc']['path'] == '/dev/AXI4_DATALOGGER_AD7177'

    assert datalogger_board['daq_channel'][0]['ch'] == 0
    assert datalogger_board['daq_channel'][0]['id'] == 'current'
    assert datalogger_board['daq_channel'][0]['port'] == 7604

    assert datalogger_board['eeprom']['partno'] == 'CAT24C08'
    assert datalogger_board['eeprom']['bus'] == 'EEPROM_IIC'
    assert datalogger_board['eeprom']['switch_channel'] == 'Datalogger-1'
    assert datalogger_board['eeprom']['addr'] == '0x53'

    #test POWER board
    power_board = Profile.get_board_by_name('power')
    assert power_board['id'] == "power"
    assert power_board['partno'] == 'Psu-001-001'

    assert power_board['digipot']['partno'] == 'AD5272'
    assert power_board['digipot']['bus'] == 'EEPROM_IIC'
    assert power_board['digipot']['switch_channel'] == 'Power_DIGIPOT'
    assert power_board['digipot']['addr'] == '0x2C'

    assert power_board['eeprom']['partno'] == 'CAT24C08'
    assert power_board['eeprom']['bus'] == 'EEPROM_IIC'
    assert power_board['eeprom']['switch_channel'] == 'Power_EEPROM'
    assert power_board['eeprom']['addr'] == '0x53'
    '''
    #test ELOAD1 board
    eload_1_board = Profile.get_board_by_name('ELOAD1')
    assert eload_1_board['id'] == 'ELOAD1'
    assert eload_1_board['partno'] == 'Eld-001-001'

    assert eload_1_board['dac']['partno'] == 'AD5667'
    assert eload_1_board['dac']['addr'] == '0x0F'
    assert eload_1_board['dac']['bus'] == 'ELOAD_IIC'

    assert eload_1_board['io']['DAC_LDAC'] == 'bit81'
    assert eload_1_board['io']['DAC_CLR'] == 'bit82'

    assert eload_1_board['eeprom']['partno'] == 'CAT24C08'
    assert eload_1_board['eeprom']['addr'] == '0x53'
    assert eload_1_board['eeprom']['bus'] == 'ELOAD_IIC'

    #test ELOAD2 board
    eload_2_board = Profile.get_board_by_name('ELOAD2')
    assert eload_2_board['id'] == "ELOAD2"
    assert eload_2_board['partno'] == 'Eld-001-001'

    assert eload_2_board['dac']['partno'] == 'AD5667'
    assert eload_2_board['dac']['addr'] == '0x0F'
    assert eload_2_board['dac']['bus'] == 'ELOAD_IIC'

    assert eload_2_board['io']['DAC_LDAC'] == 'bit81'
    assert eload_2_board['io']['DAC_CLR'] == 'bit82'

    assert eload_2_board['eeprom']['partno'] == 'CAT24C08'
    assert eload_2_board['eeprom']['addr'] == '0x57'
    assert eload_2_board['eeprom']['bus'] == 'ELOAD_IIC'

    #test SPAM board
    spam_board = Profile.get_board_by_name('SPAM')
    assert spam_board['id'] == "SPAM"
    assert spam_board['partno'] == 'Spm-001-001'
    assert spam_board['bus'] == 'AXI4_SPAM_UART'
    try:
        spam_board['category']
    except KeyError:
        assert True
    else:
        assert False
    '''
    #test ERBIUM board
    '''
    erbium_board = Profile.get_board_by_name('ERBIUM')
    assert erbium_board["id"] == "ERBIUM"
    assert erbium_board['partno'] == 'Erb-001-001'

    assert erbium_board['dac_1']['path'] == '/dev/AXI4_ERBIUM_DAC_1'
    assert erbium_board['dac_2']['path'] == '/dev/AXI4_ERBIUM_DAC_2'
    assert erbium_board['adc']['path'] == '/dev/AXI4_ERBIUM_ADC_1'

    assert cmp(erbium_board['dac_1']['function']['sine'], {"id": "AXI4_ERBIUM_SS_1", "ipcore": "Axi4SignalSource"}) ==0
    assert cmp(erbium_board['dac_1']['function']['square'], {"id": "AXI4_ERBIUM_SS_1", "ipcore": "Axi4SignalSource"}) ==0
    assert cmp(erbium_board['dac_1']['function']['arbitrary'], {"id": "AXI4_ERBIUM_SS_1", "ipcore": "Axi4SignalSource"}) ==0

    assert erbium_board['eeprom']['partno'] == 'CAT24C08'
    assert erbium_board['eeprom']['addr'] == '0x50'
    assert erbium_board['eeprom']['bus'] == 'EEPROM_IIC'
    assert erbium_board['eeprom']['switch_channel'] == 'BK'
    '''
    #test Prometheus board
    '''
    prometheus_board = Profile.get_board_by_name('Prometheus')
    assert prometheus_board['id'] == 'Prometheus'
    assert prometheus_board['partno'] == 'Prm-001-001'
    assert prometheus_board['codec_adc']['path'] == '/dev/AXI4_AD7764'

    assert cmp(prometheus_board['codec_adc']['function']['thdn'], {"id": "AXI4_Audio_Analyzer", "ipcore": "Axi4AudioAnalyzer"}) == 0
    assert cmp(prometheus_board['codec_adc']['function']['freq'], {"id": "AXI4_Audio_Analyzer", "ipcore": "Axi4AudioAnalyzer"}) == 0
    assert cmp(prometheus_board['codec_adc']['function']['vpp'], {"id": "AXI4_Audio_Analyzer", "ipcore": "Axi4AudioAnalyzer"}) == 0


    assert prometheus_board['eeprom']['partno'] == 'CAT24C08'
    assert prometheus_board['eeprom']['addr'] == '0x50'
    assert prometheus_board['eeprom']['bus'] == 'EEPROM_IIC'
    assert prometheus_board['eeprom']['switch_channel'] == 'CODEC_1'
    '''
    voltage_output_board = Profile.get_board_by_name('voltage_output')
    assert voltage_output_board['id'] == 'voltage_output'
    assert voltage_output_board['partno'] == 'Vvo-001-001'
    assert cmp(voltage_output_board['dac1'], {"id": "psu_DAC_1",  "channel": ["vo1", "vo2"]}) == 0
    assert cmp(voltage_output_board['dac2'], {"id": "psu_DAC_2", "channel": ["vo3", "vo4"]}) == 0

    freq_board = Profile.get_board_by_name('freq')
    assert freq_board['id'] == 'freq'
    assert freq_board['partno'] == 'Vfreq-001-001'
    assert freq_board['path'] == "/dev/AXI4_Signal_Meter_0"
    assert freq_board['ipcore'] == 'Axi4SignalMeter'
    assert cmp(freq_board['vo'], {"id": "voltage_output", "channel": "vo5"}) == 0

def test_get_bus_by_name():
    ps_i2c_0 = Profile.get_bus_by_name('ps_i2c_0')
    assert ps_i2c_0['bus'] == 'i2c'
    assert ps_i2c_0['path'] == '/dev/i2c-0'
    assert ps_i2c_0['rate'] == '100000'

    UUT_UART = Profile.get_bus_by_name('UUT_UART')
    assert UUT_UART['bus'] == 'uart'
    assert UUT_UART['path'] == '/dev/AXI4_UUT_UART'
    assert UUT_UART['baudrate'] == '115200'
    assert UUT_UART['ipcore'] == 'Axi4Uart'

    INSTRUMENT_IIC_2 = Profile.get_bus_by_name('INSTRUMENT_IIC_2')
    assert INSTRUMENT_IIC_2['bus'] == 'i2c'
    assert INSTRUMENT_IIC_2['path'] == '/dev/AXI4_INSTRUMENT_IIC_2'
    assert INSTRUMENT_IIC_2['rate'] == '400000'
    assert INSTRUMENT_IIC_2['ipcore'] == 'Axi4I2c'

    EEPROM_IIC = Profile.get_bus_by_name('EEPROM_IIC')
    assert EEPROM_IIC['bus'] == 'i2c'
    assert EEPROM_IIC['path'] == '/dev/AXI4_EEPROM_IIC'
    assert EEPROM_IIC['rate'] == '400000'
    assert EEPROM_IIC['ipcore'] == 'Axi4I2c'