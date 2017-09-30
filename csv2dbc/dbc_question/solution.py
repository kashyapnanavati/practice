#!/usr/bin/python
'''
######################################### Problem Statemnt ####################################
".dbc" file is widely used in auto industry to define the CAN communication matrix between
different devices.
Don't know what is CAN? No worry, CAN is a communication protocol based on Messages.
A message contains maximum 64bits data. And a message contains multiple signals based on 
how you define it.
For example, in "example.dbc" we have a message:
BO_ 528 DC_DC_Converter_Status: 7 DCDC
SG_ Input_Power : 0|12@1+ (1,0) [0|1023] "kW" VCU
SG_ Output_Current : 12|12@1- (1.5,100) [-1000|1500] "kW" VCU, BMS
SG_ DC_DC_State : 24|3@1+ (1,0) [0|7] "" BMS  

BA_ "sendPeriod" BO_ 528 10;

BA_ "FieldType" SG_ 528 DC_DC_State "DC_DC_State";
VAL_ 528 DC_DC_State 7 "Error" 6 "UnderTemp" 5 "OverTemp" 3 "Idle" 1 "Start" 0 "Init" ;

The 1st line started with "BO_" means a 7 byte(56bit) message "DC_DC_Converter_Status" has
ID 528 in decimal is sent by device called "DCDC". The formula is:

BO_ [message ID] [Message Name]: [message length in byte] [Transmitter]

The 2nd line started with "SG_" means there is a 12 bit signal "Input_Power" start from 
bit 0 to bit 11. This signal is an unsigned, little endian, normal signal received by device "VCU".
Factor = 1, Offset =0, Min = 0, Max =1023. Let's ignore the Min and Max. 
So if the raw signal is 000001001000 for example, it stands for 72*1+0 = 72kW. 
The formula is:
SG_ [signal name] : [start bit]|[length]@[1: little endian; 0: big endian][+: unsigned; -:signed] ([factor]|[offset]) [[Min]|[Max]] "[Unit]" "Receiver1,Receiver2..."
The 3rd line is similar, except it is a signed signal. The first bit is the sign bit.
So if the raw signal is 000001001000 for example, it stands for 72*1.5+100 = 208kW.
if the raw signal is 111001001000 for example, it stands for -440*1.5+100 = -560kW. 

The 4th line is a little bit different. It is an "enum" signal. Why?
Check the 6th /7th line started with "BA_" and "VAL_". 
So signal "DC_DC_State" means "Error" / "UnderTemp" / "OverTemp" / "Idle" / "Start" / "Init" when raw value is 7 6 5 3 1 0.
For the 5th line, it means the message with ID 528 is a cyclic message and been sent every 10ms.

But for some reason, one of your supplier is too lazy to provide the ".dbc" file to you. 
Instead they send you a ".csv" file to demonstrate their CAN matrix definition 
(check "example.csv" in the folder). Not like them, you are professional and smart.
So you manually translated it into ".dbc" file (check "example.dbc" in the folder). Good for you!
However, next day you check your email, and found your other 1000000 suppliers all
start to send you the ".csv" file instead of ".dbc". So you don't have time to manually
translate it and decide to write a small program to automatically do the translation for you.
So here is the requirement, use C/C++/python to write a program to automatically translate the
".csv" file to ".dbc" file. Use the "example.csv" and "example.dbc" to verify your code. 
And "test.csv" is your testing input file. Please submit your solution including your code and
"test.dbc" generated from "test.csv".
#################################################################################################
'''
'''
Name : Kashyap Nanavati
email: kashyapnanavati@gmail.com
'''
'''
Assumptions/Requirements :
1. Start of signal(main message - "*Message Name") is always 2 lines.
2. message can have finite number of normal signals and
   enumed signal in one file which can be fitted in System RAM.
   In short, file_size is assumed to be less then RAM of the system.
3. Assuming only one process is handling the input/output file.
4. Code is tested with Python Version 2.7.9
'''
'''
Following things in the description/word document are not clear :
1. In the given example.dbc file, line 3 should be,
   SG_ Output_Power : 12|12@1- (1.5,100) [-1000|1500] "kW" VCU, BMS
   Signal name is Output_Power not just Output

2. If signal is not cyclic do we need to print following line with None or discard full line in output ?
   BA_ "sendPeriod" BO_ 436
   Current, implementation doesn't print this line if message is not cyclic.
   
3. Line 6th and 7th are generated when enum is present in signal. 
   How messages should look like if one message has multiple signals with
   *Enum = Yes ?
   Currently, this senario is tested in testcases/test5 and following
   format is used. It print with B0_, then all the SG_ and then BA_ "sendPeriod"
   To test this senario Output_Power and DC_DC_State both are created enumed signal in test5
   for local testing.
   e.g. Output of test4.csv file is :
   BO_ 528 DC_DC_Converter_Status: 7 DCDC
   SG_ Input_Power : 0|12@1+ (1,0) [0|1023] "kW" VCU
   SG_ Output_Power : 12|12@1- (1.5,100) [-1000|1500] "kW" VCU, BMS
   SG_ DC_DC_State : 24|3@1+ (1,0) [0|7] "" BMS

   BA_ "sendPeriod" BO_ 528 10;

   BA_ "FieldType" SG_ 528 Output_Power "Output_Power";
   VAL_ 528 Output_Power 7 "Error" 6 "UnderTemp" 5 "OverTemp" 1 "Start" 0 "Init" ;

   BA_ "FieldType" SG_ 528 DC_DC_State "DC_DC_State";
   VAL_ 528 DC_DC_State 7 "Error" 6 "UnderTemp" 5 "OverTemp" 3 "Idle" 1 "Start" 0 "Init" ;
 '''

