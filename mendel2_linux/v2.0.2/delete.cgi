#!/usr/bin/perl
##############################################################################
#
# list_cases.cgi -> with_selected.cgi -> this_file -> (refresh to)list_cases.cgi
# list_files.cgi -> with_selected.cgi -> this_file -> (refresh to)list_cases.cgi
#
# This file deletes a case or specific files that are checked
# either in the list_cases or list_files dialogue.
#
##############################################################################

#require "parse.inc";

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

require "config.inc";
if ($os eq "windows") {
   $slash="\\";
   $rmdir="rmdir/s/q";
} else {
   $slash="/";
   $rmdir="rm -rf";
}
$user_id=$formdata{'user_id'};
$admin=$formdata{'admin'};
$case_id=$formdata{'case_id'};
$file_name=$formdata{'file_name'};
$selected_cases=$formdata{'selected_cases'};
@cases = split(/:/,$selected_cases);
$selected_files=$formdata{'selected_files'};
@files = split(/:/,$selected_files);

# turn buffering off for correct display order
$| = 1;

print "Content-type:text/html\n\n";
print "<html><body>";

#print "run_dir is $run_dir<br>";
#print "case_id is $case_id<br>";
#print "admin" is $admin";
#print "user_id is $user_id";

#print "selected_cases: $selected_cases<br>";
#print "cases: $cases<br>";
if ($#files eq "-1") {
   print "<meta http-equiv=\"refresh\" content=\"1;";
   print "URL=list_cases.cgi?user_id=$user_id&admin=$admin\">\n";

   for ( $i = 0; $i <= $#cases; ++$i )
      {
        ($uid,$cid) = split('/',$cases[$i]);
	open (MYEXE, "$rmdir $run_dir$slash$uid$slash$cid |");
        #print "$rmdir $run_dir$slash$uid$slash$cid<p>";
	while (<MYEXE>){
		print $_;
	}
	close MYEXE;
        #print "deleting case ", $cases[$i]," owned by ",$user_ids[$i],"<br>";
        print "deleting case ", $cid," owned by ",$uid,"<br>";
      }

} else {
   for ( $i = 0; $i <= $#files; ++$i )
      {
	open (MYEXE, "$rmdir $run_dir$slash$user_id$slash$case_id$slash$files[$i] |");
	while (<MYEXE>){
		print $_;
	}
	close MYEXE;
        print "deleting file ", $files[$i],"<br>";
      }
}

print "</body></html>";

