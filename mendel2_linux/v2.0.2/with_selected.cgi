#!/usr/bin/perl
##############################################################################
#
# list_cases.cgi -> this_file -> ...
# list_files.cgi -> this_file -> ...
#
# This file processes inputs from an array of checked cases (or files)
# and redirects to another Perl script for operation.
#
##############################################################################

## following line doesn't work for this file for some reason
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

$user_id=$formdata{'user_id'};
$admin=$formdata{'admin'};
$file_name=$formdata{'file_name'};
$options=$formdata{'options'};
$case_id=$formdata{'case_id'};
$run_dir=$formdata{'run_dir'};
$url_dir=$formdata{'url_dir'};
$version=$formdata{'version'};
$action=$formdata{'action'};
$show_all_users=$formdata{'show_all_users'};
$selected_cases=$formdata{'selected_cases'};
$selected_files=$formdata{'selected_files'};
@cases = split(/:/,$selected_cases);
@files = split(/:/,$selected_files);

$is_output = 0;

# turn buffering off for correct display order
$| = 1;

print "Content-type:text/html\n\n";
#print "version is $version";

#in case user inputs from buttons

if ($formdata{'plot'} ne "") {
   $action = "plot";
} elsif ($formdata{'report'} ne "") {
   $action = "report";
} elsif ($formdata{'start'} ne "") {
   $action = "start";
} elsif ($formdata{'load'} ne "") {
   $action = "load";
} elsif ($formdata{'input'} ne "") {
   $action = "input";
} elsif ($formdata{'output'} ne "") {
   $action = "output";
} elsif ($formdata{'diff'} ne "") {
   $action = "diff";
} elsif ($formdata{'lock'} ne "") {
   $action = "lock";
} elsif ($formdata{'unlock'} ne "") {
   $action = "unlock";
} elsif ($formdata{'list_files'} ne "") {
   $action = "list_files";
} elsif ($formdata{'more'} ne "") {
   $action = "more";
} elsif ($formdata{'delete'} ne "") {
   $action = "delete";
} elsif ($formdata{'rename'} ne "") {
   $action = "rename";
} elsif ($formdata{'filter'} ne "") {
   $action = "filter";
} elsif ($formdata{'tarball'} ne "") {
   $action = "tarball";
} elsif ($formdata{'touch'} ne "") {
   $action = "touch";
} elsif ($formdata{'compress'} ne "") {
   $action = "compress";
} elsif ($formdata{'uncompress'} ne "") {
   $action = "uncompress";
} elsif ($formdata{'unix2dos'} ne "") {
   $action = "unix2dos";
} elsif ($formdata{'ppmtogif'} ne "") {
   $action = "ppmtogif";
} else {
   $action = "-1";
}

#print "url_dir is $url_dir<br>";
#print "run_dir is $run_dir<br>";
#print "action is $action<br>";

#print "cases: $cases<br>";
#   for ( $i = 0; $i <= $#cases; ++$i )
#      {
#        print "case $i: ", $cases[$i],"<br>";
#      }
#print "$#cases is :",$#cases;

if ($#cases eq "-1" && $#files eq "-1") {

  print "<h1>No files are checked.</h1>";
  refresh(2);
  return;

}

