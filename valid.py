# import aerosandbox as asb
# import aerosandbox.numpy as np
import viiflowtools.vf_tools as vft
import numpy as np

optimized_airfoil=vft.repanel(vft.read_selig('optimized_airfoil.dat'))

al=[]
cl=[]
cd=[]

aoa=np.arange(0,10,1)

import viiflow as vf

ap=vf.setup(Re=300e3,Alpha=aoa[0],Ma=0.6,Silent=True)
[p,bl,x] = vf.init(optimized_airfoil,ap)
for AOA in aoa:
    ap.Alpha = AOA
    [x,flag,_,_,_] = vf.iter(x,bl,p,ap)
    if flag:
        al.append(AOA)
        cl.append(p.CL)
        cd.append(bl[0].CD)
print(al)
print(np.array(cl)/np.array(cd))
