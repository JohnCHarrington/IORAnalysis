import pandas as p
from sys import platform
if (platform == "win32"):
    import autoit
import json
from io import StringIO
import multiprocessing as mp

def log(msg):
    with open('log.txt', 'w') as f:
        f.write(msg)

class WinDes():
    '''
    Wrap WinDes4 class, enforce usage within 'with' e.g: "with WinDes() as VPP:"
    This ensures queue will always be either run or saved to file after use without continuous file changes.
    '''

    def __enter__(s):
        class WinDes4():
            ''' 
            Run WinDesign4 through PyAutoIt. Allows queueing of yachts for analysis when 
            WinDesign is not available. Yachts are stored in HDF5 database with name format: 
            "SailVar1-SailVal1.SailVarN-SailValN_BallastWeight-BallastDistance"

            Currently allows setting Sail variables: 
            ["P", "E", "BAD", "IG", "J", "LP", "HBI", "ISP", "SPL", "SMW", "SLU", "SLE"]
            and adjusting VCG by giving a ballast weight and distance.

            Like most of the IORAnalysis Module, this class is currently hard-coded for Indulgence.
            '''

            def __init__(s):
                try:  # Attempt to open queue file
                    with open('queue.json') as q_file:
                        s.q = json.load(q_file)
                # If queue file does not exist, define new empty queue
                except (OSError, IOError):
                    s.q = []

            def queue(s, Yacht):
                '''
                Adds a new yacht to the current queue, 
                if it isn't already there
                '''

                queueYacht = [Yacht.ID, Yacht.changes[0],
                              Yacht.changes[1], Yacht.BaseYacht.VPPFile, Yacht.h5ID]
                try:
                    s.q.index(queueYacht)
                except ValueError:
                    s.q.append(queueYacht)

            def saveQueue(s):
                '''Writes the current queue to a file'''

                with open('queue.json', 'w') as q_file:
                    json.dump(s.q, q_file)

            def isWinDesInstalled(s):
                if (platform == "win32"):
                    return True
                return False

            def openWinDes(s):
                autoit.win_activate('WinDesign4')

            def runYacht(s, yachtParams):
                '''
                Opens a new instance of BaseYacht VPP File in WinDesign4, sets
                required parameters, runs analysis and saves results to file
                '''

                autoit.opt("SendKeyDelay", 250)
                autoit.send("!fo" + yachtParams[3][0])
                autoit.opt("SendKeyDelay", 10)
                autoit.send(yachtParams[3][1:])
                autoit.send("{ENTER}")

                # Set Sail Parameters

                for var, val in yachtParams[1].items():
                    # Find Index of req. variable and add 5 to get TabNo
                    varArray = ["P", "E", "BAS", "IG", "J", "LPG",
                                "HB", "ISP", "SPL", "SMW", "SLU", "SLE"]
                    try:
                        tabNo = varArray.index(var) + 5
                    except ValueError:
                        continue

                    autoit.opt("SendKeyDelay", 250)
                    autoit.send("!yd")
                    autoit.win_wait_active("Yacht Define & Automake")
                    autoit.opt("SendKeyDelay", 10)
                    autoit.send("{TAB " + str(tabNo) + "}" + str(val / 3.28084) + "{TAB " + str(36 - tabNo) + "}{SPACE}{TAB}{SPACE}{TAB}{SPACE}{TAB}{SPACE}{ENTER}")

                # Set Ballast

                if yachtParams[2] != [0, 0]:
                    autoit.send("!yf")
                    # TODO: Make this work for any yacht name
                    autoit.win_wait_active("Flotation List Edit - Indulgence")
                    autoit.send("{TAB}{ENTER}")
                    autoit.win_wait_active(
                        "Flot: Condition 1     Method: Standard WinDesign")
                    autoit.send("{TAB}^C^{TAB 2}{TAB 7}" + str(-((yachtParams[2][0] * 0.45359237) * (yachtParams[2][1] * 0.3048) / autoit.clip_get())) + "{ENTER}")

                # Run Yacht and Save Data

                autoit.opt("SendKeyDelay", 250)
                # Hit the "Copy Full Report of Tables" Button
                autoit.send("{ESC}{F5}!f")
                autoit.opt("SendKeyDelay", 10)
                autoit.send("{DOWN 14}{ENTER}")

                # Close Yacht
                autoit.send("!fcn")

                return autoit.clip_get(1610612736)

            def saveYacht(s, yachtParams, result):
                r = result[12:].split('\n\n\n')  # Split tables from clipboard
                # Grab table 14 and pretend it's a file!
                stringFile = StringIO(r[13])
                # Read the pretend file into a dataframe
                df = p.read_csv(stringFile, sep='\t', skiprows={
                                                19, 20}, header=1, index_col=0)
                # Drop pointless empty last column which has magically appeared
                df.drop(df.columns[len(df.columns) - 1], axis=1, inplace=True)
                # Set column names to floats, as they're strings by default
                df.columns = df.columns.map(float)
                # Aaaand breathe...we've saved that data
                df.to_hdf('{}{}.h5'.format(yachtParams[3], yachtParams[4]), yachtParams[0])
                log("Data Saved for {}".format(yachtParams[0]))

            def runQueue(s):
                '''Runs analysis of all yachts currently queued'''

                s.openWinDes()
                autoit.win_wait_active("WinDesign4")
                for yacht in s.q[:]:
                    r = s.runYacht(yacht)
                    s.saveYacht(yacht, r)
                    s.q.remove(yacht)

        s.VPPObj = WinDes4()
        return s.VPPObj

    def __exit__(s, exc_type, exc_value, traceback):
        s.VPPObj.saveQueue()