import csv
import os
import math
import cStringIO
from collections import defaultdict
import sys
import getopt

def get_key_value_pair(key, dict):
	'''Module Level Function

	Extract value from dictionary using keys

	Args:
		key    : key from dictionary
		dict   : Dictionary which contain key-value pairs

	Returns:
		str    : Value from dictionary

	'''
	if key in dict:
	 	#print "Found Key"
	 	msg_name = dict[key]
	 	#print msg_name
	 	return msg_name
	else:
		# print "INFO! Value Doesn't Exist\n"
		return ""

def count_msgs(filename):
	'''Module Level Function

	Count messages with string "*Message Name"

	Args:
		filename : Input file name to the function

	Returns:
		int      : total number of messages in input file

	'''
	if (os.path.isfile(filename) != True):
		print "ERR! Input File Doesn't Exist\n" + filename		
		sys.exit()
	with open(filename, 'r') as f:
		buf = f.read()
		# print(buf.count("*Message Name"))
		msg_c = buf.count("*Message Name")
		f.close()
		return msg_c

def get_lines(filename):
	'''Module Level Function

	Get total number of lines in input file

	Args:
		filename : Input file name to the function

	Returns:
		int      : total number of lines in input file

	'''
	if (os.path.isfile(filename) != True):
		print "ERR! Input File Doesn't Exist\n" + filename		
		sys.exit()
	with open(filename, 'r') as f:
		#Avoid creating new list in memory
		lines = sum(1 for _ in f)
		f.close()
		return lines


def first2(s):
	'''Module Level Function

	Get first two characters of input string

	Args:
		s        : Input String

	Returns:
		str      : chops string from 2nd character and return string

	'''
	return s[:2]

def is_comment(row):
	'''Module Level Function

	Check if line is comment in input file or not

	Args:
		row        : Input List to be checked

	Returns:
		bool      : return true if row is actually a comment "//"
	
	'''
	if first2(row[0:][0])!='//':
		return False
	return True

def read_into_buffer(filename):
	'''Module Level Function

	read the input file into Buffer

	Args:
		filename    : Input File

	Returns:
		_csv.reader : Input buffer
		file        : input file handle
	
	'''
	if (os.path.isfile(filename) != True):
		print "ERR! Input File Doesn't Exist\n" + filename;
		sys.exit()
	#data = open(filename).read()
	with open(filename, 'r') as in_file:
		data = in_file.read()
	csvReader = csv.reader(cStringIO.StringIO(data))
	#csvReaderFiltered = filter(lambda row: row[0]!='//', csvReader)
	return csvReader, in_file

