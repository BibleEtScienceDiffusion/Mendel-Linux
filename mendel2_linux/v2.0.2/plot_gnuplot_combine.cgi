#!/usr/bin/perl
##############################################################################
#
# list_cases.cgi -> with_selected.cgi -> this_file -> plot_gnuplot.cgi
#
# This file displays a form to ask user about casename for 
# combined data, then calls plot_gnuplot.cgi
#
##############################################################################

# This file is required in with_selected.cgi so no parsing is needed

print "<html><body>";

print "<h1>Combine plot data</h1>";

$new_case_id=$selected_cases;
$new_case_id =~ s/://g;

#print "url_dir is $url_dir<br>";
#print "case_id is $case_id<br>";
#print "run_dir is $run_dir<br>";
#print "user_id is $user_id<br>";
#print "new_case_id is $new_case_id<br>";

if ($case_id ne "") {
#print "Case $case_id file listing.<br>  ";
#print "<em>Note: clear CaseID to see all files.</em><br>";
}

    print <<zZzZz;
        <form name="combine_plots" method="post" action="plot_gnuplot_recipes.cgi">
        <table>

        <tr>
           <td> Plot data in grayscale?</td>
           <td> <input type="checkbox" name="grayscale" value="on"></td>
        </tr>

        <tr>
        <td>Enter a new Case ID for the combined results <br>
        <em>(note that new Case ID can be more than 6 digits):</em></td>
        <td>
             <input type="text"   name="ccid" value="">
        </td>
        </tr>
        <tr>
        <td> </td>
        <td> <input type="submit" value="Combine plots"> </td>
        </tr>
        </table>

       <hr>

        <input type="hidden" name="user_id" value="$user_id">
        <input type="hidden" name="selected_cases" value="$selected_cases">
        <input type="hidden" name="labels" value="off">
        <!-- <input type="hidden" name="case_id" value="$case_id"> -->
        <input type="hidden" name="run_dir" value="$run_dir"><p>
        <input type="hidden" name="caller" value="combine"><p>
        </form>
zZzZz

