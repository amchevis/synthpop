""" A uniform age distribution """

__all__ = ["Uniform", ]
__author__ = "S. Johnson"
__date__ = "2022-07-06"
__license__ = "GPLv3"
__version__ = "1.0.0"


import numpy as np
from ._age import Age


class Uniform(Age):
    """
    Uniform subclass of Age base class. This subclass is for Populations that
    have ages characterized by a uniform distribution between two bounds. 

    Attributes
    ----------
    age_func_name : str
        A class attribute for the name of the Age base subclass that this is.
    low_bound : float [Gyr]
        The lower bound of the uniform age distribution in giga-years.
    high_bound : float [Gyr]
        The upper bound of the uniform age distribution in giga-years.
    
    Methods
    -------
    __init__(self,Population) : None
        check that required attributes of Population are present:

    draw_random_age(self, N: float or None = None) : np.ndarray , float [Gyr]
        return a random age from uniform distribution
    average_age(self) : float [Gyr]
        return the average age, (low_bound+high_bound)/2.0
    """

    def __init__(self, low_bound: float, high_bound: float, **kwargs):
        self.age_func_name = 'uniform'
        self.low_bound = low_bound
        self.high_bound = high_bound

    def draw_random_age(self, N: float or None = None) -> np.ndarray or float:
        """
        Generate a random age from a uniform distribution

        Parameters
        ----------
        N : int, None, optional
            if N is set to an integer, an array with N random ages is returned

        Returns
        -------
        age : ndarray, float [Gyr]
            single age or numpy array of N ages in Giga-years
        """
        return np.random.uniform(self.low_bound, self.high_bound, N)

    def average_age(self) -> float:
        """ Determine the average age of the population """
        return (self.low_bound + self.high_bound) / 2.0

    def get_maximum_age(self) -> float:
        """
        returns the maximum age generated by the distribution
        """
        return self.high_bound