def openFile(filename):
	'''Module Level Function

	open the file 

	Args:
		filename    : name of the file to be open

	Returns:
		file        : file handle
	
	'''
	file_handle = open(filename, 'w')
	return file_handle

def write_to_file(file_handle, value):
	'''Module Level Function

	write to file 
	Assume only one process is handling the output file

	Args:
		file_handle    : file to be written
		value          : content to be written in the file
	
	'''
	if not file_handle.closed:
		file_handle.write(value)

def closeFile(file_handle):
	'''Module Level Function

	Close the file 

	Args:
		file_handle    : file to be closed
	
	'''
	if not file_handle.closed:
		file_handle.close()

def is_valid_row(l_row):
	'''Module Level Function

	it removes comments, empty line and not used "," lines from input row list

	Args:
		l_row     : List containing all the lines from the file

	Returns:
		list      : list contain all valid lines from the file
	
	'''
	list_out = [x for x in l_row if x and not is_comment(l_row)]
	if list_out:
			# print list_out
			return list_out

def isStrNone(in_str):
	if in_str == 'None' or in_str == 'none':
		return ""
	else:
		return in_str


def periodDecode(id_n, c_time):
	'''Module Level Function

	Generate the cyclic message using given formula if
	cyclic time is not null

	Args:
		id_n      : message ID
		c_time    : cycle time of the message

	Returns:
		str      : string contains Generated cylic message
	
	'''
	if c_time: #If cyclic time is present then only signal is cyclic
		# Doing c_time[:-2] to discard "ms" from String (Assuming message is always in ms)
		# print 'BA_ "sendPeriod" BO_ %s %s;' %(id_n, c_time[:-2])
		print_val = '\nBA_ "sendPeriod" BO_ %s %s;' %(id_n, c_time[:-2])
		# print print_val
		return print_val


def msgDecode(valid_list, msg_name_list, sig_name_list, index):
	'''Module Level Function

	Generate/Decode main message from all the valid lines
	Creating list key-->value pair from row[1:3]
	Iterate over msg_list - Assume 2 lines always

	Args:
		valid_list       : Contain all the valid lines as list (string)
		msg_name_list    : List (int) of indexes of main messages where they start
		sig_name_list    : List (int) of indexes of signal messages where they start
		index            : Index of current message from messages pool

	Returns:
		str              : message id in String
		str              : cycle time in String
		str              : Decoded message
	
	'''
	#print index
	# print msg_name_list[index]
	l_list_index = msg_name_list[index]
	# print valid_list[l_list_index]
	# print valid_list[l_list_index+1] #TODO check not out of bound
	msg_dict = dict(zip(valid_list[l_list_index], valid_list[l_list_index+1]))
	# print msg_dict
	# print '\n'
	msg_name     = get_key_value_pair('*Message Name', msg_dict)
	tx           = get_key_value_pair('*Transmitter', msg_dict)
	id           = get_key_value_pair('*ID', msg_dict)
	len          = get_key_value_pair('*Length', msg_dict)
	can_bus_name = get_key_value_pair('*CAN Bus Name', msg_dict)
	cycle_time   = get_key_value_pair('*Cycle Time', msg_dict)

	
	msg_name = isStrNone(msg_name)
	tx = isStrNone(tx)
	id = isStrNone(id)
	len = isStrNone(len)
	can_bus_name = isStrNone(can_bus_name)
	cycle_time = isStrNone(cycle_time)
	#TODO : Write output to file
	#BO_ [message ID] [Message Name]: [message length in byte] [Transmitter]
	# print 'BO_ %s %s: %s %s ' % (id, msg_name, len, tx)
	print_val = 'BO_ %s %s: %s %s\n' % (id, msg_name, len, tx)
	# print print_val
	return id, cycle_time, print_val

