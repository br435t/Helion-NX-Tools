"""Standalone BE9_COTS vendor-part creation (File > New > Item)."""
import NXOpen
import NXOpen.PDM

from lib.teamcenter import configure_filenew, dump_pdm_errors

# Teamcenter folder the item is created in (":" prefix is TC folder syntax).
DEFAULT_VENDOR_FOLDER = ":NX-TOOLS-DEBUG"


def create_vendor_part(vendor_part_number, vendor_description, vendor_name,
                       part_class="Class III",
                       destination_folder=DEFAULT_VENDOR_FOLDER, lw=None,
                       revision=None):
    """Create a BE9_COTS item in Teamcenter and make it the displayed part.

    Based on example_journals/journal_create_vendor_part.py (and, for `revision`,
    journal_create_vendor_part_with_NC_rev.py). Property map:

        ID            (DB_PART_NO)       <- vendor_part_number
        Name          (DB_PART_NAME)     <- vendor_description
        Manufacturer  (HE_Manufacturer)  <- vendor_name
        Part Class    (be9_PartClass)    <- part_class ("Class III")
        Revision      (DB_PART_REV)      <- revision (e.g. "NC"); optional

    When `revision` is None the item gets Teamcenter's default revision (A).
    `lw` is an optional ListingWindow used to report PDM errors on failure.
    Commit() exceptions are re-raised. Returns the new work part.
    """
    session = NXOpen.Session.GetSession()

    fileNew = session.Parts.FileNew()
    configure_filenew(fileNew)

    opBuilder = session.PdmSession.CreateCreateOperationBuilder(
        NXOpen.PDM.PartOperationBuilder.OperationType.Create)
    fileNew.SetPartOperationCreateBuilder(opBuilder)
    opBuilder.SetOperationSubType(
        NXOpen.PDM.PartOperationCreateBuilder.OperationSubType.FromTemplate)
    opBuilder.SetModelType("master")

    # The recording creates logical objects as the dialog default type
    # (BE9_Design), sets the destination folder, then switches to BE9_COTS.
    opBuilder.SetItemType("BE9_Design")
    designObjects = opBuilder.CreateLogicalObjects()
    # The recordings read the user-attribute source objects of the Design
    # logical object at each of these points; keep the reads in place.
    designObjects[0].GetUserAttributeSourceObjects()
    opBuilder.DefaultDestinationFolder = destination_folder
    designObjects[0].GetUserAttributeSourceObjects()
    opBuilder.SetOperationSubType(
        NXOpen.PDM.PartOperationCreateBuilder.OperationSubType.FromTemplate)
    designObjects[0].GetUserAttributeSourceObjects()

    opBuilder.SetItemType("BE9_COTS")
    logicalObjects = opBuilder.CreateLogicalObjects()
    sourceObjects = logicalObjects[0].GetUserAttributeSourceObjects()

    def new_attr_builder():
        builder = session.AttributeManager.CreateAttributePropertiesBuilder(
            NXOpen.BasePart.Null, [],
            NXOpen.AttributePropertiesBuilder.OperationType.Create)
        builder.SetAttributeObjects([])
        builder.SetAttributeObjects([sourceObjects[0]])
        return builder

    attrBuilder = None

    def set_attribute(title, category, value):
        attrBuilder.Title = title
        attrBuilder.StringValue = value
        attrBuilder.Category = category
        attrBuilder.CreateAttribute()

    def set_attribute_journal_order(title, category, value):
        # Property order exactly as recorded for DB_PART_REV:
        # Title, Category, StringValue, Category, then CreateAttribute.
        attrBuilder.Title = title
        attrBuilder.Category = category
        attrBuilder.StringValue = value
        attrBuilder.Category = category
        attrBuilder.CreateAttribute()

    # The NC-revision recording creates the attribute builder and sets
    # DB_PART_REV *before* the naming-map step; keep that order when a revision
    # is requested. Without one, the builder is created after it, as before.
    if revision:
        attrBuilder = new_attr_builder()
        set_attribute_journal_order("DB_PART_REV", "BE9_COTSRevision", revision)

    # COTS parts are not auto-numbered: register an empty naming map; the id
    # is set below as DB_PART_NO.
    namingMap = opBuilder.CreateAttributeTitleToNamingPatternMap([], [])
    errorList = opBuilder.AutoAssignAttributesWithNamingPattern(
        [logicalObjects[0]], [namingMap])
    errorList.Dispose()
    opBuilder.GetErrorMessageHandler(True)

    if attrBuilder is None:
        attrBuilder = new_attr_builder()

    # Item-level attributes (category BE9_COTS).
    set_attribute("DB_PART_NO", "BE9_COTS", vendor_part_number)
    set_attribute("DB_PART_NAME", "BE9_COTS", vendor_description)
    # Revision-level attributes (category BE9_COTSRevision).
    set_attribute("HE_Manufacturer", "BE9_COTSRevision", vendor_name)
    set_attribute("Item:revision:ItemRevision:be9_PartClass",
                  "BE9_COTSRevision", part_class)

    # Finalize and commit; the recording re-applies the fileNew settings first.
    configure_filenew(fileNew)
    fileNew.MasterFileName = ""
    fileNew.MakeDisplayedPart = True
    fileNew.DisplayPartOption = NXOpen.DisplayPartOption.AllowAdditional
    opBuilder.ValidateLogicalObjectsToCommit()
    opBuilder.CreateSpecificationsForLogicalObjects([logicalObjects[0]])
    try:
        fileNew.Commit()
    except Exception:
        if lw is not None:
            dump_pdm_errors(opBuilder, lw, "after Commit failure")
        raise
    finally:
        fileNew.Destroy()
        attrBuilder.Destroy()

    return session.Parts.Work
