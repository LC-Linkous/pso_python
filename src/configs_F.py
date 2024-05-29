#! /usr/bin/python3

##--------------------------------------------------------------------\
#   pso_basic
#   './pso_basic/src/configs_F.py'
#   Constant values for objective function. Formatted for
#       automating objective function integration
#
#
#   Author(s): Lauren Linkous, Jonathan Lundquist
#   Last update: May 20, 2024
##--------------------------------------------------------------------\
import sys
try: # for outside func calls
    sys.path.insert(0, './optimizers/pso_basic/')
    from src.func_F import func_F
    from src.constr_F import constr_F
except: # for local
    sys.path.insert(0, './src/optimizers/pso_basic/src')
    from func_F import func_F
    from constr_F import constr_F

OBJECTIVE_FUNC = func_F
CONSTR_FUNC = constr_F
OBJECTIVE_FUNC_NAME = "pso_basic.func_F"
CONSTR_FUNC_NAME = "pso_basic.constr_F"

# problem dependent variables
LB = [[0.21, 0, 0.1]]       # Lower boundaries for input
UB = [[1, 1, 0.5]]          # Upper boundaries for input
IN_VARS = 3                 # Number of input variables (x-values)
OUT_VARS = 2                # Number of output variables (y-values)
TARGETS = [0, 0]            # Target values for output