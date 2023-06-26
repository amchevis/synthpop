""" Extinction maps collected from the dustmap module

Using dustmaps allows to evaluate the dustmap for each star.
which allows accurate results for larger cones.

"""

__all__ = ["Surot", ]
__author__ = "M.J. Huston"
__date__ = "2023-06-26"
__license__ = "GPLv3"
__version__ = "1.0.0"

import linecache
import numpy as np
from scipy.spatial import distance as sci_distance
from ._extinction import ExtinctionMap, EXTINCTION_DIR
import time


class Surot(ExtinctionMap):
    """
    Extinction map from Surot et al. 2020
    Map must first be converted from E(J-Ks) to A_Ks values
    Note: 
        This is a quick implementation of a 2D extinction map which repurposes the methods desgined for a 3D map used in marshall.py. While the current version will primarily be used for extinction map comparison purposes, a more careful design will likely be beneficial in the future.  

    Attributes
    ----------
    extinction_map_name : str
        name of the Extinction Map
    l_deg : float
        galactic longitude in degree set by "update_sight-line"
    b_deg : float
        galactic latitude in degree set by "update_sight-line"

    ref_wavelength : float
        reference wavelength for the extinction

    A_or_E : float or function
        total extinction or color excess, from the extinction map.
        if it is a function it will be called

    A_or_E_type : str
        Output type from the extinction map.
        If it starts with "A", A_or_E is handled  as a total extinction.
        If it starts with "E": A_or_E is handled as a color excess.
    R_V : float
        interstellar reddening parameter

    Methods
    -------
    update_line_of_sight(l_deg, b_deg) :
        specified the new galactic coordinates
        calls find_sightline() and init_sightline()
    update_extinction_in_map() :

    init_sightline(self) :

    find_sightline(self) :

    update_extinction_in_map():
        placeholder for function that updates the total extinction or color excess
        in self.extinction_map_name
    set_R_V(self,R_V):
        set interstellar reddening parameter

    get_map_properties():
        returns the basic parameters of the extinction map
        used for Communication between ExtinctionLaw and ExtinctionMap

    """

    def __init__(self, **kwargs):
        # name of the extinction map used
        self.extinction_map_name = "Surot"
        # effective wavelength for VISTA K_s bandpass (http://svo2.cab.inta-csic.es/theory/fps/index.php?id=Paranal/VISTA.Ks&&mode=browse&gname=Paranal&gname2=VISTA#filter)
        self.ref_wavelength = 2.152152
        self.A_or_E_type = "A_Ks"
        # placeholder for and location...
        self.l_deg = None
        self.b_deg = None
        self.radius_ind = None
        self.near_bin_edge = None
        self.near_bin_edge_err = None
        self.extinction_in_map = None
        self.extinction_in_map_err = None

        # get coordinates from surot_A_table.csv
        self.all_coords = np.genfromtxt(f'{EXTINCTION_DIR}/surot_A_Ks_table1.csv',
            usecols=[0, 1], delimiter=',')

        self.l_stepsize = self.all_coords[1, 0] - self.all_coords[0, 0]

        # placeholders for sightline information
        self.sightline = []
        self.sightline_l_deg = None
        self.sightline_b_deg = None
        self.chi2_allstars = None
        self.chi2_giants = None
        self.number_of_bins = None
        # set the radius index to zero
        self.radius_ind = None
        # first bin edge is 0
        self.near_bin_edge = None
        # A_Ks is zero in the zeroth bin
        self.A_Ks = None
        self.far_bin_edge = None
        self.far_bin_edge_ind = None
        self.A_Ks_ind = None

    def update_extinction_in_map(self, radius, force=False, **kwargs):
        """
        Check if the radius provided goes into a new bin, and if so update all the extinction values
        """
        # Actually, we will digitize this again to find the radius
        # this will return the far edge index, so we will want to subtract 1
        radius_ind = np.digitize(radius, self.sightline[5::4]) - 1

        # first, we will check if the radius index is different that it already is
        if radius_ind == self.radius_ind and not force:
            return 0

        # if we are at a new radius, update our index
        self.radius_ind = radius_ind

        # set to zero if we are not made it into the first bin      
        # now, we can just set the A_Ks value        
        self.near_bin_edge = self.sightline[5 + radius_ind * 4] if radius_ind > 0 else 0
        self.near_bin_edge_err = self.sightline[7 + radius_ind * 4] if radius_ind > 0 else 0

        self.extinction_in_map_err = self.sightline[8 + radius_ind * 4] if radius_ind > 0 else 0
        self.extinction_in_map = self.sightline[6 + radius_ind * 4] if radius_ind > 0 else 0

        # a generic function we will place in all self.update_extinction functions
        return 1

    def update_line_of_sight(self, l_deg, b_deg):
        """
        Set a new sight-line

        Parameters
        ----------
        l_deg : float [degree]
            galactic longitude
        b_deg : float [degree]
            galactic latitude

        """
        self.l_deg = l_deg
        self.b_deg = b_deg
        self.find_sightline()
        self.init_sightline()

    def init_sightline(self):
        """
        Routine to prep the sightline, get first values, etc. 
        """
        self.sightline_l_deg = self.sightline[0]
        self.sightline_b_deg = self.sightline[1]
        self.chi2_allstars = self.sightline[2]
        self.chi2_giants = self.sightline[3]
        self.number_of_bins = self.sightline[4]
        # set the radius index to zero
        self.radius_ind = 0
        # first bin edge is 0
        self.near_bin_edge = 0
        # A_Ks is zero in the zeroth bin
        self.A_Ks = 0
        self.far_bin_edge = self.sightline[5]
        self.far_bin_edge_ind = 5
        self.A_Ks_ind = 6
        self.update_extinction_in_map(self.near_bin_edge, force=True)

    def find_sightline(self):
        """
        A function for the Surot map that finds the closest
        sightline to the coordinates specified.
        
        Can be used to reset the class to a new sightline,
        could be more efficient.
        """
        # find the closest geometric sightline
        # find the index of the minimum distance to a coordinate pair
        if self.l_deg is None:
            min_dist_arg = sci_distance.cdist(np.array([[0., 0.]]), self.all_coords).argmin()
        else:
            # ensure that l_deg wraps correctly 
            l_deg = self.l_deg - 360 if self.l_deg > (180 - self.l_stepsize / 2) else self.l_deg 

            # find line of sight with the closest distance
            min_dist_arg = sci_distance.cdist(
                np.array([[l_deg, self.b_deg]]),
                self.all_coords
                ).argmin()

        # read in that sightline information
        # getline is 1-indexed
        line = linecache.getline(f'{EXTINCTION_DIR}/surot_A_Ks_table1.csv', min_dist_arg + 1)

        self.sightline = np.fromstring(line, dtype=float, sep=',')

        # for 5 locations the last radii is smaller than the 2nd last,
        # but the extinction is higher.
        # in such cases the last location is removed.
        if any(np.diff(self.sightline[5::4]) < 0):
            self.sightline = self.sightline[:-4]