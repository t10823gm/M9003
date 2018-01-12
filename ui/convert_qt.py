# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 14:32:07 2018

@author: maryu
"""
from PyQt5 import uic
 
fin = open('qt_ui.ui', 'r')
fout = open('qt_ui.py', 'w')
uic.compileUi(fin, fout, execute=False)
fin.close()
fout.close()