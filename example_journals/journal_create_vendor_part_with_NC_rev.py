# NX 2506
# Journal created by br435t on Wed Oct 14 14:43:02 2026 Pacific Daylight Time
#
import math
import NXOpen
import NXOpen.PDM
def main(args) : 

    theSession  = NXOpen.Session.GetSession() #type: NXOpen.Session
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    # ----------------------------------------------
    #   Menu: File->New->Item...
    # ----------------------------------------------
    markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")
    
    fileNew1 = theSession.Parts.FileNew()
    
    fileNew1.TemplateFileName = "@DB/model-plain-1-inch-template/A"
    
    fileNew1.UseBlankTemplate = False
    
    fileNew1.ApplicationName = "ModelTemplate"
    
    fileNew1.Units = NXOpen.Part.Units.Inches
    
    fileNew1.RelationType = "master"
    
    fileNew1.UsesMasterModel = "No"
    
    fileNew1.TemplateType = NXOpen.FileNewTemplateType.Item
    
    fileNew1.TemplatePresentationName = "Model"
    
    fileNew1.ItemType = "BE9_Design,BE9_Electrical,BE9_COTS,BE9_Tooling"
    
    fileNew1.Specialization = ""
    
    fileNew1.SetCanCreateAltrep(False)
    
    partOperationCreateBuilder1 = theSession.PdmSession.CreateCreateOperationBuilder(NXOpen.PDM.PartOperationBuilder.OperationType.Create)
    
    fileNew1.SetPartOperationCreateBuilder(partOperationCreateBuilder1)
    
    partOperationCreateBuilder1.SetOperationSubType(NXOpen.PDM.PartOperationCreateBuilder.OperationSubType.FromTemplate)
    
    partOperationCreateBuilder1.SetModelType("master")
    
    partOperationCreateBuilder1.SetItemType("BE9_Design")
    
    logicalobjects1 = partOperationCreateBuilder1.CreateLogicalObjects()
    
    sourceobjects1 = logicalobjects1[0].GetUserAttributeSourceObjects()
    
    partOperationCreateBuilder1.DefaultDestinationFolder = ":MCMASTER"
    
    sourceobjects2 = logicalobjects1[0].GetUserAttributeSourceObjects()
    
    partOperationCreateBuilder1.SetOperationSubType(NXOpen.PDM.PartOperationCreateBuilder.OperationSubType.FromTemplate)
    
    sourceobjects3 = logicalobjects1[0].GetUserAttributeSourceObjects()
    
    theSession.SetUndoMarkName(markId1, "New Dialog")
    
    partOperationCreateBuilder1.SetItemType("BE9_COTS")
    
    logicalobjects2 = partOperationCreateBuilder1.CreateLogicalObjects()
    
    sourceobjects4 = logicalobjects2[0].GetUserAttributeSourceObjects()
    
    objects1 = []
    attributePropertiesBuilder1 = theSession.AttributeManager.CreateAttributePropertiesBuilder(NXOpen.BasePart.Null, objects1, NXOpen.AttributePropertiesBuilder.OperationType.Create)
    
    objects2 = []
    attributePropertiesBuilder1.SetAttributeObjects(objects2)
    
    objects3 = [NXOpen.NXObject.Null] * 1 
    objects3[0] = sourceobjects4[0]
    attributePropertiesBuilder1.SetAttributeObjects(objects3)
    
    attributePropertiesBuilder1.Title = "DB_PART_REV"
    
    attributePropertiesBuilder1.Category = "BE9_COTSRevision"
    
    attributePropertiesBuilder1.StringValue = "NC"
    
    attributePropertiesBuilder1.Category = "BE9_COTSRevision"
    
    changed1 = attributePropertiesBuilder1.CreateAttribute()
    
    attributetitles1 = []
    titlepatterns1 = []
    nXObject1 = partOperationCreateBuilder1.CreateAttributeTitleToNamingPatternMap(attributetitles1, titlepatterns1)
    
    objects4 = [NXOpen.NXObject.Null] * 1 
    objects4[0] = logicalobjects2[0]
    properties1 = [NXOpen.NXObject.Null] * 1 
    properties1[0] = nXObject1
    errorList1 = partOperationCreateBuilder1.AutoAssignAttributesWithNamingPattern(objects4, properties1)
    
    errorList1.Dispose()
    errorMessageHandler1 = partOperationCreateBuilder1.GetErrorMessageHandler(True)
    
    attributePropertiesBuilder1.Title = "DB_PART_NO"
    
    attributePropertiesBuilder1.Category = "BE9_COTS"
    
    attributePropertiesBuilder1.StringValue = "vendor_pn"
    
    attributePropertiesBuilder1.Category = "BE9_COTS"
    
    changed2 = attributePropertiesBuilder1.CreateAttribute()
    
    attributePropertiesBuilder1.Title = "DB_PART_NAME"
    
    attributePropertiesBuilder1.StringValue = "vendor_description"
    
    attributePropertiesBuilder1.Category = "BE9_COTS"
    
    changed3 = attributePropertiesBuilder1.CreateAttribute()
    
    attributePropertiesBuilder1.Title = "HE_Manufacturer"
    
    attributePropertiesBuilder1.Category = "BE9_COTSRevision"
    
    attributePropertiesBuilder1.StringValue = "vendor_name"
    
    attributePropertiesBuilder1.Category = "BE9_COTSRevision"
    
    changed4 = attributePropertiesBuilder1.CreateAttribute()
    
    attributePropertiesBuilder1.Title = "Item:revision:ItemRevision:be9_PartClass"
    
    attributePropertiesBuilder1.StringValue = "Class III"
    
    attributePropertiesBuilder1.Category = "BE9_COTSRevision"
    
    changed5 = attributePropertiesBuilder1.CreateAttribute()
    
    markId2 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "New")
    
    theSession.DeleteUndoMark(markId2, None)
    
    markId3 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "New")
    
    fileNew1.TemplateFileName = "@DB/model-plain-1-inch-template/A"
    
    fileNew1.UseBlankTemplate = False
    
    fileNew1.ApplicationName = "ModelTemplate"
    
    fileNew1.Units = NXOpen.Part.Units.Inches
    
    fileNew1.RelationType = "master"
    
    fileNew1.UsesMasterModel = "No"
    
    fileNew1.TemplateType = NXOpen.FileNewTemplateType.Item
    
    fileNew1.TemplatePresentationName = "Model"
    
    fileNew1.ItemType = "BE9_Design,BE9_Electrical,BE9_COTS,BE9_Tooling"
    
    fileNew1.Specialization = ""
    
    fileNew1.SetCanCreateAltrep(False)
    
    fileNew1.MasterFileName = ""
    
    fileNew1.MakeDisplayedPart = True
    
    fileNew1.DisplayPartOption = NXOpen.DisplayPartOption.AllowAdditional
    
    partOperationCreateBuilder1.ValidateLogicalObjectsToCommit()
    
    logicalobjects3 = [NXOpen.PDM.LogicalObject.Null] * 1 
    logicalobjects3[0] = logicalobjects2[0]
    partOperationCreateBuilder1.CreateSpecificationsForLogicalObjects(logicalobjects3)
    
    errorMessageHandler2 = partOperationCreateBuilder1.GetErrorMessageHandler(True)
    
    errorMessageHandler3 = partOperationCreateBuilder1.GetErrorMessageHandler(True)
    
    theSession.UndoToMarkWithStatus(markId3, None)
    
    theSession.DeleteUndoMark(markId3, None)
    
    attributePropertiesBuilder1.Title = "DB_PART_NO"
    
    attributePropertiesBuilder1.Category = "BE9_COTS"
    
    attributePropertiesBuilder1.StringValue = "vendor_pn_test"
    
    attributePropertiesBuilder1.Category = "BE9_COTS"
    
    changed6 = attributePropertiesBuilder1.CreateAttribute()
    
    markId4 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "New")
    
    theSession.DeleteUndoMark(markId4, None)
    
    markId5 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Invisible, "New")
    
    fileNew1.TemplateFileName = "@DB/model-plain-1-inch-template/A"
    
    fileNew1.UseBlankTemplate = False
    
    fileNew1.ApplicationName = "ModelTemplate"
    
    fileNew1.Units = NXOpen.Part.Units.Inches
    
    fileNew1.RelationType = "master"
    
    fileNew1.UsesMasterModel = "No"
    
    fileNew1.TemplateType = NXOpen.FileNewTemplateType.Item
    
    fileNew1.TemplatePresentationName = "Model"
    
    fileNew1.ItemType = "BE9_Design,BE9_Electrical,BE9_COTS,BE9_Tooling"
    
    fileNew1.Specialization = ""
    
    fileNew1.SetCanCreateAltrep(False)
    
    fileNew1.MasterFileName = ""
    
    fileNew1.MakeDisplayedPart = True
    
    fileNew1.DisplayPartOption = NXOpen.DisplayPartOption.AllowAdditional
    
    partOperationCreateBuilder1.ValidateLogicalObjectsToCommit()
    
    logicalobjects4 = [NXOpen.PDM.LogicalObject.Null] * 1 
    logicalobjects4[0] = logicalobjects2[0]
    partOperationCreateBuilder1.CreateSpecificationsForLogicalObjects(logicalobjects4)
    
    errorMessageHandler4 = partOperationCreateBuilder1.GetErrorMessageHandler(True)
    
    errorMessageHandler5 = partOperationCreateBuilder1.GetErrorMessageHandler(True)
    
    nXObject2 = fileNew1.Commit()
    
    workPart = theSession.Parts.Work # vendor_pn_test.NC/vendor_description
    displayPart = theSession.Parts.Display # vendor_pn_test.NC/vendor_description
    errorMessageHandler6 = partOperationCreateBuilder1.GetErrorMessageHandler(True)
    
    theSession.DeleteUndoMark(markId5, None)
    
    fileNew1.Destroy()
    
    attributePropertiesBuilder1.Destroy()
    
    theSession.CleanUpFacetedFacesAndEdges()
    
    # ----------------------------------------------
    #   Menu: Tools->Automation->Journal->Stop Recording
    # ----------------------------------------------
    
if __name__ == '__main__':
    main(sys.argv[1:])