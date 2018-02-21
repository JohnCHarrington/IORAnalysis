import pandas as p
import autoit
import json
from io import StringIO

# First, a utility class for accessing WinDes
class WinDes():
	'''
	Wrapper for WinDes4 class, enforces usage within with e.g: "with WinDes() as VPP:"
	This ensures queue will always be either run or saved to file after use without continuous file changes.
	'''

	def __enter__(s):
		class WinDes4():
			'''	
			Runs WinDesign4 through PyAutoIt. Allows queueing of yachts for analysis when WinDesign is not available.
			Yachts are stored in HDF5 database with name format: "SailVar1-SailVal1.SailVarN-SailValN_BallastWeight-BallastDistance"

			Currently allows setting Sail variables: ["P", "E", "BAD", "IG", "J", "LP", "HBI", "ISP", "SPL", "SMW", "SLU", "SLE"]
				and adjusting VCG by giving a ballast weight and distance.

			Like most of the IORAnalysis Module, this class is currently hard-coded for Indulgence.
			'''

			def __init__(s):
				try: # Attempt to open queue file
					with open('queue.json') as q_file:
						s.q = json.load(q_file)
				except FileNotFoundError: # If queue file does not exist, define new empty queue
					s.q = []


			def queue(s, Yacht):
				'''Adds a new yacht to the current queue, if it isn't already there'''

				queueYacht = [Yacht.ID, Yacht.changes[0],  Yacht.changes[1], Yacht.BaseYacht.VPPFile]
				try:
					s.q.index(queueYacht)
				except ValueError:
					s.q.append(queueYacht)


			def saveQueue(s):
				'''Writes the current queue to a file'''

				with open('queue.json', 'w') as q_file:
					json.dump(s.q, q_file)


			def isWinDesInstalled(s):
				return False


			def openWinDes(s):
				autoit.run('WinDesign4')
				autoit.win_activate('WinDesign4')


			def runYacht(s, yachtParams):
				'''Opens a new instance of BaseYacht VPP File in WinDesign4, sets required parameters, runs analysis and saves results to file'''

				autoit.opt("SendKeyDelay",400)
				autoit.send("!fo" + yachtParams[3][0])
				autoit.opt("SendKeyDelay",10)
				autoit.send(yachtParams[3][1:])
				autoit.send("{ENTER}")

				# Set Sail Parameters

				for var, val in yachtParams[1]:
					varArray = ["P", "E", "BAD", "IG", "J", "LP", "HBI", "ISP", "SPL", "SMW", "SLU", "SLE"] # Find Index of req. variable and add 5 to get TabNo
					try:
						tabNo = varArray.index(var) + 5
					except ValueError:
						continue

					autoit.opt("SendKeyDelay",400)
					autoit.send("!yd")
					autoit.win_wait_active("Yacht Define & Automake")
					autoit.opt("SendKeyDelay",10)
					autoit.send("{TAB " + tabNo + "}" + val + "{TAB " + (36 - tabNo) + "}{SPACE}{TAB}{SPACE}{TAB}{SPACE}{TAB}{SPACE}{ENTER}")

				# Set Ballast

				if yachtParams[2] != [0,0]:
					autoit.send("!yf")
					autoit.win_wait_active("Flotation List Edit - Indulgence") # TODO: Make this work for any yacht name
					autoit.send("{TAB}{ENTER}")
					autoit.win_wait_active("Flot: Condition 1     Method: Standard WinDesign")
					autoit.send("^{TAB 2}{LEFT}{TAB 9}" & yachtParams[2][0]*yachtParams[2][1]/disp & "{ENTER}") # TODO: Find disp. value
					
				# Run Yacht and Save Data

				autoit.send("{F5}!f{DOWN 14}{ENTER}") # Hit the "Copy Full Report of Tables" Button
				r = autoit.clip_get()[12:].split('\n\n\n') # Split tables from clipboard
				stringFile = StringIO(r[13]) # Grab table 14 and pretend it's a file!
				df = p.read_csv(stringFile, sep='\t', skiprows={19,20}, header=1, index_col=0) # Read the pretend file into a dataframe
				df.drop(df.columns[len(df.columns)-1], axis=1, inplace=True) # Drop pointless empty last column which has magically appeared
				df.columns = df.columns.map(float) # Set column names to floats, as they're strings by default
				df.to_hdf(yachtParams[3] + '.h5', yachtParams[0]) # Aaaand breathe...we've saved that data

				# Close Yacht

			def runQueue(s):
				'''Runs analysis of all yachts currently queued'''

				s.openWinDes()
				autoit.win_wait_active("WinDesign4")
				for yacht in s.q[:]:
					runYacht(yacht)
					s.q.remove(yacht)

		s.VPPObj = WinDes4()
		return s.VPPObj


	def __exit__(s, exc_type, exc_value, traceback):
		if s.VPPObj.isWinDesInstalled():
			s.VPPObj.runQueue()
		else:
			s.VPPObj.saveQueue()