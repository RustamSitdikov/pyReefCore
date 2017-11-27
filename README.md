[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1050997.svg)](https://doi.org/10.5281/zenodo.1050997)

# pyReef-Core

**pyReef-Core** is a deterministic, one-dimensional (1-D) numerical model, that simulates the vertical coralgal growth patterns observed in a drill core, as well as the physical, environmental processes that effect coralgal growth. The model is capable of integrating ecological processes like coralgal community interactions over centennial-to-millennial scales using predator-prey or _Generalised Lotka-Volterra Equations_.


<div align="center">
    <img width=900 src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/fig1.jpg" alt="Schematic view" title="Schematic view"</img>
</div>

_Schematic figure of a hypothetical reef with transitions from shallow to deep assemblages occurring down-core, illustrating growth-form responses of corals to environmental forcing including light, sea level changes (**sl**), uplift and subsidence (**u/s**), hydrodynamic energy (**w** wave conditions and **c** currents), nutrients input **nu**, ocean temperature (**T**) and acidity (**pH**), karstification (**k**) and sediment flux._

Content:
- [Generalized Lotka-Volterra model](#generalized-lotka-volterra-model)
- [Species rate and community matrix](#species-rate-and-community-matrix)
- [Carbonate production](#carbonate-production)
- [Model workflow](#model-workflow)
- [Installation](#installation)
- [Usage](#usage)
- [Input file structure](#input-file-structure)
- [Examples](#examples)

## <a name="generalized-lotka-volterra-model"></a> Generalized Lotka-Volterra model 

The most common models of species evolution in ecological modeling are the predator-prey **Lotka-Volterra (LV)** equation and its modifications.

From LV equations, one can formulate the **Generalized Lotka-Volterra (GLV)** equation that allows unlimited number of species and different types of interactions among species. The GLV equation is mainly formed by two parts, the logistic growth/decay of a species and its interaction with the other species,

<p align="center"><img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/36c0f67b25b915d50ae129824705fc29.svg?invert_in_darkmode" align=middle width=173.0751pt height=50.188545pt/></p>

where <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/9fc20fb1d3825674c6a279cb0d5ca636.svg?invert_in_darkmode" align=middle width=13.993485pt height=14.10255pt/> is the population density of species _i_; <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/1cd32b0756da515bc59142b9318ff797.svg?invert_in_darkmode" align=middle width=11.28105pt height=14.10255pt/> is the intrinsic rate of increase/decrease of a population of species _i_ (also called **Malthusian** parameter); <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/8175b4b012861c57d7f99a503fdcaa72.svg?invert_in_darkmode" align=middle width=21.19161pt height=14.10255pt/> is the interaction coefficient among the species association _i_ and _j_, (a particular case is <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/ff41937f5cd113c5b9d670fd51ac28f1.svg?invert_in_darkmode" align=middle width=19.743405pt height=14.10255pt/>, the interaction of one species association with itself); and _t_ is time. Equation 1 can be written in matrix formulation as:

<p align="center"><img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/75aeba56acecbc8c3ead4fd18a21d6b3.svg?invert_in_darkmode" align=middle width=169.01445pt height=33.769395pt/></p>

where <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/cbfb1b2a33b28eab8a3e59464768e810.svg?invert_in_darkmode" align=middle width=14.85297pt height=22.38192pt/> is the vector of population densities of each species _i_, <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/7ccca27b5ccc533a2dd72dc6fa28ed84.svg?invert_in_darkmode" align=middle width=6.6475035pt height=14.10255pt/> is the vector of all _Mathusian_ parameters, <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/53d147e7f3fe6e47ee05b88b166bd3f6.svg?invert_in_darkmode" align=middle width=12.282765pt height=22.38192pt/> is the matrix of interaction coefficients, also known as community matrix, and <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/9f0dfe8a0e850780e96018103aa5fe64.svg?invert_in_darkmode" align=middle width=55.17996pt height=24.56553pt/> is a square matrix with diagonal elements equal to <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/cbfb1b2a33b28eab8a3e59464768e810.svg?invert_in_darkmode" align=middle width=14.85297pt height=22.38192pt/>, and zeros outside the diagonal.

## <a name="species-rate-and-community-matrix"></a> Species rate and community matrix

To solve the ODEs, the user needs to define several initial conditions:

- the initial species population number <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/8058174c3e47972feecfee6a81720995.svg?invert_in_darkmode" align=middle width=23.046375pt height=22.38192pt/>
- the intrinsic rate of a population species <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/7ccca27b5ccc533a2dd72dc6fa28ed84.svg?invert_in_darkmode" align=middle width=6.6475035pt height=14.10255pt/>
- the interaction coefficients among the species association <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/c745b9b57c145ec5577b82542b2df546.svg?invert_in_darkmode" align=middle width=10.537065pt height=14.10255pt/>

Several other input are required and will need to be set in the **XmL** inputfile. An example of such file is provided [here](https://github.com/pyReef-model/pyReefCore/blob/master/Tests/input.xml).

## <a name="solving-the-odes-system"></a> Solving the ODEs system

The mathematical model for the species population evolution results in a set of differential equations (ODEs), one for each species associations modeled. The **Runge-Kutta-Fehlberg** method (_RKF45_ or _Fehlberg_ as defined in the [**odespy**](http://hplgit.github.io/odespy/doc/pub/tutorial/html/main_odespy.html) library) is used to solve the **GLV ODE system**.

## <a name="carbonate-production"></a> Carbonate production

Once a species association population is computed, carbonate production is calculated using a carbonate production factor. Production factors are specified for the maximum population, and linearly scaled to the actual population following the relation
<p align="center"><img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/86747a51e4fe91aa94ce20bfe5b4a600.svg?invert_in_darkmode" align=middle width=106.14813pt height=36.235155pt/></p>

where <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/df5a289587a2f0247a5b97c1e8ac58ca.svg?invert_in_darkmode" align=middle width=12.78882pt height=22.38192pt/> is the carbonate production, <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/4f4f4e395762a3af4575de74c019ebb5.svg?invert_in_darkmode" align=middle width=5.913963pt height=20.1465pt/> is time, <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/ea449f9e9a48e2959872aac8fa65e1ca.svg?invert_in_darkmode" align=middle width=38.586405pt height=22.38192pt/> is the carbonate production factor when population is at its maximum, and <img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/655ca15e2b101fb431577b12d4442580.svg?invert_in_darkmode" align=middle width=18.5427pt height=22.38192pt/> is the maximum population of species _i_, computed as

<p align="center"><img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/43e99ce899b3ecaaa637f00ee554b2ae.svg?invert_in_darkmode" align=middle width=63.86358pt height=31.913475pt/></p>

which gives:

<p align="center"><img src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/2baed347518e8396d33d82d9c18e283b.svg?invert_in_darkmode" align=middle width=124.960935pt height=36.235155pt/></p>

We define the maximum carbonate production rate (m/y) for each species in the **XmL** input file.

## <a name="model-workflow"></a> Model workflow

<div align="center">
    <img width=900 src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/fig2.jpg" alt="workflow" title="Workflow"</img>
</div>

Illustration outlining **PyReef-Core** workflow (left) and of the resulting simulated core (right). First boundary conditions for sea level, sediment input, tectonics, temperature, pH, nutrients and flow velocity are set, which describes their relationship to either depth or time. The boundary conditions are used to establish the environment factor _fenv_ which describes the proportion of the maximum growth rate that an assemblage can achieve, depending on whether the environmental conditions exceed the optimal conditions for growth. The environment factor is set to scale the Malthusian parameter, which is in turn used as input in the GLVE equations to determine assemblage populations. Larger assemblage populations contribute to a faster rate of vertical accretion (here referred to as carbonate production). In case of subaerial exposure, karstification might occur. At the end of the timestep, boundary conditions are updated and the process is repeated.

## <a name="installation"></a> Installation

- [Local install](#local-install)
- [Docker container](#docker-container)

### <a name="local-install"></a> Local install

The code is available from our github [page](https://github.com/pyReef-model/pyReefCore.git) and can be obtained either from this page or using **git**
```
git clone https://github.com/pyReef-model/pyReefCore.git
```

Once donwloaded, navigate to the **pyReefCore** folder and run the following command:
```
pip install -e /workspace/volume/pyReefCore/
```

### <a name="docker-container"></a> Docker container

The code is available from Docker Hub at [pyreefmodel/pyreef-Docker](https://hub.docker.com/u/pyreefmodel/) and can be downloaded using **Kitematic**. Examples are provided in the [Tests](https://github.com/pyReef-model/pyReefCore/tree/master/Tests) folder and are ran through IPython Notebooks.

## <a name="usage"></a> Usage

pyReefCore can be use from an _IPython notebook_ or a _python script_ directly. An example of functions available is provided below:

```python

%matplotlib inline

import numpy as np
import cmocean as cmo
import matplotlib.pyplot as plt

%config InlineBackend.figure_format = 'svg'

from pyReefCore.model import Model

# Initialise model
reef = Model()

# Define the XmL input file
reef.load_xml('input.xml')

# Visualise initial setting parameters
reef.core.initialSetting(size=(10,4), fname='input')

# Run to a given time (for example 500 years)
reef.run_to_time(500.,showtime=500.,verbose=False)

# Define a colorscale to display the core
# Some colormaps are available from the following link:
# http://matplotlib.org/examples/color/colormaps_reference.html
from matplotlib.cm import terrain, plasma
nbcolors = len(reef.core.coralH)+10
colors = terrain(np.linspace(0, 1, nbcolors))
nbcolors = len(reef.core.layTime)+3
colors2 = plasma(np.linspace(0, 1, nbcolors))

# Plot evolution of species population with time
reef.plot.speciesTime(colors=colors, size=(10,4), font=8, dpi=100,fname='apop_t.pdf')

# Plot evolution of species population with depth
reef.plot.speciesDepth(colors=colors, size=(10,4), font=8, dpi=100, fname ='apop_d.pdf')

# Plot temporal evolution of accommodation and core thickness 
reef.plot.accomodationTime(size=(10,4), font=8, dpi=100, fname ='acc_t.pdf')

# Plot coral facies distribution, assemblages as a synthetic core
reef.plot.drawCore(lwidth = 3, colsed=colors, coltime = colors2, size=(10,8), font=8, dpi=380, 
                   figname=('core.pdf'), filename='core.csv', sep='\t')
```

## <a name="input-file-structure"></a> Input file structure

- [Grid structure](#grid-structure)
- [Time structure](#time-structure)
- [Stratal structure](#stratal-structure)
- [Sea-level structure](#sea-level-structure)
- [Tectonic structure](#tectonic-structure)
- [Precipitation structure](#precipitation-structure)
- [Stream power law structure](#stream-power-law-structure)
- [Erodibility structure](#erodibility-structure)
- [Hillslope structure](#hillslope-structure)
- [Flexural isostasy structure](#flexural-isostasy-structure)
- [Output folder](#output-folder)


```xml
<?xml version="1.0" encoding="UTF-8"?>
<badlands xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
```

### <a name="grid-structure"></a> Grid structure

REQUIRED

```xml
    <!-- Regular grid structure -->
    <grid>
        <!-- Digital elevation model file path -->
        <demfile>data/regularMR.csv</demfile>
        <!-- Optional parameter (integer) used to decrease TIN resolution.
             The default value is set to 1. Increasing the factor
             value will multiply the digital elevation model resolution
             accordingly.  -->
        <resfactor>2</resfactor>
        <!-- Boundary type: flat, slope, fix or wall -->
        <boundary>slope</boundary>
        <!-- Optional parameter (integer) used to force depression-less
             surface at the start of the simulation. The default value is 0
             to turn the option off, put it to 1 to enable it. (Optional) -->
        <nopit>0</nopit>
        <!-- Underworld flag used to enable underworld linkage. The default value is 0
             to turn the option off, put it to 1 to enable it.  (Optional) -->
        <udw>0</udw>
    </grid>
```


## <a name="examples"></a> Examples

A series of examples are shipped with the code and can form the basis for defining your own case.

<div align="center">
    <img width=600 src="http://sydney.edu.au/science/geosciences/images/core.jpg" alt="OTR core from the Geocoastal Group - USyD" title="OTR core from the Geocoastal Group - USyD"</img>   
</div>

Example of a core sample, including a well-preserved Faviidae coral recovered from 16 m depth. The red arrows are drawn on to indicate upwards recovery direction from One Tree Reef (Geocoastal Research Group - The UNiversity of Sydney).

Using the XmL input file you will be able to calibrate the environmental threshold functions for different assemblages. Figure below shows an example of calibration for shallow, moderate-deep and deep assemblages characteristic of a synthetic exposed margin. The x-axis indicates the limitation on maximum vertical accretion for conditions outside the optimal, 100% maximum growth window, indicated for clarity for the moderate-deep assemblage.

<div align="center">
    <img width=600 src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/input.jpg" alt="environmental threshold functions" title="environmental threshold functions"</img>   
</div>

### <a name="idealised-case-shallowing-up-fossil-reef-sequence"></a> Idealised case shallowing-up fossil reef sequence

<div align="center">
    <img width=800 src="https://rawgit.com/pyReef-model/pyReefCore/master/mfigs/ex1.jpg" alt="Idealised case shallowing-up fossil reef sequence" title="Idealised case shallowing-up fossil reef sequence"</img>
</div>

Schematic representation of synthetic data construction. (Left) Ideal shallowing-up fossil reef sequence representing a ‘catch-up’ growth strategy with associated assemblage compositions and changes, adapted from Dechnik (2016); (Right) Model output of synthetic core representing ideal shallowing-upward, ‘catch-up’ sequence and detail of the assignment of a vector of numerical IDs to synthetic core.