def enumDecodeN(valid_list, msg_name_list, sig_name_list, index, msg_id, last_signal, max_val):
	'''Module Level Function

	Generate/Decode enum message : if enum message is present in current signal then
	decode otherwise send empty string
	Length of enum messages are depends on max_val (*MAX or 2^(*Length) - 1)

	Args:
		valid_list       : Contain all the valid lines as list (string)
		msg_name_list    : List (int) of indexes of main messages where they start
		sig_name_list    : List (int) of indexes of signal messages where they start
		index            : Index of current message from messages pool
		msg_id           : message id to construct line 6th and 7th
		last_signal      : current signal with enum = "Yes" to construct 6th and 7th line
		max_val          : max Enum value (*Max or 2^(*Length) - 1)

	Returns:
		str              : Decoded message
		str              : Number of Enum lines (int cast as str)
	
	'''
	print_val_l = ''
	# When enum is present then max value will be the total number of enums
	no_of_enum_lines = 1 # consider "*Enum Value *Meaning" line
	# print 'enumDecodeN Debug Start:\n'
	# print 'index = ', index
	# print 'valid_list[index+1]', valid_list[index+1]
	# print 'max_val', max_val
	# print 'BA_ "Field Type" SG_ %s %s "%s";' %(msg_id, last_signal, last_signal)
	print_val_l = '\n\nBA_ "FieldType" SG_ %s %s "%s";\n' %(msg_id, last_signal, last_signal)
	print_val_l += 'VAL_ %s %s' %(msg_id, last_signal)

	# Need this list store and print in reversed order.
	# Cannot use reversed directly because, not always all the enums will present in file and it will give
	# wrong values if we iterate in reverse order
	# Also, max_val = 2^length - 1 (either we can use length or max both are same)
	enum_list = [[0 for x in range(2)] for y in range(int(max_val))]

	for index, (item) in enumerate(valid_list[int(index+1):int(index+1)+int(max_val)]):
		# print item[0], item[1]
		# print 'Is digit =' , item[0].isdigit()
		# Enum is never negative or float
		if item[0].isdigit() :
			enum_list[index] = [item[0], item[1]]
			no_of_enum_lines = no_of_enum_lines + 1
			# print 'no_of_enum_lines = ', no_of_enum_lines
		else :
			#It is possible that, not all the enum values are present and next line can be new message
			break

	# print enum_list
	for index in reversed(range(no_of_enum_lines-1)):
		# print enum_list[index]
		print_val_l += ' %s "%s"' %(enum_list[index][0], enum_list[index][1])
		# print 'print_val_l = ', print_val_l

	print_val_l += ' ;'
	# print 'no_of_enum_lines = ', no_of_enum_lines
	# print 'enumDecodeN Debug End:\n'
	return print_val_l, no_of_enum_lines

def single_sigDecode(sig_dict):
 	'''Module Level Function

	Generate/Decode single signal message from current dictionary

	Args:
		sig_dict        : Current signal as part of dictionary

	Returns:
		str              : Decoded message
		str              : enum value (Is enum present or not ?)
		str              : name of signal
		str              : max Value (it will be used only when enum is present in signal)
	
 	'''
	# Parse --> *Signal Name,*Start Bit,*Length,*Endian Type,*Signed or Not,*Enum,*Factor,*Offset,*Min,*Max,*Unit,*Receivers		
	sig_name     = get_key_value_pair('*Signal Name', sig_dict)
	start_bit    = get_key_value_pair('*Start Bit', sig_dict)
	length       = get_key_value_pair('*Length', sig_dict)
	endian_type  = get_key_value_pair('*Endian Type', sig_dict)
	is_signed    = get_key_value_pair('*Signed or Not', sig_dict)
	enum_val     = get_key_value_pair('*Enum', sig_dict)
	factor       = get_key_value_pair('*Factor', sig_dict)
	offset       = get_key_value_pair('*Offset', sig_dict)
	min_val      = get_key_value_pair('*Min', sig_dict)
	max_val      = get_key_value_pair('*Max', sig_dict)
	unit         = get_key_value_pair('*Unit', sig_dict)
	receivers    = get_key_value_pair('*Receivers', sig_dict)
	if endian_type[:1] == 'L' or endian_type[:1] == 'l':
		endian_value = 1
	else:
		endian_value = 0
	if is_signed[:1] == 'U' or is_signed[:1] == 'u':
		sign_field_value = '+'
	else:
		sign_field_value = '-'
	# Handling None/none - modify this based on requirement
	# problem statemet is not clear what to do if any int value is none ?)
	receivers    = isStrNone(receivers)
	unit         = isStrNone(unit)
	sig_name     = isStrNone(sig_name)
	start_bit    = isStrNone(start_bit)
	length       = isStrNone(length)
	endian_type  = isStrNone(endian_type)
	enum_val     = isStrNone(enum_val)
	factor       = isStrNone(factor)
	offset       = isStrNone(offset)
	min_val      = isStrNone(min_val)
	max_val      = isStrNone(max_val)
	print_val = ''
	print_val += 'SG_ %s : %s|%s@%d%s (%s,%s) [%s|%s] "%s" %s' % (sig_name, start_bit, length, endian_value, sign_field_value, factor, offset, min_val, max_val, unit, receivers)
	print_val += '\n'
	#Handle if max_value is None and enum is present - Assuming atleast length or max_val present when enum is "Yes"
	if enum_val == 'yes' or enum_val == 'Yes' and max_val =='' and length != '':
		#Update max_val using length
		max_val_l = pow(2, int(length)) - 1
		max_val = str(max_val_l)
	elif enum_val == 'yes' or enum_val == 'Yes' and max_val =='' and length == '':
		print 'CSV FILE ERROR : enum is present but max_val and length is not present !!'
		sys.exit()
	return print_val, enum_val, sig_name, max_val

