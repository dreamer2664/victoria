"""Maintenance-scale additions to the existing connected plant.
No crank/rod/shaft/propeller/pipe-network datum is altered for decoration.
"""
import math
import numpy as np
from meshkit import *
from shipdesign.leonidas_ii import BOILER_XS,BOILER_YS,ENGINE_XS


def build():
 # Bolted identification plates on real flat furnace fronts. Roman bars
 # are geometry, not invented maker's marks or a fake certification label.
 for row,x in enumerate(BOILER_XS):
  m=Mesh()
  for j,y in enumerate(BOILER_YS):
   yy=y+1.27;zz=5.05;m.box((x-1.813,yy,zz),(.034,.31,.14),'Brass',.005)
   for n in range(row+1):m.rod((x-1.831,yy-.075+n*.070,zz-.035),(x-1.831,yy-.075+n*.070,zz+.035),.006,'Black',6)
   for dy in (-.13,.13):
    for dz in (-.05,.05):m.cylinder((x-1.832,yy+dy,zz+dz),.007,.009,'Steel',7,(1,0,0))
  m.emit('Boiler_Row_'+str(row+1)+'_Fastened_Plates',collection('Boilers'),kind='boiler',deck='machinery',room=['E_Boilers_A','E_Boilers_M','E_Boilers_F'][row])
 m=Mesh()
 for i,x in enumerate(ENGINE_XS):
  m.box((x,-2.786,1.84),(.36,.026,.18),'Brass',.008)
  for dx in (-.15,.15):
   for dz in (-.06,.06):m.cylinder((x+dx,-2.805,1.84+dz),.008,.014,'Steel',7,(0,1,0))
  for j in range(i+1):m.rod((x-.07+j*.065,-2.802,1.80),(x-.07+j*.065,-2.802,1.88),.006,'Black',6)
 m.emit('Engine_CastBed_Fastened_Identification',collection('Engine'),kind='engine',deck='machinery',room='E_Engine')
 # Oil cups are seated in actual bearing crowns, not arbitrary points in
 # the aisle. Steam-service hangers intersect both roof and pipe bands.
 m=Mesh()
 for x in np.arange(-67,-28,5.):
  m.lathe((float(x)+.9,0,3.365),[(0,.025),(.025,.03),(.055,.043),(.14,.044),(.16,.025)],'Brass',12)
  m.cylinder((float(x)+.9,0,3.535),.03,.02,'Brass',10)
 for x in (-65.,-53.,-41.,-29.):
  m.cylinder((x,1.15,4.670),.055,.022,'Iron',12)
  m.rod((x,1.15,4.669),(x,1.15,4.555),.010,'Iron',8)
  m.ring((x,1.15,4.5),.052,.010,'Iron',16,6,(1,0,0))
 for x in (-61.,-42.):
  m.box((x,1.472,2.74),(.34,.028,.13),'Brass',.005)
  for dx in (-.14,.14):m.cylinder((x+dx,1.452,2.74),.007,.012,'Iron',7,(0,1,0))
  for dx in (-.08,0,.08):m.box((x+dx,1.454,2.74),(.035,.009,.055),'Black')
 m.emit('ShaftAlley_Lubricators_And_RealPipeHangers',collection('ShaftAlley'),kind='equipment',deck='machinery',room='E_Alley')
