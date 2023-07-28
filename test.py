import aerosandbox as asb
import aerosandbox.numpy as np
from aerosandbox.geometry.airfoil.airfoil_families import get_kulfan_coordinates,get_kulfan_parameters
from neuralfoil import get_aero_from_kulfan_parameters
import logging
logging.basicConfig(level=logging.INFO,format='%(levelname)s - %(asctime)s - %(message)s...')

def track_opt(iter):
    logging.info(f"optimizer state at iteration {iter}")
    track_lp.append(opti.debug.value(lp))
    track_up.append(opti.debug.value(up))

oriairfoil=asb.Airfoil(name='rae2822')
# oriairfoil.draw()
initcst=get_kulfan_parameters(coordinates=oriairfoil.coordinates)
# print(initcst)

opti = asb.Opti()

lp = opti.variable(init_guess=initcst['lower_weights'], upper_bound=-0.03, lower_bound=-0.5)
up = opti.variable(init_guess=initcst['upper_weights'], upper_bound=0.5, lower_bound=0.05)

mycst = dict(lower_weights=lp, upper_weights=up, TE_thickness=0, leading_edge_weight=0)
# myairfoil=asb.Airfoil(name='myairfoil',coordinates=get_kulfan_coordinates(upper_weights=up,lower_weights=lp,))

rsaero = get_aero_from_kulfan_parameters(kulfan_parameters=mycst, alpha=2, Re=6.98886e+06)
ck = -rsaero["CL"] / rsaero["CD"]

# objv=np.sum(up)

opti.minimize(ck)
track_lp=[]
track_up=[]
sol = opti.solve(callback=track_opt,verbose=False)
print(track_lp[-1])
print(track_up[-1])
print(sol.stats()['iterations']['obj'])


# optairfoil = asb.Airfoil(
#     coordinates=get_kulfan_coordinates(
#         lower_weights=sol.value(lp), upper_weights=sol.value(up)
#     )
# )
# optairfoil.draw()