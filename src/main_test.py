#! /usr/bin/python3

##--------------------------------------------------------------------\
#   pso_python
#   './pso_python/src/main_test.py'
#   Test function/example for using the 'swarm' class in particle_swarm.py.
#       This has been modified from the original to include message 
#       passing back to the parent class or testbench, rather than printing
#       error messages directly from the 'swarm' class. Format updates are 
#       for integration in the AntennaCAT GUI.
#
#   Author(s): Jonathan Lundquist, Lauren Linkous
#   Last update: March 12, 2025
##--------------------------------------------------------------------\

import pandas as pd

from particle_swarm import swarm

# OBJECTIVE FUNCTION SELECTION
#import one_dim_x_test.configs_F as func_configs     # single objective, 1D input
#import himmelblau.configs_F as func_configs         # single objective, 2D input
import lundquist_3_var.configs_F as func_configs     # multi objective function



if __name__ == "__main__":


    # Constant variables
    NO_OF_PARTICLES = 50         # Number of particles in swarm
    T_MOD = 0.65                 # Variable time-step extinction coefficient
    TOL = 10 ** -6               # Convergence Tolerance
    MAXIT = 5000                 # Maximum allowed iterations
    BOUNDARY = 1                 # int boundary 1 = random,      2 = reflecting
                                    #              3 = absorbing,   4 = invisible
    WEIGHTS = [[0.7, 1.5, 0.5]]       # Update vector weights
    VLIM = 0.5                        # Initial velocity limit


    LB = func_configs.LB              # Lower boundaries, [[0.21, 0, 0.1]]
    UB = func_configs.UB              # Upper boundaries, [[1, 1, 0.5]]   
    OUT_VARS = func_configs.OUT_VARS  # Number of output variables (y-values)
    TARGETS = func_configs.TARGETS    # Target values for output


    # Objective function dependent variables
    func_F = func_configs.OBJECTIVE_FUNC  # objective function
    constr_F = func_configs.CONSTR_FUNC   # constraint function


    best_eval = 1

    parent = None            # for the PSO_TEST ONLY

    suppress_output = True   # Suppress the console output of particle swarm

    allow_update = True      # Allow objective call to update state 


    # Constant variables in a list format
    opt_params = {'NO_OF_PARTICLES': [NO_OF_PARTICLES], # Number of particles in swarm
                'T_MOD': [T_MOD],                       # Variable time-step extinction coefficient
                'BOUNDARY': [BOUNDARY],                 # int boundary 1 = random,      2 = reflecting
                                                        #              3 = absorbing,   4 = invisible
                'WEIGHTS': [WEIGHTS],                   # Update vector weights
                'VLIM':  [VLIM] }                       # Initial velocity limit

    # dataframe conversion
    opt_df = pd.DataFrame(opt_params)

    # optimizer initialization
    myOptimizer = swarm(LB, UB, TARGETS, TOL, MAXIT,
                            func_F, constr_F,
                            opt_df,
                            parent=parent)  

    while not myOptimizer.complete():
        # step through optimizer processing
        # this will update particle or agent locations
        myOptimizer.step(suppress_output)
        # call the objective function, control 
        # when it is allowed to update and return 
        # control to optimizer
        myOptimizer.call_objective(allow_update)
        # check the current progress of the optimizer
        # iter: the number of objective function calls
        # eval: current 'best' evaluation of the optimizer
        iter, eval = myOptimizer.get_convergence_data()
        if (eval < best_eval) and (eval != 0):
            best_eval = eval
        
        # optional. if the optimizer is not printing out detailed 
        # reports, preview by checking the iteration and best evaluation

        if suppress_output:
            if iter%100 ==0: #print out every 100th iteration update
                print("Iteration")
                print(iter)
                print("Best Eval")
                print(best_eval)

    print("Optimized Solution")
    print(myOptimizer.get_optimized_soln())
    print("Optimized Outputs")
    print(myOptimizer.get_optimized_outs())
