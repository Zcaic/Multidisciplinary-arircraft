import aerosandbox as asb
import aerosandbox.numpy as np
from aerosandbox.geometry.airfoil.airfoil_families import (
    get_kulfan_coordinates,
    get_kulfan_parameters,
)
from neuralfoil import get_aero_from_kulfan_parameters
from utils.asb2cad import af2geometry


lp = np.array([-0.05640185, -0.03, -0.03, -0.03, -0.03, -0.03, -0.03, -0.03])  # the optimal lp
up = np.array([0.13740123, 0.29148949, 0.29450211, 0.27986522, 0.5, 0.5, 0.17367956, 0.3624671]) # the optimal up

myairfoil=asb.Airfoil(coordinates=get_kulfan_coordinates(lower_weights=lp,upper_weights=up))
# rsaero=myairfoil.get_aero_from_neuralfoil(alpha=2,Re=6.98886e+06)
# ck=rsaero['CL']/rsaero['CD']
# print(ck)
# xf=asb.XFoil(airfoil=myairfoil,Re=6.98886e+06)
# rsaero=xf.alpha(2)
# ck=rsaero['CL']/rsaero['CD']
# print(ck)

# af2geometry(myairfoil,'optairfoil.step')
myairfoil=myairfoil.repanel(60)
myairfoil.write_dat('myaf.dat')