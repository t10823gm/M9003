# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:47:48 2018

@author: Gembu Maryu
"""

from ctypes import *

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
b_setting = dll.M9003Setup(hM9003, 0x08, 0x03, 0x00, g_time, 0, 0x01)
print('Setting: ', b_setting)

''' read Data
        photon countint data is obtained with this function. '''
dll.M9003ReadData.restype = c_bool
# import numpy as np
dataBuffer = (wintypes.DWORD*1670000*2)()
# dataLnegth value should be assigned via GUI
dataLength = byref(wintypes.DWORD(200000))
rd = dll.M9003ReadData(hM9003, dataBuffer, dataLength)
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

''' convert data type of dataBuffer '''
convData = cast(dataBuffer, POINTER(c_int))
countData = [convData[i] for i in range(1670000)]
# numpy array is better than list in terms of calculation speed.
