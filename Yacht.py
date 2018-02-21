import pandas as p
import copy

# Make more yachts!
class Yacht():
	''''''

	def __init__(s, BaseYacht, changes):
		s.BaseYacht = BaseYacht
		s.IOR = copy.copy(BaseYacht.IOR)
		s.IOR.updateCert(changes)
		s.changes = changes
		s.ID = s.genID(changes)


	def genID(s, changes):
		ID = ""
		for var, val in changes[0].items():
			ID += "." + var + "-" + ('%f' % (round(val/3.28084, 3))).rstrip('0').rstrip('.')
		ID = ID[1:]

		if changes[1] != [0,0]:
			ID += "_" + str(changes[1][0]) + "." + str(changes[1][1])

		return ID


	def getSpeedDF(s):
		df = p.read_hdf(s.BaseYacht.VPPFile + '.h5', s.ID)
		df.columns = df.columns.map(float)
		return df


	def getSpeed(s, ws, wa):
		return s.getSpeedDF()[ws][wa]