def sigDecodeN(valid_list, msg_name_list, sig_name_list, index, msg_id, cyclic_time):
	'''Module Level Function

	Generate/Decode signal message for current message.
	First, we calculate the length of signal messages for current message
	then we extract signal message one by one from valid list.
	1. Decode signal using dictionary
	2. If enum present, decode all enum lines and store
	3. If enum not present in current signal, decode next signal
	4. Once all signals are printed check for cyclic message
	5. If signal is cyclic, then decode/print "sendPeriod" after all the signals are printed.
	6. Print all the enum lines for current message

	Args:
		valid_list       : Contain all the valid lines as list (string)
		msg_name_list    : List (int) of indexes of main messages where they start
		sig_name_list    : List (int) of indexes of signal messages where they start
		index            : Index of current message from messages pool
		msg_id           : Message ID
		cyclic_time      : If signal is cyclic then it will have valid cyclic time in ms

	Returns:
		str              : Decoded message
	
	'''
	# print 'sigDecodeN Start ...'
	sig_start = sig_name_list[index] # Line number where signal is starting for current message
	# print 'sig_start = ', sig_start
	sig_end = msg_name_list[index+1] # Line number where signal is ending for current message
	# print 'sig_end = ', sig_end
	sig_count = sig_start + 1 # First line is "*Signal Name,*Start Bit..." discard this
	line_processed = 0;
	print_val = '' # Store final string
	print_enum_val = '' # Store enum string
	while sig_count < sig_end :
		sig_dict = dict(zip(valid_list[sig_start], valid_list[sig_count]))
		# print sig_dict
		sig_count = sig_count + 1
		p_val, enum_val, last_signal, max_val = single_sigDecode(sig_dict)
		# print p_val
		print_val += p_val
		# print print_val		
		if enum_val == 'Yes' or enum_val == 'yes':
			p_val, enum_lines = enumDecodeN(valid_list, msg_name_list, sig_name_list, sig_count, msg_id, last_signal, max_val)
			# print p_val
			# print enum_lines
			sig_count = sig_count + enum_lines
			print_enum_val += p_val
	
	p_val_period = periodDecode(msg_id, cyclic_time)
	if p_val_period:
		print_val += p_val_period

	print_val += print_enum_val
	# print print_val
	# print 'sigDecodeN End ...'
	return print_val

