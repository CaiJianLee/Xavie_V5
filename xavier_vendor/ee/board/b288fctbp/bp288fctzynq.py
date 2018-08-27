#-*- coding: UTF-8 -gg*-
import copy
from ee.ipcore.axi4_gpio import Axi4Gpio
from ee.common import logger
from ee.profile.profile import Profile
import ee.common.utility as utility
import ee.overlay.extendio as ExtendIo
from ee.chip.AD5061 import AD5061
from ee.chip.ad5601 import AD5601
from ee.ipcore.axi4_signal_meter import Axi4SignalMeter
from ee.ipcore.axi4_frame_config import Axi4Frame
from ee.ipcore.axi4_fft_analyzer  import Axi4FftAnalyzer
from ee.chip.ad7175 import AD7175
from ee.chip.ina231 import INA231
from ee.ipcore.axi4_time_detect import Axi4TimeDetect
from ee.ipcore.axi4_xadc import XadcDevice
from ee.board.b288fctbp.axi4_time_detect_v1 import Axi4TimeDetect_v1
import time

class bp288fctzynq(object):
    """TESTBASE board SE23002CM01PCB driver

    Public methods:
    - board_initial: 
    - signal_square_output: signal output square waveform
    - signal_square_disoutput: signal output disable.
    - signal_pdm_output: signal output pdm waveform.
    - signal_pdm_disoutput: signal output disable.
    - parse_board_profile:
    """

    def __init__(self,profile):
        self.profile = profile
        self.dac_device=dict()
        self.dac_device['psu1_ocp']=AD5061(self.profile['psu1_ocp']['path'],self.profile['psu1_ocp']['vref']) 
        self.dac_device['psu1_ovp']=AD5061(self.profile['psu1_ovp']['path'],self.profile['psu1_ovp']['vref'])   
        self.dac_device['psu1_current']=AD5061(self.profile['psu1_current']['path'],self.profile['psu1_current']['vref']) 
        self.dac_device['psu1_voltage']=AD5061(self.profile['psu1_voltage']['path'],self.profile['psu1_voltage']['vref']) 
        self.dac_device['psu2_ocp']=AD5061(self.profile['psu2_ocp']['path'],self.profile['psu2_ocp']['vref']) 
        self.dac_device['psu2_ovp']=AD5061(self.profile['psu2_ovp']['path'],self.profile['psu2_ovp']['vref'])      
        self.dac_device['psu2_current']=AD5061(self.profile['psu2_current']['path'],self.profile['psu2_current']['vref']) 
        self.dac_device['psu2_voltage']=AD5061(self.profile['psu2_voltage']['path'],self.profile['psu2_voltage']['vref']) 
        self.dac_device['psu3_ocp']=AD5061(self.profile['psu3_ocp']['path'],self.profile['psu3_ocp']['vref']) 
        self.dac_device['psu3_ovp']=AD5061(self.profile['psu3_ovp']['path'],self.profile['psu3_ovp']['vref']) 
        self.dac_device['psu3_current']=AD5061(self.profile['psu3_current']['path'],self.profile['psu3_current']['vref']) 
        self.dac_device['psu3_voltage']=AD5061(self.profile['psu3_voltage']['path'],self.profile['psu3_voltage']['vref']) 
        self.dac_device['TP_board_voltage']=AD5601(self.profile['TP_board_voltage']['path'],self.profile['TP_board_voltage']['vref']) 
                                                   
        self.gpio_device_name=Axi4Gpio(self.profile["switch_gpio_path"])
        self.ad7175_device=AD7175(self.profile["adc7175_path"],self.profile["adc7175_vref"] )

        self.ina231_device=dict()              
        self.ina231_device["psu1_ina231"]=INA231(self.profile['psu1_ina231']['ina231_path'],self.profile['psu1_ina231']["ina231_addr"] )        
        self.ina231_device["psu2_ina231"]=INA231(self.profile['psu2_ina231']['ina231_path'],self.profile['psu2_ina231']["ina231_addr"] )        
        self.ina231_device["psu3_ina231"]=INA231(self.profile['psu3_ina231']['ina231_path'],self.profile['psu3_ina231']["ina231_addr"] )        
  
        self.adc_device=XadcDevice(self.profile["adc_path"] )
        self.adc_vref=self.profile["adc_vref"] 
 
        self.width_meter_device=dict()
        self.width_meter_device['psu1']= Axi4TimeDetect(self.profile["iowidthfunction"]["psu1"]["path"])
        self.width_meter_device['psu2'] = Axi4TimeDetect(self.profile["iowidthfunction"]["psu2"]["path"])
        self.width_meter_device['psu3'] = Axi4TimeDetect(self.profile["iowidthfunction"]["psu3"]["path"])
        self.width_meter_device['ppulse'] = Axi4TimeDetect(self.profile["ppulse"])  

        self.protectwavemeasure_device=Axi4TimeDetect(self.profile["protectwavemeasure"]["path"])       
                          
        self.frequncy_meter_device=dict()
        self.frequncy_meter_device['freq']= Axi4SignalMeter(self.profile["freq"])
        
        self.audio_frame_device=Axi4Frame(self.profile["frame_dev_path"])
        self.audio_fft_device=Axi4FftAnalyzer(self.profile["audio_dev_path"])
        
        self.wave_measure_device=Axi4TimeDetect(self.profile["wave_measure"]["path"])       
         
