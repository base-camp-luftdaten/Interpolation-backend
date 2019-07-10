import numpy as np
import scipy.io as sio
from scipy.interpolate import griddata, SmoothBivariateSpline
import json as js

def germanyInter(interPoint,dir='00_00_0000T00_00',sP1=None,sP2=None,kxP1=3,kxP2=3,kyP1=3,kyP2=3,epsP1=None,epsP2=None):
    mat_contents = sio.loadmat('germany.mat')
    Ger = mat_contents['Val']
    Ger = np.flip(Ger, 0)
    grid_lat, grid_lon = np.mgrid[47:55:4001j,5:16:2751j]

    netP1 = SmoothBivariateSpline(interPoint[:, 0], interPoint[:, 1], interPoint[:, 2], w=None, kx=kxP1, ky=kyP1, s=sP1, bbox=[5, 16, 47, 55],eps=epsP1)
    netP2 = SmoothBivariateSpline(interPoint[:, 0], interPoint[:, 1], interPoint[:, 3], w=None, kx=kxP2, ky=kyP2, s=sP2, bbox=[5, 16, 47, 55],eps=epsP2)

    grid_P1 = netP1.ev(grid_lon, grid_lat)
    grid_P2 = netP2.ev(grid_lon, grid_lat)

    grid_P1 = np.multiply(Ger, grid_P1)
    grid_P2 = np.multiply(Ger, grid_P2)

    dataDir='{}.mat'.format(dir)

    sio.savemat(dataDir, {'grid_P1': grid_P1,'grid_P2': grid_P2})

    return grid_P1,grid_P2

def germanyInterJS(json_string,sP1J=None,sP2J=None,kxP1J=3,kxP2J=3,kyP1J=3,kyP2J=3,epsP1J=None,epsP2J=None):
    data = js.loads(json_string)
    points=np.array(data['points'])
    dirJ=data['dir']+'/'+data['timestamp']
    grid_P1,grid_P2 = germanyInter(points,dir=dirJ,sP1=sP1J,sP2=sP2J,kxP1=kxP1J,kxP2=kxP2J,kyP1=kyP1J,kyP2=kyP2J,epsP1=epsP1J,epsP2=epsP2J)
    return grid_P1,grid_P2

########################################################################
# Formatvorlage für den Json-String-Input
########################################################################

#Json-String Format:
#{
#    "timestamp": "00-00-0000T00-00",
#    "dir": "C:/Users/User/Documents/",
#    "points": [[Lon, Lat, P1, P2],[Lon, Lat, P1, P2],[Lon, Lat, P1, P2],[Lon, Lat, P1, P2],[Lon, Lat, P1, P2],[Lon, Lat, P1, P2], ...]
#}

########################################################################
# Beispiel Inputs
########################################################################

#test_points=np.array([[10, 50, 7, 10],[11, 48, 6, 9],[9, 51, 8, 11],[12, 52, 7.5, 11.5],[9.5, 50, 7, 10],[11.5, 48, 6, 9],[9.5, 51, 8, 11],[12.5, 52, 7.5, 11.5],[13, 50, 7, 10],[8.5, 48, 6, 9],[14.5, 51, 8, 11],[13, 52, 7.5, 11.5],[8, 50, 7, 10],[11.5, 54, 6, 9],[9.5, 53, 8, 11],[12.5, 52.5, 7.5, 11.5]])

#json_test_string = """
#{
#    "timestamp": "00-00-0000T00-00",
#    "dir": "C:/Users/Tom/Documents/MATLAB",
#    "points": [[10, 50, 7, 10],[11, 48, 6, 9],[9, 51, 8, 11],[12, 52, 7.5, 11.5],[9.5, 50, 7, 10],[11.5, 48, 6, 9],[9.5, 51, 8, 11],[12.5, 52, 7.5, 11.5],[13, 50, 7, 10],[8.5, 48, 6, 9],[14.5, 51, 8, 11],[13, 52, 7.5, 11.5],[8, 50, 7, 10],[11.5, 54, 6, 9],[9.5, 53, 8, 11],[12.5, 52.5, 7.5, 11.5]]
#}
#"""

########################################################################
# Beispiel Aufrufe
########################################################################

#P1,P2 = germanyInterJS(json_test_string)
#P1,P2 = germanyInter(test_points)

########################################################################
# Darstellung für Testzwecke
########################################################################

#import matplotlib.pyplot as plt

#grid_lat, grid_lon = np.mgrid[47:55:4001j,5:16:2751j]

#plt.subplot(221)
#plt.contourf(grid_lon,grid_lat,P1)
#plt.title('P1')

#plt.subplot(222)
#plt.contourf(grid_lon,grid_lat,P2)
#plt.title('P2')

#plt.show()
