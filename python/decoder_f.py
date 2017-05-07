#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
   Copyright 2017 Matthew Snowdon

   Final Year Undergraduate Project 
   BEng Electrical and Electronic Engineering
   Aston University, Birmingham, United Kingdom
 
   This is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3, or (at your option)
   any later version.
  
   This software is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
'''

from __future__ import division
from __future__ import print_function
import numpy as np
from gnuradio import gr
from ctypes import c_uint32
from time import gmtime, strftime
import pmt
import sys

data_frame = []
remaining_bits = 0
ogn_str = ""

class decoder_f(gr.sync_block):
    """
    Framer and decoder for OGN (Open Glider Network) packets. More details available on the OGN wiki. 
    """
    def __init__(self):
        gr.sync_block.__init__(self,
            name="decoder_f",
            in_sig=[np.float32],
            out_sig=None)
        timestamp = "\nReceiver started at: " + strftime("%Y-%m-%d %H:%M:%S", gmtime())
        print (timestamp)
        with open("decoder_output", "a") as output_file:			           
            output_file.write(timestamp)

    def manchester_decode(self, frame_received):	#Use the IEEE standard for Manchester decoding to process the data   
        frame_decoded_index = 0
	error_detected = False
        frame_decoded = np.zeros(len(frame_received)/2) #Two Manchester encoded bits = 1 user bit. Therefore define the output array at half the length 

        for i in xrange(0, len(frame_received), 2):				#Step through the input array, process two bits at a time     
            if (frame_received[i] == 1) and (frame_received[i+1] == 0):         
                frame_decoded[frame_decoded_index] = 0  			#1 and 0 = 0
            elif (frame_received[i] == 0) and (frame_received[i+1] == 1):
                frame_decoded[frame_decoded_index] = 1				#0 and 1 = 1
            else:
                frame_decoded[frame_decoded_index] = 0
                error_detected = True						#We've found an invalid pattern! Error detected 
            frame_decoded_index += 1
        return frame_decoded, error_detected 

    def array2dec(self, input_array):	#Used for converting bits in the Header to decimal values 
        output = input_array.astype(int)        #Convert to integer 
        output = np.array_str(output)           #Convert to string 
        output = output.translate(None, ' []')  #Remove characters left over from the array 
        output = int(output, 2)                 #Convert the string back to int 
        return output

    def bitword2hex(self, input_array):	#Used for converting 32 bit value to hex (correct format for TEA decryption)  
        before_sort = []
        after_sort = []
        output_array = np.zeros((4), dtype=np.int8)	#For processing 4 bits at a time 
       
        for i in xrange (0, 32, 4):			#Step through the input array, process 4 bits at a time 
            for p in range (0, 4): 			#Append the 4 bits to a new array 
                output_array = np.append(output_array, input_array[i+p].astype(int))
            before_sort.append(hex(np.packbits(output_array, axis=-1))[2:])	#Convert the 4 bits to a hex value, and drop the "0x" 
            output_array = np.zeros((4), dtype=np.int8)				#Reset the output array to process the next chunk 
        for i in xrange (6, -1, -2):			#Data is stored in little endian format. Need to rearrange the values (e.g. 15911B becomes 1B9115)
            for p in range (0, 2):                      #Step through the array in reverse 
                after_sort.append(before_sort[i+p])     #Move each pair of values to the beginning 
        after_sort = str(after_sort) 			#Convert to string 
        after_sort = after_sort.translate(None, ' [],\'')	#Remove characters left over from the array 
        after_sort = int("0x" + after_sort, 0)		#Rebuild the hex string and convert to int 
        return after_sort

    def decrypt_block(self, block):	#TEA decryption algorithm. Key = 0
        assert len(block) == 2
        delta = c_uint32(0x9e3779b9)		#Constant used in TEA 
        sumation = c_uint32(delta.value * 8)	#OGN implementation uses 8 loops 
        for index in range(0, 8):
            block[1].value -= (block[0].value << 4) ^ (block[0].value + sumation.value) ^ (block[0].value >> 5);
            block[0].value -= (block[1].value << 4) ^ (block[1].value + sumation.value) ^ (block[1].value >> 5);
            sumation.value -= delta.value
        return block

    def decode_position(self, frame_0, frame_1):	#Extract the latitude and longitude from the raw data 
        decrypt_input_args = (c_uint32(self.bitword2hex(frame_0)), c_uint32(self.bitword2hex(frame_1)))		#Convert raw data into hex value, ready for decryption 
        decrypt_output = self.decrypt_block(decrypt_input_args)							
        decrypt_output_hex = (format(decrypt_output[0].value, "#08x"), format(decrypt_output[1].value, "#08x")) #Format the decryption result back into hex 

        decrypt_output_lat = decrypt_output_hex[0][4:10]	#We're only interested in the last 6 bits
        decrypt_output_lat = "0x" + decrypt_output_lat + "80"	#Shift left by 8 to move the sign bit into the top bit
        decrypt_output_lat = int(decrypt_output_lat, 16)        #^ also add 8 to undo a possible rounding. Then convert string into int value (base 16 for hex) 
        if decrypt_output_lat > 0X7FFFFFFF:			#Accounts for a negative hex value 
            decrypt_output_lat -= 0X100000000
        decrypt_output_lat = decrypt_output_lat/600000/32	#Scale to provide 1.5 meter accuracy 

        decrypt_output_lon = decrypt_output_hex[1][4:10]	#Similar process again, we only want the last 6 bits
        decrypt_output_lon = "0x" + decrypt_output_lon + "80"	#Move the sign bit into top bit, undo rounding 
        decrypt_output_lon = int(decrypt_output_lon, 16)	#Convert the string into an int
        if decrypt_output_lon > 0X7FFFFFFF:			#Account for negative values
            decrypt_output_lon -= 0X100000000
        decrypt_output_lon = decrypt_output_lon/600000/16	#Scale to provide 3 meter accuracy 
        return "%.6f" % decrypt_output_lat, "%.6f" % decrypt_output_lon	#Return as floats with 6 decimal point precision

    def decode_id(self, aircraft_id):		#Convert the Aircraft ID into appropriate format 
        before_sort = hex(aircraft_id)[2:]		#Convert into hex and drop the "0x" 
        after_sort = []

        for i in xrange (4, -1, -2):			#Data is stored in little endian format. Need to rearrange the values (e.g. 15911B becomes 1B9115)
            for p in range (0, 2):			#Step through the array in reverse 
                after_sort.append(before_sort[i+p])	#Move each pair of values to the beginning 
        after_sort = str(after_sort) 			#Convert to string 
        after_sort = after_sort.translate(None, ' [],\'')	#Remove characters left over from the array 
        return after_sort

    def decode_alt(self, frame_0, frame_1):	#Convert the raw data into an altitude value in meters 
        decrypt_input_args = (c_uint32(self.bitword2hex(frame_0)), c_uint32(self.bitword2hex(frame_1)))		#Arrange the two hex words for decryption
        decrypt_output = self.decrypt_block(decrypt_input_args)							#Decrypt
        decrypt_output_hex = (format(decrypt_output[0].value, "#08x"), format(decrypt_output[1].value, "#08x"))	#Format output as hex
        decrypt_output_alt = decrypt_output_hex[0][6:10]	#We're only interested in the last 10 bits
        decrypt_output_alt = int(decrypt_output_alt, 16)	#Convert to int (base 16 as value is hex) 
        return decrypt_output_alt

    def display_result(self, frame_decoded):	#Print each packet in an easily readable format 
        global ogn_str

        """
        Print values for debugging 
 
        print ("\n")   
        print ("##### Header Field #####")
        print ("Aircraft ID: ",ac_id)         #Packet bits 1-24            
        print ("Emergency flag: ",self.array2dec(frame_decoded[24]))                       #Packet bit 25
        print ("Encryption flag: ",self.array2dec(frame_decoded[25]))                      #Packet bit 26
        print ("Relay count: ",self.array2dec(frame_decoded[26:28]))                       #Packet bits 27-28
        print ("Parity: ",self.array2dec(frame_decoded[28]))                               #Packet bit 29
        print ("Other data: ",self.array2dec(frame_decoded[29]))                           #Packet bit 30
        print ("Address type: ",self.array2dec(frame_decoded[30:32]))                      #Packet bits 31-32
        print ("Second 32 bit word: ",self.bitword2hex(frame_decoded[32:64]))              #Packet bits 33-64
        print ("Third 32 bit word: ",self.bitword2hex(frame_decoded[64:96]))               #Packet bits 65-96
        print "Fourth 32 bit word: ",self.bitword2hex(frame_decoded[96:128])               #Packet bits 97-128
        print "Fifth 32 bit word: ",self.bitword2hex(frame_decoded[128:160])               #Packet bits 129-160

        print ("##### Data Field #####")
        print ("Latitude: ",lat)
        print ("Longitude: ",lon)#
        print ("Altitude: ",alt)
	"""

        ac_id = self.decode_id(self.array2dec(frame_decoded[0:24]))			    #Decode the aircraft ID
        lat, lon = self.decode_position(frame_decoded[32:64], frame_decoded[64:96])	    #Convert the raw data to position 
        alt = self.decode_alt(frame_decoded[96:128], frame_decoded[128:160])	            #Convert raw altitude into decimal value
        output_str = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": ID: " + ac_id + " Lat: " + lat + " Lon: " + lon + " Src: OGN"
        print (output_str)								    #Format and print the aircraft information 

        with open("decoder_output", "a") as output_file:	            #Append the data to the shared log file
            output_file.write("\n" + output_str)

        ogn_str += '{"icao": "%s", "lat": "%s", "lng": "%s"},' % \
        (ac_id,
          "%s" % lat,
          "%s" % lon,
        )							#Build the OGN JSON string

        ogn_str_formatted = "[" + ogn_str			#Format the OGN data for the JSON array 
        ogn_str_formatted = ogn_str_formatted[:-1]
        ogn_str_formatted += "]" 				#Ensure entries in the JSON file are contained within square brackets, to make it an array 

        with open("ogn_json", "w") as output_file:		#Write the JSON data to the log file, overwrite previous data
            output_file.write(ogn_str_formatted)	

    def tag_detect(self, in0):		#Detect if a tag is present
        global remaining_bits		#Number of bits needed to fill the data_frame - since this could take multiple work loop iterations this needs to be global 
        nread = self.nitems_read(0)	#Index of number of samples read

        for tag in self.get_tags_in_window(0, 0, len(in0), pmt.intern("ogn_sync")):
            offset_start = tag.offset - nread			#Define the start and end of the packet
            data_packet = in0[offset_start:offset_start+320]
            remaining_bits = 320 - len(data_packet)		#Update the number of remaining bits required 
            return data_packet 
            
    def work(self, input_items, output_items):
        global remaining_bits
        global data_frame
        in0 = input_items[0]

        if (remaining_bits > 0):						#If we still need more bits to capture the entire data packet
            data_frame = np.append(data_frame, in0[0:remaining_bits])		#Then append on the appropriate amount of bits to the data_frame 
            remaining_bits = 320 - len(data_frame)				#Update the number of remaining bits required 
        elif (remaining_bits == 0):                      
            data_frame = self.tag_detect(in0)					#We have not yet found a packet, so look for a tag 
        if data_frame is not None:						#If we have data in the data frame
            if len(data_frame) == 320:					        #And the number of bits is correct (320 = OGN data packet length) 
                data_frame, decoding_error = self.manchester_decode(data_frame) #Try Manchester Decoding 
                if (decoding_error == False):                                   #If we didn't encounter any errors 
                    self.display_result(data_frame) 				#Then we've got a full packet! Display the results 
                    data_frame = []						#Reset the data frame for the next packet 
        return len(input_items[0])
