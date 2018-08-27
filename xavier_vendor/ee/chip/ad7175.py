"""24bits AD7175 ADC Chip driver

"""
from __future__ import division
import time
from ee.ipcore.axi4_ad717x import Axi4Ad717x
from ee.common import logger

__version__="1.0"

class AD7175(object):
    def __init__(self,name,vref):
        self.device = Axi4Ad717x(name)
        self.device_path = name
        self.vref = vref


    def reset(self):
        """ Reset FPGA ad717x function and AD7175 chip

            Returns:
                bool: True | False, True for success, False for failed.
        """
        self.device.disable()
        self.device.enable()
        self.device.reset()
        #make sure ADC chip reset ok
        time.sleep(0.1)

        return True

    def single_sample_mode(self):
        """ Make ADC chip exit continue sample mode and into single mode
            It can be used, when  ADC work in single mode

            Returns:
                bool: True | False, True for success, False for failed.
        """
        return self.device.single_sample_mode()
        

    def register_read(self,reg_addr):
        """ Read value from ADC chip register
            It can be used, when  ADC work in single mode

            Args:
                reg_addr: ADC chip register address(0x00-0xff)

            Returns:
                register value: (0x00-0xffffffff)
        """
        return self.device.register_read(reg_addr);
    
    def register_write(self,reg_addr,reg_data):
        """ Write value to ADC chip register
            It can be used, when  ADC work in single mode

            Args:
                reg_addr: ADC chip reg (0x00-0xff)
                reg_data: register value(0x00-0xffffffff)

            Returns:
                bool: True | False, True for success, False for failed.
        """
        return self.device.register_write(reg_addr,reg_data)

    def voltage_channel_enable(self,channel,config):
        """ enable the select channel
            You can use this function open more channel


            Args:
                channel: ["chan0","chan1","chan2","chan3"]
                config: channel configuration
                  {"P":AIN,"N":AIN}
                    AIN:["AIN0","AIN1","AIN2","AIN3","AIN4","Temp+","Temp-","AVDD1","AVSS","REF+","REF-"]
            Returns:
                bool: True | False, True for success, False for failed.

            Raise:
                KeyError,TypeError
        """
        channels={"chan0":0x10,"chan1":0x11,"chan2":0x12,"chan3":0x13}
        setups={"chan0":0x00,"chan1":0x01,"chan2":0x02,"chan3":0x03}
        ains={"AIN0":0x0,"AIN1":0x01,"AIN2":0x02,"AIN3":0x03,"AIN4":0x04,
                        "Temp+":0x11,"Temp-":0x12,"AVDD1":0x13,"AVSS":0x14,"REF+":0x15,"REF-":0x16}

        channel_reg = channels[channel]

        reg_value = 0x8000;
        temp = setups[channel]<<12
        reg_value |= temp

        temp = ains[config["P"]] << 5
        reg_value |= temp

        temp = ains[config["N"]]
        reg_value |= temp

        return self.register_write(channel_reg,reg_value)
        
    def voltage_channel_disable(self,channel):
        """ disable the select channel

            Args:
                channel: ["chan0","chan1","chan2","chan3","all"]
            Returns:
                bool: True | False, True for success, False for failed.

            Raise:
                KeyError,TypeError
        """
        channels={"chan0":0x10,"chan1":0x11,"chan2":0x12,"chan3":0x13}

        if channel == "all":
            for channel in channels:
                channel_reg = channels[channel]
                reg_value = 0x0001
                if self.register_write(channel_reg,reg_value) is False:
                    return False
        else:
            channel_reg = channels[channel]
            reg_value = 0x0001
            if self.register_write(channel_reg,reg_value) is False:
                return False

        return True

    def voltage_single_channel_select(self,channel,config):
        """ channel register Select ADC work channel,open select channel,and close other channels
            It can be used, when  ADC work in single mode

            Args:
                channel: ["chan0","chan1","chan2","chan3"]
                config: channel configuration
                  {"P":AIN,"N":AIN}
                    AIN:["AIN0","AIN1","AIN2","AIN3","AIN4","Temp+","Temp-","AVDD1","AVSS","REF+","REF-"]
            Returns:
                bool: True | False, True for success, False for failed.

            Raise:
                KeyError
        """
        channels={"chan0":0x10,"chan1":0x11,"chan2":0x12,"chan3":0x13}
        setups={"chan0":0x00,"chan1":0x01,"chan2":0x02,"chan3":0x03}
        ains={"AIN0":0x0,"AIN1":0x01,"AIN2":0x02,"AIN3":0x03,"AIN4":0x04,
                    "Temp+":0x11,"Temp-":0x12,"AVDD1":0x13,"AVSS":0x14,"REF+":0x15,"REF-":0x16}

        channel_reg = channels[channel]

        reg_value = 0x8000;
        temp = setups[channel]<<12
        reg_value |= temp

        temp = ains[config["P"]] << 5
        reg_value |= temp

        temp = ains[config["N"]]
        reg_value |= temp

        for channel_tmp in channels:
            reg = channels[channel_tmp]
            if reg == channel_reg:
                value = reg_value
            else:
                value = 0x0001
            ret = self.register_write(reg,value)
            if ret is False:
                return False

        return True

    def voltage_get(self,channel,config):
        """ get acd measure voltage result
            It can be used, when  ADC work in single mode

            Args:
                channel: ["chan0","chan1","chan2","chan3"]
                config: channel configuration
                  {"P":AIN,"N":AIN}
                    AIN:["AIN0","AIN1","AIN2","AIN3","AIN4","Temp+","Temp-","AVDD1","AVSS","REF+","REF-"]

            Returns:
                if success:
                    (value,"mV")
                if failed:
                    False

            Raise:
                KeyError
        """
        #single measure: select the channel
        if self.voltage_single_channel_select(channel,config) is False:
            logger.warning("AD7175[%s] single channel select failed"%(self.device_path))
            return False

        data = self.device.single_sample_code_get();
        if data is False:
            logger.warning("AD7175[%s] single sample code get failed"%(self.device_path))
            return False
        logger.debug("AD7175[%s] channel %s  code: "%(self.device_path,channel)+str(data))

        #check read data's channel if is you want to read
        '''
        if data[0] != 'NULL':
            channels={"chan0":0x00,"chan1":0x01,"chan2":0x02,"chan3":0x03}
            if data[0] != channels[channel]:
                logger.warning("code: ",data[0],"log channel",channels[channel])
                return False
        '''
        code = data[1]
        volt = self.device.code_2_mvolt(code,self.vref,24)
        return volt

    def is_comunication_ok(self):
        """ Whether the communication is normal by check ADC ID

            Returns:
                bool: True | False, True for OK, False for failed.
        """
        read_times = 5
        ret = False
        while read_times > 0:
            ret = self.register_read(0x07)
            if ret is False or 0xcd0 != (ret&0xfff0):
                self.reset()
                read_times -= 1
                time.sleep(0.001)
            else:
                ret = True
                break

        return ret

    def ifmode_register_set(self,data_state_channel_flag="enable",data_bits="24bits"):
        """ ADC IFMODE register set
            Args:
                data_state_channel_flag: ["enable","disable"]
                    enable: sample code will have channel section
                    disable: sample code only is sample code
                data_bits: ["16bits","24bits"]
                    AD7175 sample code have 16 bits and 24bits mode
            Returns:
                bool: True | False, True for success, False for failed.

            Raise:
                KeyError
        """
        channel_flags={"enable":0x01,"disable":0x00}
        ad7175_data_bits={"16bits":0x01,"24bits":0x00}
        ifmode_reg = 0x02
        value = 0x00
        #code if have channel id
        value = value | (channel_flags[data_state_channel_flag]<<6)

        #code bits
        value = value | (ad7175_data_bits[data_bits])

        return self.register_write(ifmode_reg, value)

    def mode_register_set(self,clock_source="internal"):
        """ ADC mode register config
            Args:
                clock_source: ["internal","clock","crystal"]

            Returns:
                bool: True | False, True for success, False for failed.

            Raise:
                KeyError
        """
        #DB2-DB3
        clock_sources={"internal":0x00,"clock":0x02,"crystal":0x03}

        reg = 0x01

        value = 0x8000
        value |= clock_sources[clock_source] <<2

        return self.register_write(reg,value)


    def setup_register_set(self,channel,code_polar="bipolar",reference="extern",buffer_flag="enable"):
        """ setup register set, code polar,refrence, buffer

            Args:
                channel: ["chan0","chan1","chan2","chan3"]
                code_polar:["unipolar","bipolar"]
                reference:["extern","internal","AVDD-AVSS"]
                buffer: ["enable","disable"]

            Returns:
                bool: True | False, True for success, False for failed.

            Raise:
                KeyError
        """
        #setup reg
        channels={"chan0":0x20,"chan1":0x21,"chan2":0x22,"chan3":0x23}
        #value
        #DB12
        polars={"bipolar":0x01,"unipolar":0x00}
        #DB8-DB11
        buffers={"enable":0x0f,"disable":0x00}
        #DB4-DB5
        references={"extern":0x00,"internal":0x02,"AVDD-AVSS":0x03}

        value = 0x000000
        value |= polars[code_polar]<<12
        value |= buffers[buffer_flag]<<8
        value |= references[reference]<<4

        setup_reg = channels[channel]

        return self.register_write(setup_reg, value)

    def samplerate_set(self, channel,samplerate):
        """ Set ADC one channel samplerate
            It can be used, when  ADC work in single mode

            Args:
                channel: ["chan0","chan1","chan2","chan3"]
                samplerate: (rate,"Hz")
                    tuple data, adc samplerate
            Returns:
                bool: True | False, True for success, False for failed.

            Raise:
                KeyError,TypeError,ValueError
        """
        #filter reg
        channels={"chan0":0x28,"chan1":0x29,"chan2":0x2a,"chan3":0x2b}

        filter_reg = channels[channel]
        value = self.register_read(filter_reg)
        if value is False:
            return False

        if not isinstance(samplerate,(tuple,list)):
            raise TypeError(str("Input:")+str(samplerate), str("Args:")+str("(rate,'Hz')"))

        if  len(samplerate) != 2 or not isinstance(samplerate[0],(int,float)):
            raise ValueError(str("Input:")+str(samplerate), str("Args:")+str("(rate,'Hz')"))

        #Hz
        samplerate = samplerate[0]
        if samplerate <= 5:
            samplerate = 0x14
        elif samplerate <= 10:
            samplerate = 0x13
        elif samplerate <= 16:
            samplerate = 0x12
        elif samplerate <= 20:
            samplerate = 0x11
        elif samplerate <= 49:
            samplerate = 0x10
        elif samplerate <= 59:
            samplerate = 0x0f
        elif samplerate <= 100:
            samplerate = 0x0e
        elif samplerate <= 200:
            samplerate = 0x0d
        elif samplerate <= 397:
            samplerate = 0x0c
        elif samplerate <= 500:
            samplerate = 0x0b
        elif samplerate <= 1000:
            samplerate = 0x0a
        elif samplerate <= 2500:
            samplerate = 0x09
        elif samplerate <= 5000:
            samplerate = 0x08
        elif samplerate <= 10000:
            samplerate = 0x07
        elif samplerate <= 15625:
            samplerate = 0x06
        elif samplerate <= 25000:
            samplerate = 0x05
        elif samplerate <= 31250:
            samplerate = 0x04
        elif samplerate <= 50000:
            samplerate = 0x03
        elif samplerate <= 62500:
            samplerate = 0x02
        elif samplerate <= 125000:
            samplerate = 0x01
        else: 
            #250000
            samplerate = 0x00
        
        value = value&(~0x1f)
        value = (value | samplerate)
        return self.register_write(filter_reg, value)
    
    def samplerate_get(self, channel):
        """ Set ADC one channel samplerate
            It can be used, when  ADC work in single mode

            Args:
                channel: ["chan0","chan1","chan2","chan3"]
                
            Returns:
                tuple: (value,"Hz")
                    adc samplerate

            Raise:
                KeyError
        """
        #filtereg
        channels={"chan0":0x28,"chan1":0x29,"chan2":0x2a,"chan3":0x2b}

        filter_reg = channels[channel]

        data = self.register_read(filter_reg)
        if data is False:
            return False

        data = data & (0x1f)

        if data == 0x14:
            samplerate = 5
        elif data == 0x13: 
            samplerate = 10
        elif data == 0x12:  
            samplerate = 16
        elif data ==  0x11:
            samplerate = 20
        elif data ==  0x10:
            samplerate = 49
        elif data == 0x0f :
            samplerate = 59
        elif data ==  0x0e:
            samplerate = 100
        elif data ==  0x0d:
            samplerate = 200
        elif data == 0x0c:
            samplerate = 397
        elif data == 0x0b:
            samplerate = 500
        elif data ==  0x0a:
            samplerate = 1000
        elif data ==  0x09:
            samplerate = 2500
        elif data ==  0x08:
            samplerate = 5000
        elif data ==  0x07:
            samplerate = 10000
        elif data ==  0x06:
            samplerate = 15625
        elif data ==  0x05:
            samplerate = 25000
        elif data == 0x04 :
            samplerate = 31250
        elif data ==  0x03:
            samplerate = 50000
        elif data == 0x02:
            samplerate = 62500
        elif  data ==  0x01:
            samplerate = 125000
        else: 
            samplerate = 250000

        return (samplerate,'Hz')


    def continue_mode_frame_config_set(self,chip_no,samplerate):
        """ Frame channel number and sample rate set.
            It ws used befor "continue_sample_mode" function

            Args:
                chip_no: chip number
                    int type
                samplerate: ADC samplerate (value,"Hz")

            Returns:
                bool: True | False, True for success, False for failed.
        """
        return self.device.frame_channel_and_samplerate_set(chip_no,samplerate)


    def continue_sample_mode(self):
        """ make ADC chip work mode into continue sample mode
            It can be used, when  ADC work in single mode

            Returns:
                bool: True | False, True for success, False for failed.
        """
        return self.device.continue_sample_mode()
