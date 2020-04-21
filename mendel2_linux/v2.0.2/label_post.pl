#!/usr/bin/perl
##############################################################################
#
# label_form.cgi -> this_file
#
# This file takes the inputs from label_form.cgi 
# and writes the labels to a file in the run_dir/case_id directory
# called README.  These labels are then displayed when the user
# clicks the "List Cases" button, which is handled by list_cases.cgi
#
##############################################################################

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
$case_id=$formdata{'case_id'};
$run_dir=$formdata{'run_dir'};
$admin=$formdata{'admin'};
$show_all_users=$formdata{'show_all_users'};
$user_id=$formdata{'user_id'};
$url_dir=$formdata{'url_dir'};
$rating=$formdata{'rating'};
$label=$formdata{'label'};
$long_label=$formdata{'long_label'};
$archive=$formdata{'archive'};

require "./config.inc";

if (lc($archive) eq "on") {
        $archive ="A";
} else {
        $archive ="";
}

# turn buffering off for correct display order
$| = 1;

print "Content-type:text/html\n\n";
print "<meta http-equiv=\"refresh\" content=\"1;";
print "URL=list_cases.cgi?user_id=$user_id&admin=$admin&show_all_users=$show_all_users\">\n";

#print "url_dir is $url_dir<br>";
#print "case_id is $case_id<br>";
#print "run_dir is $run_dir<br>";
#print "label is: $label<br>";
#print "long labels are: $long_label<br>";
#print "buffer is: $buffer<br>";

print "<h2>Labels added</h2>\n";
print "Labels are stored in README file located in $run_dir/$case_id directory<p>";
print "They can be viewed by clicking on \"List files\" button.<p>";

system("echo $archive$rating $label  > $run_dir/$case_id/README");
system("echo $long_label >> $run_dir/$case_id/README");

