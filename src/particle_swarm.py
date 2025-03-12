#! /usr/bin/python3

##--------------------------------------------------------------------\
#   pso_basic
#   './pso_basic/src/particle_swarm.py'
#   Particle swarm class. This class has been modified from the original
#       to include message passing for UI integration, and underflow 
#       and overflow min/max caps to accommodate wider user input
#       options in AntennaCAT. Does not use time step modulation.
#       
#
#   Author(s):  Lauren Linkous, Jonathan Lundquist
#   Last update: March 12, 2025
##--------------------------------------------------------------------\

import numpy as np
from numpy.random import Generator, MT19937
import sys
np.seterr(all='raise')

class swarm:
    # arguments should take form: 
    # swarm([[float, float, ...]], [[float, float, ...]], [[float, ...]], float, int,
    # func, func,
    # dataFrame,
    # class obj) 
    #  
    # opt_df contains class-specific tuning parameters
    # NO_OF_PARTICLES: int
    # weights: [[float, float, float]]
    # boundary: int. 1 = random, 2 = reflecting, 3 = absorbing,   4 = invisible
    # vlim: float
    # 
   
    def __init__(self,  lbound, ubound, targets, E_TOL, maxit,
                 obj_func, constr_func, 
                 opt_df,
                 parent=None): 

        # Optional parent class func call to write out values that trigger constraint issues
        self.parent = parent 

        #unpack the opt_df standardized vals
        NO_OF_PARTICLES = opt_df['NO_OF_PARTICLES'][0]
        weights = opt_df['WEIGHTS'][0]
        boundary = opt_df['BOUNDARY'][0]
        vlimit = opt_df['VLIM'][0]


        # optimizer init:
        heightl = np.shape(lbound)[0]
        widthl = np.shape(lbound)[1]
        heightu = np.shape(ubound)[0]
        widthu = np.shape(ubound)[1]

        lbound = np.array(lbound[0])
        ubound = np.array(ubound[0])

        self.rng = Generator(MT19937())

        if ((heightl > 1) and (widthl > 1)) \
           or ((heightu > 1) and (widthu > 1)) \
           or (heightu != heightl) \
           or (widthl != widthu):
            
            if self.parent == None:
                pass
            else:
                self.parent.error_message_generator("Error lbound and ubound must be 1xN-dimensional \
                                                        arrays  with the same length")
           
        else:
        
            if heightl == 1:
                lbound = lbound
        
            if heightu == 1:
                ubound = ubound

            self.lbound = lbound
            self.ubound = ubound
            variation = ubound-lbound


            self.M = np.array(np.multiply(self.rng.random((1,np.max([heightl, widthl]))), 
                                                                variation)+lbound)    

            self.V = np.array(np.multiply(self.rng.random((1,np.max([heightl,widthl]))), 
                                                                     vlimit))

            for i in range(2,int(NO_OF_PARTICLES)+1):
                
                self.M = \
                    np.vstack([self.M, 
                               np.multiply( self.rng.random((1,np.max([heightl, widthl]))), 
                                                                               variation) 
                                                                               + lbound])

                self.V = \
                    np.vstack([self.V,
                               np.multiply( self.rng.random((1,np.max([heightl, widthl]))), 
                                                                               vlimit)])
            '''
            self.M                      : An array of current particle locations.
            self.V                      : An array of current particle velocities.
            self.output_size            : An integer value for the output size of obj func
            self.Active                 : An array indicating the activity status of each particle.
            self.Gb                     : Global best position, initialized with a large value.
            self.F_Gb                   : Fitness value corresponding to the global best position.
            self.Pb                     : Personal best position for each particle.
            self.F_Pb                   : Fitness value corresponding to the personal best position for each particle.
            self.weights                : Weights for the optimization process.
            self.targets                : Target values for the optimization process.
            self.maxit                  : Maximum number of iterations.
            self.E_TOL                  : Error tolerance.
            self.obj_func               : Objective function to be optimized.      
            self.constr_func            : Constraint function.  
            self.iter                   : Current iteration count.
            self.current_particle       : Index of the current particle being evaluated.
            self.number_of_particles    : Total number of particles. 
            self.allow_update           : Flag indicating whether to allow updates.
            self.boundary               : Boundary conditions for the optimization problem.
            self.Flist                  : List to store fitness values.
            self.Fvals                  : List to store fitness values.
            self.vlimit                 : Velocity limits for the particles.
            self.Mlast                  : Last location of particle
            '''

            self.output_size = len(targets)
            self.Active = np.ones((NO_OF_PARTICLES))                        
            self.Gb = sys.maxsize*np.ones((1,np.max([heightl, widthl])))   
            self.F_Gb = sys.maxsize*np.ones((1,self.output_size))                
            self.Pb = sys.maxsize*np.ones(np.shape(self.M))                 
            self.F_Pb = sys.maxsize*np.ones((NO_OF_PARTICLES,self.output_size))  
            self.weights = np.array(weights)                     
            self.targets = np.array(targets).reshape(-1, 1)                      
            self.maxit = maxit                                             
            self.E_TOL = E_TOL                                              
            self.obj_func = obj_func                                             
            self.constr_func = constr_func                                   
            self.iter = 0                                                   
            self.current_particle = 0                                       
            self.number_of_particles = NO_OF_PARTICLES                      
            self.allow_update = 0                                           
            self.boundary = boundary                                       
            self.Flist = []                                                 
            self.Fvals = []                                                 
            self.vlimit = vlimit                                            
            self.Mlast = 1*self.ubound                                      

            self.error_message_generator("swarm successfully initialized")

    def call_objective(self, allow_update):
        if self.Active[self.current_particle]:
            # call the objective function. If there's an issue with the function execution, 'noError' returns False
            newFVals, noError = self.obj_func(self.M[self.current_particle], self.output_size)
            if noError == True:
                self.Fvals = np.array(newFVals).reshape(-1, 1)
                if allow_update:
                    self.Flist = abs(self.targets - self.Fvals)
                    self.iter = self.iter + 1
                    self.allow_update = 1
                else:
                    self.allow_update = 0
            return noError# return is for error reporting purposes only
    
    def update_velocity(self,particle):
        for i in range(0,np.shape(self.V)[1]):        

            self.V[particle,i] = \
                self.weights[0][0]* self.rng.random()*self.V[particle,i] \
                + self.weights[0][1]*self.rng.random()*(self.Pb[particle,i]-self.M[particle,i]) \
                + self.weights[0][2]*self.rng.random()*(self.Gb[i]-self.M[particle,i])
            
    def check_bounds(self, particle):
        update = 0
        for i in range(0,(np.shape(self.M)[1])):
            if (self.lbound[i] > self.M[particle,i]) \
               or (self.ubound[i] < self.M[particle,i]):
                update = i+1        
        return update

    def random_bound(self, particle):
        # If particle is out of bounds, bring the particle back in bounds
        # The first condition checks if constraints are met, 
        # and the second determines if the values are to large (positive or negative)
        # and may cause a buffer overflow with large exponents (a bug that was found experimentally)
        update = self.check_bounds(particle) or not self.constr_func(self.M[particle])
        if update > 0:
            while(self.check_bounds(particle)>0) or (self.constr_func(self.M[particle])==False):
                variation = self.ubound-self.lbound
                self.M[particle] = \
                    np.squeeze(self.rng.random() * 
                                np.multiply(np.ones((1,np.shape(self.M)[1])),
                                            variation) + self.lbound)
            
    def reflecting_bound(self, particle):        
        update = self.check_bounds(particle)
        constr = self.constr_func(self.M[particle])
        if (update > 0) and constr:
            self.M[particle] = 1*self.Mlast
            NewV = np.multiply(-1,self.V[update-1,particle])
            self.V[update-1,particle] = NewV
        if not constr:
            self.random_bound(particle)

    def absorbing_bound(self, particle):
        update = self.check_bounds(particle)
        constr = self.constr_func(self.M[particle])
        if (update > 0) and constr:
            self.M[particle] = 1*self.Mlast
            self.V[particle,update-1] = 0
        if not constr:
            self.random_bound(particle)

    def invisible_bound(self, particle):
        update = self.check_bounds(particle) or not self.constr_func(self.M[particle])
        if update > 0:
            self.Active[particle] = 0  
        else:
            pass          

    def handle_bounds(self, particle):
        if self.boundary == 1:
            self.random_bound(particle)
        elif self.boundary == 2:
            self.reflecting_bound(particle)
        elif self.boundary == 3:
            self.absorbing_bound(particle)
        elif self.boundary == 4:
            self.invisible_bound(particle)
        else:
            self.error_message_generator("Error: No boundary is set!")

    def check_global_local(self, Flist, particle):

        if np.linalg.norm(Flist) < np.linalg.norm(self.F_Gb):
            self.F_Gb = np.array([Flist])
            self.Gb = np.array(self.M[particle]) # stays 1D on update because of math happening later
        
        if np.linalg.norm(Flist) < np.linalg.norm(self.F_Pb[particle]):
            self.F_Pb[particle] = np.squeeze(Flist)
            self.Pb[particle] = self.M[particle]
    
    def update_point(self,particle):
        self.Mlast = 1*self.M[particle]
        self.V[particle] = self.floating_point_error_handler("self.V[particle] ", self.V[particle] )        
        self.M[particle] = self.M[particle] + self.V[particle]

    def converged(self):
        convergence = np.linalg.norm(self.F_Gb) < self.E_TOL
        return convergence
    
    def maxed(self):
        max_iter = self.iter > self.maxit
        return max_iter
    
    def complete(self):
        done = self.converged() or self.maxed()
        return done
    
    def step(self, suppress_output):
        if not suppress_output:
            msg = "\n-----------------------------\n" + \
                "STEP #" + str(self.iter) +"\n" + \
                "-----------------------------\n" + \
                "Current Particle:\n" + \
                str(self.current_particle) +"\n" + \
                "Current Particle Velocity\n" + \
                str(self.V[self.current_particle]) +"\n" + \
                "Current Particle Location\n" + \
                str(self.M[self.current_particle]) +"\n" + \
                "Absolute mean deviation\n" + \
                str(self.absolute_mean_deviation_of_particles()) +"\n" + \
                "-----------------------------"
            self.error_message_generator(msg)
            

        if self.allow_update:
            if self.Active[self.current_particle]:
                self.check_global_local(self.Flist,self.current_particle)
                self.update_velocity(self.current_particle)
                self.update_point(self.current_particle)
                self.handle_bounds(self.current_particle)
            self.current_particle = self.current_particle + 1

            if self.current_particle == self.number_of_particles:
                self.current_particle = 0


            if self.complete() and not suppress_output:
                msg = "\nOPTIMIZATION COMPLETE:\nPoints: \n" + str(self.Gb) + "\n" + \
                    "Iterations: \n" + str(self.iter) + "\n" + \
                    "Flist: \n" + str(self.F_Gb) + "\n" + \
                    "Norm Flist: \n" + str(np.linalg.norm(self.F_Gb)) + "\n"
                self.error_message_generator(msg)


    def export_swarm(self):
        swarm_export = {'lbound': self.lbound,
                        'ubound': self.ubound,
                        'targets': self.targets,
                        'E_TOL': self.E_TOL,
                        'maxit': self.maxit,                                                
                        'M': self.M,
                        'V': self.V,
                        'output_size': self.output_size,
                        'Gb': self.Gb,
                        'F_Gb': self.F_Gb,
                        'Pb': self.Pb,
                        'F_Pb': self.F_Pb,
                        'weights': self.weights,                        
                        'iter': self.iter,
                        'current_particle': self.current_particle,
                        'number_of_particles': self.number_of_particles,
                        'allow_update': self.allow_update,
                        'Flist': self.Flist,
                        'Fvals': self.Fvals,
                        'Active': self.Active,
                        'Boundary': self.boundary,
                        'Mlast': self.Mlast,
                        'vlimit': self.vlimit}
        return swarm_export

    def import_swarm(self, swarm_export, obj_func, constr_func):
        self.lbound = swarm_export['lbound'] 
        self.ubound = swarm_export['ubound'] 
        self.M = swarm_export['M'] 
        self.V = swarm_export['V'] 
        self.Gb = swarm_export['Gb'] 
        self.F_Gb = swarm_export['F_Gb'] 
        self.Pb = swarm_export['Pb'] 
        self.F_Pb = swarm_export['F_Pb'] 
        self.weights = swarm_export['weights'] 
        self.targets = swarm_export['targets'] 
        self.maxit = swarm_export['maxit'] 
        self.E_TOL = swarm_export['E_TOL'] 
        self.iter = swarm_export['iter'] 
        self.current_particle = swarm_export['current_particle'] 
        self.number_of_particles = swarm_export['number_of_particles'] 
        self.allow_update = swarm_export['allow_update'] 
        self.Flist = swarm_export['Flist'] 
        self.Fvals = swarm_export['Fvals']
        self.Active = swarm_export['Active']
        self.boundary = swarm_export['Boundary']
        self.Mlast = swarm_export['Mlast']
        self.vlimit = swarm_export['vlimit']
        self.output_size = swarm_export['output_size']
        self.obj_func = obj_func 
        self.constr_func = constr_func 

    def get_obj_inputs(self):
        return np.vstack(self.M[self.current_particle])
    
    def get_convergence_data(self):
        best_eval = np.linalg.norm(self.F_Gb)
        iteration = 1*self.iter
        return iteration, best_eval
        
    def get_optimized_soln(self):
        return self.Gb.reshape(-1, 1) #standardization 
    
    def get_optimized_outs(self):
        return self.F_Gb[0] #correction for extra brackets that happen with the math/passing
    
    def absolute_mean_deviation_of_particles(self):
        mean_data = np.array(np.mean(self.M, axis=0)).reshape(1, -1)
        abs_data = np.zeros(np.shape(self.M))
        for i in range(0,self.number_of_particles):
            abs_data[i] = np.squeeze(np.abs(self.M[i]-mean_data))

        abs_mean_dev = np.linalg.norm(np.mean(abs_data,axis=0))
        return abs_mean_dev

    def floating_point_error_handler(self, varName, varValue):
        # function added to handle floating point errors caused by user input variations
        # longer than it has to be for explicit print out messages + modification

        # buffer overflows happen when vlim, and the weights are all high
        # buffer underflows happen when vlim, and the weights are all low
        # other combinations may cause either issue, but these have been found experimentally

        # constr_buffer.py or constr_F.py may be stricter depending on the function
        # this is the limit for the optimizer, not the objective function.

        # this function applies a max or min cap to the passed variable
        capValue = varValue 

        if type(varValue) == np.ndarray:
            capValue = np.clip(varValue, 1e-50, 1e50)
        else:
            if varValue == 0:
                pass
            elif abs(varValue) > 1e50:
                capValue = 1e50*np.sign(varValue)
            elif abs(varValue) < 1e-50:
                capValue = 1e-50*np.sign(varValue)

        return capValue

    def error_message_generator(self, msg):
        if self.parent == None:
            print(msg)
        else:
            self.parent.debug_message_printout(msg)

