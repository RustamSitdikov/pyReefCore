##~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~##
##                                                                                   ##
##  This file forms part of the pyReefCore synthetic coral reef core model app.      ##
##                                                                                   ##
##  For full license and copyright information, please refer to the LICENSE.md file  ##
##  located at the project root, or contact the authors.                             ##
##                                                                                   ##
##~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~#~##
"""
This module builds the core records through time based on coral species evolution and
the interactions between the active forcing paramters.
"""
import os
import numpy
import pandas as pd
import skfuzzy as fuzz

import matplotlib
from matplotlib import gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

class coreData:
    """
    This class defines the core parameters
    """

    def __init__(self, input = input):
        """
        Constructor.
        """

        self.dt = input.tCarb

        # Initial core depth
        self.topH = input.depth0

        # Production rate for each carbonate
        self.prod = input.speciesProduction
        self.names = input.speciesName

        # Core parameters size based on layer number
        self.layNb = int((input.tEnd - input.tStart)/input.laytime)+1
        self.thickness = numpy.zeros(self.layNb,dtype=float)
        self.coralH = numpy.zeros((input.speciesNb+1,self.layNb),dtype=float)
        self.karstero = numpy.zeros(self.layNb,dtype=float)

        # Diagonal part of the community matrix (coefficient ii)
        self.communityMatrix = input.communityMatrix
        self.alpha = input.communityMatrix.diagonal()
        self.layTime = numpy.arange(input.tStart, input.tEnd+input.laytime, input.laytime)
        self.sealevel = numpy.zeros(len(self.layTime),dtype=float)
        self.sedinput = numpy.zeros(len(self.layTime),dtype=float)
        self.tecrate = numpy.zeros(len(self.layTime),dtype=float)
        self.waterflow = numpy.zeros(len(self.layTime),dtype=float)
        self.nutrient = numpy.zeros(len(self.layTime),dtype=float)
        self.temperature = numpy.zeros(len(self.layTime),dtype=float)
        self.pH = numpy.zeros(len(self.layTime),dtype=float)
        self.waterflow = numpy.zeros(len(self.layTime),dtype=float)
        self.prodscale = input.prodscale

        # Shape functions
        self.seaOn = input.seaOn
        self.edepth = numpy.array([[0.,0.,1000.,1000.],]*input.speciesNb)
        if input.seaOn:
            self.edepth = input.enviDepth
        self.flowOn = input.flowOn
        self.eflow = numpy.array([[0.,0.,5000.,5000.],]*input.speciesNb)
        if input.flowOn:
            self.eflow = input.enviFlow
        self.sedOn = input.sedOn
        self.esed = numpy.array([[0.,0.,500.,500.],]*input.speciesNb)
        if input.sedOn:
            self.esed = input.enviSed

        # Environmental forces functions
        self.seatime = None
        self.sedtime = None
        self.flowtime = None
        self.seaFunc = input.sedfile
        self.sedFunc = input.sedfunc
        self.flowFunc = input.flowfunc
        self.sedfctx = None
        self.sedfcty = None
        self.flowfctx = None
        self.flowfcty = None
        self.folder = input.outDir

        return

    def _plot_fuzzy_curve(self, xd, xs, xf, dtrap, strap, ftrap, size,
                          dpi, font, colors, width, fname):

        matplotlib.rcParams.update({'font.size': font})

        for s in range(len(self.names)):
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=size, sharey=True, dpi=dpi)
            ax1.set_facecolor('#f2f2f3')
            ax2.set_facecolor('#f2f2f3')
            ax3.set_facecolor('#f2f2f3')
            fig.tight_layout()
            ax1.grid()
            ax2.grid()
            ax3.grid()
            ax1.plot(xd, dtrap[s], linewidth=width, label=self.names[s],c=colors[s])
            ax2.plot(xs, strap[s], linewidth=width, label=self.names[s],c=colors[s])
            ax3.plot(xf, ftrap[s], linewidth=width, label=self.names[s],c=colors[s])
            ax1.set_ylabel('Proportion max. vertical \n accretion rate factor',size=font+3)
            ax1.set_ylim(-0.1, 1.1)
            ax1.set_xlabel('Water Depth [m]',size=font+2)
            ax3.set_xlabel('Flow Velocity [m/s]',size=font+2)
            ax3.set_ylim(-0.1, 1.1)
            ax2.set_xlabel('Sediment Input [m/d]',size=font+2)
            ax2.set_ylim(-0.1, 1.1)
            ax3.yaxis.set_label_position("right")
            ax3.set_ylabel(self.names[s],size=font+3,fontweight='bold')
            plt.show()
            if fname is not None:
                names = self.folder+'/'+self.names[s]+fname
                fig.savefig(names, bbox_inches='tight')

        return

    def initialSetting(self, font=8, size=(8,2.5), size2=(8,3.5), width=3, dpi=80, fname=None):
        """
        Visualise the initial conditions of the model run.

        Parameters
        ----------
        variable : font
            Environmental shape figures font size

        variable : size
            Environmental shape figures size

        variable : size2
            Environmental function figures size

        variable : width
            Environmental shape figures line width

        variable : dpi
            Figure resolution

        variable : fname
            Save filename.
        """

        from matplotlib.cm import terrain
        nbcolors = len(self.names)+3
        colors = terrain(numpy.linspace(0, 1, nbcolors))

        print 'Community matrix aij representing the interactions between communities:'
        print ''
        cols = []
        ids = []
        for i in range(len(self.names)):
            cols.append('a'+str(i))
            ids.append('a'+str(i)+'j')
        df = pd.DataFrame(self.communityMatrix, index=ids)
        df.columns = cols
        print df
        print ''
        print 'Communities maximum production rates [m/y]:'
        print ''
        index = [self.names]
        df = pd.DataFrame(self.prod,index=index)
        df.columns = ['Prod.']
        print df
        print ''
        print 'Environmental trapezoidal shape functions:'

        # Visualise fuzzy production curve
        xs = numpy.linspace(0, self.esed.max(), num=201, endpoint=True)
        xf = numpy.linspace(0, self.eflow.max(), num=201, endpoint=True)
        xd = numpy.linspace(0, self.edepth.max(), num=201, endpoint=True)
        dtrap = []
        strap = []
        ftrap = []
        for s in range(0,len(self.names)):
            dtrap.append(fuzz.trapmf(xd, self.edepth[s,:]))
            strap.append(fuzz.trapmf(xs, self.esed[s,:]))
            ftrap.append(fuzz.trapmf(xf, self.eflow[s,:]))
        self._plot_fuzzy_curve(xd, xs, xf, dtrap, strap, ftrap, size,
                               dpi, font, colors, width, fname)

        if self.seaFunc is None and self.sedFunc is None and self.flowFunc is None:
            if self.sedfctx is None and self.flowfctx is None:
                return
        return

        print ''
        print 'Environmental functions:'

        if self.seaFunc is not None and self.sedFunc is not None and self.flowFunc is not None:
            matplotlib.rcParams.update({'font.size': font})
            fig = plt.figure(figsize=size2, dpi=dpi)
            gs = gridspec.GridSpec(1,12)
            ax1 = fig.add_subplot(gs[:4])
            ax2 = fig.add_subplot(gs[4:8]) #, sharey=ax1)
            ax3 = fig.add_subplot(gs[8:12]) #, sharey=ax1)
            ax1.set_facecolor('#f2f2f3')
            ax2.set_facecolor('#f2f2f3')
            ax3.set_facecolor('#f2f2f3')
            # Legend, title and labels
            ax1.grid()
            ax2.grid()
            ax3.grid()
            ax1.locator_params(axis='x', nbins=4)
            ax2.locator_params(axis='x', nbins=5)
            ax3.locator_params(axis='x', nbins=5)
            ax1.locator_params(axis='y', nbins=10)
            ax1.plot(self.seaFunc(self.seatime), self.seatime, linewidth=width, c='slateblue')
            ax1.set_xlim(self.seaFunc(self.seatime).min()-0.0001, self.seaFunc(self.seatime).max()+0.0001)
            ax2.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
            ax2.set_xlim(self.sedFunc(self.sedtime).min(), self.sedFunc(self.sedtime).max())
            ax3.plot(self.flowFunc(self.flowtime), self.flowtime, linewidth=width, c='darkcyan')
            ax3.set_xlim(self.flowFunc(self.flowtime).min()-0.0001, self.flowFunc(self.flowtime).max()+0.0001)
            # Axis
            ax1.set_ylabel('Time [years]', size=font+2)
            # Title
            tt1 = ax1.set_title('Sea-level [m]', size=font+3)
            tt2 = ax2.set_title('Water flow [m/s]', size=font+3)
            tt3 = ax3.set_title('Sediment input [m/d]', size=font+3)
            tt1.set_position([.5, 1.03])
            tt2.set_position([.5, 1.03])
            tt3.set_position([.5, 1.03])
            fig.tight_layout()
            plt.show()
            if fname is not None:
                names = self.folder+'/'+'input-seasedflow.png'
                fig.savefig(names, bbox_inches='tight')
            return

        if self.seaFunc is not None and self.sedFunc is not None:
            matplotlib.rcParams.update({'font.size': font})
            fig = plt.figure(figsize=size2, dpi=dpi)
            gs = gridspec.GridSpec(1,12)
            ax1 = fig.add_subplot(gs[:4])
            ax2 = fig.add_subplot(gs[4:8], sharey=ax1)
            ax1.set_facecolor('#f2f2f3')
            ax2.set_facecolor('#f2f2f3')
            # Legend, title and labels
            ax1.grid()
            ax2.grid()
            ax1.locator_params(axis='x', nbins=4)
            ax2.locator_params(axis='x', nbins=5)
            ax1.locator_params(axis='y', nbins=10)
            ax1.plot(self.seaFunc(self.seatime), self.seatime, linewidth=width, c='slateblue')
            ax1.set_xlim(self.seaFunc(self.seatime).min()-0.0001, self.seaFunc(self.seatime).max()+0.0001)
            ax2.plot(self.sedFunc(self.sedtime), self.sedtime, linewidth=width, c='sandybrown')
            ax2.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
            ax2.set_xlim(self.sedFunc(self.sedtime).min(), self.sedFunc(self.sedtime).max())
            # Axis
            ax1.set_ylabel('Time [years]', size=font+2)
            # Title
            tt1 = ax1.set_title('Sea-level [m]', size=font+2)
            tt2 = ax2.set_title('Sediment input [m/d]', size=font+2)
            tt1.set_position([.5, 1.03])
            tt2.set_position([.5, 1.03])
            fig.tight_layout()
            plt.show()
            if fname is not None:
                names = self.folder+'/'+'input-seased.png'
                fig.savefig(names)
            if self.flowfcty is not None:
                fig = plt.figure(figsize=size2, dpi=dpi)
                gs = gridspec.GridSpec(1,12)
                ax1 = fig.add_subplot(gs[:4])
                ax1.set_facecolor('#f2f2f3')
                # Legend, title and labels
                ax1.grid()
                ax1.locator_params(axis='x', nbins=4)
                ax1.locator_params(axis='y', nbins=10)
                ax1.plot(self.flowfctx, self.flowfcty, linewidth=width, c='darkcyan')
                ax1.set_xlim(self.flowfctx.min(), self.flowfctx.max())
                # Axis
                ax1.set_ylabel('Depth [m]', size=font+2)
                # Title
                tt1 = ax1.set_title('Water flow [m/s]', size=font+3)
                tt1.set_position([.5, 1.03])
                plt.show()
                if fname is not None:
                    names = self.folder+'/'+'input-flow.png'
                    fig.savefig(names, bbox_inches='tight')

            return

        if self.seaFunc is not None and self.flowFunc is not None:
            matplotlib.rcParams.update({'font.size': font})
            fig = plt.figure(figsize=size2, dpi=dpi)
            gs = gridspec.GridSpec(1,12)
            ax1 = fig.add_subplot(gs[:4])
            ax2 = fig.add_subplot(gs[4:8], sharey=ax1)
            ax1.set_facecolor('#f2f2f3')
            ax2.set_facecolor('#f2f2f3')
            # Legend, title and labels
            ax1.grid()
            ax2.grid()
            ax1.locator_params(axis='x', nbins=4)
            ax2.locator_params(axis='x', nbins=5)
            ax1.locator_params(axis='y', nbins=10)
            ax1.plot(self.seaFunc(self.seatime), self.seatime, linewidth=width, c='slateblue')
            ax1.set_xlim(self.seaFunc(self.seatime).min()-0.0001, self.seaFunc(self.seatime).max()+0.0001)
            ax2.plot(self.flowFunc(self.sedtime), self.sedtime, linewidth=width, c='darkcyan')
            ax2.set_xlim(self.flowFunc(self.sedtime).min(), self.flowFunc(self.sedtime).max())
            # Axis
            ax1.set_ylabel('Time [years]', size=font+2)
            # Title
            tt1 = ax1.set_title('Sea-level [m]', size=font+2)
            tt2 = ax2.set_title('Water flow [m/s]', size=font+2)
            tt1.set_position([.5, 1.03])
            tt2.set_position([.5, 1.03])
            fig.tight_layout()
            plt.show()
            if fname is not None:
                names = self.folder+'/'+'input-seaflow.png'
                fig.savefig(names, bbox_inches='tight')

            if self.sedfcty is not None:
                fig = plt.figure(figsize=size2, dpi=dpi)
                gs = gridspec.GridSpec(1,12)
                ax1 = fig.add_subplot(gs[:4])
                ax1.set_facecolor('#f2f2f3')
                # Legend, title and labels
                ax1.grid()
                ax1.locator_params(axis='x', nbins=4)
                ax1.locator_params(axis='y', nbins=10)
                ax1.plot(self.sedfctx, self.sedfcty, linewidth=width, c='sandybrown')
                ax1.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
                ax1.set_xlim(self.sedfctx.min(), self.sedfctx.max())
                # Axis
                ax1.set_ylabel('Depth [m]', size=font+2)
                # Title
                tt1 = ax1.set_title('Sediment input [m/d]', size=font+2)
                tt1.set_position([.5, 1.03])
                plt.show()
                if fname is not None:
                    names = self.folder+'/'+'input-sed.png'
                    fig.savefig(names, bbox_inches='tight')

            return

        else:
            matplotlib.rcParams.update({'font.size': font})
            fig = plt.figure(figsize=size2, dpi=dpi)
            gs = gridspec.GridSpec(1,12)
            ax1 = fig.add_subplot(gs[:4])
            ax1.set_facecolor('#f2f2f3')
            # Legend, title and labels
            ax1.grid()
            ax1.locator_params(axis='x', nbins=4)
            ax1.locator_params(axis='y', nbins=10)
            if self.seaFunc is not None:
                ax1.plot(self.seaFunc(self.seatime), self.seatime, linewidth=width, c='slateblue')
                ax1.set_xlim(self.seaFunc(self.seatime).min()-0.0001, self.seaFunc(self.seatime).max()+0.0001)
            else:
                ax1.plot(numpy.zeros(len(self.layTime)), self.layTime, linewidth=width, c='slateblue')
                ax1.set_xlim(-0.1, 0.1)
            # Axis
            ax1.set_ylabel('Time [years]', size=font+2)
            # Title
            tt1 = ax1.set_title('Sea-level [m]', size=font+2)
            tt1.set_position([.5, 1.03])
            plt.show()
            if fname is not None:
                names = self.folder+'/'+'input-sea.png'
                fig.savefig(names)

            if self.sedfcty is not None:
                fig = plt.figure(figsize=size2, dpi=dpi)
                gs = gridspec.GridSpec(1,12)
                ax1 = fig.add_subplot(gs[:4])
                ax1.set_facecolor('#f2f2f3')
                # Legend, title and labels
                ax1.grid()
                ax1.locator_params(axis='x', nbins=4)
                ax1.locator_params(axis='y', nbins=10)
                ax1.plot(self.sedfctx, self.sedfcty, linewidth=width, c='sandybrown')
                ax1.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
                ax1.set_xlim(self.sedfctx.min(), self.sedfctx.max())
                # Axis
                ax1.set_ylabel('Depth [m]', size=font+2)
                # Title
                tt1 = ax1.set_title('Sediment input [m/d]', size=font+2)
                tt1.set_position([.5, 1.03])
                plt.show()
                if fname is not None:
                    names = self.folder+'/'+'input-sed.png'
                    fig.savefig(names, bbox_inches='tight')

            if self.flowfcty is not None:
                fig = plt.figure(figsize=size2, dpi=dpi)
                gs = gridspec.GridSpec(1,12)
                ax1 = fig.add_subplot(gs[:4])
                ax1.set_facecolor('#f2f2f3')
                # Legend, title and labels
                ax1.grid()
                ax1.locator_params(axis='x', nbins=4)
                ax1.locator_params(axis='y', nbins=10)
                ax1.plot(self.flowfctx, self.flowfcty, linewidth=width, c='darkcyan')
                ax1.set_xlim(self.flowfctx.min(), self.flowfctx.max())
                # Axis
                ax1.set_ylabel('Depth [m]', size=font+2)
                # Title
                tt1 = ax1.set_title('Water flow [m/s]', size=font+2)
                tt1.set_position([.5, 1.03])
                plt.show()
                if fname is not None:
                    names = self.folder+'/'+'input-flow.png'
                    fig.savefig(names, bbox_inches='tight')

            plt.show()

        return

    def coralProduction(self, layID, coral, epsilon, sedh, ero, verbose):
        """
        This function estimates the coral growth based on newly computed population.

        Parameters
        ----------

        variable : layID
            Index of current stratigraphic layer.

        variable : coral
            Species population distribution at current time step.

        variable : epsilon
            Intrinsic rate of a population species (malthus parameter)

        variable : sedh
            Silicilastic sediment input m/d

        variable : ero
            Amount of erosion due to karstification
        """

        # Compute production for the given time step [m]
        production = numpy.zeros((coral.shape))
        ids = numpy.where(epsilon>0.)[0]
        production[ids] = self.prod[ids] * coral[ids] * self.dt / self.prodscale
        maxProd = self.prod * self.dt
        tmpids = numpy.where(production>maxProd)[0]
        production[tmpids] = maxProd[tmpids]

        # Total thickness deposited
        sh = sedh * self.dt
        toth = production.sum() + sh

        if verbose:
            print ' Thick:', toth, '\n Prod:', production, '\n Accom: ', self.topH #, '\n fac: ', envfac

        # In case there is no accommodation space
        if self.topH < 0. and ero == 0:
            # Do nothing
            return

        # In case there is no accommodation space and karstification is activated
        if self.topH < 0. and ero < 0:
            remero = -ero
            for k in range(layID,-1,-1):
                if remero <= 0.:
                    break
                ch = self.thickness[k]
                if self.thickness[k] > remero:
                    perc = remero/self.thickness[k]
                    self.thickness[k] -= remero
                    self.karstero[k] += remero
                    self.topH += remero
                    for j in range(len(self.prod)+1):
                        self.coralH[j,k] -= perc*self.coralH[j,k]
                    remero = 0.
                else:
                    remero -= self.thickness[k]
                    self.karstero[k] += self.thickness[k]
                    self.coralH[:,k] = 0.
                    self.topH += self.thickness[k]
                    self.thickness[k] = 0.

            return

        # If there is some accommodation space but it is all filled by sediment
        elif self.topH > 0. and self.topH - sh < 0.:
            # Just add the sediments to the sea-level
            self.coralH[len(self.prod),layID] += self.topH
            # Update current layer thickness
            self.thickness[layID] += self.topH
            # Update current layer top elevation
            self.topH = 0.

        # If there is some accommodation space that will disappear due to a
        # combination of carbonate growth and sediment input
        elif self.topH > 0. and self.topH - toth < 0:
            maxcarbh = self.topH - sh
            frac = maxcarbh/production.sum()
            production *= frac
            toth = production.sum() + sh

            # Update current layer composition
            self.coralH[0:len(self.prod),layID] += production
            # Convert sediment input from m/d to m/a
            self.coralH[len(self.prod),layID] += sh
            # Update current layer thickness
            self.thickness[layID] += toth
            # Update current layer top elevation
            self.topH -= toth

        # Otherwise
        elif self.topH > 0.:
            # Update current layer composition
            self.coralH[0:len(self.prod),layID] += production
            # Convert sediment input from m/d to m/a
            self.coralH[len(self.prod),layID] += sh
            # Update current layer thickness
            self.thickness[layID] += toth
            # Update current layer top elevation
            self.topH -= toth

        return