def convert_csv_to_dbc(input_filename, output_filename):
	'''Module Level Function

	main driver function to decode CSV file and construct DBC file

	Args:
		input_filename     : input file name to be decoded (.CSV)
		output_filename    : output file to be written (.DBC)
	
	'''
	# Do not change Below line, we are opening input file, counting msgs and closing the file
	total_msg = count_msgs(input_filename)
	# Do not change Below line, we are opening input file, counting lines and closing the file
	total_lines = get_lines(input_filename)
	# Read CSV file into Buffer - cvsbuf
	csvbuf, in_file_handle = read_into_buffer(input_filename)
	#Open file for write
	out_file_handle = openFile(output_filename)
	# Count total number of Valid lines in File (Ignore comment, ',,,,' and empty lines)
	count = 0
	# Size of list is total_msg + 1 (why +1 ? ---> to store last line number in file)
	# Maintaining list of messages (line number in File) start with '*Message Name'
	msg_name_list = [0 for i in range(total_msg+1)]
	# Maintaining list of signals (line number in File) start with '*Signal Name'
	sig_name_list = [0 for i in range(total_msg+1)]
	msg_name_id, i, j = 0, 0, 0
	#2D List to hold all rows
	#TODO : Need Optimization - Assuming file size is < RAM size of the system
	valid_row_list = [[] for x in range(total_lines)]

	for row in csvbuf:
		if is_valid_row(row):
			new_row = is_valid_row(row)
			valid_row_list.append(new_row)
			print "%d:" %(count),
			print new_row
			 	#print row
			if new_row[0:][0] == "*Message Name":
				# print row
				msg_name_list[i]  = msg_name_id
				i=i+1
			elif new_row[0:][0] == "*Signal Name":
				# print row
				sig_name_list[j]  = msg_name_id
				j=j+1
			msg_name_id = msg_name_id + 1
			count = count + 1

	print 'messages list         :', msg_name_list
	print 'signals list          :', sig_name_list

	#Update msg_name_list to get correct len for last message
	#Note : from msg_name list we can get number of row in each msgs
	for index, item in enumerate(msg_name_list):
		# msg_name_list size is total messages + 1, So, msg_name_list[index] will 0
		# only for first message and last index, here only update last list value with
		# last line number in file
		if index !=0 and msg_name_list[index] == 0:
			msg_name_list[index] = count
	print 'Updated messages list :', msg_name_list

	# Woraround as during append, empty lists are added - removing Empty List
	valid_row_list[:] = [item for item in valid_row_list if item]
	# for x in valid_row_list:
	# 	print x
	print_val = ''
	for i in range(0,(total_msg)):
		print_val = ''
		msg_id, cyclic_time, print_val_msg = msgDecode(valid_row_list, msg_name_list, sig_name_list, i)
		print_val += print_val_msg
		print_val_sig = sigDecodeN(valid_row_list, msg_name_list, sig_name_list, i, msg_id, cyclic_time)
		print_val += print_val_sig	
		if i < total_msg-1:
			print_val += '\n\n'
		print print_val
		#Write to output File
		write_to_file(out_file_handle, print_val)

	# print print_val
	#Close all the open files
	closeFile(out_file_handle)
	closeFile(in_file_handle)


def usage():
	print 'Usage :\nsolution.py -i <inputfile> -o <outputfile>\n'

def main(argv):
	input_file = ''
	output_file = ''
	try:
		options, args = getopt.getopt(argv,"hi:o:",["help","inputfile=","outputfile="])
		if not options:
			print 'Invalid Arguments'
			usage()
			sys.exit()
	except getopt.GetoptError:
		print 'Invalid Arguments'
		usage()
		sys.exit(2)
	for opt, arg in options:
		if opt in ("-h", "--help"):
			usage()
			sys.exit(0)
		elif opt in ("-i", "--inputfile"):
			input_file = arg
		elif opt in ("-o", "--outputfile"):
			output_file = arg
	if not input_file or not output_file:
		print 'Invalid Arguments'
		usage()
		sys.exit(0)
	print 'Input file is : ', input_file
	print 'Output file is : ', output_file
	#Test 1 (single msg)
	# input_file = "example.csv"
	# output_file = "example_out.dbc"
	# convert_csv_to_dbc(input_file, output_file)
	convert_csv_to_dbc(input_file, output_file)

if __name__ == "__main__":
	main(sys.argv[1:])