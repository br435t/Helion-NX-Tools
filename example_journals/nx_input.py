# intellisense by theScriptingEngineer (www.theScriptingEngineer.com)
# Created by theScriptingEngineer

# NXOpen Python Reference Guide:
# https://docs.plm.automation.siemens.com/data_services/resources/nx/1899/nx_api/custom/en_US/nxopen_python_ref/index.html

# https://docs.plm.automation.siemens.com/data_services/resources/nx/10/nx_api/en_US/custom/nxopen_python_ref/NXOpen.UF.Ui.AskStringInput.html#NXOpen.UF.Ui.AskStringInput
# https://docs.sw.siemens.com/en-US/doc/209349590/PL20221117716122093.nxopen_python_ref/nxopen_python_ref

import NXOpen
import NXOpen.UF


the_session: NXOpen.Session = NXOpen.Session.GetSession()
the_uf_session: NXOpen.UF.UFSession = NXOpen.UF.UFSession.GetUFSession()
base_part: NXOpen.BasePart = the_session.Parts.BaseWork
the_lw: NXOpen.ListingWindow = the_session.ListingWindow
the_UI: NXOpen.UI = NXOpen.UI.GetUI() # type: ignore


def main():
    the_lw.Open()
    the_lw.WriteFullline("Starting Main() in " + the_session.ExecutingJournal)

    question: str = 'Please provide some text'
    the_UI.LockAccess()
    # returns a tuple with 
    #  - The returned text
    #  - THe length of the text
    #  - Info on the window: 
    #       1 = Back 
    #       2 = Cancel 
    #       3 = OK (Accept default ) 
    #       5 = Data entered 
    #       8 = Disallowed state
    response = the_uf_session.Ui.AskStringInput('Title', question)
    the_UI.UnlockAccess()



    answer: str = response[0]
    value: float
    if answer.isnumeric():
        value = float(answer)
        the_lw.WriteFullline(str(type(value)))
    else:
        # not a numerical value
        response = the_UI.NXMessageBox.Show('Error', NXOpen.NXMessageBox.DialogType.Error, 'You need to provide a numerical value. Please try again')
        return


if __name__ == '__main__':
    main()
