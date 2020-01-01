import numpy as np
import pandas as pd
import re
import requests
import scipy.io as sio
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
# import matplotlib.pyplot as plt
import time
import urllib.request
import json
import os
import socket

# BASE_URL = "http://localhost:8080"
BASE_URL = "http://basecamp-demos.informatik.uni-hamburg.de:8080/AirDataBackendService"


def getSensorList(time):
    fullDataUrl = BASE_URL + \
        "/api/measurements/getAllByHour/?timestamp=" + str(time)

    print(fullDataUrl)

    sensorList = []
    allMeasurements = []
    try:
        response = requests.get(fullDataUrl, timeout=120)
        allMeasurements = response.json()
    except (requests.exceptions.ReadTimeout, socket.timeout, requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
        print("Timeout or error while fetching: " + fullDataUrl)
        print(e)
        return []

    for measurement in allMeasurements:
        lat = measurement['lat']
        lon = measurement['lon']
        p10 = measurement['p10']
        p25 = measurement['p25']

        point = [lon, lat, p10, p25]
        sensorList.append(point)

    return np.array(sensorList)


def getTestData():
    mat = sio.loadmat('points.mat')
    sensorList = mat['sensorList']
    return sensorList


def filterValue(Liste, derivation):
    size = len(Liste)
    index = int(derivation*size)-1
    return np.sort(Liste)[index]


def derivationFilter(sensorL, P1der, P2der):
    P1tres = filterValue(sensorL[:, 2], P1der)
    P2tres = filterValue(sensorL[:, 3], P2der)

    size = len(sensorL[:, 2])

    P1List = []
    P2List = []

    for i in range(0, size-1):
        if(5 <= sensorL[i, 0] and sensorL[i, 0] <= 16 and 47 <= sensorL[i, 1] and sensorL[i, 1] <= 55):

            if(sensorL[i, 2] <= P1tres):
                P1List.append([sensorL[i, 0], sensorL[i, 1], sensorL[i, 2]])
            if (sensorL[i, 3] <= P2tres):
                P2List.append([sensorL[i, 0], sensorL[i, 1], sensorL[i, 3]])
    return np.array(P1List), np.array(P2List)


def interpolation(sensorList, derivP1, derivP2, sigma, saveResult, dir='P1_P2_grid'):

    grid_lat, grid_lon = np.mgrid[47:55:4001j, 5:16:2751j]

    mat_contents = sio.loadmat('germany.mat')
    Ger = mat_contents['Val']
    Ger = np.flip(Ger, 0)

    P1L, P2L = derivationFilter(sensorList, derivP1, derivP2)

    backgroundP1 = griddata(P1L[:, 0:2], P1L[:, 2],
                            (grid_lon, grid_lat), method='nearest')
    backgroundP2 = griddata(P2L[:, 0:2], P2L[:, 2],
                            (grid_lon, grid_lat), method='nearest')

    maingridP1 = griddata(P1L[:, 0:2], P1L[:, 2],
                          (grid_lon, grid_lat), method='linear')
    maingridP2 = griddata(P2L[:, 0:2], P2L[:, 2],
                          (grid_lon, grid_lat), method='linear')

    gridP1 = np.where(np.isnan(maingridP1), backgroundP1, maingridP1)
    gridP2 = np.where(np.isnan(maingridP2), backgroundP2, maingridP2)

    gridP1 = gaussian_filter(gridP1, sigma, mode='reflect')
    gridP2 = gaussian_filter(gridP2, sigma, mode='reflect')

    grid_P1 = np.multiply(Ger, gridP1)
    grid_P2 = np.multiply(Ger, gridP2)

    if(saveResult == True):
        dataDir = '{}.mat'.format(dir)
        sio.savemat(dataDir, {'grid_P1': grid_P1, 'grid_P2': grid_P2})

    return grid_P1, grid_P2


# def visualise(grid_P1, grid_P2):
#     grid_lat, grid_lon = np.mgrid[47:55:4001j, 5:16:2751j]
#     plt.subplot(121)
#     x1 = plt.contourf(grid_lon, grid_lat, grid_P1)
#     plt.colorbar(x1)

#     plt.subplot(122)
#     x2 = plt.contourf(grid_lon, grid_lat, grid_P2)
#     plt.colorbar(x2)
#     plt.show()


# make sure this part is only executed right after every full hour
# generate 5 heatmaps, starting from now
apiKey = os.environ.get('API_KEY')
now = int(time.time())

for i in range(5):
    timestamp = now + (i * 3600)
    sensorList = getSensorList(timestamp)
    print(timestamp)
    print(len(sensorList))

    if (len(sensorList) < 1):
        print("No data available 😔")
    else:
        filename = 'data-'+str(timestamp)
        # change the 5 to a higher value when there are not enough points
        grid_P1, grid_P2 = interpolation(
            sensorList, 0.975, 0.99, 5, True, dir=filename)
        with open(filename + '.mat', 'rb') as f:
            try:
                r = requests.post(BASE_URL + "/heatmap/",
                                  timeout=360,
                                  files={'file': f}, data={'apiKey': apiKey, 'timestamp': timestamp})
            except (requests.exceptions.ReadTimeout, socket.timeout, requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
                print("Timeout or error while uploading heatmap: " + filename)
                print(e)

        os.remove(filename + '.mat')
