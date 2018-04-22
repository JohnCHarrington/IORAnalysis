'''
Generates a yacht ID, runs IOR calculations and
allows retrieval of speed data if it has been calculated.
'''

import pandas as p
import copy


class Yacht():
    ''''''

    def __init__(s, BaseYacht, changes=[{}, [0, 0]], h5ID=''):
        s.BaseYacht = BaseYacht
        s.h5ID = h5ID
        if (s.h5ID != ''):
            s.h5ID = '.{}'.format(s.h5ID)
        s.IOR = copy.copy(BaseYacht.IOR)
        s.IOR.updateCert(changes)
        s.changes = changes
        s.ID = s.genID(changes)

    def genID(s, c):
        ID = ""
        for var in sorted(c[0]):
            ID += "." + var + "-" + \
                ('%f' % (round(c[0][var] / 3.28084, 3))
                 ).rstrip('0').rstrip('.')
        ID = ID[1:]

        if c[1] != [0, 0]:
            ID += "_" + str(c[1][0]) + "." + str(c[1][1])

        return ID

    def getSpeedDF(s):
        df = p.read_hdf('{}{}.h5'.format(s.BaseYacht.VPPFile, s.h5ID), s.ID)
        df.replace('-', 0.0, inplace=True)
        df.columns = df.columns.map(float)
        return df

    def getSpeed(s, ws, wa):
        return s.getSpeedDF()[ws][wa]
