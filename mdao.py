import aerosandbox as asb
import aerosandbox.numpy as np

import casadi as ca

import openmdao.api as om

import matplotlib.pyplot as plt
import scienceplots
plt.style.use(['science','no-latex'])

from omxdsm import write_xdsm

from utils.asb2cad import af2geometry,af2VSP,af2XYZ

benchmark_airfoil=asb.KulfanAirfoil(name='naca0012')

opti=asb.Opti()
optVar=opti.variable(init_guess=0,freeze=True)
optLw=opti.variable(init_guess=benchmark_airfoil.lower_weights,freeze=True)
optUw=opti.variable(init_guess=benchmark_airfoil.upper_weights,freeze=True)

need2opt_airfoil=asb.KulfanAirfoil(
    name='need2opt_airfoil',
    lower_weights=optLw,
    upper_weights=optUw,
    leading_edge_weight=benchmark_airfoil.leading_edge_weight
)

ap=need2opt_airfoil.get_aero_from_neuralfoil(alpha=optVar,Re=1.4e7,mach=0.6,model_size='xxxlarge')

# print(ap)

CK=ca.Function('aero',[optVar,optLw,optUw],[ap['CL']/ap['CD']],['alpha','Lw','Uw'],['ck'])
dCK_dalpha=ca.Function('sens_alpha',[optVar,optLw,optUw],[ca.gradient(ap['CL']/ap['CD'],optVar)],['alpha','Lw','Uw'],['dck_dalpha'])
dCK_dLw=ca.Function('sens_Lw',[optVar,optLw,optUw],[ca.gradient(ap['CL']/ap['CD'],optLw)],['alpha','Lw','Uw'],['dck_dLw'])
dCK_dUw=ca.Function('sens_Uw',[optVar,optLw,optUw],[ca.gradient(ap['CL']/ap['CD'],optUw)],['alpha','Lw','Uw'],['dck_dUw'])

# print(CK(alpha=0,Lw=benchmark_airfoil.lower_weights,Uw=benchmark_airfoil.upper_weights)['ck'])
# print(dCK_dLw(alpha=0,Lw=benchmark_airfoil.lower_weights,Uw=benchmark_airfoil.upper_weights)['dck_dLw'])
# print(dCK_dUw(alpha=0,Lw=benchmark_airfoil.lower_weights,Uw=benchmark_airfoil.upper_weights)['dck_dUw'])

class Cal_Ck(om.ExplicitComponent):
    def initialize(self):
        return super().initialize()

    def setup(self):
        self.add_input('alpha',shape=1)
        self.add_input('Lw',shape=(8,1))
        self.add_input('Uw',shape=(8,1))
        self.add_output('ck',shape=1)
        # self.add_output('-ck')

    def setup_partials(self):
        self.declare_partials('ck','alpha')
        self.declare_partials('ck','Lw')
        self.declare_partials('ck','Uw')

    def compute(self, inputs, outputs, discrete_inputs=None, discrete_outputs=None):
        outputs['ck']=CK(alpha=inputs['alpha'],Lw=inputs['Lw'],Uw=inputs['Uw'])['ck']
    
    def compute_partials(self, inputs, partials, discrete_inputs=None):
        partials['ck','alpha']=dCK_dalpha(alpha=inputs['alpha'],Lw=inputs['Lw'],Uw=inputs['Uw'])['dck_dalpha']
        partials['ck','Lw']=dCK_dLw(alpha=inputs['alpha'],Lw=inputs['Lw'],Uw=inputs['Uw'])['dck_dLw']
        partials['ck','Uw']=dCK_dUw(alpha=inputs['alpha'],Lw=inputs['Lw'],Uw=inputs['Uw'])['dck_dUw']

prob=om.Problem()
prob.model.add_subsystem('Aerodynamics',Cal_Ck(),promotes=['*'])

prob.driver=om.ScipyOptimizeDriver()
prob.driver.options['optimizer']='SLSQP'
prob.driver.options['maxiter']=1000
# prob.driver.opt_settings['max_iter']=1000

# prob.model.add_design_var('alpha',lower=-5,upper=10)
prob.model.add_design_var('Lw',lower=np.full((8,1),-0.5),upper=np.full((8,1),-0.1))
prob.model.add_design_var('Uw',lower=np.full((8,1),0.1),upper=np.full((8,1),0.5))
prob.model.add_objective('ck',scaler=-1)

prob.setup()
prob.set_val('alpha',4)
prob.set_val('Lw',benchmark_airfoil.lower_weights)
prob.set_val('Uw',benchmark_airfoil.upper_weights)

# prob.check_partials(compact_print=True)
prob.run_driver()

print(prob['alpha'],prob['Aerodynamics.ck'])

opted_airfoil=asb.KulfanAirfoil(
    lower_weights=prob['Lw'],
    upper_weights=prob['Uw'],
    leading_edge_weight=benchmark_airfoil.leading_edge_weight
    )

# opted_airfoil.draw()
# af2geometry(opted_airfoil.to_airfoil(),filename='optimized_airfoil.step')
# af2geometry(benchmark_airfoil.to_airfoil(),filename='benchmark_airfoil.step')
# opted_airfoil.to_airfoil(n_coordinates_per_side=100).write_dat('optimized_airfoil.dat')
# benchmark_airfoil.to_airfoil(n_coordinates_per_side=100).write_dat('benchmark_airfoil.dat')
# af2VSP(opted_airfoil.to_airfoil(n_coordinates_per_side=100),'optimized_airfoil.af')
af2XYZ(opted_airfoil.to_airfoil(n_coordinates_per_side=100),'optimized_airfoil.xyz')

print(CK(alpha=4,Lw=benchmark_airfoil.lower_weights,Uw=benchmark_airfoil.upper_weights)['ck'])


fig,ax=plt.subplots()
ax.plot(benchmark_airfoil.coordinates[:,0],benchmark_airfoil.coordinates[:,1],label="benchmark")
ax.plot(opted_airfoil.coordinates[:,0],opted_airfoil.coordinates[:,1],label="optimized")
ax.legend()
plt.show()