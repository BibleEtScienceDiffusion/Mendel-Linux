#!/usr/bin/perl
##############################################################################
#
# toc.php -> this_file -> with_selected.cgi 
#
# This file allows the user to either view or delete
# specific files located in the case_id sub-directory.
#
##############################################################################

require "./parse.inc";
require "./config.inc";

if ($os eq "windows") {
   print "Content-type:text/html\n\n";
   #print "<meta http-equiv=\"refresh\" content=\0;";
   #print "URL=$url_dir\">\n";
   print "<a href=\"$url_dir\"><h1>Click here to access files</h1></a><br>\n";
   exit;
}

$filter=$formdata{'filter'};
# if this file is posted from a form
if ($case_id eq "") {
   $case_id=$formdata{'case_id'};
   $user_id=$formdata{'user_id'};
   # in case case is in uid/cid form (e.g. john/test01)
   if($case_id =~ /%2F/) {
     ($user_id,$case_id)=split(/%2F/,$case_id);
   }
   print "Content-type:text/html\n\n";
}

print <<zZzZz;
<html>
<head>
<title>Contents</title>
<script language="javascript">
        function selectAll(cbList,bSelect) {
          for (var i=0; i<cbList.length; i++)
            cbList[i].selected = cbList[i].checked = bSelect
        }
        // make focus to List Files filter when clicking "/" button
        document.onkeyup = KeyCheck;       
        function KeyCheck(e) {
           var KeyID = (window.event) ? event.keyCode : e.keyCode;
           //document.show_all.filter.value = KeyID;
           switch(KeyID) {
              case 191:
                 document.show_all.filter.focus();
           }
        }
</script>
</head>
<body onLoad="document.show_all.filter.focus()">
zZzZz

# turn buffering off for correct display order
$| = 1;

#print "url_dir is $url_dir<br>";
#print "case_id is $case_id<br>";

if ($case_id eq "") {
   print "ERROR: CaseID missing.";
   die;
} else {
   if ($os eq "linux") {
      # check if directory exists
      open (MYEXE, "cd $run_dir/$user_id/$case_id; pwd | grep -c var.www.cgi-bin |");
      $i=1;
      while (<MYEXE>){
        ($error) = split(' ', $_, 9999);
         #print "error is $error<br>";
         $i++;
      }
      close MYEXE;
      if ($error eq "0") {
         print "<em>Note: file listing of case $case_id</em><br>";
      } else {
         print "<b>ERROR</b>: Case does not exist.<br>";
         print "<b>SOLUTION</b>: Enter a valid CaseID.<br>";
         exit;
      }
   }
}

if ($os eq "windows") {
   open (MYEXE, "dir/os/a-d $run_dir\\$case_id\\*$filter* | more +5 |");
   $num_files=`dir/os/a-d $run_dir\\$case_id\\*$filter* | find "File(s)"`;
   ($num_files,$buf,$buf,$buf) = split(' ', $num_files, 9999);
} else {
   open (MYEXE, "cd $run_dir/$user_id/$case_id;ls -l *$filter* |");
   $num_files=`cd $run_dir/$user_id/$case_id;ls -l *$filter* | wc -l`;
}

print "<form name=\"show_all\" method=\"post\" action=\"list_files.cgi\">";
print "File filter (e.g. 000, hap, leave empty to show all): ";
print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
print "<input type=\"hidden\" name=\"case_id\" value=\"$case_id\">";
print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
print "<input type=\"text\" name=\"filter\" style=\"width:5em\" value=\"$filter\" accesskey=\"F\" onfocus=\"this.select();\">";
print "<input type=\"submit\" name=\"show_cases\" value=\"Show files\">";
print "</form>";

print "<form name=\"list_files\" method=\"post\" action=\"with_selected.cgi\">";
print "<input type=\"hidden\" name=\"case_id\" value=\"$case_id\">";
print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
print "<input type=\"hidden\" name=\"selected_cases\">";
print "<script language=\"javascript\">";
print "   var browserName=navigator.appName;";
print "   var browserVer=parseInt(navigator.appVersion);";
print "   document.write('<input type=\"hidden\" name=\"browser\" value=\"'+browserName+'\">');";
print "</script>";

print "<hr>";
print "<table><tr>";
print "<td><input type=\"submit\" name=\"delete\" value=\"Delete\" accesskey=\"W\" style=\"width:5em\"></td>";
#print "<td><input type=\"text\" name=\"options\" style=\"width:10em\"></td>";
print "<td bgcolor=red><input type=\"text\" name=\"options\" value=\"keyword\" onFocus=\"if(this.value=='keyword')this.value='';\" onBlur=\"if(this.value=='')this.value='keyword';\" title=\"enter a word to search within selected files (e.g. select the $case_id.out file, then enter any keyword: mutn, and then click the More button)\" style=\"width:5em\"/></td>";
print "<td><input type=\"submit\" name=\"more\" value=\"More\" style=\"width:5em\" accesskey=\"M\"></td>";
#print "<td><input type=\"submit\" name=\"ppmtogif\" value=\"ppmtogif\" style=\"width:5em\" accesskey=\"M\"></td>";
print "<td><input type=\"submit\" name=\"compress\" value=\"Compress\" style=\"width:7em\" accesskey=\"M\"></td>";
print "<td><input type=\"submit\" name=\"uncompress\" value=\"Uncompress\" style=\"width:7em\" accesskey=\"M\"></td>";
print "<td><input type=\"submit\" name=\"unix2dos\" value=\"Unix2DOS\" style=\"width:7em\" accesskey=\"M\"></td>";
print "<td><input type=\"button\" value=\"All\" onclick=\"selectAll(this.form.selected_files,true)\" style=\"width:5em\"></td>";
print "<td><input type=\"reset\" name=\"reset\"></td>";
print "</tr></table>";
print "<hr>";

print "<table cellpadding=3 border=0>";
print "<tr>";
print "<th></th><th>File</th><th>Size (bytes)</th><th>Date</th><th>Time</th></tr>\n";

$i=1;

while (<MYEXE>){
   if ($os eq "windows") {
      $_ =~ tr/\\|[|]|<|!|"|$|{|}|*|#|'|>|||;|%/ /; 
      if ($i <= $num_files ) {
        ($month,$time,$size,$file) = split(' ', $_, 9999);
	print "<tr>";
        print "<td><input type=\"checkbox\" name=\"selected_files\" value=\"$file:\" accesskey=\"$i\"></td>";
	print "<td><a href=\"$url_dir/$case_id/$file\">$file</a></td>";
	print "<td>".$size."</td>";
	print "<td>".$month." ".$day."</td>";
	print "<td>".$time."</td>";
	print "</tr>";
      }
   } else {
       ($Fld1,$Fld2,$Fld3,$Fld4,$size,$month,$day,$time,$file) =
           split(' ', $_, 9999);
        print "<tr>";
        print "<td><input type=\"checkbox\" name=\"selected_files\" value=\"$file:\" accesskey=\"$i\"></td>";
        print "<td><a href=\"$url_dir/$user_id/$case_id/$file\">$file</a></td>";
        print "<td>".$size."</td>";
        print "<td>".$month." ".$day."</td>";
        print "<td>".$time."</td>";
	print "</tr>";
        $total_size += $size;
   }
   $i++;
}

$total_size_mb = $total_size/1024/1024;
print sprintf("<i>Total size for this case: %7.1fMb</i><br><br>",$total_size_mb);

print "</table>";
print "</body>";
close MYEXE;
