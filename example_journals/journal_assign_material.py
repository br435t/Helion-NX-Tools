# NX 2506
# Journal created by br435t on Tue Oct 20 10:35:44 2026 Pacific Daylight Time
#
import math
import NXOpen
import NXOpen.PhysMat
def main(args) : 

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    
    physicalMaterialListBuilder1 = workPart.MaterialManager.PhysicalMaterials.CreateListBlockBuilder()
    
    physicalMaterialAssignBuilder1 = workPart.MaterialManager.PhysicalMaterials.CreateMaterialAssignBuilder()
    
    theSession.SetUndoMarkName(markId1, "Assign Material Dialog")
    
    id1 = theSession.GetNewestUndoMark(NXOpen.Session.MarkVisibility.AnyVisibility)
    
    markId2 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Assign Material")
    
    physicalMaterial1 = workPart.MaterialManager.PhysicalMaterials.FindObject("PhysicalMaterial[Stainless Steel AISI 304]")
    objects1 = [NXOpen.NXObject.Null] * 1 
    body1 = workPart.Bodies.FindObject("UNPARAMETERIZED_FEATURE(1)")
    objects1[0] = body1
    physicalMaterial1.AssignObjects(objects1)
    
    theSession.DeleteUndoMark(markId2, None)
    
    theSession.SetUndoMarkName(id1, "Assign Material")
    
    physicalMaterialAssignBuilder1.Destroy()
    
    physicalMaterialListBuilder1.Destroy()
    
    markId3 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    
    physicalMaterialListBuilder2 = workPart.MaterialManager.PhysicalMaterials.CreateListBlockBuilder()
    
    physicalMaterialAssignBuilder2 = workPart.MaterialManager.PhysicalMaterials.CreateMaterialAssignBuilder()
    
    theSession.SetUndoMarkName(markId3, "Assign Material Dialog")
    
    id2 = theSession.GetNewestUndoMark(NXOpen.Session.MarkVisibility.AnyVisibility)
    
    # ----------------------------------------------
    #   Dialog Begin Assign Material
    # ----------------------------------------------
    physicalMaterialAssignBuilder2.Destroy()
    
    physicalMaterialListBuilder2.Destroy()
    
    theSession.UndoToMark(id2, None)
    
    theSession.DeleteUndoMark(id2, None)
    
    theSession.CleanUpFacetedFacesAndEdges()
    
    # ----------------------------------------------
    #   Menu: Tools->Automation->Journal->Stop Recording
    # ----------------------------------------------
    
if __name__ == '__main__':
    main(sys.argv[1:])