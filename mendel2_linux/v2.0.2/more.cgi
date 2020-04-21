#!/usr/bin/perl
##############################################################################
#
# list_cases.cgi -> with_selected.cgi -> this_file -> (refresh to)list_cases.cgi
# list_files.cgi -> with_selected.cgi -> this_file -> (refresh to)list_cases.cgi
#
# This file either: displays a file or files using the "cat" command,
# or if a keyword is given, it only displays the line of the file(s)
# which contains the specific keyword using the "grep" command. 
#
##############################################################################

require "./parse.inc";

$cols=$formdata{'cols'};

# in case this is posted from form instead of included/required
if ($case_id eq "") {
   $case_id=$formdata{'case_id'};
   $user_id=$formdata{'user_id'};
   # in case case is in uid/cid form (e.g. john/test01)
   if($case_id =~ /%2F/) {
     ($user_id,$case_id)=split(/%2F/,$case_id);
   }
   print "Content-type:text/html\n\n";
} else {
  # I can't remember why the following lines were needed
  #if ($os eq "windows") {
  #  $run_dir=sprintf("%s",substr($run_dir,0,length($run_dir)-7)); 
  #}
}

if ($file_name eq "") {
   $file_name=$formdata{'file_name'};
}
if ($options eq "keyword") {
   $options = "";
}

require "./config.inc";

$selected_cases=$formdata{'selected_cases'};
@cases = split(/:/,$selected_cases);
$selected_files=$formdata{'selected_files'};
@files = split(/:/,$selected_files);

# turn buffering off for correct display order
$| = 1;

#print "<h1> case_id is $case_id</h1>";
#print "<h1> user_id is $user_id</h1>";
#print "<h1> #cases is $#cases</h1>";
#print "file_name is $file_name<br>";
#print "run_dir is $run_dir<br>";
#print "url_dir is $url_dir<br>";
#print "options are $options<br>";

if ($#files eq "-1") {
   $nfiles = 0;
   $layout_type = "rows";
} else {
   $nfiles = $#files;
}

if ($#cases eq "-1") {
   $ncases = 0;
   $layout_type = "cols";
} else {
   $ncases = $#cases;
}

if ($options ne "") {
   $layout_type = "cols";
}

if ($layout_type eq "rows") { 
   print "<table><tr>"; 
}

for ( $j = 0; $j <= $ncases; $j++ ) {

	if ($#cases ne "-1") {
	   ($user_id,$case_id) = split('/',$cases[$j]);
 	}

	for ( $i = 0; $i <= $nfiles; $i++ ) {

		if ($#files ne "-1") {
		   $file_name = $files[$i];
		} elsif ($is_output) {
		   $file_name = $case_id.".out";
		}

		if ($layout_type eq "rows") { 
		   print "<td valign=top>";
		}
		print "<h1>$user_id/$case_id/$file_name:<p></h1>";
		print "<pre>";

                $path = "$run_dir/$user_id/$case_id/$file_name";
                if(!-e $path) {
                   print "ERROR: $file_name does not exist<br>";
                   print "\$path is: $path<br>";
                   die;
                }

                # get contents of file
		if ($options eq "") {
                   open(MYEXE,"$path");
   		} else {
                   # search for string $options in $path
		   open (MYEXE, "grep $options $path | ");
		}

                # display contents to user
		while (<MYEXE>){
			print "$_";
		}
		close MYEXE;

		print "</pre>";
		if ($layout_type eq "rows") { 
		   print "</td>";
 		}
	}

}
if ($layout_type eq "rows") { 
   print "</tr></table>";
}

