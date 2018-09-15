# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:47:48 2018

@author: Gembu Maryu
"""

from ctypes import *
import numpy as np
import struct

''' load DLL '''
dll = windll.LoadLibrary('./M9003api.dll')

''' get handle '''
dll.M9003Open.restype = wintypes.HANDLE
hM9003 = dll.M9003Open()
print('GetHandle: ', hM9003)

''' Reset handle
        this process must be done before use counting board
'''
dll.M9003Reset(hM9003)

''' set parameters
        args value is referenced by M9003api.h'''
# g_time value should be assigned via GUI
g_time = 40
dll.M9003Setup.restype = c_bool
dll.M9003Setup.argtypes = [wintypes.HANDLE, wintypes.BYTE, wintypes.BYTE,
                           wintypes.BYTE, wintypes.BYTE, wintypes.BYTE, wintypes.BYTE]
'''
BOOL M9003Setup( HANDLE hM9003,
                 BYTE CountMode,
                 BYTE ChannelEnable,
                 BYTE TriggerMode,
                 BYTE GateTime,
                 BYTE NumberOfGate,
                 BYTE GateDelimiter )
Params: 
#define M9003_RECIPROCAL        0x0C
#define M9003_GATE_BYTE_DATA    0x08
#define M9003_GATE_WORD_DATA    0x09
#define M9003_CH0_ENABLE        0x01
#define M9003_CH1_ENABLE        0x02
#define M9003_CH0_CH1_ENABLE    0x03
#define M9003_EXT_TRIGGER       0x0F
#define M9003_INT_TRIGGER       0x00
#define M9003_DELIMITER_NONE    0x00
#define M9003_DELIMITER_INSERT  0x01

#define M9003_GATE_ALL          0
'''
b_setting = dll.M9003Setup(hM9003, 0x08, 0x01, 0x00, g_time, 0, 0x00)
print('Setting: ', b_setting)

''' read Data
        photon countint data is obtained with this function. '''
dll.M9003ReadData.restype = c_bool
#dll.M9003ReadData.argtypes = [wintypes.HANDLE, c_void_p, POINTER(wintypes.DWORD)]

#dataBuffer = (c_int*1670)()
dataBuffer = (wintypes.DWORD*6680)()

"""
class dBuf(Structure):
    __fields__ = [('dataBuffer', pointer(wintypes.DWORD))]
    """

# dataLnegth value should be assigned via GUI
dataLength = byref(wintypes.DWORD(1670))
#dataLength = byref(c_int(1670))
rd = dll.M9003ReadData(hM9003, dataBuffer, dataLength)
#rd = dll.M9003ReadData(hM9003, dataBuffer, dataLength)
print('ReadData: ', rd)

''' Count Stop
        this process must be done before M9003GetInfo '''
dll.M9003CountStop.restype = c_bool
cs = dll.M9003CountStop(hM9003)
print('CountStop', cs)

''' get Information
        info value indicate a leakage of data'''
info = c_int16()
dll.M9003GetInfo.restype = c_bool
# dll.M9003GetInfo.argtypes =(, c_int16)
getinfo = dll.M9003GetInfo(hM9003, byref(info))
print("GetInfo: ", getinfo)
print("info value: ", info.value)

''' close handle '''
dll.M9003Close.restype = c_bool
cl = dll.M9003Close(hM9003)
print(cl)

''' endian '''
import sys
print(sys.byteorder)

''' convert data type of dataBuffer '''
convData = cast(dataBuffer, POINTER(wintypes.DWORD))
#convData = cast(dataBuffer, POINTER(c_int))
y = []
for i in range(1670):
    x = struct.pack('L', convData[i])
    y.append(struct.unpack('<BBBB', x))
countData = [convData[i] for i in range(1670)]

