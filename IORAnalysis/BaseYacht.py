from .IOR import IOR


class BaseYacht():
    '''
    Define the basic yachts from which changes are made

    Attributes
    ----------
    cert : dict
        Dictionary containing certificate values for the base yacht.
    VPPFile : str
        String containing path to VPP file for base yacht.
    '''

    def __init__(s, cert: dict, VPPFile: str):
        s.cert = cert
        s.VPPFile = VPPFile
        s.IOR = IOR(s.cert)
