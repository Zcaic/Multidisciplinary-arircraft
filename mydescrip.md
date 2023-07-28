### it is my test
```python
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
initcst=get_kulfan_parameters(coordinates=oriairfoil.coordinates)

opti = asb.Opti()

lp = opti.variable(init_guess=initcst['lower_weights'], upper_bound=-0.03, lower_bound=-0.5)
up = opti.variable(init_guess=initcst['upper_weights'], upper_bound=0.5, lower_bound=0.05)

mycst = dict(lower_weights=lp, upper_weights=up, TE_thickness=0, leading_edge_weight=0)
rsaero = get_aero_from_kulfan_parameters(kulfan_parameters=mycst, alpha=2, Re=6.98886e+06)

ck = -rsaero["CL"] / rsaero["CD"]
opti.minimize(ck)

track_lp=[]
track_up=[]
sol = opti.solve(callback=track_opt,verbose=False)
print(track_lp[-1])
print(track_up[-1])
print(sol.stats()['iterations']['obj'])

```
```
the history of obj is:
[-71.97528142783199, -72.13468982455441, -67.62159392513874, -79.97649494975234, -122.52266687532232, -133.51252039590796, -180.17954523397108, -183.93608137653388, -184.81119028819847, -210.3904160677403, -210.82175351449737, 
-232.7252212728867, -243.22206547147832, -251.63075279570074, -254.38170153061793, -255.48376530501085, -255.55609826991125, -255.59643616947838, -255.5969481213508, -255.59695565203143]
```

it seems to work sucessfully\
then I use optimal solution (lp and up) to verify:
```python
lp = np.array([-0.05640185, -0.03, -0.03, -0.03, -0.03, -0.03, -0.03, -0.03])  # the optimal lp
up = np.array([0.13740123, 0.29148949, 0.29450211, 0.27986522, 0.5, 0.5, 0.17367956, 0.3624671]) # the optimal up

myairfoil=asb.Airfoil(coordinates=get_kulfan_coordinates(lower_weights=lp,upper_weights=up))
rsaero=myairfoil.get_aero_from_neuralfoil(alpha=2,Re=6.98886e+06)
ck=rsaero['CL']/rsaero['CD']
print(f"neuralfoil: {ck}")
xf=asb.XFoil(airfoil=myairfoil,Re=6.98886e+06)
rsaero=xf.alpha(2)
ck=rsaero['CL']/rsaero['CD']
print(f"xfoil: {ck}")
```
```
output:
neuralfoil: [255.59443472]
xfoil: [248.25301205]

```
it works well although the CL/CD has a little difference between neuralfoil and xfoil
