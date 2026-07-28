# NX 2506
# Journal created by br435t on Tue Jul 28 14:47:44 2026 Pacific Daylight Time
#
import math
import NXOpen
def main(args) : 

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    # ----------------------------------------------
    #   Menu: File->Open...
    # ----------------------------------------------
    # Potential journal callback detected. Pausing journal.
    
if __name__ == '__main__':
    main(sys.argv[1:])