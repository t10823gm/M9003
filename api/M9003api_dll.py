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
g_time = 4
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
b_setting = dll.M9003Setup(hM9003, 0x08, 0x03, 0x00, g_time, 0, 0x00)
print('Setting: ', b_setting)

''' read Data
        photon countint data is obtained with this function. '''
dll.M9003ReadData.restype = c_bool
dll.M9003ReadData.argtypes = [wintypes.HANDLE, c_void_p, POINTER(wintypes.DWORD)]

# FCCS
dataBuffer = (wintypes.DWORD*2*3340)()

# FCS
#dataBuffer = (wintypes.BYTE*6680)()


"""dataLnegth value should be assigned via GUI
    dataLength value must be smaller than dataBuffer size"""
dataLength = 6000
rd = dll.M9003ReadData(hM9003, dataBuffer, byref(wintypes.DWORD(dataLength)))
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
dll.M9003GetInfo.argtypes =(wintypes.HANDLE, POINTER(c_int16))
getinfo = dll.M9003GetInfo(hM9003, byref(info))
print("GetInfo: ", getinfo)
print("info value: ", info.value)

''' close handle '''
dll.M9003Close.restype = c_bool
cl = dll.M9003Close(hM9003)
print("CloseHandle: ", cl)

''' endian '''
import sys
print("Endian of this PC: ", sys.byteorder)

''' convert data type of dataBuffer '''
#convData = cast(dataBuffer, POINTER(wintypes.DWORD))
#convData = cast(dataBuffer, POINTER(POINTER(wintypes.DWORD)))

def conv2darray(db, dlen):
    casted = cast(db, POINTER(wintypes.DWORD))
    for i in range(dlen):
        tmp = casted[i]
        x = struct.pack('<L', tmp)
        y = (struct.unpack('<BBBB', x))
        chl1.append(y[0])
        chl1.append(y[2])
        chl2.append(y[1])
        chl2.append(y[3])

def convDWORD2int(data):
    x = struct.pack('<L', data)
    y = (struct.unpack('<BBBB', x))
    return y
#hoge = [[convDWORD2int(convData[o][i]) for i in range(2)]
#            for o in range(1670)]
cha = 1
def convDWORD2int2(data, ch):
    x = struct.pack('L', data)
    if cha == 1:
        y = (struct.unpack('<xBxB', x))
    elif cha ==2:
        y = (struct.unpack('<BxBx', x))
        
    return y


def cast_2d_pointer_to_2d_list(ctype_2d_pointer_value, outer_rank, inner_rank):
    '''Cast ctypes's 2d-pointer or 2d-array to Python 2d-List
    Args:
        ctype_2d_pointer_value (POINTER(POINTER(c_types object))): 2d-pointer of c_types objects
        outer_rank (int): outer dimention of list
        inner_rank (int): inner dimention of list
    Returns:
        List(python object like c_types): Python cast list
    '''
    return [[ctype_2d_pointer_value[o][i] for i in range(inner_rank)]
            for o in range(outer_rank)]

dworddata = cast_2d_pointer_to_2d_list(dataBuffer,3340,2)