import getpass
import sys
sys.path.insert(0,'/Users/yz3937/.pyenv/versions/3.8.5/lib/python3.8/site-packages/')
sys.path.append(f'/Users/{getpass.getuser()}/Dropbox/Thesis/code')
from utils.settings import *
import utils.utils as utils

def read_pdfs():

    path = f'{root}data/energy_communities/n-23-29-appendix-a.pdf'
    table = tabula.read_pdf(pdf_file, pages='all',output_format="dataframe" ,lattice = 'True')

