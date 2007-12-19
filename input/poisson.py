# 14.02.2007
# last revision: 03.12.2007
#!
#! Poisson Equation
#! ================
#$ \centerline{Example input file, June 1, 2007}

#! Mesh
#! ----
fileName_mesh = 'database/simple.mesh'

#! Materials
#! ---------
#$ Here we define just a constant coefficient $c$ of the Poisson equation.
#$ The 'here' mode says that. Other possible mode is 'function', for
#$ material coefficients computed/obtained at runtime.

material_2 = {
    'name' : 'coef',
    'mode' : 'here',
    'region' : 'Omega',
    'coef' : 1.0,
}

#! Fields
#! ------
#! A field is used mainly to define the approximation on a (sub)domain, i.e. to
#$ define the discrete spaces $V_h$, where we seek the solution.
#!
#! The Poisson equation can be used to compute e.g. a temperature distribution,
#! so let us call our field 'temperature'. On a region called 'Omega'
#! (see below) it will be approximated using P1 finite elements.

field_1 = {
    'name' : 'temperature',
    'dim' : (1,1),
    'flags' : (),
    'domain' : 'Omega',
    'bases' : {'Omega' : '3_4_P1'}
}

#! Variables
#! ---------
#! One field can be used to generate discrete DOFs of several variables.
#! Here the unknown variable (the temperature) is called 't', it's asssociated
#! DOF number is set to 30 --- this will be referred to
#! in the Dirichlet boundary section (ebc). The corresponding test variable of
#! the weak formulation is called 's'. Notice that the last item of a test
#! variable must specify the unknown it corresponds to.

variables = {
    't' : ('field', 'unknown', 'temperature', (30,), 0),
    's' : ('field', 'test', 'temperature', (30,), 't'),
}

#! Regions and Boundary Conditions
#! -------------------------------
region_1000 = {
    'name' : 'Omega',
    'select' : 'elements of group 6',
}
region_03 = {
    'name' : 'Gamma_Left',
    'select' : 'nodes in (x < 0.00001)',
}
region_4 = {
    'name' : 'Gamma_Right',
    'select' : 'nodes in (x > 0.099999)',
}

ebc = {
    'Gamma_Left' : ('T3', (30,), 2.0),
    'Gamma_Right' : ('T3', (30,), -2.0),
}

#! Equations
#! ---------
#$ \usepackage{bm}
#$ The weak formulation of the Poisson equation is:
#$ \begin{center}
#$ Find $t \in V$, such that
#$ $\int_{\Omega} c\ \nabla t : \nabla s = f, \quad \forall s \in V_0$.
#$ \end{center}
#$ The equation below directly corresponds to the discrete version of the
#$ above, namely:
#$ \begin{center}
#$ Find $\bm{t} \in V_h$, such that
#$ $\bm{s}^T (\int_{\Omega_h} c\ \bm{G}^T G) \bm{t} = 0, \quad \forall \bm{s}
#$ \in V_{h0}$,
#$ \end{center}
#$ where $\nabla u \approx \bm{G} \bm{u}$. Below we use $f = 0$ (Laplace
#$ equation).

integral_1 = {
    'name' : 'i1',
    'kind' : 'v',
    'quadrature' : 'gauss_o1_d3',
}
equations = {
    'Temperature' : """dw_laplace.i1.Omega( coef, s, t ) = 0"""
}

#! Linear solver parameters
#! ---------------------------
solver_0 = {
    'name' : 'ls',
    'kind' : 'ls.umfpack',
}

#! Nonlinear solver parameters
#! ---------------------------
solver_1 = {
    'name' : 'newton',
    'kind' : 'nls.newton',

    'iMax'      : 1,
    'epsA'      : 1e-10,
    'epsR'      : 1.0,
    'macheps'   : 1e-16,
    'linRed'    : 1e-2, # Linear system error < (epsA * linRed).
    'lsRed'     : 0.1,
    'lsRedWarp' : 0.001,
    'lsOn'      : 1.1,
    'lsMin'     : 1e-5,
    'check'     : 0,
    'delta'     : 1e-6,
    'isPlot'    : False,
    'matrix'    : 'internal', # 'external' or 'internal'
    'problem'   : 'nonlinear', # 'nonlinear' or 'linear' (ignore iMax)
}

#! Options
#! -------
#! Use them for anything you like... Here we show how to tell which solvers
#! should be used - reference solver by their name.
options = {
    'nls' : 'newton',
    'ls' : 'ls',
}


#! FE assembling parameters
#! ------------------------
fe = {
    'chunkSize' : 1000
}
