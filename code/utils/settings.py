# General

import pandas as pd
import numpy as np
import glob
import os
import pickle
import wrds
from cleanco import basename
import string
import time
import sys
import getpass
import cleanco
import importlib
from string import punctuation
import collections
import requests
import json
import random

# Graphing

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import matplotlib.ticker as tick
from matplotlib.font_manager import FontProperties
import seaborn as sns
#import plotly.express as px
#import tabula
#from dbfread import DBF
from pypdf import PdfMerger

# Stats

import statsmodels.api as sm
from linearmodels.panel import PanelOLS
from linearmodels.panel.data import PanelData
from scipy.stats.mstats import winsorize

# Geospatial tools

from shapely.geometry import Point
from shapely.geometry import Polygon
# NOTE: there is a package issue with geopandas where we need shapely=1.8.4
import geopandas as gpd
from geopandas import GeoDataFrame
import plotly.figure_factory as ff
# NOTE: rasterstats works with downgraded numpy==1.20.3
import rasterstats
import rasterio
import pvlib
import pathlib
import plotly

# Options and Globals

pd.options.mode.chained_assignment = None

user = getpass.getuser()
root = f'/Users/{user}//Dropbox/Thesis/'

sns.set(style="ticks", font_scale=1.5)
sns.despine()
plt.rcParams['lines.linewidth'] = 2