#///////////////////////////////////////////////////////////////////////////
#Continue mode

    def continue_mode_codes_get(self,data_count):
        """ Frame channel number and sample rate set.
            It can be used, when  ADC work in continue mode

            Args:
                data_count: int type (1-)

            Returns:
                if success:
                    list type:
                    [data1,...,datan]
                if failed:
                    
        """
        return self.device.data_analysis(data_count)

        

"""
example:
    
    simple measure:  Voltage channel={"P":"AIN0","N":"AIN1","vref":(5000,"mV")}
    
        ad7175 = Ad7175("/device/AXI4_DMM_AD7175",(5000,"mV"))

        ad7175.reset()
        ad7175.single_sample_mode()

        if ad7175.is_comunication_ok() is False:
            return False

        #Channel register: channel combination
        ad7175.voltage_channel_single_select("chan0",{"P":"AIN0","N":"AIN1"})
        ad7175.voltage_channel_single_select("chan1",{"P":"AIN3","N":"AIN2"})

        #setup register: code polar=biploar,refrence=extern, buffer=enable
        ad7175.setup_register_set()

        #filter register: samplerate config
        ad7175.samplerate_set(self, "chan0",(5,"Hz")):

        #adc mode register: internal clock
        ad7175.mode_register_set()

        #the first one discarded
        ad7175.voltage_get("chan0",{"P":"AIN0","N":"AIN1"})
        
        #the first one discarded
        ad7175.voltage_get("chan1",{"P":"AIN3","N":"AIN2"})

"""