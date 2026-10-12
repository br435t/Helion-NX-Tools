"""Teamcenter / NX Open helpers: existence check, COTS part creation, import."""
import NXOpen
import NXOpen.PDM

# Teamcenter destination folder for created COTS parts. The ":" prefix is TC
# folder syntax; using the real ":MCMASTER" folder (per the working recording
# journal_create_vendor_part.py) is what lets the manual-id Commit() succeed.
MCMASTER_TC_FOLDER = ":MCMASTER"

# Revision rules used to resolve an item id when checking for existence.
# An empty rule does NOT resolve existing parts here (verified via
# check_part_exists.py); "Latest Working" catches unreleased parts and
# "Any Status; Working" catches any status. If any rule resolves the id, the
# part exists. Extend this list if a part is known to exist but isn't detected.
_TC_EXISTENCE_REVISION_RULES = ("Latest Working", "Any Status; Working")


def import_parasolid(the_session, input_file, curves=True, surfaces=True, solids=True):
    """Import a Parasolid (*.x_t) file into the current work part.

    Mirrors the recorded File > Import > Parasolid flow (see import_Parasolid.py).
    """
    importer = the_session.DexManager.CreateParasolidImporter()
    try:
        importer.ObjectTypes.Curves = curves
        importer.ObjectTypes.Surfaces = surfaces
        importer.ObjectTypes.Solids = solids
        importer.SetMode(NXOpen.BaseImporter.Mode.NativeFileSystem)
        importer.InputFile = input_file
        importer.Commit()
    finally:
        importer.Destroy()


def item_exists_in_teamcenter(the_session, item_id, log=None):
    """Best-effort check whether an item id already exists in Teamcenter.

    Uses PdmSession.GetConfiguredRevisionOfItems across a few revision rules
    (see _TC_EXISTENCE_REVISION_RULES). Returns True as soon as one rule
    resolves a revision for the id. Any other outcome -- id not found under any
    rule, or an API error -- returns False so creation proceeds; a genuine
    duplicate that slips through is then caught at Commit() (operation-failure
    code 940519) and reported via dump_pdm_errors(). Never raises.
    """
    _log = log or (lambda m: None)
    try:
        pdm = the_session.PdmSession
        for rule in _TC_EXISTENCE_REVISION_RULES:
            query = NXOpen.PDM.PdmSession.GetConfiguredRevisionInput()
            query.ItemId = item_id
            query.RevisionRuleName = rule
            _errors, results = pdm.GetConfiguredRevisionOfItems([query])
            for res in (results or []):
                spec = (res.ItemRevisionCliSpec or "").strip()
                if not res.HasFailed and spec:
                    _log("  Teamcenter already has {0} (revision {1}, "
                         "rule '{2}').".format(item_id, spec, rule))
                    return True
        return False
    except Exception as ex:
        _log("  existence pre-check inconclusive ({0}); relying on "
             "commit-time validation.".format(ex))
        return False


def dump_pdm_errors(builder, lw, label):
    """Print the PDM builder's error/warning messages to the Listing Window.

    The generic "not a valid file specification" NXException hides the real
    per-object failure; ErrorMessageHandler.GetErrorMessages() and
    GetOperationFailures() carry the specifics. Best-effort — never raises.
    """
    try:
        handler = builder.GetErrorMessageHandler(True)
        try:
            errs = list(handler.GetErrorMessages() or [])
            warns = list(handler.GetWarningMessages() or [])
        finally:
            handler.Dispose()
        for m in errs:
            lw.WriteLine("  [{0}] ERROR:   {1}".format(label, m))
        for m in warns:
            lw.WriteLine("  [{0}] warning: {1}".format(label, m))
        if not errs and not warns:
            lw.WriteLine("  [{0}] (no PDM messages)".format(label))
    except Exception as ex:
        lw.WriteLine("  [{0}] could not read PDM messages: {1}".format(label, ex))
    # Structured operation-failure list (NXOpen.ErrorInfo: ErrorCode +
    # Description + ErrorObjectDescription). This is the reliable channel --
    # GetErrorMessages() tends to return NULL for these PDM builders.
    try:
        failures = builder.GetOperationFailures()
        try:
            count = failures.Length
            for i in range(count):
                info = failures.GetErrorInfo(i)
                try:
                    try:
                        code = info.ErrorCode
                    except Exception:
                        code = "?"
                    try:
                        desc = info.Description
                    except Exception:
                        desc = "?"
                    try:
                        obj = info.ErrorObjectDescription
                    except Exception:
                        obj = ""
                    lw.WriteLine("  [{0}] failure[{1}]: code={2} | {3}{4}".format(
                        label, i, code, desc,
                        (" | object: " + obj) if obj else ""))
                finally:
                    info.Dispose()
        finally:
            failures.Dispose()
    except Exception as ex:
        lw.WriteLine("  [{0}] could not read operation failures: {1}".format(
            label, ex))


def configure_filenew(fn):
    """Apply the File > New > Item settings used by the COTS-create recording."""
    fn.TemplateFileName = "@DB/model-plain-1-inch-template/A"
    fn.UseBlankTemplate = False
    fn.ApplicationName = "ModelTemplate"
    fn.Units = NXOpen.Part.Units.Inches
    fn.RelationType = "master"
    fn.UsesMasterModel = "No"                  # NOTE: string, not bool
    fn.TemplateType = NXOpen.FileNewTemplateType.Item
    fn.TemplatePresentationName = "Model"
    fn.ItemType = "BE9_Design,BE9_Electrical,BE9_COTS,BE9_Tooling"
    fn.Specialization = ""
    fn.SetCanCreateAltrep(False)


