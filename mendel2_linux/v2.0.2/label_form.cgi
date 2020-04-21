#!/usr/bin/perl
##############################################################################
#
# toc.php -> this_file -> label_post.pl
# with_selected.cgi -> this_file -> label_post.pl
#
# This file prompts the user for labels related to a specific case 
# and posts the results to label_post.pl for processing.
#
##############################################################################

# NOTE: this is required in with_selected.cgi

#print "url_dir is $url_dir<br>";
#print "case_id is $case_id<br>";
#print "run_dir is $run_dir<br>";

if ($case_id eq "") {
print "ERROR: you must enter the Case ID<br><br>";
print "<em>Note</em>: if you have already entered the case id, please make sure to hit ENTER with the cursor in the CaseID box 1 time, then re-enter casename and click Inputs without clicking enter.<br>";
return -1;
}

if ($#cases eq "-1") {
  $ncases = 0;
} else {
  $ncases = $#cases;
}

for ( $i = 0; $i <= $ncases; $i++ ) {

if ($#cases ne "-1") {
   $case_id = $cases[$i];
}

$label=`head -1 $run_dir/$case_id/README`;
$long_label=`tail -1 $run_dir/$case_id/README`;

print <<End_of_Doc;
	<form name="label_form" method="post" action="./label_post.pl">
	<h2>Enter label to be added for case $case_id?</h2>
        <p>Note: may only use alphabet characters.  Some symbols such as = )  ! & will be intrepeted by the form parser as meaning something other than you intended. Recommend using standard Fortran conventions. For example, instead of "test=1" use "test.eq.1".</p>

	<input type="hidden" name="url_dir" value="$url_dir">
	<input type="hidden" name="case_id" value="$case_id">
	<input type="hidden" name="user_id" value="$user_id">
	<input type="hidden" name="admin" value="$admin">
	<input type="hidden" name="case_id" value="$show_all_users">
	<input type="hidden" name="run_dir" value="$run_dir">

	<table>

	<tr>
	<td><u>O</u>ne-line label:</td>
	<td><input type="text" name="label" value="$label" style="width:20em" accesskey="O"></td>
	</tr>

	<tr>
	<td></td>
	<td><input type="submit" value="Add label"></td>
	</tr>
	</table>

	</form>

End_of_Doc
}

