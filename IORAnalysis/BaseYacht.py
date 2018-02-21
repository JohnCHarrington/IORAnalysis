from .IOR import IOR

# Define the basic yachts from which changes are made, takes a base certificate and a VPP file
class BaseYacht():
	"""docstring for BaseYacht"""

	def __init__(s, cert, VPPFile):
		s.cert = cert
		s.VPPFile = VPPFile
		s.IOR = IOR(s.cert)