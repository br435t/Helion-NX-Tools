# NX 2506
# Journal created by br435t on Fri Oct 16 15:34:47 2026 Pacific Daylight Time
#
import math
import NXOpen
import NXOpen.Assemblies
def main(args) : 

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    # ----------------------------------------------
    #   Menu: Edit->Properties...
    # ----------------------------------------------
    markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    
    objects1 = [NXOpen.NXObject.Null] * 1 
    component1 = workPart.ComponentAssembly.RootComponent.FindObject("COMPONENT 4835K32/NC 1")
    objects1[0] = component1
    assembliesGeneralPropertiesBuilder1 = workPart.PropertiesManager.CreateAssembliesGeneralPropertiesBuilder(objects1)
    
    assembliesGeneralPropertiesBuilder1.RealQuantity = 1.0
    
    objects2 = [NXOpen.NXObject.Null] * 1 
    objects2[0] = component1
    attributePropertiesBuilder1 = theSession.AttributeManager.CreateAttributePropertiesBuilder(workPart, objects2, NXOpen.AttributePropertiesBuilder.OperationType.NotSet)
    
    attributePropertiesBuilder1.IsArray = False
    
    attributePropertiesBuilder1.IsArray = False
    
    attributePropertiesBuilder1.IsArray = False
    
    attributePropertiesBuilder1.DataType = NXOpen.AttributePropertiesBaseBuilder.DataTypeOptions.String
    
    attributePropertiesBuilder1.Units = "Inch"
    
    objects3 = [NXOpen.NXObject.Null] * 1 
    objects3[0] = component1
    massPropertiesBuilder1 = workPart.PropertiesManager.CreateMassPropertiesBuilder(objects3)
    
    selectNXObjectList1 = massPropertiesBuilder1.SelectedObjects
    
    objects4 = selectNXObjectList1.GetArray()
    
    massPropertiesBuilder1.LoadPartialComponents = True
    
    massPropertiesBuilder1.Accuracy = 0.98999999999999999
    
    objects5 = [NXOpen.NXObject.Null] * 1 
    objects5[0] = component1
    objectGeneralPropertiesBuilder1 = workPart.PropertiesManager.CreateObjectGeneralPropertiesBuilder(objects5)
    
    selectNXObjectList2 = objectGeneralPropertiesBuilder1.SelectedObjects
    
    objectGeneralPropertiesBuilder1.Name = "4835K32"
    
    objectGeneralPropertiesBuilder1.NameLocationSpecified = False
    
    objectGeneralPropertiesBuilder1.Index = 1
    
    objects6 = [NXOpen.NXObject.Null] * 1 
    objects6[0] = component1
    assembliesParameterPropertiesBuilder1 = workPart.PropertiesManager.CreateAssembliesParameterPropertiesBuilder(objects6)
    
    selectComponentList1 = assembliesParameterPropertiesBuilder1.SelectedObjects
    
    objects7 = selectComponentList1.GetArray()
    
    assembliesParameterPropertiesBuilder1.Arrangements = NXOpen.Assemblies.AssembliesParameterPropertiesBuilder.ArrangementOptions.IndividuallyPositioned
    
    selectComponentList2 = assembliesParameterPropertiesBuilder1.SelectedObjects
    
    objects8 = selectComponentList2.GetArray()
    
    assembliesParameterPropertiesBuilder1.Arrangements = NXOpen.Assemblies.AssembliesParameterPropertiesBuilder.ArrangementOptions.SamePositionInAll
    
    objects9 = [NXOpen.NXObject.Null] * 1 
    objects9[0] = component1
    attributePropertiesBuilder1.SetAttributeObjects(objects9)
    
    attributePropertiesBuilder1.Units = "Inch"
    
    theSession.SetUndoMarkName(markId1, "Component Properties Dialog")
    
    nonGeometricState1 = component1.GetNonGeometricState()
    
    attributePropertiesBuilder1.DateValue.DateItem.Day = NXOpen.DateItemBuilder.DayOfMonth.Day16
    
    attributePropertiesBuilder1.DateValue.DateItem.Month = NXOpen.DateItemBuilder.MonthOfYear.Oct
    
    attributePropertiesBuilder1.DateValue.DateItem.Year = "2026"
    
    attributePropertiesBuilder1.DateValue.DateItem.Time = "00:00:00"
    
    selectNXObjectList3 = objectGeneralPropertiesBuilder1.SelectedObjects
    
    selectComponentList3 = assembliesParameterPropertiesBuilder1.SelectedObjects
    
    objects10 = selectComponentList3.GetArray()
    
    assembliesGeneralPropertiesBuilder1.SpecificColor = False
    
    markId2 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Component Properties")
    
    theSession.DeleteUndoMark(markId2, None)
    
    markId3 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "Component Properties")
    
    nXObject1 = assembliesGeneralPropertiesBuilder1.Commit()
    
    updateoption1 = massPropertiesBuilder1.UpdateOnSave
    
    nXObject2 = massPropertiesBuilder1.Commit()
    
    nXObject3 = objectGeneralPropertiesBuilder1.Commit()
    
    nXObject4 = assembliesParameterPropertiesBuilder1.Commit()
    
    id1 = theSession.GetNewestUndoMark(NXOpen.Session.MarkVisibility.Visible)
    
    nErrs1 = theSession.UpdateManager.DoUpdate(id1)
    
    theSession.DeleteUndoMark(markId3, None)
    
    theSession.SetUndoMarkName(id1, "Component Properties")
    
    assembliesGeneralPropertiesBuilder1.Destroy()
    
    attributePropertiesBuilder1.Destroy()
    
    massPropertiesBuilder1.Destroy()
    
    objectGeneralPropertiesBuilder1.Destroy()
    
    assembliesParameterPropertiesBuilder1.Destroy()
    
    theSession.CleanUpFacetedFacesAndEdges()
    
    # ----------------------------------------------
    #   Menu: Tools->Automation->Journal->Stop Recording
    # ----------------------------------------------
    
if __name__ == '__main__':
    main(sys.argv[1:])