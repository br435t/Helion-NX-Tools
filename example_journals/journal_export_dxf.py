# NX 2506
# Journal created by br435t on Tue Oct 27 10:05:30 2026 Pacific Daylight Time
#
import math
import NXOpen
def main(args) : 

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    # ----------------------------------------------
    #   Menu: File->Export->AutoCAD DXF/DWG...
    # ----------------------------------------------
    markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    
    dxfdwgCreator1 = theSession.DexManager.CreateDxfdwgCreator()
    
    dxfdwgCreator1.ExportData = NXOpen.DxfdwgCreator.ExportDataOption.Drawing
    
    dxfdwgCreator1.AutoCADRevision = NXOpen.DxfdwgCreator.AutoCADRevisionOptions.R2004
    
    dxfdwgCreator1.ViewEditMode = True
    
    dxfdwgCreator1.FlattenAssembly = True
    
    dxfdwgCreator1.ExportScaleValue = 1.0
    
    dxfdwgCreator1.SettingsFile = "C:\\SPLM\\NX\\NX2506\\dxfdwg\\dxfdwg.def"
    
    dxfdwgCreator1.OutputFileType = NXOpen.DxfdwgCreator.OutputFileTypeOption.Dwg
    
    dxfdwgCreator1.ExportData = NXOpen.DxfdwgCreator.ExportDataOption.Modeling
    
    dxfdwgCreator1.ExportSelectionBlock.SelectionScope = NXOpen.ObjectSelector.Scope.SelectedObjects
    
    dxfdwgCreator1.ObjectTypes.Curves = True
    
    dxfdwgCreator1.ObjectTypes.Annotations = True
    
    dxfdwgCreator1.ObjectTypes.Structures = True
    
    dxfdwgCreator1.FlattenAssembly = False
    
    dxfdwgCreator1.ExportDestination = NXOpen.BaseCreator.ExportDestinationOption.NativeFileSystem
    
    dxfdwgCreator1.OutputFile = "C:\\Code\\Helion-NX-Tools\\example_journals\\DXF_export_output\\1152112-001.01_TEMP.dwg"
    
    dxfdwgCreator1.InputFile = "@DB/1152112-001/01"
    
    dxfdwgCreator1.ExportDestination = NXOpen.BaseCreator.ExportDestinationOption.NativeFileSystem
    
    dxfdwgCreator1.OutputFile = "C:\\Code\\Helion-NX-Tools\\example_journals\\DXF_export_output\\1152112-001.01_TEMP_1.dwg"
    
    theSession.SetUndoMarkName(markId1, "Export AutoCAD DXF/DWG File Dialog")
    
    dxfdwgCreator1.OutputFileType = NXOpen.DxfdwgCreator.OutputFileTypeOption.Dxf
    
    dxfdwgCreator1.ExportDestination = NXOpen.BaseCreator.ExportDestinationOption.NativeFileSystem
    
    dxfdwgCreator1.OutputFile = "C:\\Code\\Helion-NX-Tools\\example_journals\\DXF_export_output\\1152112-001.01_TEMP_1.dxf"
    
    # ----------------------------------------------
    #   Dialog Begin Export AutoCAD DXF/DWG File
    # ----------------------------------------------
    dxfdwgCreator1.ExportSelectionBlock.SelectionScope = NXOpen.ObjectSelector.Scope.EntirePart
    
    dxfdwgCreator1.ExportSelectionBlock.SelectionScope = NXOpen.ObjectSelector.Scope.SelectedObjects
    
    body1 = workPart.Bodies.FindObject("EXTRUDE(1)")
    added1 = dxfdwgCreator1.ExportSelectionBlock.SelectionComp.Add(body1)
    
    # ----------------------------------------------
    #   Dialog Begin Export AutoCAD DXF/DWG File
    # ----------------------------------------------
    markId2 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Export AutoCAD DXF/DWG File")
    
    theSession.DeleteUndoMark(markId2, None)
    
    markId3 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Export AutoCAD DXF/DWG File")
    
    dxfdwgCreator1.ExportDestination = NXOpen.BaseCreator.ExportDestinationOption.NativeFileSystem
    
    dxfdwgCreator1.OutputFile = "C:\\Code\\Helion-NX-Tools\\example_journals\\DXF_export_output\\1152112-001.01_TEMP_1.dxf"
    
    dxfdwgCreator1.TextFontMappingFile = "C:\\Users\\br435t\\AppData\\Local\\Temp\\br43l7_yrh1o_1svp.txt"
    
    dxfdwgCreator1.WidthFactorMode = NXOpen.DxfdwgCreator.WidthfactorMethodOptions.AutomaticCalculation
    
    dxfdwgCreator1.LayerMask = "1-256"
    
    dxfdwgCreator1.DrawingList = "_ALL_"
    
    dxfdwgCreator1.ViewList = "\"Top\""
    
    dxfdwgCreator1.ProcessHoldFlag = True
    
    nXObject1 = dxfdwgCreator1.Commit()
    
    theSession.DeleteUndoMark(markId3, None)
    
    theSession.SetUndoMarkName(markId1, "Export AutoCAD DXF/DWG File")
    
    dxfdwgCreator1.Destroy()
    
    # ----------------------------------------------
    #   Menu: File->
    # ----------------------------------------------
    # ----------------------------------------------
    #   Menu: Tools->Automation->Journal->Stop Recording
    # ----------------------------------------------
    
if __name__ == '__main__':
    main(sys.argv[1:])