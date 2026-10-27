# NX 2506
# Journal created by br435t on Tue Oct 27 10:07:59 2026 Pacific Daylight Time
#
import math
import NXOpen
def main(args) : 

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    # ----------------------------------------------
    #   Menu: Snap View
    # ----------------------------------------------
    matrix1 = NXOpen.Matrix3x3()
    
    matrix1.Xx = 0.47068592756955668
    matrix1.Xy = 0.88230083168270113
    matrix1.Xz = 0.0
    matrix1.Yx = -0.88230083168270113
    matrix1.Yy = 0.47068592756955668
    matrix1.Yz = 0.0
    matrix1.Zx = 0.0
    matrix1.Zy = -0.0
    matrix1.Zz = 1.0
    workPart.ModelingViews.WorkView.Orient(matrix1)
    
    markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Add View")
    
    view1 = workPart.Views.SaveAsPreservingCase(workPart.ModelingViews.WorkView, "Trimetric#1", True, False)
    
    markId2 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Rename View")
    
    modelingView1 = view1
    modelingView1.SetName("dxf normal")
    
    markId3 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Rename View")
    
    modelingView1.SetName("dxf_normal")
    
    # ----------------------------------------------
    #   Menu: Tools->Automation->Journal->Stop Recording
    # ----------------------------------------------
    
if __name__ == '__main__':
    main(sys.argv[1:])