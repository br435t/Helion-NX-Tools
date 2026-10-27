# NX 2506
# Journal created by br435t on Tue Oct 27 11:41:36 2026 Pacific Daylight Time
#
import math
import NXOpen
def main(args) : 

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    # ----------------------------------------------
    #   Menu: Shaded Type->Fully Shaded
    # ----------------------------------------------
    workPart.ModelingViews.WorkView.ShadedDisplayType = NXOpen.View.ShadedDisplayModeType.FullyShaded
    
    # ----------------------------------------------
    #   Menu: Tools->Automation->Journal->Stop Recording
    # ----------------------------------------------
    
if __name__ == '__main__':
    main(sys.argv[1:])