#     def audio_measure(self,band,measure_time):
#         self.gpio_device_name.gpio_set([(self.profile["audio_reset"],0)])
#         self.gpio_device_name.gpio_set([(self.profile["audio_enable"],1),(self.profile["audio_reset"],1)])
#         time.sleep(0.001)
#         self.audio_device.upload_disable()
#         self.audio_device.disable()
#         self.audio_device.enable()
#         self.audio_device.upload_enable()
# 
#         ''' 采样频率参数跟着板卡定　sample_rate:(1000 - 1000000)，　去掉通道选择　保留 '''
#         self.audio_device.measure_paramter_set(band,192000,"auto",'IIS')
#         if self.audio_device.measure_start() is False:
#             return False
#         return True
    def audio_datalogger_open(self):
        self.gpio_device_name.gpio_set([(self.profile["audio_reset"],0)])
        self.gpio_device_name.gpio_set([(self.profile["audio_enable"],1),(self.profile["audio_reset"],1)])
        self.audio_frame_device.disable()
        self.audio_frame_device.enable() 
        if self.audio_frame_device.frame_state_set('always_open') is  False:
            return False
        self.audio_frame_device.frame_config_set(0x10,0,4,'TS',config_list=[0,0,0,0,0,0,0,0,0,0])  
        return True
    
    def audio_datalogger_close(self):
    #      self.gpio_device_name.gpio_set([(self.profile["audio_enable"],0),(self.profile["audio_reset"],0)])
        self.audio_frame_device.frame_state_set('close')
        self.audio_frame_device.disable()
        return True


    def ina231_register_read(self,channel,reg_addr):
        return self.ina231_device[channel].register_read(reg_addr)

    def ina231_register_write(self,channel,reg_addr,reg_data):
        return self.ina231_device[channel].register_write(reg_addr,reg_data)  
    def shunt_and_bus_voltage_read(self,channel,res):
        return self.ina231_device[channel].shunt_and_bus_voltage_read(res)
    
    def ina231_config(self,channel,average,vbus_conversion_time,shunt_conversion_time):
        ret=self.ina231_device[channel].average_set(average)
        if ret is False:
            return False
        ret=self.ina231_device[channel].bus_conversion_time_set(vbus_conversion_time)
        if ret is False:
            return False
        ret=self.ina231_device[channel].shunt_conversion_time_set(shunt_conversion_time)
        if ret is False:
            return False     
        return True
        
    def ad7175_voltage_measure(self,channel):
        """Get voltage measure channel result
        
        Returns:
            result:(value,unit)
                value: voltage measure value
                unit: ('uV','mV','V')
        """
        if not self.ad7175_device.samplerate_set(channel,self.profile["adc7175_samplerate"]):
            logger.warning("%s AD7175[ chip voltage channel samplerate configure failed")
            return False        
        if self.ad7175_device.voltage_channel_disable("all") is False:
            logger.warning("ad7175[%s]  chip channel reg  all disable config failed"%(self.profile["adc7175_path"]))
            return False
    
        if not self.ad7175_device.single_sample_mode():
            logger.warning("set ad7175 signal sample is false")
            return False
