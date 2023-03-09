""" A Gaussian age distribution """

__all__ = ['Gaussian']
__author__ = "J. Klüter"
__date__ = "2022-07-06"
__license__ = "GPLv3"
__version__ = "1.0.0"

import numpy as np
from ._age import Age


class Gaussian(Age):
    """
    Gaussian subclass of Age base class. This subclass is for populations that
    have age characterized by a single gaussian age distribution.

    Attributes
    ----------
    metallicity_func_name : str
        A class attribute for the name of the _Age subclass that this is.
    mean : float [[Fe/H]]
        the mean age in Gyr for the Gaussian distribution
    std : float [[Fe/H]]
        the standard deviation of age in Gyr for the Gaussian distribution
    lower_bound : float [[Gyr]]
        lower limit for truncation of the distribution
    upper_bound : float [[Gyr]]
        upper limit for truncation of the distribution


    Methods
    -------
    __init__(self,Population) : None
        initialize the metallicity class, and set the control parameters.
    draw_random_metallicity(self, N: int or None = None) : np.ndarray, float [[Fe/H]]
        return a random metallicity drawn from a Gaussian distribution
    average_metallicity(self) : float [[Fe/H]]
        return the average metallicity
    """

    def __init__(
            self, mean: float, std: float,
            low_bound: float = 1e-4, high_bound: float = 19.9526231497, **kwargs
            ):
        self.age_func_name = 'gaussian'
        self.mean = mean
        self.std = std
        self.lower = low_bound
        self.upper = high_bound

        if self.lower >= self.upper:
            raise ValueError(f"{low_bound = } has to be strictly smaller than {high_bound = }")

    def draw_random_age(self, N: int or None = None, **kwargs) -> np.ndarray or float:
        """
        Returns one or more metallicities in [Fe/H] from a Gaussian distribution.

        Parameters
        ----------
        N : int, None, optional
            if N is set to an integer, an array with N random ages is returned

        Returns
        -------
        val : ndarray, float [Gyr]
            single metallicities or ndarray of N metallicities in [Fe/H]
        """
        if N is None:
            # generate a single value
            while True:
                val = np.random.normal(self.mean, self.std)
                if self.lower < val < self.upper:
                    return val

        else:
            # generate multiple values
            val = np.random.normal(self.mean, self.std, N)
            while True:
                outside = (self.lower > val) | (val > self.upper)
                if not any(outside):
                    return val
                val[outside] = np.random.normal(self.mean, self.std, sum(outside))

    def average_age(self) -> float:
        """Determine the average metallicity of the population"""
        return self.mean

    def get_maximum_age(self) -> float:
        """
        returns the maximum age generated by the distribution
        if there is no maximum, it should return None.
        """
        return self.upper
