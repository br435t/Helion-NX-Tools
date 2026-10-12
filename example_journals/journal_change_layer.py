# NX 2506
# Journal created by br435t on Mon Oct 12 13:57:19 2026 Pacific Daylight Time
#
import math
import NXOpen
import NXOpen.Layer
def main(args) : 

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    # ----------------------------------------------
    #   Menu: Format->Layer Settings...
    # ----------------------------------------------
    markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    
    theSession.SetUndoMarkName(markId1, "Layer Settings Dialog")
    
    theSession.SetUndoMarkName(markId1, "Layer Settings")
    
    theSession.DeleteUndoMark(markId1, None)
    
    # ----------------------------------------------
    #   Menu: Format->Move to Layer...
    # ----------------------------------------------
    markId2 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Move Layer")
    
    markId3 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Start")
    
    theSession.SetUndoMarkName(markId3, "Class Selection Dialog")
    
    markId4 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Class Selection")
    
    theSession.DeleteUndoMark(markId4, None)
    
    markId5 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Class Selection")
    
    theSession.DeleteUndoMark(markId5, None)
    
    theSession.SetUndoMarkName(markId3, "Class Selection")
    
    theSession.DeleteUndoMark(markId3, None)
    
    # ----------------------------------------------
    #   Dialog Begin Layer Move
    # ----------------------------------------------
    objectArray1 = [NXOpen.DisplayableObject.Null] * 1 
    body1 = workPart.Bodies.FindObject("UNPARAMETERIZED_FEATURE(1)")
    objectArray1[0] = body1
    workPart.Layers.MoveDisplayableObjects(70, objectArray1)
    
    # ----------------------------------------------
    #   Menu: Tools->Automation->Journal->Stop Recording
    # ----------------------------------------------
    
if __name__ == '__main__':
    main(sys.argv[1:])