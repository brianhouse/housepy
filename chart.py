#!/usr/bin/env python3

"""Convenience wrapper for matplotlib plotting"""

import numpy as np
import matplotlib
from mpl_toolkits import mplot3d
from matplotlib import pylab
from pylab import plt

matplotlib.rcParams['toolbar'] = 'None'
figure = plt.figure()
figure.canvas.set_window_title("")
ax = plt.axes()
plt.style.use("ggplot")
is_3d = False

def _3d(make_3d=True):
    global ax, is_3d
    if not is_3d and make_3d:
        is_3d = True
        ax = plt.axes(projection='3d')

def plot(data, scatter=False, sample_axis=False, **args):
    data = np.array(data)
    dimensions = data.shape[1]
    if sample_axis:
        data = np.column_stack((range(0, len(data)), data))
        dimensions += 1        
    if dimensions == 3:
        _3d()
    f = ax.plot if not scatter else ax.scatter
    if dimensions == 2:
        f(data[:,0], data[:,1], **args)
    if dimensions == 3:
        f(data[:,0], data[:,1], data[:,2], **args)


def show():
    # fix everything if in 3D mode
    plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)

    # also do this if in 2d mode
    if not is_3d:
        frame1 = plt.gca()
        frame1.axes.get_xaxis().set_visible(False)
        frame1.axes.get_yaxis().set_visible(False)

    figure.savefig('test2png.png', dpi=150, facecolor=figure.get_facecolor(), edgecolor='none')

    plt.show()



if __name__ == "__main__":
    pass

