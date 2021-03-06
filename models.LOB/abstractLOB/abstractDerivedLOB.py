'''
Created on Jan 28, 2015

@author: weiluo
'''
import numpy as np
from abstractLOB import AbstractImplicitLOB
import abc
from _pyio import __metaclass__
from scipy import sparse
from abc import abstractmethod

"""
If we use those class to implement, for instance, BrownianMotion_expUti_Implicit_NeumannBC,
then we may get into the situation of multiple inheritance.
Look carefully at those method, they are mainly static helper functions.
So instead, I write a class of static helper functions which could be included
into an instance of BrownianMotion_expUti_Implicit_NeumannBC, and avoid
the multiple inheritence.

Those new classes are in the BC_helpers.py

"""

class AbstractImplicitLOB_sameSlopeBC(AbstractImplicitLOB):
    '''
    The boundary condition for HJB equation becomes 
    V_1 - V_0 = V_2 - V_1 and V_T - V_(T-1) = V_(T-1) - V_(T-2)
    which makes the co_matrix not a triangle matrix anymore    
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(AbstractImplicitLOB_sameSlopeBC, self).__init__(*args, **kwargs)
    
    def coef_at_minus_one_helper(self, short_arr, positive=True):
        """
        short_arr should be the coef at minus for 
        space = implement_q_space[1],...,implement_q_space[-2]
        
        It will return an array with length implement_I. The 
        return array will append the input two 1 at the end.
        """
        append_sign = 1 if positive else -1
        return np.append(short_arr, np.array([-2,-2]) * append_sign)
    
    def coef_at_plus_one_helper(self, short_arr, positive=True):
        append_sign = 1 if positive else -1
        return np.hstack((np.array([-2,-2]) * append_sign, short_arr))
    
    def coef_at_curr_helper(self, short_arr, positive=True):
        append_sign = 1 if positive else -1
        return np.hstack((append_sign, short_arr, append_sign))
    
    def equation_right_helper(self, short_arr):
        return np.hstack((0, short_arr, 0))
    
    
    @abstractmethod
    def linear_system_helper(self, v_curr, curr_control, step_index):
        """
        should return [co_left, co_right, co_mid, eq_right]
        
        each of them should be an array of length implement_I.
        
        co_left corresponding to the lower-left part of triangle matrix whose last element would not show up in the triangle matrix.
        
        co_right corresponding to the upper-right part of triangle matrix whose first element would not show up in the triangle matrix.
        """  
        pass
   
    def linear_system(self, v_curr, curr_control, step_index):
        co_left, co_right, co_mid, eq_right = self.linear_system_helper(v_curr, curr_control)
       
        minus2_diag = np.zeros(self.implement_I)
        minus2_diag[-2] = 1
        plus2_diag = np.zeros(self.implement_I)
        plus2_diag[1] = 1        
        data = [minus2_diag, co_left, co_mid, co_right, plus2_diag]   #mind the sign here.
        diags = [-2, -1, 0, 1, 2]
        co_matrix = sparse.spdiags(data, diags, self.implement_I, self.implement_I, format = 'csc')
       
        return [eq_right, co_matrix]
     
    
   
   
   
   
   
class AbstractImplicitLOB_NeumannBC(AbstractImplicitLOB):
    '''
    Neumann Boundary Condition.
    Provide helper function for coef_at_minus_one,
    coef_at_plus_one, coef_at_curr, equation_right
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(AbstractImplicitLOB_NeumannBC, self).__init__(*args, **kwargs)
        
    def coef_at_minus_one_helper(self, short_arr, positive=True):
        """
        short_arr should be the coef at minus for 
        space = implement_q_space[1],...,implement_q_space[-2]
        
        It will return an array with length implement_I. The 
        return array will append the input two 1 at the end.
        """
        append_sign = 1 if positive else -1
        return np.append(short_arr, np.array([1,1]) * append_sign)
    
    def coef_at_plus_one_helper(self, short_arr, positive=True):
        append_sign = 1 if positive else -1
        return np.hstack((np.array([1,1]) * append_sign, short_arr))
    
    def coef_at_curr_helper(self, short_arr, positive=True):
        append_sign = 1 if positive else -1
        return np.hstack((append_sign, short_arr, append_sign))
    
    def equation_right_helper(self, short_arr):
        return np.hstack((0, short_arr, 0))
    
    
    @abstractmethod
    def linear_system_helper(self, v_curr, curr_control, step_index):
        """
        should return [co_left, co_right, co_mid, eq_right]
        
        each of them should be an array of length implement_I.
        
        co_left corresponding to the lower-left part of triangle matrix whose last element would not show up in the triangle matrix.
        
        co_right corresponding to the upper-right part of triangle matrix whose first element would not show up in the triangle matrix.
        """  
        pass
    def linear_system(self, v_curr, curr_control, step_index):
        co_left, co_right, co_mid, eq_right = self.linear_system_helper(v_curr, curr_control, step_index)
        data = [co_left, co_mid, co_right]   #mind the sign here.
        diags = [-1, 0, 1]
        co_matrix = sparse.spdiags(data, diags, self.implement_I, self.implement_I, format = 'csc')
       
        return [eq_right, co_matrix]
        
        
    