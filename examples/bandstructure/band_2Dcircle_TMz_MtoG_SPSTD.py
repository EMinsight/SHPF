#!/usr/bin/env python
import os, time, datetime, sys, psutil
import matplotlib
matplotlib.use('Agg')
import numpy as np
from mpi4py import MPI
import matplotlib.pyplot as plt
from scipy.constants import c
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import source, space2D, plotfield, structure, collector, recorder

#------------------------------------------------------------------#
#--------------------- Space object settings ----------------------#
#------------------------------------------------------------------#

savedir = '/home/ldg/2nd_paper/SHPF.cupy.diel.CPML.MPI/'

nm = 1e-9
um = 1e-6

Lx, Ly = 574*nm, 574*nm
Nx, Ny = 256, 256
dx, dy = Lx/(Nx-1), Ly/(Ny-1)

courant = 1./4
dt = courant * min(dx,dy) / c
Tsteps = int(sys.argv[2])

TF = space2D.Basic2D('TM', (Nx, Ny), (dx, dy), dt, Tsteps, np.complex64, np.complex64, method='SPSTD', engine='cupy')

TF.malloc()

########## Set PML and PBC
TF.apply_PML({'x':'', 'y':''}, 10)
TF.apply_BBC({'x':True,'y':True})
TF.apply_PBC({'x':False,'y':False})

########## Save PML data.
#TF.save_pml_parameters('./')

#------------------------------------------------------------------#
#--------------------- Source object settings ---------------------#
#------------------------------------------------------------------#

########## Gaussian source
#wvc = 200*nm
#interval = 2
#spread   = 0.3
#pick_pos = 1000
#wvlens = np.arange(100,500, interval)*nm
#freqs = c / wvlens
#np.save("../graph/freqs", freqs)
#src = source.Gaussian(dt, wvc, spread, pick_pos, dtype=np.float32)
#src.plot_pulse(Tsteps, freqs, savedir)
#wvlen = wvc 

########## Sine source
#smth = source.Smoothing(dt, 1000)
#src1 = source.Sine(dt, np.float64)
#wvlen = 250*nm
#src1.set_wvlen(wvlen)

########## Harmonic source
#smth = source.Smoothing(dt, 1000)
#src1 = source.Harmonic(dt)
#wvlen = float(sys.argv[1])*nm
#src1.set_wvlen(wvlen)

########## Delta source
src1 = source.Delta(10)
src2 = source.Delta(20)
src3 = source.Delta(50)
src4 = source.Delta(30)
#wvlen = Lz/2

########## Momentum of the source.
#wvlen = float(sys.argv[1])*nm
#k0 = 2*np.pi / wvlen
#theta = 30*np.pi/180

# mmt for plane wave normal to x axis
# theta is the angle between k0cos(phi) and x-axis.
#kx = k0 * np.cos(theta)
#ky = k0 * np.sin(theta)

# mmt for plane wave normal to y axis
# theta is the angle between k0cos(phi) and y-axis.
#kx = k0 * np.sin(theta)
#ky = k0 * np.cos(theta)

# mmt for M to G.
wvlen = float(sys.argv[1])*nm
lambx = wvlen
lamby = lambx
kx = 2*np.pi / lambx
ky = 2*np.pi / lamby
phi, theta = 0, np.arctan(lambx/lamby)

mmt = (kx, ky)
#mmt = (0, 0)

########## Line src along x-axis.
#setter1 = source.Setter(TF, (0, 200*nm, 300*nm), (Lx, 200*nm+dy, 300*nm+dz), mmt)
#setter2 = source.Setter(TF, (0, 150*nm, 100*nm), (Lx, 150*nm+dy, 100*nm+dz), mmt)
#setter3 = source.Setter(TF, (0, 300*nm, 450*nm), (Lx, 300*nm+dy, 450*nm+dz), mmt)
#setter4 = source.Setter(TF, (0, 450*nm, 196*nm), (Lx, 450*nm+dy, 196*nm+dz), mmt)

########## Line src along y-axis.
#setter1 = source.Setter(TF, (140*nm, 0), (140*nm+dx, Ly), mmt)
#setter2 = source.Setter(TF, (200*nm, 0), (410*nm+dx, Ly), mmt)
#setter3 = source.Setter(TF, (100*nm, 0), (410*nm+dx, Ly), mmt)
#setter4 = source.Setter(TF, (100*nm, 0), (410*nm+dx, Ly), mmt)

