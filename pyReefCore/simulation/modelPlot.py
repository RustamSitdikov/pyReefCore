##~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~##
##                                                                                   ##
##  This file forms part of the pyReefCore synthetic coral reef core model app.      ##
##                                                                                   ##
##  For full license and copyright information, please refer to the LICENSE.md file  ##
##  located at the project root, or contact the authors.                             ##
##                                                                                   ##
##~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~##
"""
Here we set plotting functions used to visualise pyReef dataset.
"""

import matplotlib
import numpy as np
import pandas as pd
from matplotlib import gridspec
import matplotlib.pyplot as plt

from scipy.ndimage.filters import gaussian_filter
from matplotlib.ticker import FormatStrFormatter

import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)

class modelPlot():
    """
    Class for plotting outputs from pyReef model.
    """

    def __init__(self, input=None):
        """
        Constructor.
        """

        self.names = np.empty(input.speciesNb+1, dtype="S14")
        self.names[:input.speciesNb] = input.speciesName
        self.names[-1] = 'silicilastic'
        self.step = int(input.laytime/input.tCarb)
        self.pop = None
        self.timeCarb = None
        self.depth = None
        self.accspace = None
        self.karstero = None
        self.timeLay = None
        self.surf = None
        self.sedH = None
        self.sealevel = None
        self.tecinput = None
        self.mbsl = None
        self.sedinput = None
        self.waterflow = None
        self.pH = None
        self.temperature = None
        self.nutrient = None
        self.folder = input.outDir

        return

    def two_scales(self, ax1, time, data0, data1, c1, c2, font):
        """

        Parameters
        ----------
        ax : axis
            Axis to put two scales on

        time : array-like
            x-axis values for both datasets

        data1: array-like
            Data for left hand scale

        data2 : array-like
            Data for right hand scale

        c1 : color
            Color for line 1

        c2 : color
            Color for line 2

        Returns
        -------
        ax : axis
            Original axis
        ax2 : axis
            New twin axis
        """
        ax2 = ax1.twinx()

        ax1.plot(time, data0, color=c1, linewidth=3)
        ax1.set_xlabel('Time [y]',size=font+2)
        ax1.set_ylabel('accommodation space [m]',size=font+2)
        ax1.yaxis.label.set_color(c1)

        ax2.plot(time, data1, color=c2, linewidth=3)
        ax2.set_ylabel('core elevation [m]',size=font+2)
        ax2.yaxis.label.set_color(c2)

        return ax1, ax2

    def two_scales2(self, ax1, time, data0, data1, c1, c2, font):
        """

        Parameters
        ----------
        ax : axis
            Axis to put two scales on

        time : array-like
            x-axis values for both datasets

        data1: array-like
            Data for left hand scale

        data2 : array-like
            Data for right hand scale

        c1 : color
            Color for line 1

        c2 : color
            Color for line 2

        Returns
        -------
        ax : axis
            Original axis
        ax2 : axis
            New twin axis
        """
        ax2 = ax1.twinx()

        ax1.plot(time, data0, color=c1, linewidth=3)
        ax1.set_xlabel('Time [y]',size=font+2)
        ax1.set_ylabel('cumulative thickness [m]',size=font+2)
        ax1.yaxis.label.set_color(c1)

        ax2.plot(time, data1, color=c2, linewidth=3) #, linestyle='--')
        ax2.set_ylabel('growth rate [mm/y]',size=font+2)
        ax2.yaxis.label.set_color(c2)

        return ax1, ax2

    def color_y_axis(self, ax, color):
        """Color your axes."""
        for t in ax.get_yticklabels():
            t.set_color(color)

        return None

    def accommodationTime(self, colors=None, size=(10,5), font=9, dpi=80, fname=None):
        """
        This function estimates the accommodation space through time.

        Parameters
        ----------

        variable : colors
            Matplotlib color map to use

        variable : size
            Figure size

        variable : font
            Figure font size

        variable : dpi
            Figure resolution

        variable : fname
            Save PNG filename.
        """

        matplotlib.rcParams.update({'font.size': font})

        if colors is not None:
            c1 = colors[0]
            c2 = colors[-1]
        else:
            c2 = '#1f77b4'
            c1 = '#229649'

        # Define figure size
        fig, ax = plt.subplots(1,figsize=size, dpi=dpi)
        ax.set_facecolor('#f2f2f3')
        tmp = self.mbsl[:-2]-self.accspace[:-2]
        tmp2 = np.ediff1d(tmp)

        ax1, ax2 = self.two_scales(ax,self.timeCarb[:-2],self.accspace[:-2],tmp,c1,c2,font)

        # Plotting curves
        #ax.plot(self.timeCarb[:-2], self.accspace[:-2], linewidth=3,c=colors)
        #ax.plot(self.timeCarb[:-2], tmp, linewidth=3,c=colors)
        #plt.xlabel('Time [y]',size=font+2)
        #plt.ylabel('accommodation space [m]',size=font+2)

        ttl = ax.title
        ttl.set_position([.5, 1.05])
        plt.title('Accommodation space & core elevation through time',size=font+3)

        self.color_y_axis(ax1, c1)
        self.color_y_axis(ax2, c2)
        ax2.plot(self.timeLay, self.sealevel, linewidth=2, c='#4badf2', linestyle='--', label='sealevel', zorder=0)

        plt.xlim(self.timeCarb.min(), self.timeCarb.max())

        # Legend, title and labels
        lgd = ax2.legend(frameon=False,bbox_to_anchor=(1.14, 1.05))
        plt.setp(lgd.get_texts(), color='#4badf2', fontsize=font+1)
        plt.grid()
        plt.show()

        if fname is not None:
            name = self.folder+'/'+fname
            fig.savefig(name, bbox_inches='tight')

        # Define figure size
        fig, ax = plt.subplots(1,figsize=size, dpi=dpi)
        ax.set_facecolor('#f2f2f3')

        # Plotting curves
        #ax.plot(self.timeCarb[:-2], d, linewidth=3,c='#2ca02c')
        sedh = np.sum(self.sedH,axis=0)
        sedhcoral = np.sum(self.sedH[:-1,:],axis=0)
        rate = sedhcoral*1000./(self.timeLay[1]-self.timeLay[0])
        ax1, ax2 = self.two_scales2(ax,self.timeLay,np.cumsum(sedh),rate,c1,c2,font)


        ttl = ax.title
        ttl.set_position([.5, 1.05])
        plt.title('Core cumulative thickness & production rate through time',size=font+3)

        self.color_y_axis(ax1, c1)
        self.color_y_axis(ax2, c2)
        # plt.xlabel('Time [y]',size=font+2)
        # plt.ylabel('Core thickness [m]',size=font+2)
        # ax.yaxis.label.set_color('#2ca02c')
        plt.xlim(self.timeCarb.min(), self.timeCarb.max())

        # Legend, title and labels
        plt.grid()
        plt.show()

        if fname is not None:
            name = self.folder+'/prodvsdepth-'+fname
            fig.savefig(name, bbox_inches='tight')

        return

    def communityTime(self, colors=None, size=(10,5), font=9, dpi=80, fname=None):
        """
        This function estimates the coral growth based on newly computed population.

        Parameters
        ----------

        variable : colors
            Matplotlib color map to use

        variable : size
            Figure size

        variable : font
            Figure font size

        variable : dpi
            Figure resolution

        variable : fname
            Save PNG filename.
        """

        matplotlib.rcParams.update({'font.size': font})

        # Define figure size
        fig, ax = plt.subplots(1,figsize=size, dpi=dpi)
        ax.set_facecolor('#f2f2f3')

        # Plotting curves
        for s in range(len(self.pop)):
            ax.plot(self.timeCarb, self.pop[s,:], label=self.names[s],linewidth=3,c=colors[s])

        # Legend, title and labels
        plt.grid()
        lgd = plt.legend(frameon=False,loc=4,prop={'size':font+1}, bbox_to_anchor=(1.2,-0.02))
        plt.xlabel('Time [y]',size=font+2)
        plt.ylabel('Population',size=font+2)
        plt.ylim(0., int(self.pop.max())+1)
        plt.xlim(self.timeCarb.min(), self.timeCarb.max())


        ttl = ax.title
        ttl.set_position([.5, 1.05])
        plt.title('Evolution of community populations with time',size=font+3)
        plt.show()

        if fname is not None:
            name = self.folder+'/'+fname
            fig.savefig(name, bbox_extra_artists=(lgd,), bbox_inches='tight')

        return

    def communityDepth(self, colors=None, size=(10,5), font=9, dpi=80, fname=None):
        """
        Variation of coral growth with depth

        Parameters
        ----------

        variable : colors
            Matplotlib color map to use

        variable : size
            Figure size

        variable : font
            Figure font size

        variable : dpi
            Figure resolution

        variable : fname
            Save PNG filename.
        """

        matplotlib.rcParams.update({'font.size': font})

        # Define figure size
        fig, ax = plt.subplots(1,figsize=size, dpi=dpi)
        ax.set_facecolor('#f2f2f3')

        # Plotting curves
        bottom = self.surf + self.depth.sum()
        d = bottom - np.cumsum(self.depth)
        for s in range(len(self.pop)):
            ax.plot(d, self.pop[s,::self.step], label=self.names[s],linewidth=3,c=colors[s])

        # Legend, title and labels
        plt.grid()
        lgd = plt.legend(frameon=False,loc=4,prop={'size':font+1}, bbox_to_anchor=(1.2,-0.02))
        plt.xlabel('Depth [m]',size=font+2)
        plt.ylabel('Population',size=font+2)
        plt.ylim(0., int(self.pop.max())+1)
        plt.xlim(d.max(), d.min())

        ttl = ax.title
        ttl.set_position([.5, 1.05])
        plt.title('Evolution of communities population with depth',size=font+3)
        plt.show()

        if fname is not None:
            name = self.folder+'/'+fname
            fig.savefig(name, bbox_extra_artists=(lgd,), bbox_inches='tight')

        return

    def drawCore(self, depthext = None, thext = None, propext = [0.,1.], tstep = 10, lwidth = 3,
                 colsed=None, coltime=None, size=(8,10), font=8, dpi=80, figname=None,
                 filename = None, sep = '\t'):
        """
        Plot core evolution

        Parameters
        ----------

        variable : depthext
            Core depth extension to plot [m]

        variable : thext
            Core thickness range to plot [m]

        variable : propext
            Core ranging proportion to plot between [0,1.]

        variable : tstep
            Steps used to output time layer intervals

        variable : lwidth
            Figure lines width

        variable : colsed
            Matplotlib color map to use for production plots

        variable : coltime
            Matplotlib color map to use for time layer plots

        variable : size
            Figure size

        variable : font
            Figure font size

        variable : dpi
            Figure resolution

        variable : figname
            Save gigure (the type of file needs to be provided e.g. .png or .pdf).

        variable : filename
            Save model output to a CSV file.

        variable : sep
            Separator used in the CSV file.
        """

        p1 = self.sedH[:,:-1]
        ids = np.where(self.depth[:-1]>0)[0]
        p2 = np.zeros((self.sedH.shape))
        p3 = np.zeros((self.sedH.shape))
        p6 = self.karstero[:-1]
        p2[:,ids] = self.sedH[:,ids]/self.depth[ids]
        p3[:,ids] = np.cumsum(self.sedH[:,ids]/self.depth[ids],axis=0)
        bottom = self.surf + self.depth[:-1].sum()
        d = bottom - np.cumsum(self.depth[:-1])
        facies = np.argmax(p1, axis=0)

        if thext == None:
            thext = [0.,p1.max()]

        if depthext == None:
            depthext = [self.surf,bottom-self.depth[0]]


        colsed[len(self.sedH)-1]=np.array([244./256.,164/256.,96/256.,1.])

        # Define figure size
        fig = plt.figure(figsize=size, dpi=dpi)
        gs = gridspec.GridSpec(1,21)
        ax1 = fig.add_subplot(gs[:5])
        ax2 = fig.add_subplot(gs[5:10], sharey=ax1)
        ax3 = fig.add_subplot(gs[10:15], sharey=ax1)
        ax6 = fig.add_subplot(gs[15:17], sharey=ax1)
        ax42 = fig.add_subplot(gs[17:19], frame_on=False)
        ax4 = fig.add_subplot(gs[17:19], sharey=ax1)
        ax52 = fig.add_subplot(gs[19:21], frame_on=False)
        ax5 = fig.add_subplot(gs[19:21], sharey=ax1)
        ax3.set_facecolor('#f2f2f3')
        ax4.set_facecolor('#f2f2f3')
        ax5.set_facecolor('#f2f2f3')
        x = np.zeros(2)
        y = np.zeros(2)
        x[0] = 0.
        x[1] = 1.
        old = np.zeros(2)
        old[0] = bottom
        old[1] = bottom

        # Plotting curves
        for s in range(len(self.sedH)):
            ax1.plot(p1[s,:], d, label=self.names[s], linewidth=lwidth, c=colsed[s])
            ax2.plot(p2[s,:-1], d, label=self.names[s], linewidth=lwidth, c=colsed[s])
            if s == 0:
                ax3.fill_betweenx(d, 0, p3[s,:-1], color=colsed[s])
            else:
                ax3.fill_betweenx(d, p3[s-1,:-1], p3[s,:-1], color=colsed[s])
            ax3.plot(p3[s,:-1], d, 'w--', label=self.names[s], linewidth=lwidth-2)

        ax6.plot(p6, d, linewidth=lwidth-1, c='#6349d2')

        tmpx = np.zeros(len(d))
        tmpx[-1] = 1
        ax42.plot(tmpx, d, zorder=1)
        ax42.yaxis.tick_right()
        ax52.plot(tmpx, d, zorder=1)
        ax52.yaxis.tick_right()
        ticks = []
        ttime = []
        p = 0
        for s in range(len(d)):
            y[0] = d[s]
            y[1] = d[s]
            ax4.fill_between(x, old, y, color=coltime[s], zorder=10)
            ax5.fill_between(x, old, y, color=colsed[facies[s]], zorder=10)
            old[0] = y[0]
            old[1] = y[1]
            p += 1
            ax4.plot(x,y,'k', zorder=10,linewidth=0.25)
            if p == tstep:
                # if len(ticks)>0:
                #     print len(ticks),ticks[-1],y[1]
                # ticks.append(y[1])
                # ttime.append(int(self.timeLay[s+1]))
                # ax4.plot(x,y,'k', zorder=10,linewidth=1)
                # ax5.plot(x,y,'k', zorder=10,linewidth=1)
                if len(ticks) > 0:
                    if ticks[-1] > y[1]:
                        ticks.append(y[1])
                        ttime.append((self.timeLay[s+1]/1000.))
                        ax4.plot(x,y,'#db20bf', zorder=10,linewidth=3)
                        ax5.plot(x,y,'#db20bf', zorder=10,linewidth=3)
                else:
                    ticks.append(y[1])
                    ttime.append((self.timeLay[s+1]/1000.))
                    # ttime.append(int(self.timeLay[s+1]))
                    ax4.plot(x,y,'#db20bf', zorder=10,linewidth=3)
                    ax5.plot(x,y,'#db20bf', zorder=10,linewidth=3)
                p = 0

        ax42.set_yticks(ticks)
        ax42.set_yticklabels(ttime, minor=False, fontsize=font, rotation=90, va='center')
        ax52.set_yticks(ticks)
        ax52.set_yticklabels(ttime, minor=False, fontsize=font, rotation=90, va='center')

        # Legend, title and labels
        ax1.grid()
        ax2.grid()
        ax3.grid()
        ax6.grid()
        ax42.get_xaxis().set_visible(False)
        ax4.get_xaxis().set_visible(False)
        ax52.get_xaxis().set_visible(False)
        ax5.get_xaxis().set_visible(False)
        lgd = ax1.legend(frameon=False, loc=1, prop={'size':font+1}, bbox_to_anchor=(6.2,0.2))
        ax1.locator_params(axis='x', nbins=5)
        ax2.locator_params(axis='x', nbins=5)
        ax3.locator_params(axis='x', nbins=5)
        ax6.locator_params(axis='x', nbins=3)
        ax1.locator_params(axis='y', nbins=10)

        # Axis
        ax1.set_ylabel('Depth below present mean sea-level [m]', size=font+4)
        ax1.set_ylim(depthext[1], depthext[0])
        ax1.set_xlim(thext[0], thext[1]+thext[1]*0.1)
        ax2.set_ylim(depthext[1], depthext[0])
        ax2.set_xlim(propext[0], propext[1])
        ax3.set_ylim(depthext[1], depthext[0])
        ax6.set_ylim(depthext[1], depthext[0])
        ax42.set_ylim(depthext[1], depthext[0])
        ax4.set_ylim(depthext[1], depthext[0])
        ax52.set_ylim(depthext[1], depthext[0])
        ax5.set_ylim(depthext[1], depthext[0])
        ax3.set_xlim(0., 1.)
        ax6.set_xlim(-0.1, p6.max()+0.1)
        ax1.xaxis.tick_top()
        ax2.xaxis.tick_top()
        ax3.xaxis.tick_top()
        ax6.xaxis.tick_top()
        ax1.tick_params(axis='y', pad=5)
        ax42.tick_params(axis='y', pad=5)
        ax52.tick_params(axis='y', pad=5)
        ax5.tick_params(axis='y', pad=5)
        ax5.yaxis.set_label_position('right')
        ax1.tick_params(axis='x', pad=5)
        ax2.tick_params(axis='x', pad=5)
        ax3.tick_params(axis='x', pad=5)
        ax6.tick_params(axis='x', pad=5)

        # Title
        tt1 = ax1.set_title('Thickness [m]', size=font+3)
        tt2 = ax2.set_title('Proportion', size=font+3)
        tt3 = ax3.set_title('Strat.\nabundance', size=font+3)
        tt6 = ax6.set_title('Karst. [m]', size=font+3)
        tt4 = ax4.set_title('Time\nlayers', size=font+3)
        tt5 = ax5.set_title('Bio.\nfacies', size=font+3)
        tt1.set_position([.5, 1.025])
        tt2.set_position([.5, 1.025])
        tt3.set_position([.5, 1.025])
        tt6.set_position([.5, 1.025])
        tt4.set_position([.5, 1.025])
        tt5.set_position([.5, 1.025])
        fig.tight_layout()
        plt.tight_layout()
        plt.figtext(1.01, 0.3, 'Two last cores axes \nleft: depth [m] \nright:time [ky]',horizontalalignment='left', fontsize=font+1)
        plt.show()


        if figname is not None:
            name = self.folder+'/'+figname
            fig.savefig(name, bbox_extra_artists=(lgd,), bbox_inches='tight')
            print 'Figure has been saved in',name

        # Define figure size
        fig = plt.figure(figsize=size, dpi=dpi)
        gs = gridspec.GridSpec(1,12)
        ax1 = fig.add_subplot(gs[:3])
        ax2 = fig.add_subplot(gs[3:6], sharey=ax1)
        ax3 = fig.add_subplot(gs[6:9], sharey=ax1)
        ax4 = fig.add_subplot(gs[9:12], sharey=ax1)

        ax1.plot(self.sealevel, self.timeLay, linewidth=lwidth, c='slateblue')
        ax2.plot(self.waterflow, self.timeLay, linewidth=lwidth, c='darkcyan')
        ax3.plot(self.sedinput, self.timeLay, linewidth=lwidth, c='sandybrown')
        ax4.plot(self.tecinput*1000., self.timeLay, linewidth=lwidth, c='limegreen')

        ax1.set_ylabel('Simulation time [y]', size=font+4)
        ax1.set_ylim(self.timeLay.min(), self.timeLay.max())
        ax2.set_ylim(self.timeLay.min(), self.timeLay.max())
        ax3.set_ylim(self.timeLay.min(), self.timeLay.max())
        ax4.set_ylim(self.timeLay.min(), self.timeLay.max())
        ax1.set_facecolor('#f2f2f3')
        ax2.set_facecolor('#f2f2f3')
        ax3.set_facecolor('#f2f2f3')
        ax4.set_facecolor('#f2f2f3')
        ax1.locator_params(axis='x', nbins=5)
        ax2.locator_params(axis='x', nbins=5)
        ax3.locator_params(axis='x', nbins=5)
        ax4.locator_params(axis='x', nbins=4)

        ax2.get_yaxis().set_visible(False)
        ax3.get_yaxis().set_visible(False)
        ax4.get_yaxis().set_visible(False)

        # Title
        tt1 = ax1.set_title('Sea-level [m]', size=font+3)
        tt2 = ax2.set_title('Water flow [m/s]', size=font+3)
        tt3 = ax3.set_title('Sediment input [m/d]', size=font+3)
        tt4 = ax4.set_title('Tectonic rate [mm/y]', size=font+3)
        tt1.set_position([.5, 1.01])
        tt2.set_position([.5, 1.01])
        tt3.set_position([.5, 1.01])
        tt4.set_position([.5, 1.01])
        fig.tight_layout()
        plt.tight_layout()
        plt.show()
        if figname is not None:
            name = self.folder+'/envi'+figname
            fig.savefig(name, bbox_extra_artists=(lgd,), bbox_inches='tight')
            print 'Figure has been saved in','envi'+name
        print ''

        if filename is not None:
            tmp = np.column_stack((d.T,p1.T))
            tmp1 = np.column_stack((tmp,p2[:,:-1].T))
            tmp2 = np.column_stack((tmp1,p3[:,:-1].T))
            tmp3 = np.column_stack((tmp2,self.sealevel[:-1].T))
            tmp4 = np.column_stack((tmp3,self.waterflow[:-1].T))
            tmp5 = np.column_stack((tmp4,self.sedinput[:-1].T))
            tmp6 = np.column_stack((tmp5,self.tecinput[:-1].T))
            tmp7 = np.column_stack((tmp6,p6.T))

            cols = []
            cols.append('depth')
            for s in range(len(self.names)):
                cols.append('th_'+self.names[s])
            for s in range(len(self.names)):
                cols.append('prop_'+self.names[s])
            for s in range(len(self.names)):
                cols.append('acc_'+self.names[s])
            cols.append('sealevel')
            cols.append('waterflow')
            cols.append('sedinput')
            cols.append('tecrate')
            cols.append('karstification')

            df = pd.DataFrame(tmp7)
            df.columns = cols
            name = self.folder+'/'+filename
            df.to_csv(name, sep=sep, encoding='utf-8', index=False)
            print 'Model results have been saved in',name

        return
