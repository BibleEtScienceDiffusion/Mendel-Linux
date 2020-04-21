#!/usr/bin/perl

############################################################################
# This file does the directory listing for Windows
# It does not use the DIR system command but rather 
# uses Perl native calls in the subroutine read_dir
# 
# This file borrows the read_file subroutine from:
# Author: Joe Smith <js-cgi@inwap.com> 11-Feb-1996
############################################################################

require "./config.inc";
require "./parse.inc";

$user_id = $formdata{'user_id'};
$mendel_run_dir = "$run_dir/$user_id";

$namew = &read_dir(".");
if ($namew == 0) {
  print "Content-type: text/plain\n\nDirectory $dir is unreadable: $!\n";
  exit;
}

$sort = "byname";
#$sort = "bydate";
#$reverse = 1;

sub bysize {return $size{$b} <=> $size{$a};}	# Largest first
sub bydate {return $date{$b} <=> $date{$a};}	# Newest first

if ($sort eq "bysize") {
  @files = sort bysize keys %size;	# Largest file first
} elsif ($sort eq "bydate") {
  @files = sort bydate keys %date;	# Newest file first
} elsif ($sort eq "bydesc") {
  @files = &ordered(keys %date);	# List in same order as in index.txt
} else {
  @files = sort keys %size;		# Default is "byname";
}
@files = reverse @files if $reverse;

# Create an HTML listing of the files in this directory

if (defined $ENV{DOCUMENT_NAME}) {
  print "Content-type: text/html\n\n" if $cgi =~ /cgi$/;
  $anchor = "#index";
} else {
  $title = "Files in directory '$dirname'";
  print "Content-type: text/html\n\n<HTML><HEAD>";
print <<zZzZ;
  <script language="javascript">
        function selectAll(cbList,bSelect) {
          for (var i=0; i<cbList.length; i++)
            cbList[i].selected = cbList[i].checked = bSelect
        }

	function fxn_set_caseid(i) {
	   parent.parent.parent.frames.contents.caseidform.case_id.value = 
	      list_cases.selected_cases[i-1].value.substring(0,6);
	}
  </script>
  <style> 
    th { 
      font-face: helvetica; 
      color: #ffffff; 
    } 
  </style>
zZzZ
  print "<TITLE>$title</TITLE></HEAD>\n";
  print "<body bgcolor=FFFFFF>\n";
}

print "<form name=\"list_cases\" method=\"post\" action=\"with_selected.cgi\">";

print "<table><tr>";
print "<td bgcolor=orange><input type=\"button\" value=\"All\" onclick=\"selectAll(this.form.selected_cases,true)\" style=\"width:5em\"></td>";
print "<td bgcolor=orange><input type=\"reset\" name=\"reset\" value=\"Clear\" style=\"width:5em\"></td>";
print "<td bgcolor=red><input type=\"submit\" name=\"input\" value=\"Inputs\" style=\"width:5em\"></td>";
#print "<td bgcolor=red><input type=\"submit\" name=\"output\" value=\"Outputs\" style=\"width:5em\"></td>";
print "<td bgcolor=green><input type=\"submit\" name=\"delete\" value=\"Delete\" style=\"width:5em\" accesskey=\"W\" title=\"Delete case (W)\"></td>";
print "</tr></table>";

print "<table cellpadding=5 cellspacing=0 border=0>";
print "<tr bgcolor=blue><th></th><th>Case</th><th>Mutations</th><th>Fitness</th><th>Version</th><th>Labels</th></tr>";

$j=0;

while ($file = shift @files) {
  $cid = substr($file,0,$namew);

  open(DAT,"< $run_dir/$user_id/$cid/version");
  @version=<DAT>;
  close(DAT);

  open(DAT,"< $run_dir/$user_id/$cid/README");
  @labels=<DAT>;
  close(DAT);

  if ($cid ne "..") { # don't show parent directory ..
     # zebra stripe the output
     if($j%2 == 0) {
        print "<tr bgcolor=\"dfdfef\">";
     } else {
        print "<tr bgcolor=\"efefff\">";
     }
     printf("<td valign=center><input type=\"checkbox\" onclick=\"fxn_set_caseid($j)\" 
           name=\"selected_cases\" value=\"$cid:\" accesskey=\"$j\">
           <td>$cid</td>
           <td><a href=\"$url_dir/$cid/${cid}_mutn_hst.png\"><img src=\"$url_dir/$user_id/$cid/${cid}_mutn_hst.png\" width=100 height=75></a></td>
           <td><a href=\"$url_dir/$cid/${cid}_fit_hst.png\"><img src=\"$url_dir/$user_id/$cid/${cid}_fit_hst.png\"  width=100 height=75></a></td>
           <td> $version[0]  </td>
           <td> $labels[0] </td>
           </tr>\n");
  }
  $j++;
}
print "</table></form></body></html>";

exit;

###########################################################################

sub read_dir {		# Read directory, set %size, %date and $namewidth
  local($rel_dir) = @_;
  local($namelength) = 0;
  opendir(DIR,$mendel_run_dir);
  foreach $_ ("..",grep(!/^\./,readdir(DIR))) {	# Skip dot files, include ".."
    next if defined $exclude{$_};
    $_ = "$rel_dir/$_" if $rel_dir ne ".";	# Use right name for stat()
    ($size{$_},$date{$_}) = (stat $_)[7,9];
    ($size{$_},$date{$_}) = (-1,$^T) if -d _;	# Dir => minus size, this date
    $namelength = length($_) if length($_) > $namelength;
    $namelength = length($_)+1 if length($_) == $namelength && (-d _);
  }; closedir(DIR);
  return $namelength;
}

