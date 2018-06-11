'''
This module provides tools for the analysis of IOR era yachts,
using VPP files for each yacht and values from it's rating
certificate.

It allows changes to be made to the yacht rigging, which can
then have it's new rating calculated and it's performance
tested in the VPP.
'''
from .IOR import IOR
from .WinDes import WinDes
from .BaseYacht import BaseYacht
from .Yacht import Yacht