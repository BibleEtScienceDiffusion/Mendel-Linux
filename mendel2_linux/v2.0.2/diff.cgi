#!/usr/bin/perl
##############################################################################
#
# list_cases.cgi -> with_selected.cgi -> this_file 
#
# This file runs either the "diff" program for 2 files 
# or the "diff3" program for 3 files and displays the results to the screen.
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
$url_dir=$formdata{'url_dir'};

# turn buffering off for correct display order
$| = 1;

print "Content-type:text/html\n\n<p>";

  if ($#cases eq "1") {
     print "<pre>";
     #open (MYEXE, "diff $run_dir/$cases[0]/mendel.in $run_dir/$cases[1]/mendel.in | ");
     open (MYEXE, "diff $run_dir/$cases[0]/mendel.in $run_dir/$cases[1]/mendel.in | sed -e 's!<!$cases[0]:!' -e 's!>!$cases[1]:!' |");
     $i=1;
     while (<MYEXE>){
        print "$_";
        $i++;
     }
     close MYEXE;
     print "</pre>";
  } elsif ($#cases eq "2") {
     print "<pre>";
     open (MYEXE, "diff3 $run_dir/$cases[0]/mendel.in $run_dir/$cases[1]/mendel.in $run_dir/$cases[2]/mendel.in | sed -e 's!1:!$cases[0]:!' -e 's!2:!$cases[1]:!' -e 's!3:!$cases[2]:!' |");
     $i=1;
     while (<MYEXE>){
        print "$_";
        $i++;
     }
     close MYEXE;
     print "</pre>";
  } else {
    print "<p><h1>ERROR: Diff requires exactly two or three cases.</h1></p>";
  }
