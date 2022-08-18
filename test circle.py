# -*- coding: utf-8 -*-
"""
Created on Thu Jun 16 08:40:21 2022

TITLE: 

@author: Alejandro Condori aleja
E-mail: alejandrocondori2@gmail.com
Cel-WhatsApp: +54 9 294 412 5003
"""
import numpy as np

wi = 30


mat = np.zeros((wi,wi))
# print(mat)

r = (wi-1)/2
A = np.arange(-r,r+1)**2
dists = np.sqrt(A[:,None] + A)
circ = (dists-r<0.3).astype(int)
hue = (np.abs(dists-r)<0.5).astype(int)
hue2 = (dists-r<0.3).astype(int)
print(hue2)
# print(hue2.tolist())

if wi % 2:  # impar
    ce = wi // 2
    mat[ce] = np.ones(wi)
    for i in range(ce):
        line = []
        for j in range(ce):
            if j < i:
                line += [1]
            else:
                line += [0]
        line = line[::-1] + [1] + line
        mat[i] = np.array(line)
        mat[wi-i-1] = np.array(line)
            
# print(mat)