#        self.ad7175_device.voltage_channel_enable(channel,self.profile["adc7175_config"][channel])
 #       logger.warning(str(self.profile["adc7175_config"][channel]))  
        if channel not in self.profile["adc7175_config"]:
            logger.warning("channel parameter error")  
            return False          
        volt = self.ad7175_device.voltage_get(channel,self.profile["adc7175_config"][channel])
        if volt is False:
            logger.warning("ad7175 voltage measure voltage get failed!")
            return False
        return volt
    
    def voltage_set(self,channel,voltage):
        """ dac voltage set
            Args:
                channel("uut1_batt_volt","uut2_batt_volt","uut3_batt_volt","uut4_batt_volt",
                "uut1_vbus_volt","uut2_vbus_volt","uut3_vbus_volt","uut4_vbus_volt","uut1_batt_curr" 
                ,"uut2_batt_curr" ,"uut3_batt_curr","uut4_batt_curr","uut1_vbus_curr" ,"uut2_vbus_curr" ,
                "uut3_vbus_curr" ,"uut4_vbus_curr" )
            Returns:
                bool: True| False, False for adc set failed,True for success
        """
        if channel !="TP_board_voltage":
            self.gpio_device_name.gpio_set(self.profile[channel]['gpio'])
        ret=self.dac_device[channel].set_volt(voltage)
        return ret
    
    def adc_voltage_read(self):
        """get  adc voltage of zynq  adc           
            Returns:
                voltage| False,
                    False:False  for adc read failed,   
                    voltage：voltage value               
        """
        xadc_func = self.adc_device
        rd_data = xadc_func.register_read(0x20c, 4)
        if rd_data==False:
            return False
        v_data = (rd_data[0] + rd_data[1] * 256) / 16
        v_data = v_data * self.adc_vref / 4096
        return v_data 

    def frequency_measure(self,channel,measure_time,sample_rate):
        """frequency measure         
            Returns:
                {frequency,duty_value}| False,
                    False:False  for frequency  measure
                    {frequency,duty_value}：frequncy value and duty value          
        """
        frequency_value=[]
        self.frequncy_meter_device[channel] .disable()
        self.frequncy_meter_device[channel] .enable()   
        logger.error(str)
        ret = self.frequncy_meter_device[channel].measure_start(measure_time,sample_rate)
        if ret is False:
            frequency_value.append(0)
            duty_value =0
        else:
            frequency_value = self.frequncy_meter_device[channel].frequency_measure('LP')
            duty = self.frequncy_meter_device[channel].duty_measure()
            duty_value = duty[0]

        resultdata={'fre':frequency_value,'duty':duty_value}
        return resultdata

    def protect_flag_status(self,channel,p_gpio):
        """width measure         
            Returns:
                time| False,
                    False:False  for width  measure
                    time：dalay time value ,unit ns:         
        """
        ret =self.gpio_device_name.gpio_get([(self.profile["iowidthfunction"][channel][p_gpio],255)])  
        return ret
   
    def delay_time_measure(self,channel,mesure_time):
        """width measure         
            Returns:
                time| False,
                    False:False  for width  measure
                    time：dalay time value ,unit ns:         
        """
        if channel not in self.width_meter_device:
            return False
        self.width_meter_device[channel].disable()
        self.width_meter_device[channel].enable()  
        if channel=="ppulse"   :
            self.width_meter_device[channel].start_edge_set('A-POS') 
            self.width_meter_device[channel].stop_edge_set('A-NEG')   
        else:  
            self.width_meter_device[channel].start_edge_set('A-POS') 
            self.width_meter_device[channel].stop_edge_set('B-POS') 
        self.width_meter_device[channel].measure_disbale()    
        self.width_meter_device[channel].measure_enable()
        ret=self.width_meter_device[channel].detect_time_get(mesure_time)
        self.width_meter_device[channel].disable()
        self.width_meter_device[channel].measure_disbale()       
        return ret

    def protectwavemeasure_fun(self,channel,mesure_time):
        """width measure         
            Returns:
                time| False,
                    False:False  for width  measure
                    time：dalay time value ,unit ns:         
        """
        self.gpio_device_name.gpio_set(eval(self.profile["protectwavemeasure"]["switch_gpio"][channel]))
        self.protectwavemeasure_device.disable()
        self.protectwavemeasure_device.enable()  
        self.protectwavemeasure_device.start_edge_set('A-POS') 
        self.protectwavemeasure_device.stop_edge_set('A-NEG')   
        self.protectwavemeasure_device.measure_disbale()    
        self.protectwavemeasure_device.measure_enable()
        ret=self.protectwavemeasure_device.detect_time_get(mesure_time)
        self.protectwavemeasure_device.disable()
        self.protectwavemeasure_device.measure_disbale()       
        return ret

    def wave_measure_start(self,start_channel,stop_channel):
        if start_channel not in self.profile["wave_measure"]["start_switch_gpio"]:
            return False 
        if stop_channel not in self.profile["wave_measure"]["stop_switch_gpio"]:
            return False 
        self.gpio_device_name.gpio_set(eval(self.profile["wave_measure"]["start_switch_gpio"][start_channel]))
        self.gpio_device_name.gpio_set(eval(self.profile["wave_measure"]["stop_switch_gpio"][stop_channel]))
        self.wave_measure_device.disable()
        self.wave_measure_device.measure_disbale()
        self.wave_measure_device.enable()
        self.wave_measure_device.start_edge_set('A-POS')
        self.wave_measure_device.stop_edge_set('B-PORN')
        self.wave_measure_device.measure_enable()     
        return True  
    
    def wave_measure_get(self,mesure_time):
        time_data=self.wave_measure_device.detect_time_get(mesure_time)
        return time_data
        
    
    @staticmethod
    def parse_board_profile(board):
        board_name = board['id']
        boards = Profile.get_boards()
        boards[board_name] = dict()
        boards[board_name]['id'] = board_name
        boards[board_name]['partno'] = board['partno']
        boards[board_name]['switch_gpio_path'] =  utility.get_dev_path()  +'/' +board['switch_gpio']
        boards[board_name]['daq_channel'] =board['daq_channel']
        for key in board['dacfunction'].keys():
            boards[board_name][key] =  dict()
            boards[board_name][key]["vref"] = board['dacfunction'][key]['vref']
            boards[board_name][key]['path']=utility.get_dev_path()  +'/' + board['dacfunction'][key]['path']
            boards[board_name][key]['gpio']=[(board['dacfunction'][key]['gpio1'],board['dacfunction'][key]['gpio1_state']),
                                             (board['dacfunction'][key]['gpio0'],board['dacfunction'][key]['gpio0_state'])]       
                     
        boards[board_name]['adc7175_path']= utility.get_dev_path()  +'/' +board['adc7175function']['path']
        boards[board_name]['adc7175_vref']=(board['adc7175function']['vref'],"mV")
        boards[board_name]['adc7175_samplerate']=(board['adc7175function']['samplerate'],"Hz")
        boards[board_name]['adc7175_config']=copy.deepcopy(board['adc7175function']['config'])
        
        for key in board['ina231funtion'].keys():
            boards[board_name][key] =  dict()       
            boards[board_name][key]['ina231_path']=utility.get_dev_path()  +'/' + board['ina231funtion'][key]['iic_path']
            boards[board_name][key]['ina231_addr']= int(board['ina231funtion'][key]['addr'],16)
    
        boards[board_name]['adc_path']= utility.get_dev_path()  +'/' +board['adcfunction']['path']
        boards[board_name]['adc_vref']=board['adcfunction']['vref']
        
        boards[board_name]['iowidthfunction']= copy.deepcopy(board['iowidthfunction'])
        for key in board['iowidthfunction'].keys():
            boards[board_name]['iowidthfunction'][key]["path"]=utility.get_dev_path()  +'/' +board['iowidthfunction'][key]["path"]
            
        boards[board_name]['protectwavemeasure']= copy.deepcopy(board['protectwavemeasure'])      
        boards[board_name]['protectwavemeasure']["path"]=utility.get_dev_path()  +'/' +board['protectwavemeasure']["path"]           
          
        boards[board_name]['wave_measure']= copy.deepcopy(board['wave_measure'])
        boards[board_name]['wave_measure']["path"]= utility.get_dev_path()  +'/' +board['wave_measure']['path']
                         
        boards[board_name]['freq']= utility.get_dev_path()  +'/' +board['meterfunction']['freq']['path']
        boards[board_name]['ppulse']=utility.get_dev_path()  +'/' +board['meterfunction']['ppulse']['path']   
        
        boards[board_name]['frame_dev_path']= utility.get_dev_path()  +'/' +board['audiofunction']['frame_dev_path']
        boards[board_name]['audio_dev_path']= utility.get_dev_path()  +'/' +board['audiofunction']['audio_dev_path']
        boards[board_name]['audio_reset']= board['audiofunction']['reset_gpio']
        boards[board_name]['audio_enable']= board['audiofunction']['enable_gpio']
    
#         boards[board_name]['audiofunction_path']= utility.get_dev_path()  +'/' +board['audiofunction']['path']
#         boards[board_name]['audio_reset']= board['audiofunction']['reset_gpio']
#         boards[board_name]['audio_enable']= board['audiofunction']['enable_gpio']
#             
        
            
    def board_initial(self):
#        self.initial_flag
        return True