def create_cots_part(the_session, lw, part_no, part_name, part_desc,
                     manufacturer, part_class):
    """Create the BE9_COTS item (File > New > Item) and make it the work part.

    This is a faithful transcription of the working recorded journal
    (example_journals/journal_create_vendor_part.py). The exact call order
    matters: NX derives the new part's on-disk filename during Commit(), and
    deviating from the recording (single-pass creation, skipping the fileNew
    re-sets or the extra CreateLogicalObjects) produces "The new filename is
    not a valid file specification". Keep this in lockstep with the recording.

    Returns the new work part.
    """
    fileNew = the_session.Parts.FileNew()
    configure_filenew(fileNew)

    opBuilder = the_session.PdmSession.CreateCreateOperationBuilder(
        NXOpen.PDM.PartOperationBuilder.OperationType.Create)
    fileNew.SetPartOperationCreateBuilder(opBuilder)
    opBuilder.SetOperationSubType(
        NXOpen.PDM.PartOperationCreateBuilder.OperationSubType.FromTemplate)
    opBuilder.SetModelType("master")

    # Phase 1: create the logical objects as the dialog default type
    # (BE9_Design), set the destination folder, then re-assert the sub-type --
    # exactly as the recording does before switching to COTS.
    opBuilder.SetItemType("BE9_Design")
    opBuilder.CreateLogicalObjects()
    opBuilder.DefaultDestinationFolder = MCMASTER_TC_FOLDER
    opBuilder.SetOperationSubType(
        NXOpen.PDM.PartOperationCreateBuilder.OperationSubType.FromTemplate)

    # Phase 2: re-apply the fileNew settings, switch to BE9_COTS with no master,
    # and recreate the logical objects. The recording calls CreateLogicalObjects
    # a second time after grabbing the source objects; preserve that extra call.
    configure_filenew(fileNew)
    opBuilder.SetAddMaster(False)
    opBuilder.SetItemType("BE9_COTS")
    logicalObjects = opBuilder.CreateLogicalObjects()
    sourceObjects = logicalObjects[0].GetUserAttributeSourceObjects()
    opBuilder.CreateLogicalObjects()

    # COTS parts are not auto-numbered: register an empty naming map (the part
    # number is set below as the DB_PART_NO attribute).
    namingMap = opBuilder.CreateAttributeTitleToNamingPatternMap([], [])
    errorList = opBuilder.AutoAssignAttributesWithNamingPattern(
        [logicalObjects[0]], [namingMap])
    errorList.Dispose()
    opBuilder.GetErrorMessageHandler(True)

    attrBuilder = the_session.AttributeManager.CreateAttributePropertiesBuilder(
        NXOpen.BasePart.Null, [],
        NXOpen.AttributePropertiesBuilder.OperationType.Create)
    attrBuilder.SetAttributeObjects([])
    attrBuilder.SetAttributeObjects([sourceObjects[0]])

    # Item-level attributes (category BE9_COTS). Property-set order (Title,
    # Category, StringValue) matches the recording.
    attrBuilder.Title = "DB_PART_NO"
    attrBuilder.Category = "BE9_COTS"
    attrBuilder.StringValue = part_no
    attrBuilder.CreateAttribute()

    attrBuilder.Title = "DB_PART_NAME"
    attrBuilder.StringValue = part_name
    attrBuilder.Category = "BE9_COTS"
    attrBuilder.CreateAttribute()

    attrBuilder.Title = "DB_PART_DESC"
    attrBuilder.Category = "BE9_COTS"
    attrBuilder.StringValue = part_desc
    attrBuilder.CreateAttribute()

    # Revision-level attributes (category BE9_COTSRevision).
    attrBuilder.Title = "HE_Manufacturer"
    attrBuilder.Category = "BE9_COTSRevision"
    attrBuilder.StringValue = manufacturer
    attrBuilder.CreateAttribute()

    attrBuilder.Title = "Part Class"
    attrBuilder.StringValue = part_class
    attrBuilder.Category = "BE9_COTSRevision"
    attrBuilder.CreateAttribute()

    # Finalize and commit. The recording re-applies the fileNew settings once
    # more here, right before validating and committing.
    configure_filenew(fileNew)
    fileNew.MasterFileName = ""
    fileNew.MakeDisplayedPart = True
    fileNew.DisplayPartOption = NXOpen.DisplayPartOption.AllowAdditional
    opBuilder.ValidateLogicalObjectsToCommit()
    dump_pdm_errors(opBuilder, lw, "after Validate")
    opBuilder.CreateSpecificationsForLogicalObjects([logicalObjects[0]])
    dump_pdm_errors(opBuilder, lw, "after CreateSpecs")
    try:
        fileNew.Commit()
    except Exception as commit_ex:
        lw.WriteLine("Commit() raised: {0}".format(commit_ex))
        dump_pdm_errors(opBuilder, lw, "after Commit failure")
        raise

    work_part = the_session.Parts.Work
    lw.WriteLine("Created COTS part: {0}".format(work_part.Leaf))

    fileNew.Destroy()
    attrBuilder.Destroy()
    return work_part