########## Point src.
setter1 = source.Setter(TF, (100*nm, 140*nm), (100*nm+dx, 140*nm+dy), mmt)
setter2 = source.Setter(TF, (200*nm, 300*nm), (200*nm+dx, 300*nm+dy), mmt)
setter3 = source.Setter(TF, (300*nm, 400*nm), (300*nm+dx, 400*nm+dy), mmt)
setter4 = source.Setter(TF, (400*nm, 220*nm), (400*nm+dx, 220*nm+dy), mmt)

#------------------------------------------------------------------#
#-------------------- Structure object settings -------------------#
#------------------------------------------------------------------#

########## Box
#srt = ( 800*um,    0*um,    0*um)
#end = (1000*um, 1280*um, 1280*um)
#box = structure.Box(TF, srt, end, 4., 1.)

########## Circle
radius = 114.8*nm
#center1 = (Lx/2, Ly/2)
center1 = ( 0, 0)
center2 = ( 0, Ly)
center3 = ( Lx, 0)
center4 = ( Lx, Ly)
#cylinder1 = structure.Cylinder(TF, 'x', radius, height, center1, 8.9, 1.)
cylinder1 = structure.Circle(TF, radius, center1, 8.9, 1.)
cylinder2 = structure.Circle(TF, radius, center2, 8.9, 1.)
cylinder3 = structure.Circle(TF, radius, center3, 8.9, 1.)
cylinder4 = structure.Circle(TF, radius, center4, 8.9, 1.)

########## Save eps, mu data.
#TF.save_eps_mu(savedir)
#sys.exit()

#------------------------------------------------------------------#
#-------------------- Collector object settings -------------------#
#------------------------------------------------------------------#

#loc1 = (120*nm, 100*nm)
#loc2 = (450*nm, 300*nm)
#loc3 = ( 90*nm, 270*nm)
#loc4 = (300*nm, 480*nm)
#loc5 = (250*nm, 250*nm)

loc1 = (420*nm, 150*nm)
loc2 = (170*nm, 170*nm)
loc3 = (200*nm, 270*nm)
loc4 = (380*nm, 220*nm)
loc5 = (280*nm, 410*nm)

filename = "MtoG/wvlen{:05d}" .format(int(round(wvlen/nm)))

fap1 = collector.FieldAtPoint("fap1", savedir+"graph/{}" .format(filename), TF, loc1, 'cupy')
fap2 = collector.FieldAtPoint("fap2", savedir+"graph/{}" .format(filename), TF, loc2, 'cupy')
fap3 = collector.FieldAtPoint("fap3", savedir+"graph/{}" .format(filename), TF, loc3, 'cupy')
fap4 = collector.FieldAtPoint("fap4", savedir+"graph/{}" .format(filename), TF, loc4, 'cupy')
fap5 = collector.FieldAtPoint("fap5", savedir+"graph/{}" .format(filename), TF, loc5, 'cupy')

#------------------------------------------------------------------#
#-------------------- Graphtool object settings -------------------#
#------------------------------------------------------------------#

# Set plotfield options
plot_per = 1000
TFgraphtool = plotfield.Graphtool(TF, 'TF', savedir)

#------------------------------------------------------------------#
#------------------------ Time loop begins ------------------------#
#------------------------------------------------------------------#

# Save what time the simulation begins.
start_time = datetime.datetime.now()

