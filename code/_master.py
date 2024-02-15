import getpass
import sys
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

# -----------------------------------------------------------------------
# Data Preparation
# -----------------------------------------------------------------------

# Base file (construct the counties) panel
os.system('python ' + os.path.join(root, 'code', 'data_prep', 'counties',
                                   'clean_counties.py'))

# EIA ---------------------------------------------------------------

# First, get the metadata from the EIA files
# inside this code there is a manual step of tagging files
os.system('python ' + os.path.join(root, 'code', 'data_prep', 'eia',
                                   'metadata.py'))

# Clean the generator data
os.system('python ' + os.path.join(root, 'code', 'data_prep', 'eia',
                                   'clean_generator.py'))

# Clean the plant data
os.system('python ' + os.path.join(root, 'code', 'data_prep', 'eia',
                                   'clean_plants.py'))

# Merge and make a county level dataset
os.system('python ' + os.path.join(root, 'code', 'data_prep', 'eia',
                                   'merge_eia.py'))

# Wind ---------------------------------------------------------------

# Clean the wind data (for each county get the average wind speed at different height)
os.system('python ' + os.path.join(root, 'code', 'data_prep', 'global_atlas',
                                      'clean_wind.py'))


# Solar ---------------------------------------------------------------

# Clean the solar data (get the tilt irr and the fixed irr for each county)
os.system('python ' + os.path.join(root, 'code', 'data_prep', 'nsrd',
                                   'clean_solar.py'))


# Other ---------------------------------------------------------------

# Clean the turbine data
os.system('python ' + os.path.join(root, 'code', 'data_prep', 'other',
                                      'clean_turbine.py'))


# Bank ----------------------------------------------------------------

# Clean the bank data
# https://www.ffiec.gov/cra/craflatfiles.htm
# https://www.federalreserve.gov/consumerscommunities/data_tables.htm

os.system('python ' + os.path.join(root, 'code', 'data_prep', 'bank',
                                   'clean_bank.py'))

# QCEW ------------------------------------------------------------------

# Note that QCEW is on the grid, so we need to run the data combining separately

os.system('python ' + os.path.join(root, 'code', 'data_prep', 'qcew',
                                   'clean_qcew.py'))

# Zillow ---------------------------------------------------------------

os.system('python ' + os.path.join(root, 'code', 'data_prep', 'zillow',
                                   'clean_zillow.py'))

# State and Local ------------------------------------------------------


# -----------------------------------------------------------------------
# Main Merge
# -----------------------------------------------------------------------

os.system('python ' + os.path.join(root, 'code', 'data_prep',
                                   'merge.py'))

# -----------------------------------------------------------------------
# Summary Statistics
# -----------------------------------------------------------------------


