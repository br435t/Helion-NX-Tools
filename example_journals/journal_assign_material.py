# NX 2506
# Journal created by br435t on Tue Oct 20 11:25:01 2026 Pacific Daylight Time
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
    
    physicalMaterial1 = workPart.MaterialManager.PhysicalMaterials.LoadFromMatmlLibrary("\\\\usantpvwtcor001\\NXStore\\NX_PROD_CUSTOM\\NXcustom\\NXcommonlibrary\\Materials\\helion_material_library.xml", "G-10 Garolite")
    
    objects1 = [NXOpen.NXObject.Null] * 1 
    body1 = workPart.Bodies.FindObject("EXTRUDE(1)2")
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
    markId4 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Assign Material")
    
    physicalMaterial2 = workPart.MaterialManager.PhysicalMaterials.LoadFromMatmlLibrary("\\\\usantpvwtcor001\\NXStore\\NX_PROD_CUSTOM\\NXcustom\\NXcommonlibrary\\Materials\\helion_material_library.xml", "Aluminum 7075")
    
    objects2 = [NXOpen.NXObject.Null] * 1 
    body2 = workPart.Bodies.FindObject("EXTRUDE(1)3")
    objects2[0] = body2
    physicalMaterial2.AssignObjects(objects2)
    
    theSession.DeleteUndoMark(markId4, None)
    
    theSession.SetUndoMarkName(id2, "Assign Material")
    
    physicalMaterialAssignBuilder2.Destroy()
    
    physicalMaterialListBuilder2.Destroy()
    
    markId5 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    
    physicalMaterialListBuilder3 = workPart.MaterialManager.PhysicalMaterials.CreateListBlockBuilder()
    
    physicalMaterialAssignBuilder3 = workPart.MaterialManager.PhysicalMaterials.CreateMaterialAssignBuilder()
    
    theSession.SetUndoMarkName(markId5, "Assign Material Dialog")
    
    id3 = theSession.GetNewestUndoMark(NXOpen.Session.MarkVisibility.AnyVisibility)
    
    # ----------------------------------------------
    #   Dialog Begin Assign Material
    # ----------------------------------------------
    markId6 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Assign Material")
    
    physicalMaterial3 = workPart.MaterialManager.PhysicalMaterials.LoadFromMatmlLibrary("\\\\usantpvwtcor001\\NXStore\\NX_PROD_CUSTOM\\NXcustom\\NXcommonlibrary\\Materials\\helion_material_library.xml", "Nylon 6/6 Plastic")
    
    objects3 = [NXOpen.NXObject.Null] * 1 
    body3 = workPart.Bodies.FindObject("EXTRUDE(1)")
    objects3[0] = body3
    physicalMaterial3.AssignObjects(objects3)
    
    theSession.DeleteUndoMark(markId6, None)
    
    theSession.SetUndoMarkName(id3, "Assign Material")
    
    physicalMaterialAssignBuilder3.Destroy()
    
    physicalMaterialListBuilder3.Destroy()
    
    markId7 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    
    physicalMaterialListBuilder4 = workPart.MaterialManager.PhysicalMaterials.CreateListBlockBuilder()
    
    physicalMaterialAssignBuilder4 = workPart.MaterialManager.PhysicalMaterials.CreateMaterialAssignBuilder()
    
    theSession.SetUndoMarkName(markId7, "Assign Material Dialog")
    
    id4 = theSession.GetNewestUndoMark(NXOpen.Session.MarkVisibility.AnyVisibility)
    
    # ----------------------------------------------
    #   Dialog Begin Assign Material
    # ----------------------------------------------
    markId8 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Assign Material")
    
    physicalMaterial4 = workPart.MaterialManager.PhysicalMaterials.LoadFromMatmlLibrary("\\\\usantpvwtcor001\\NXStore\\NX_PROD_CUSTOM\\NXcustom\\NXcommonlibrary\\Materials\\helion_material_library.xml", "Glass")
    
    objects4 = [NXOpen.NXObject.Null] * 1 
    body4 = workPart.Bodies.FindObject("EXTRUDE(1)1")
    objects4[0] = body4
    physicalMaterial4.AssignObjects(objects4)
    
    theSession.DeleteUndoMark(markId8, None)
    
    theSession.SetUndoMarkName(id4, "Assign Material")
    
    physicalMaterialAssignBuilder4.Destroy()
    
    physicalMaterialListBuilder4.Destroy()
    
    markId9 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    
    physicalMaterialListBuilder5 = workPart.MaterialManager.PhysicalMaterials.CreateListBlockBuilder()
    
    physicalMaterialAssignBuilder5 = workPart.MaterialManager.PhysicalMaterials.CreateMaterialAssignBuilder()
    
    theSession.SetUndoMarkName(markId9, "Assign Material Dialog")
    
    id5 = theSession.GetNewestUndoMark(NXOpen.Session.MarkVisibility.AnyVisibility)
    
    # ----------------------------------------------
    #   Dialog Begin Assign Material
    # ----------------------------------------------
    physicalMaterialAssignBuilder5.Destroy()
    
    physicalMaterialListBuilder5.Destroy()
    
    theSession.UndoToMark(id5, None)
    
    theSession.DeleteUndoMark(id5, None)
    
    theSession.CleanUpFacetedFacesAndEdges()
    
    # ----------------------------------------------
    #   Menu: Tools->Automation->Journal->Stop Recording
    # ----------------------------------------------
    
if __name__ == '__main__':
    main(sys.argv[1:])