# time loop begins
for tstep in range(Tsteps):

    # At the start point
    if tstep == 0:
        TF.MPIcomm.Barrier()
        if TF.MPIrank == 0:
            print("Total time step: %d" %(TF.tsteps))
            print(("Size of a total field array : %05.2f Mbytes" %(TF.TOTAL_NUM_GRID_SIZE)))
            print("Simulation start: {}".format(datetime.datetime.now()))
        
    # pulse for gaussian wave.
    #pulse_re = src.pulse_re(tstep)

    # pulse for Sine or Harmonic wave.
    #pulse1 = src1.apply(tstep) * smth.apply(tstep)

    # pulse for Delta function wave.
    pulse1 = src1.apply(tstep)
    pulse2 = src2.apply(tstep)
    pulse3 = src3.apply(tstep)
    pulse4 = src4.apply(tstep)

    """
    setter1.put_src('Ex', pulse1, 'soft')
    setter2.put_src('Ex', pulse2, 'soft')
    setter3.put_src('Ex', pulse3, 'soft')
    setter4.put_src('Ex', pulse4, 'soft')

    setter1.put_src('Ey', pulse_re, 'soft')
    setter2.put_src('Ey', pulse_re, 'soft')
    setter3.put_src('Ey', pulse_re, 'soft')
    setter4.put_src('Ey', pulse_re, 'soft')
    """

    setter1.put_src('Ez', pulse1, 'soft')
    setter2.put_src('Ez', pulse2, 'soft')
    setter3.put_src('Ez', pulse3, 'soft')
    setter4.put_src('Ez', pulse4, 'soft')

    TF.updateH(tstep)
    TF.updateE(tstep)

    fap1.get_time_signal(tstep)
    fap2.get_time_signal(tstep)
    fap3.get_time_signal(tstep)
    fap4.get_time_signal(tstep)
    fap5.get_time_signal(tstep)

    # Plot the field profile
    if tstep % plot_per == 0:

        #Ex = TFgraphtool.gather('Ex')
        #TFgraphtool.plot2D3D(Ex, tstep, xidx=TF.Nxc, colordeep=1e-2, stride=3, zlim=1e-2)
        #TFgraphtool.plot2D3D(Ey, tstep, yidx=TF.Nyc, colordeep=1., stride=2, zlim=1.)
        #TFgraphtool.plot2D3D(Ez, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hx, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hy, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hz, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)

        #Ey = TFgraphtool.gather('Ey')
        #TFgraphtool.plot2D3D(Ex, tstep, yidx=TF.Nyc, colordeep=2., stride=1, zlim=2.)
        #TFgraphtool.plot2D3D(Ey, tstep, yidx=TF.Nyc, colordeep=1., stride=2, zlim=1.)
        #TFgraphtool.plot2D3D(Ez, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hx, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hy, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hz, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)

        #Ey = IFgraphtool.gather('Ey')
        #IFgraphtool.plot2D3D(Ex, tstep, yidx=TF.Nyc, colordeep=2., stride=1, zlim=2.)
        #IFgraphtool.plot2D3D(Ey, tstep, yidx=IF.Nyc, colordeep=2., stride=1, zlim=2.)
        #IFgraphtool.plot2D3D(Ez, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #IFgraphtool.plot2D3D(Hx, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #IFgraphtool.plot2D3D(Hy, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #IFgraphtool.plot2D3D(Hz, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)

        #Ey = SFgraphtool.gather('Ey')
        #SFgraphtool.plot2D3D(Ex, tstep, yidx=TF.Nyc, colordeep=2., stride=1, zlim=2.)
        #SFgraphtool.plot2D3D(Ey, tstep, yidx=SF.Nyc, colordeep=2., stride=1, zlim=2.)
        #SFgraphtool.plot2D3D(Ez, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #SFgraphtool.plot2D3D(Hx, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #SFgraphtool.plot2D3D(Hy, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #SFgraphtool.plot2D3D(Hz, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)

        #Ez = TFgraphtool.gather('Ez')
        #TFgraphtool.plot2D3D(Ex, tstep, xidx=TF.Nxc, colordeep=1e-2, stride=3, zlim=1e-2)
        #TFgraphtool.plot2D3D(Ey, tstep, yidx=TF.Nyc, colordeep=1., stride=2, zlim=1.)
        #TFgraphtool.plot2D3D(Ez, tstep, xidx=TF.Nxc, colordeep=1, stride=2, zlim=1)
        #TFgraphtool.plot2D3D(Hx, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hy, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)
        #TFgraphtool.plot2D3D(Hz, tstep, xidx=TF.Nxc, colordeep=.1, stride=1, zlim=.1)

        if TF.MPIrank == 0:

            interval_time = datetime.datetime.now()
            print(("time: %s, step: %05d, %5.2f%%" %(interval_time-start_time, tstep, 100.*tstep/TF.tsteps)))

#------------------------------------------------------------------#
#--------------------------- Data analysis ------------------------#
#------------------------------------------------------------------#

fap1.save_time_signal(binary=True, txt=False)
fap2.save_time_signal(binary=True, txt=False)
fap3.save_time_signal(binary=True, txt=False)
fap4.save_time_signal(binary=True, txt=False)
fap5.save_time_signal(binary=True, txt=False)

#------------------------------------------------------------------#
#------------------- Record simulation history --------------------#
#------------------------------------------------------------------#

if TF.MPIrank == 0: recording = recorder.Recorder(TF, start_time, "../record/")
