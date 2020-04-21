#!/usr/bin/perl
##############################################################################
#
# list_cases.cgi -> with_selected.cgi -> this_file -> display results
#       toc.html ->                      this_file -> display results
#
# This file plots the results of the simulation by create PNG images
# and displaying the PNG images in HTML.
#
##############################################################################

require "parse.inc";

# if posting from control panel 
if ($case_id eq "") {
   $case_id=$formdata{'case_id'};
   $user_id=$formdata{'user_id'};
   $version=$formdata{'version'};
   if($case_id =~ /%2F/) {
     ($user_id,$case_id)=split(/%2F/,$case_id);
   }
   print "Content-type:text/html\n\n";
   #print "cid: $case_id uid: $user_id cuid: $cuid<p>";
   if ($case_id eq "") {
      print "ERROR: Case_ID missing<br>";   
      die;
   }
}

require "config.inc";

$selected_cases=$formdata{'selected_cases'};
$program=$formdata{'program'};
@case = split(/:/,$selected_cases);

#print "program is $program";

if($program eq "gnuplot") {
   require "plot_gnuplot.cgi";
} elsif($program eq "flot") {
   require "plot_flot.cgi";
} elsif($program eq "jqplot") {
   require "plot_jqplot.cgi";
} else {
   require "plot_flot.cgi";
}

