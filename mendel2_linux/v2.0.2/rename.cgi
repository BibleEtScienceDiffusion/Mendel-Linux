#!/usr/bin/perl
##############################################################################
#
# list_cases.cgi -> with_selected.cgi -> this_file -> (refresh to)list_cases.cgi
#
# This file archives a list of cases which have been checked in the
# list_cases dialogue.
#
##############################################################################

#require "./parse.inc";

read(STDIN, $buffer,$ENV{'CONTENT_LENGTH'});
$buffer =~ tr/+/ /;
$buffer =~ s/\r/ /g;
$buffer =~ s/\n/ /g;
$buffer =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
$buffer =~ s/<!--(.|\n)*-->/ /g;
$buffer =~ tr/\\|[|]|<|!|"|$|{|}|*|#|'|>|||;|%/ /; 

@pairs = split(/&/,$buffer);
foreach $pair(@pairs){
  ($key,$value)=split(/=/,$pair);
  $formdata{$key}.="$value";
}

require "./config.inc";

$copy=$formdata{'copy'};
$file_name=$formdata{'file_name'};
$case_id=$formdata{'case_id'};
$run_dir=$formdata{'run_dir'};
$url_dir=$formdata{'url_dir'};
$user_id=$formdata{'user_id'};
$admin=$formdata{'admin'};
$show_all_users=$formdata{'show_all_users'};
$new_case_id=$formdata{'new_case_id'};
$selected_cases=$formdata{'selected_cases'};
@cases = split(/:/,$selected_cases);

# turn buffering off for correct display order
$| = 1;

print "Content-type:text/html\n\n";
print "<meta http-equiv=\"refresh\" content=\"10;";
print "URL=list_cases.cgi\">\n";
print "<html><body>";

#print "url_dir is $url_dir<br>";
#print "case_id is $case_id<br>";
#print "run_dir is $run_dir<br>";
#print "user_id is $user_id<br>";
#print "new_case_id is $new_case_id<br>";
#print "selected_cases: $selected_cases<br>";
#print "cases: $cases<br>";
#print "case $i: ", $cases[$i],"<br>";

chdir $run_dir;

if ($#cases < 0) {
  $ncases = 0;
} else {
  $ncases = $#cases;
}

for ( $i = 0; $i <= $ncases; ++$i ) {

    ($uid,$cid) = split('/',$cases[$i]);
    ($nuid,$ncid) = split('/',$new_case_id);
    #print "nuid is:$nuid.<br>";
    
    #system("mv $cases[0] $new_case_id");
    system("mkdir -p $nuid");
    
    # if more than one case, move to directories
    if ($ncases > 0) { $ncid = $cid; }
    
    if($nuid eq $cid) {
       print "<h1>ERROR: failed to specify user (e.g. john/case01)</h1>";
       sleep 10;
       exit -1;
    }

    if($copy eq "on") {
	print "$cases[$i] copied to $new_case_id<br>";
	system("cp -r $uid/$cid $nuid/$ncid");
    } else {
	print "$cases[$i] renamed to $new_case_id<br>";
	system("mv $uid/$cid $nuid/$ncid");
    }
    
    if($ncases eq 0) {
       chdir "$nuid/$ncid";
       # note that Debian systems rename works differently than the 
       # following. So, on Debian systems try:
       # system("rename 's/$cid/$ncid/' $cid* &> /dev/null");
       system("rename $cid $ncid $cid* &> /dev/null");
       system("sed -i -e 's/$cid/$ncid/g' *.gnu pbs.script mendel.in");
    }
    
    $case_id = $cases[i];
}

print("<script language=\"Javascript\">parent.frames.contents.caseidform.case_id.value = \"$ncid\";</script>\n");
print "<meta http-equiv=\"refresh\" content=\"1;URL=list_cases.cgi?user_id=$user_id&admin=$admin&show_all_users=$show_all_users\">\n";
print "</body></html>";

