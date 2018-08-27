#-*- coding: UTF-8 -*-
from __future__ import division
import os
import re
import json
import time
import os.path
import sys
import command.server.handle_utility as utility
import ee.common.utility as ee_utility
from ee.common import net
from ee.common import logger
from ee.ipcore.axi4_sysreg import Axi4Sysreg

from command.handle import eeprom as Eeprom

from ee.common import xavier as Xavier

sn_file_name = "/opt/seeing/config/sn.txt"

global board_sn_list
board_sn_list=None

sn_address = 0x50
sn_max_len = 32

def get_board_sn_list():
	global board_sn_list
	board_sn_list = []
	if Eeprom.eeprom_id_list is None:
		Eeprom.get_eeprom_id_list()

	board_sn_list.extend(Eeprom.eeprom_id_list)
	board_sn_list.append("zynq")


@utility.timeout(1)
def SG_sn_write_handle(params):
	if board_sn_list is None:
		get_board_sn_list()
	help_info = "sn write(<board_name>,<key_n_key_e>,<\"serila-number\">)$\r\n\
\tboard-name:(" + ",".join(board_sn_list) + ")$\r\n\
\tkey_n_key_e: private key eg: 222_33$\r\n\
\tserila-number:(""), a string, max 32 bytes\" \"\r\n"

	''' help '''    
	if utility.is_ask_for_help(params) is True:
		return utility.handle_done(help_info)

	'''  params analysis '''
	param_count = len(params)
	if param_count != 3 :
		return utility.handle_error(utility.handle_errorno["handle_errno_parameter_invalid"],"param length error" )

	buf = ""
	for index in range(0,param_count):
		if index == 0:
			board_name = params[index]
		elif index == 1:
			regular_expression = re.match( r'(\w+)_(\w+)', params[index])
			if regular_expression is None:
				return utility.handle_error(utility.handle_errorno['handle_errno_parameter_invalid'] - index,"param error")

			key_n = int(regular_expression.group(1), 10)
			key_e =int(regular_expression.group(2), 10)
		elif index == 2:
			if buf != "":
				buf += ","
			buf += params[index]
		else:
			return utility.handle_error(utility.handle_errorno["handle_errno_parameter_invalid"] - index,"param length error" )

	if board_name not in board_sn_list:
		return utility.handle_error(utility.handle_errorno["handle_errno_parameter_invalid"],"param board_name error" )

	if len(buf) > sn_max_len +2:
		return utility.handle_error(utility.handle_errorno["handle_errno_parameter_invalid"] - 2,"write data is too long max is %d"%(sn_max_len) )
		
	content = []
	for index in range(0,len(buf)):
		if (buf[index] != '\"') and (buf[index] != '\0') :
			content += [pow(ord(buf[index]),key_e)%key_n]

	if len(content) < 32:
		content += [0x00]

	if board_name == "zynq":
		msg = ""
		for index in range(0,len(content)):
			if content[index] == 0x00:
				break;
			msg += chr(content[index])
		with open(sn_file_name,"w") as sn_file:
			sn_file.write(msg)
		sn_file.close()
	else :
		if Xavier.call('eeprom_write', board_name, sn_address, content) is True:
			return utility.handle_done()
		else:
			return utility.handle_error(utility.handle_errorno["handle_errno_execute_failure"],"message execute failed")

@utility.timeout(1)
def SG_sn_read_handle(params):
	if board_sn_list is None:
		get_board_sn_list()
	help_info = "sn read(<board_name>,)$\r\n\
\tboard-name:(" + ",".join(board_sn_list) + ")$\r\n"
	
	''' default operation  '''
	key_n = 247
	key_d = 11

	''' help '''    
	if utility.is_ask_for_help(params) is True:
		return utility.handle_done(help_info)

	'''  params analysis '''
	param_count = len(params)
	if param_count != 1 :
		return utility.handle_error(utility.handle_errorno["handle_errno_parameter_invalid"],"param length error" )

	for index in range(0,param_count):
		if index == 0:
			board_name = params[0]

	if board_name not in board_sn_list:
		return utility.handle_error(utility.handle_errorno["handle_errno_parameter_invalid"],"param board_name error" )

	result = ""
	if board_name == "zynq":
		if os.path.exists(sn_file_name): 
			logger.info("sn file is exist ")
			#1) file exist : read vendor message 
			with open(sn_file_name) as sn_file:
				result = list(sn_file.read(sn_max_len))
			sn_file.close()
			for index in range(0,len(result)):
				result[index] = ord(result[index])
	else:
		result = Xavier.call('eeprom_read', board_name, sn_address, sn_max_len )
		if  result is False:
			return utility.handle_error(utility.handle_errorno["handle_errno_execute_failure"],"read failed" )

	msg = ""
	msg += '\"'
	result_flag = True
	for index in range(0,len(result)):
		if result[index] == 0x00:
			break;

		de_crypt = pow(result[index],key_d)%key_n
		if de_crypt & 0x80 != 0x00:
			result_flag = False
		msg += chr(de_crypt)
	msg += '\"'
	msg += '\0'
	
	if result_flag:
		return utility.handle_done(msg)
	else:
		return utility.handle_error(utility.handle_errorno["handle_errno_crc_checksum_failure"],msg)
