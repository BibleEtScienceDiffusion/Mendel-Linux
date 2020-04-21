function qrand(n) {
        RandSeed = (RandMultiplier * RandSeed + RandIncrement) % 0x7fffffff
        return (RandSeed >> 16) % n
}
function qinit() {
        RandMultiplier = 0x015a4e35
        RandIncrement = 1

        // Initialize using the computer's date and time...
        var now = new Date()
        RandSeed = now.getTime() % 0xffffffff
        FirstSentence = 1
        FirstAmerica = 1
}
//=======================================================================
function getRandomTip(){
        n = 12;
        // if windows:
        // n = 8;
        vn = qrand(n);
        //vn = 2;
        if (vn == 0 ) verse="<b>Comparing cases</b>. User's can combine several cases onto a single plot.  Select the desired cases in the \"Cases\" dialogue and click \"Plots\". Then the user will be asked if he wants to combine both plots.";
        if (vn == 1 ) verse="<b>Modify plots</b>.  You can modify MENDEL plots (change scaling, lines/points, etc.) by clicking the \"Modify plots\" button after plotting a case.";
        if (vn == 2 ) verse="<b>Mendel doesn't fit on my screen.</b> If the plots are too big to show up on your screen, you can use your browsers Zoom features (Typically under the View menu) and Zoom out enough times that Mendel fits properly on your screen.";
        if (vn == 3 ) verse="<b>Inputs/Outputs</b>.  Suppose you want to know what the population size is of five different cases.  Select the desired cases in the \"Cases\" dialogue, and then enter <em>pop_size</em> as the keyword and click either \"Inputs\" or \"Ouputs\" to search for the keyword in either the input or output files respectively.";
        if (vn == 4 ) verse="<b>Labels</b>. Labels or descriptions can be used to group a set of cases.  For example, use <em>PNAS</em> to group all cases related to PNAS.  Then, instead of search for Case ID's, select the checkbox next to the \"Show Cases\" button. Labels or descriptions can later be input by clicking <em>Comment</em> button.";
        if (vn == 5 ) verse="<b>Which Browser?</b> Mendel works in most browsers, except Internet Explorer.  It is fastest using Google Chrome or Opera, but is most elegant in Apple Safari.  For Linux, Mendel works well in either Firefox or Konqueror.";
        if (vn == 6 ) verse="<b>Changing parameters shown on plot</b>. Sometimes, you may want to change the parameters which show up on a plot, or in case you are running a parallel case, you want to plot individual tribes instead of averaged data.  To do this, the recipe files that Gnuplot uses must be rewritten. This can be done by selecting the case from the Cases dialogue (or manually entering Case ID in control panel), clicking Start (Alt-s, Shift-Alt-u in Firefox), Enter same casename (or click checkbox to right of Case ID box, or hit [Shift]-Alt-u then Execute (just one time Alt-x), then click Plot again (Alt-G), this will rewrite the Gnuplot recipes and replot the data with the new parameters.";
        if (vn == 7 ) verse="<b>I found a bug!</b> In the case that you find a bug in Mendel, please report bugs by visiting <a href=\"http://sf.net/projects/mendelsaccount\" target=\"_blank\">http://sf.net/projects/mendelsaccount</a> and click on one of the project admins (jcsanford, jrbaumgardner, or whbrewer) and click \"Send me a message\".";
        if (vn == 8 ) verse="<b>Zip (Linux version)</b>.  Check several cases and click the Zip button in the \"Cases\" dialogue to create a compressed archive of the selected cases.  This archive will then show up with a URL link when clicking the \"Cases\" button, and can be downloaded to the user's computer by clicking on the filename and uncompressed using many available software (e.g. WinZip, PowerArchiver, ZipGenius).";
        if (vn == 9 ) verse="<b>Diff (Linux version)</b>. Suppose you want to find how the inputs differ for several cases.  Select the desired cases in the\"Cases\" dialogue and click the \"Diff\" button.  Diff can only be used on 2 or 3 cases.";
        if (vn == 10 ) verse="<b>Disabled features (Windows version).</b> There are some items which are disabled and unsupported in the Windows version. To access these features, you will need to request an online account at <a href=\"http://www.mendelsaccountant.info\" target=\"_blank\">http://www.mendelsaccountant.info</a>";
        if (vn == 11 ) verse="<b>\"Status Button\" (Windows version).</b> In Windows version, for the status to report correctly, the user should press the Status button <i>after</i> starting a job, <u>but</u> <i>before</i> clicking \"Output\". Or, the user may press the \"Status\" button, but then click the browser's Stop button.";
        return verse;
}