#print "selected_cases: $selected_cases<br>";

  if ($action eq "delete") {

        #print "<h1>files: $files $#files</h1>";
        #print "<h1>cases: $cases $#cases</h1>";
        #print "<h1>case_id is: $case_id</h1>";
        #print "<h1>run_dir is: $run_dir</h1>";
        #print "<h1>url_dir is: $url_dir</h1>";
 
	print "<form name=\"delete_confirm\" method=\"post\" action=\"delete.cgi\">";
        # delete case
        if ($#files eq "-1") {
	   print "<h2>Are you sure that you want to delete $selected_cases?</h2>";
	   print "<input type=\"hidden\" name=\"selected_cases\" value=\"$selected_cases\">";
        # delete files 
        } else {
	   print "<h2>Are you sure that you want to delete $selected_files?</h2>";
	   print "<input type=\"hidden\" name=\"selected_files\" value=\"$selected_files\">";
        }
        print "<table><tr><td valign=top>";
        print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
        print "<input type=\"hidden\" name=\"admin\" value=\"$admin\">";
	print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
	print "<input type=\"hidden\" name=\"case_id\" value=\"$case_id\">";
	print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
	print "<input type=\"submit\" value=\"Yes - Delete\" style=\"width:10em\" accesskey=\"Y\">";
	print "</form></td>";

	print "<td valign=top><form name=\"delete_deny\" method=\"post\" action=\"list_cases.cgi\">";
        print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
        print "<input type=\"hidden\" name=\"admin\" value=\"$admin\">";
	print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
	print "<input type=\"hidden\" name=\"case_id\" value=\"$case_id\">";
	print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
	print "<input type=\"submit\" value=\"No\" style=\"width:10em\" accesskey=\"N\">";
	print "</form></td></tr></table>";

   } elsif ($action eq "touch") {
        chdir $run_dir;
        for ( $i = 0; $i <= $#cases; $i++ ) {
           print "touching $cases[$i]...<br>";
           system("touch $cases[$i]");
        }
        refresh(1);
   } elsif ($action eq "rename") {
	print "<form method=\"post\" action=\"rename.cgi\"> <table>";
        if($#cases > 0) {
           print "<b>case_id's are:</b>";
           print "$selected_cases<p>";
	   print "<em>Note: if more than one case was selected, the ";
           print "new file name which is entered will be treated as a directory ";
           print "instead of file. Therefore, instead of using <b>gregor/case02</b> as ";
           print "you will want to just use <b>gregor</b> if copying multiple files.</em>";
           print "<tr> <td>New name (e.g. gregor/case01 -> gregor/case02):</td> ";
           print "<td><input type=\"text\"   name=\"new_case_id\" value=\"$user_id\"></td>";

        } else {
           print "<h2>case_id is: $cases[0]</h2>";
           print "<tr> <td>New name (e.g. pre130/case01:pre130/case02 -> gregor):</td> ";
           ($uid,$cid) = split('/',$cases[0]);
           #print "<td><input type=\"text\"   name=\"new_case_id\" value=\"$cases[0]\"></td>";
           print "<td><input type=\"text\"   name=\"new_case_id\" value=\"$user_id/$cid\"></td>";
 	}
        print <<zZzZz;
        <tr><td> Copy instead of move/rename: </td>
            <td> <input type="checkbox" name="copy" value="on" CHECKED> </td> </tr>
        <tr><td></td><td> <input type="submit" value="Ok"> </td> </tr> 
        </table>
	<input type="hidden" name="selected_cases" value="$selected_cases">
	<input type="hidden" name="case_id" value="$case_id">
	<input type="hidden" name="user_id" value="$user_id">
	<input type="hidden" name="admin" value="$admin">
	<input type="hidden" name="show_all_users" value="$show_all_users">
	<input type="hidden" name="run_dir" value="$run_dir"><p>
	</form>
zZzZz
        refresh(60);

   } elsif ($action eq "plot") {
     if ($#cases > 0) { require "./plot_gnuplot_combine.cgi"; }
     require "./plot_gnuplot.cgi";

   } elsif ($action eq "diff") {
     require "./diff.cgi";

   } elsif ($action eq "input") {
     $file_name = "mendel.in";
     require "./more.cgi";

   } elsif ($action eq "output") {
     $case_id = $cases[0];
     $is_output = 1;
     require "./more.cgi";

   } elsif ($action eq "start") {
     $case_id = $cases[0];
     require "./start.cgi";
 
   } elsif ($action eq "load") {
     $case_id = $cases[0];
     require "./load.cgi";
 
   } elsif ($action eq "more") {
     $case_id = $cases[0];
     require "./more.cgi";

   } elsif ($action eq "lock") {
     for ( $i = 0; $i <= $#cases; $i++ ) {
	system ("chmod -R u-w $run_dir/$cases[$i]");
        print "<h1>case $cases[$i] locked</h1>";
     }
     refresh(1);

   } elsif ($action eq "unlock") {
     for ( $i = 0; $i <= $#cases; $i++ ) {
	system ("chmod -R u+w $run_dir/$cases[$i]");
        print "<h1>case $cases[$i] unlocked</h1>";
     }
     refresh(1);

   } elsif ($action eq "list_files") {
     $case_id = $cases[0];
     require "./list_files.cgi";

   } elsif ($action eq "filter") {
     if ($filter ne "keyword") {
        $filter=$options;
     }
     require "./list_cases.cgi";

   } elsif ($action eq "report") {
       require "./label_form.cgi";

   } elsif ($action eq "tarball") {
     chdir $run_dir;
     print $run_dir."<br>";
     $compress = "zip -r";
     for ( $i = 0; $i <= $#cases; $i++ ) {
        #print "tarring + compressing $cases[$i]...<br>";
        #system("tar cfz $cases[$i].tgz $cases[$i]");
        print "compressing $cases[$i]...<br>";
        system("$compress $cases[$i].zip $cases[$i]");
     }
     refresh(2);

   } elsif ($action eq "compress") {

     print "<h2>Compressing files</h2>";
     $path = "$run_dir/$user_id/$case_id";
     chdir $path;
     print "$path<br>";
     for ( $i = 1; $i <= $#files+1; $i++ ) {
        $my_file_name = $files[$i-1];
        print "compressing $my_file_name...<br>";
        system("bzip2 $my_file_name");
     }
     print "<meta http-equiv=\"refresh\" content=\"1;";
     print "URL=list_files.cgi?case_id=$case_id&user_id=$user_id\">\n";

   } elsif ($action eq "uncompress") {

     print "<h2>Uncompressing files</h2>";
     $path = "$run_dir/$user_id/$case_id";
     chdir $path;
     print "$path<br>";
     for ( $i = 1; $i <= $#files+1; $i++ ) {
        $my_file_name = $files[$i-1];
        print "Uncompressing $my_file_name...<br>";
        system("bunzip2 $my_file_name");
     }
     print "<meta http-equiv=\"refresh\" content=\"1;";
     print "URL=list_files.cgi?case_id=$case_id&user_id=$user_id\">\n";

   } elsif ($action eq "unix2dos") {

     print "<h2>Converting files to DOS format</h2>";
     $path = "$run_dir/$user_id/$case_id";
     chdir $path;
     print "$path<br>";
     for ( $i = 1; $i <= $#files+1; $i++ ) {
        $my_file_name = $files[$i-1];
        print "Converting $my_file_name...<br>";
        system("unix2dos -c ascii $my_file_name");
     }
     print "<meta http-equiv=\"refresh\" content=\"1;";
     print "URL=list_files.cgi?case_id=$case_id&user_id=$user_id\">\n";

   } elsif ($action eq "ppmtogif") {
     print "<h2>Converting PPM files to GIF</h2>";
     chdir $run_dir."/".$case_id;
     print $run_dir."/".$case_id."<br>";
     for ( $i = 1; $i <= $#files+1; $i++ ) {
        $ppm_file_name = $files[$i-1];
        $gif_file_name = $ppm_file_name;
        $gif_file_name =~ s/ppm/gif/;
        print "converting $ppm_file_name to $gif_file_name<br>";
        system("ppmtogif $ppm_file_name > $gif_file_name");
     }
   } else {
     print "action not supported<br>";
   }

sub refresh {
   my $refresh_seconds = shift;
   print "<meta http-equiv=\"refresh\" content=\"$refresh_seconds;";
   print "URL=list_cases.cgi?user_id=$user_id\">\n";
}
