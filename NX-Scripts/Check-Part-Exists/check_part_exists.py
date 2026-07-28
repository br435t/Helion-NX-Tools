# NX 2506
# Standalone Teamcenter existence check.
#
# Run via File -> Execute -> NX Open... with an active Teamcenter (managed)
# session. Probes whether an item id (part number) already exists in
# Teamcenter and prints the result to the Listing Window.
#
# Background: creating a COTS item whose id already exists fails at Commit()
# with the opaque "The new filename is not a valid file specification"; the
# underlying operation-failure is code 940519 ("Cannot create a new revision
# of an existing part using New. Use Save As for this operation."). This script
# finds a reliable pre-check so CREATE_MCMASTER_PART.py can detect the collision
# up front instead.
#
# PdmSession.GetConfiguredRevisionOfItems looks up an item revision by id, but
# it needs a *revision rule*: with an empty rule it fails to configure a
# revision even for parts that exist (a false "not found"). This script tries a
# set of common revision-rule names and reports which ones resolve the part, so
# we can wire the working rule into the main tool.
import NXOpen
import NXOpen.PDM

# The part number to check. Change this to probe a different id.
PART_NUMBER = "97135A225"

# Revision rules to try, in order. "" asks Teamcenter for its configured
# default (which, empirically, does NOT resolve existing parts here -- kept
# first so its behavior is visible in the log). The rest are common TC rule
# names; the site's actual rule set may differ.
REVISION_RULES = [
    "",
    "Latest Working",
    "Any Status; Working",
    "Latest Released",
    "Precise",
    "Latest",
]


def _try_rule(pdm, item_id, rule, lw):
    """Look up item_id under one revision rule. Returns True if it resolves."""
    try:
        query = NXOpen.PDM.PdmSession.GetConfiguredRevisionInput()
        query.ItemId = item_id
        query.RevisionRuleName = rule
        _errors, results = pdm.GetConfiguredRevisionOfItems([query])
        rule_label = rule if rule else "(default/empty)"
        found = False
        for res in (results or []):
            spec = (res.ItemRevisionCliSpec or "").strip()
            lw.WriteLine(
                "  rule {0:<22} -> HasFailed={1}  spec='{2}'".format(
                    rule_label, res.HasFailed, spec))
            if not res.HasFailed and spec:
                found = True
        if not results:
            lw.WriteLine("  rule {0:<22} -> (no results)".format(rule_label))
        return found
    except Exception as ex:
        lw.WriteLine("  rule {0:<22} -> error: {1}".format(
            rule if rule else "(default/empty)", ex))
        return False


def main(args):
    theSession = NXOpen.Session.GetSession()  # type: NXOpen.Session
    lw = theSession.ListingWindow
    lw.Open()
    lw.WriteLine("=" * 60)
    lw.WriteLine("Teamcenter existence check for part: {0}".format(PART_NUMBER))
    lw.WriteLine("=" * 60)

    pdm = theSession.PdmSession
    if pdm is None:
        lw.WriteLine("No PdmSession -- is this a Teamcenter (managed) session?")
        return

    exists = False
    for rule in REVISION_RULES:
        if _try_rule(pdm, PART_NUMBER, rule, lw):
            exists = True

    lw.WriteLine("-" * 60)
    if exists:
        lw.WriteLine("VERDICT: {0} EXISTS in Teamcenter "
                     "(resolved by at least one revision rule above).".format(
                         PART_NUMBER))
    else:
        lw.WriteLine("VERDICT: {0} was NOT resolved by any rule tried. "
                     "If you know it exists, note which rules were attempted "
                     "so we can add the right one.".format(PART_NUMBER))


if __name__ == '__main__':
    main(None)
