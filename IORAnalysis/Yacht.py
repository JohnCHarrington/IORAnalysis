from .BaseYacht import BaseYacht
import pandas as p
import copy


class Yacht():
    '''
    Generates a yacht ID, runs IOR calculations and
    allows retrieval of speed data if it has been calculated.

    Attributes
    ----------
    BaseYacht : :obj:`IORAnalysis.BaseYacht.BaseYacht`
        The basis vessel to be modified, provides VPP file and
        initial IOR certificate values.
    IOR : :obj:`IORAnalysis.IOR.IOR`
        Instance of the IOR() class. Used to access all rating data.
    '''

    def __init__(s, BaseYacht: BaseYacht, changes: list=[{}, [0, 0]], h5ID: str=''):
        ''''''
        s.BaseYacht = BaseYacht
        s.h5ID = h5ID
        s.IOR = copy.copy(BaseYacht.IOR)
        s.changes = changes

    @property
    def changes(s):
        '''
        :obj:`list`:
            * :obj:`dict`
                Dictionary containing changes to certificate values for
                the yacht.
            * :obj:`list`
                List containing [Ballast Amount, Distance  Moved].
                Direction follows standard ship conventions, with
                upwards being positive.
        If blank, the yacht is a copy of the basis vessel, but can
        then be used to access VPP data if it exists.
        '''
        return s.__changes

    @changes.setter
    def changes(s, c: list):
        s.IOR.updateCert(c)
        s.__changes = c

    @property
    def h5ID(s):
        '''
        :obj:`str`:
            The identifier for the specific h5 file the VPP data for this
            yacht is stored in. Can be used to separate sets of data from
            the same basis vessel into different files, for instance one
            for each case study.
        '''
        return s.__h5ID

    @h5ID.setter
    def h5ID(s, h5ID: str):
        if (h5ID != ''):
            s.__h5ID = '.{}'.format(h5ID)
        else:
            s.__h5ID = ''

    @property
    def ID(s):
        '''
        str:
            Unique identifier string for this yacht, generated from *changes*.
        '''
        c = s.changes
        ID = ""
        for var in sorted(c[0]):
            ID += "." + var + "-" + \
                ('%f' % (round(c[0][var] / 3.28084, 3))
                 ).rstrip('0').rstrip('.')
        ID = ID[1:]

        if c[1] != [0, 0]:
            ID += "_" + str(c[1][0]) + "." + str(c[1][1])

        return ID

    def getSpeedDF(s) -> p.DataFrame:
        '''
        Returns the times for 1nm for this yacht.
        '''
        df = p.read_hdf('{}{}.h5'.format(s.BaseYacht.VPPFile, s.h5ID), s.ID)
        df.replace('-', 0.0, inplace=True)
        df.columns = df.columns.map(float)
        return df

    def getSpeed(s, ws: int, wa: int) -> int:
        '''
        Returns the time for 1nm for this yacht at the given wind speed
        and angle.
        '''
        return s.getSpeedDF()[ws][wa]
