#!/usr/bin/perl
##############################################################################
#
# toc.php -> this_file -> with_selected.cgi
#
# This file lists cases located in the $run_dir and allows the user 
# to perform a myriad of functions such as delete, archive, etc. on 
# the selected cases.  This file makes a system call to the Unix command 
# "ls -ltd" and parses and formats the resulting output.  list_cases_win.cgi,
# on the other hand, uses pure Perl to do the directory listing.
#
##############################################################################

require "parse.inc";
require "config.inc";

if ($os eq "windows") {
   require "list_cases_win.cgi";
   exit;
}

$cuid=$formdata{'cuid'};
$user_id=$formdata{'user_id'};
$admin=$formdata{'admin'};
$num_lines=$formdata{'num_lines'};
$num_cases=$formdata{'num_cases'};
$options=$formdata{'case_id'};
$show_all_users_cases=$formdata{'show_all_users_cases'};
if($show_all_users_cases ne "1") { $show_all_users_cases = 0; }
$show_users=$formdata{'show_users'};
$search_labels=$formdata{'search_labels'};
if ($search_labels eq "on") {
   $options = "search_labels";
}
$filter=$formdata{'filter'};
$version=$formdata{'version'};
$head=$formdata{'head'};
$recursion_level=$formdata{'recursion_level'};
if ($recursion_level < 0) {
   # for previous click
   $recursion_level=-$recursion_level - 1; 
} else {
   # for next click
   $recursion_level++;
}

# turn buffering off for correct display order
$| = 1;

$space = "&nbsp;&nbsp;&nbsp;";

print "Content-type:text/html\n\n";
#print "admin level is $admin<br>";
#print "cuid: $cuid user_id: $user_id<br>";
#print "Version: $version";
#print "recursion_level is $recursion_level<br>";

if($user_id eq "" && !$show_users && !$cuid) {
   print "<h1>ERROR: NO USER_ID DETECTED.</h1>";
   print "Click button on control panel or login.";
   die;
}

# in case user clicks "show users" button
if($cuid) {
   $user_id = $cuid;
}

if (! -e "$run_dir/$user_id") {
   print "<font size=+2>";
   print "ERROR: the directory which stores data for user $user_id<br>";
   print " has not yet been created yet.  To create the directory, <br>";
   print " first run a simulation by clicking \"Start\".<br>";
   print "</font>";
   exit -1; 
}

print <<zZzZz;
<html>
<head>
<link type="text/css" rel="StyleSheet" href="/mendel/css/form.css" />
<script language="javascript" type="text/javascript" src="/mendel/js/jquery.js"></script>
<script type="text/javascript" src="/mendel/js/jquery.sparkline.js"></script>
<title>Contents</title>
<script language="javascript">
        function selectAll(cbList,bSelect) {
          for (var i=0; i<cbList.length; i++)
            cbList[i].selected = cbList[i].checked = bSelect
        }

	function fxn_set_caseid(i,sauc) {
           // first split the different uid/cid pairs:
           // this looks like wes/test01:wes/test02:wes/test03
           var uidcid = list_cases.selected_cases[i-1].value.split(":");
           if(sauc == 1) {
	      parent.frames.contents.caseidform.case_id.value = 
	         uidcid[0];
           } else {
              // now split first uid/cid pair to get thiscid
              var thiscid = uidcid[0].split("/"); 
	      parent.frames.contents.caseidform.case_id.value = 
	         thiscid[1];
           }
	}

        // make focus to List Files filter when clicking "/" button
        document.onkeyup = KeyCheck;
        function KeyCheck(e) {
           var KeyID = (window.event) ? event.keyCode : e.keyCode;
           //document.show_all.filter.value = KeyID;
           switch(KeyID) {
              case 191:
                 document.use_filter.filter.focus();
           }
        }

    \$(function() {
        /** This code runs when everything has been loaded on the page */
        /* Inline sparklines take their values from the contents of the tag */
        \$('.inlinesparkline').sparkline(); 
        //\$('.inlinesparkline').sparkline('html', { type:'bar' }); 

        /* Sparklines can also take their values from the first argument 
        passed to the sparkline() function */
        var myvalues = [10,8,5,7,4,4,1];
        \$('.dynamicsparkline').sparkline(myvalues);

        /* The second argument gives options such as chart type */
        \$('.dynamicbar').sparkline(myvalues, {type: 'bar', barColor: 'green'} );

        /* Use 'html' instead of an array of values to pass options 
        to a sparkline with data in the tag */
        \$('.inlinebar').sparkline('html', {type: 'bar', barColor: 'red'} );
    });

</script>
<style>
th {
  font-face: helvetica;
  color: #ffffff;
}
</style>
</head>
<body onLoad="document.use_filter.filter.focus()">
zZzZz

#print "url_dir is $url_dir<br>";
#print "case_id is $case_id<br>";
#print "user_id is $user_id<br>";
#print "options is $options<br>";
#print "show_all_users_cases is $show_all_users_cases";
#print "os is $os<br>";

if ($show_all_users_cases) {
   print "<em><font color=\"red\">Showing all users. click \"Cases\" on Control Panel to show only your cases.</font></em>";
   $my_user_id = "";
   $my_filter = "*/*";
} else {
   if (!$show_users) {
      print "<em>Showing cases for user $user_id</em>";
   }
   $my_user_id = $user_id;
   $my_filter = "*";
}

if ($os eq "windows") {
   if ($options eq "use_filter") {
      open (MYEXE, "dir/ad/o-d $run_dir\*$filter* |");
      $num_dirs=`dir/ad/o-d $run_dir | find "Dir(s)"`;
   } else {
      $num_dirs=`dir/ad/o-d $run_dir | find "Dir(s)"`;
      open (MYEXE, "dir/ad/o-d $run_dir | more +5 |");
   }
   ($num_dirs,$buf,$buf,$buf,$buf,$buf,$buf) = 
                          split(' ', $num_dirs, 9999);
   $num_cases=$num_dirs-2;
   $total_cases = `dir/ad/o-d $run_dir | find "Dir(s)"`;
} else {
   $total_cases = `cd $run_dir/$my_user_id; ls -ld $my_filter | wc -l`;
   #print "total_cases: $total_cases";

   if ($options eq "use_filter" && $admin) {
      if($show_all_users_cases) {
         open (MYEXE, "cd $run_dir;ls -ltd */$filter* |");
         $num_cases = `cd $run_dir; ls -ld */$filter* | wc -l`;
      } else {
         open (MYEXE, "cd $run_dir;ls -ltd $user_id/$filter* |");
         $num_cases = `cd $run_dir; ls -ld $user_id/$filter* | wc -l`;
      }
   } elsif ($options eq "search_labels") {
      if($show_all_users_cases) {
         @cases = split(' ',`cd $run_dir; 
            grep $filter */*/README | awk -F'/' '{printf("%s/%s ",\$1,\$2)}'`);
         open (MYEXE, "cd $run_dir; ls -ltd @cases |");
      } else {
         @cases = split(' ',`cd $run_dir/$user_id; 
                        grep $filter */README | awk -F'/' '{print \$1}'`);
         open (MYEXE, "cd $run_dir/$user_id; ls -ltd @cases |");
      }
      #print "<p>cases are: @cases<br>";
      $num_cases = $#cases+1;
   } elsif ($options eq "next") {
      if($num_cases < 1 or $num_cases eq "") { $num_cases = 12; }
      if ($recursion_level eq "2") { 
         $head = 2*$num_cases; 
      } elsif ($head < $total_cases) {
         $head = $head + $num_cases;
      } else {
         $head = $num_cases;
      }
      open (MYEXE, "cd $run_dir/$my_user_id;ls -ltd $my_filter | \
                    head -n $head | tail -n $num_cases |");
   } elsif ($options eq "previous") {
      if($num_cases < 1 or $num_cases eq "") { $num_cases = 12; }
      if ($head > $num_cases) {
         $head = $head - $num_cases;
      } else {
         $head = $num_cases;
      }
      open (MYEXE, "cd $run_dir/$my_user_id;ls -ltd $my_filter | \
                    head -n $head | tail -n $num_cases |");
   } else {
      if($show_users) {
         $num_cases = 1000;
      } else {
         if($num_cases < 1 or $num_cases eq "") { $num_cases = 12; }
      }
      open (MYEXE, "cd $run_dir/$my_user_id;ls -ltd $my_filter | \
                    head -n $num_cases |");
   }
}

## DEBUG statements
#print "<p>";
#while (<MYEXE>) {
#   print "$_<br>";
#}
#print "<p>";

#print "number of lines in header is $head<br>";
#print "<h2>num_cases is $num_cases $admin $my_user_id</h2>";

$i=1;

print "<table width=600><tr>";

if ($os eq "windows") {
   #chop($date=`time/t`.`date/t`);
   ($now,$day,$date) = split(' ',`time/t`.`date/t`);
    $date=$now." ".$date;
} else {
   chop($date=`date`);
   $mrd_size=`du -hs $run_dir | cut -f 1`;
   $mrd_size=~ s/G//;
   #if ($mrd_size > 20) {
   #   $mrd_size = "<font color=\"red\"><b>$mrd_size</b></font>";
   #} 
   #$disk_usage=`df | awk '/hda3/ {print \$5}'`;
   $disk_usage=$disk_usage_cmd;
}

if ($filter ne "") {
    print "<td valign=\"top\"><em>Listing $num_cases cases (of $total_cases total cases) with keyword \"$filter\".</em></td>";
} else {
        $ordinal_suffix = $recursion_level;
        $ordinal_suffix =~ s/^1$/1st/g;
        $ordinal_suffix =~ s/^2$/2nd/g;
        $ordinal_suffix =~ s/^3$/3rd/g;
        $ordinal_suffix =~ s/4$|5$|6$|7$|8$|9$|0$|1$|2$|3$/$&th/g;
        if(!$show_users) {
	   print "<td valign=\"top\"><em>Listing $ordinal_suffix most recent $num_cases cases (of $total_cases total cases).</em></td>";
        }
}

#open file(TDATA,"</var/log/temp");
#my @temp = <TDATA>;
$temp = `cat /var/log/temp`;
chomp($temp);

print "<td width=260 align=right>$date<br><font size=\"-1\">$this_server | $version | $os | ${mrd_size} | $disk_usage full | ${temp}F</font></td>";
print "</tr></table>";

# Case filter
if($admin and !$show_dir and !$show_users){
   print "<form name=\"use_filter\" method=\"post\" action=\"list_cases.cgi\">";
   print "<u>C</u>ase filter (e.g. abc*, *bc1*, *12): ";
   print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
   print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
   print "<input type=\"hidden\" name=\"case_id\" value=\"use_filter\">";
   print "<input type=\"hidden\" name=\"admin\" value=\"$admin\">";
   print "<input type=\"hidden\" name=\"version\" value=\"$version\">";
   print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
   print "<input type=\"hidden\" name=\"show_all_users_cases\" value=\"$show_all_users_cases\">";
   #print "<input type=\"hidden\" name=\"show_all_users_cases\" value=\"1\">";
   print "<input type=\"text\" name=\"filter\" style=\"width:5em\" title=\"Note: filter is case-sensitive so xy is not same as XY\" value=\"$filter\" accesskey=\"C\" onfocus=\"this.select();\">";
   print "<input type=\"checkbox\" name=\"search_labels\" title=\"Check to search labels instead of casenames.\" value=\"on\">";
   if($show_all_users_cases) {
      print "<input type=\"submit\" name=\"show_cases\" value=\"Search all cases\">";
   } else {
      print "<input type=\"submit\" name=\"show_cases\" value=\"Search my cases\">";
   }
   print "</form>";
}

print "<form name=\"list_cases\" method=\"post\" action=\"with_selected.cgi\">";
print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
print "<input type=\"hidden\" name=\"admin\"   value=\"$admin\">";
print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
print "<input type=\"hidden\" name=\"version\" value=\"$version\">";
print "<input type=\"hidden\" name=\"show_all_users_cases\" value=\"$show_all_users_cases\">";

print "<script language=\"javascript\">";
print "   var browserName=navigator.appName;";
print "   var browserVer=parseInt(navigator.appVersion);";
print "   document.write('<input type=\"hidden\" name=\"browser\" value=\"'+browserName+'\">');";
print "</script>";

if(!$show_users) {
    #print "<fieldset>";
    print "<table width=600 cellpadding=0 bgcolor=efefef><tr>";
    print "<td><span class=\"button\"><input class=\"all\" type=\"button\" value=\"\" onclick=\"selectAll(this.form.selected_cases,true)\" title=\"Select All\"></span></td>";
    #print "<td bgcolor=\"\"><span class=\"button\"><input class=\"plot\" type=\"submit\" name=\"plot\" title=\"Run Gnuplo(t) for selected case/s\" value=\"Plots\" accesskey=\"T\" style=\"width:5em\"></span></td>";
    print "<td bgcolor=\"\"><span class=\"button\"><input class=\"label\" type=\"submit\" name=\"report\" value=\"Label\" style=\"width:6em\"></span></td>";
#print "<td bgcolor=\"\"><input type=\"submit\" name=\"list_files\" value=\"List Files\" style=\"width:5em\"></td>";
    print "<td bgcolor=\"\"><span class=\"button\"><input class=\"diff\" type=\"submit\" name=\"diff\" value=\"Diff\" title=\"Select two or three cases and click this button to give the difference in the input files\" style=\"width:6em\"></span></td>";
    print "<td><span class=\"button\"><input class=\"delete\" type=\"submit\" name=\"delete\" value=\"Delete\" style=\"width:6em\" accesskey=\"W\" title=\"Delete case (W)\"></span></td>"; 
    if($admin) {
	print "<td bgcolor=\"\"><span class=\"button\"><input class=\"rename\" type=\"submit\" name=\"rename\" value=\"Rename\" style=\"width:6em\" title=\"Rename, Archive, Copy\"></span></td>";
    }
    if ($os ne "windows") {
	print "<td bgcolor=\"\"><span class=\"button\"><input class=\"lock\" type=\"submit\" name=\"lock\" value=\"Lock\" style=\"width:6em\"></span></td>";
	print "<td><span class=\"button\"><input class=\"unlock\" type=\"submit\" name=\"unlock\" value=\"Unlock\" style=\"width:6em\"></span></td>";
    }
    print "</tr>";
    #print "</table>";
    
    #print "<table cellpadding=0>";
    print "<tr>";
    print "<td><span class=\"button\"><input class=\"clear\" type=\"reset\" name=\"reset\" value=\"\" title=\"Clear selected\"></span></td>";
    print "<td><span class=\"button\"><input class=\"inputs\" type=\"submit\" name=\"input\" value=\"Input\" style=\"width:5em\"></span></td>";
#print "<td><input type=\"text\" name=\"options\" style=\"width:5em\"></td>";
    print "<td><input type=\"text\" name=\"options\" value=\"keyword\" accesskey=\"K\" onFocus=\"if(this.value=='keyword')this.value='';\" onBlur=\"if(this.value=='')this.value='keyword';\" title=\"enter a word to search within either the input or output files (e.g. select one or more cases, then enter any keyword such as: pop_size, and then either click the Input or Output button)\" style=\"width:7.5em;height:2em\"/></td>";
    print "<td><span class=\"button\"><input class=\"output\" type=\"submit\" name=\"output\" value=\"Output\" style=\"width:6em\"></span></td>";
    if($admin) {
	print "<td><span class=\"button\"><input class=\"touch\" type=\"submit\" name=\"touch\" value=\"Touch\" style=\"width:6em\" title=\"Move selected case/s to top of list\"></span></td>";
    }
    print "<td><span class=\"button\"><input class=\"compress\" type=\"submit\" name=\"tarball\" value=\"Zip\" style=\"width:6em\" title=\"Compress the case for downloading\"></span></td>";
    print "</tr></table>";
    #print "</fieldset>";
}

#if($time_to_delete ne "never") {
#   print "<font size=\"-1\"><em>WARNING: cases will be automatically deleted in $time_to_delete unless they are locked.</font></em>";
#}

#print "<fieldset>";
print "<table width=648 cellpadding=0 cellspacing=0 border=0>";
print "<tr bgcolor=blue>";
if($show_all_users_cases) {
   print "<th></th><th> </th><th> User </th><th>Case</th><th>Date</th><th>Time</th>"; 
} elsif($show_users) {
   print "<th></th><th> User </th><th>Size</th><th>Date</th><th>Time</th>"; 
} else {
   print "<th></th><th></th><th align=left>Case</th><th align=left>Date</th><th align=left>Time</th>"; 
}
if(!$show_users) {
   #print "<th>Pop. size</th><th>#Gens</th><th>Mutn. Rate</th><th>Ben/Del</th>";
   #print "<th>Deleterious</th><th>Favorables</th>";
   print "<th align=left>Version</th><th align=left>Labels</th>";
}
print "</tr>\n";
$j=1;

while (<MYEXE>) {
    $num = $j + $head;
    if ($os eq "windows") {
	# change <DIR>, which was causing problems, to DIR
	$_ =~ tr/<|>/ /; 
	($month,$time,$Fld3,$cid) = split(' ', $_, 9999);
    } else {
	($octal,$Fld2,$Fld3,$Fld4,$size,$month,$day,$time,$uid_cid) =
	    split(' ', $_, 9999);
	
        if($show_all_users_cases || $options eq "use_filter") { 
           ($uid,$cid) = split('/', $uid_cid); 
           #print "cid is: $cid; uid is: $uid<br>";
        } else {
            $uid = $user_id;
            $cid = $uid_cid;
            $uid_cid = "$user_id/$cid";
        }
	
	$label = "";
	open (MYEXE2, "head -1 $run_dir/$uid/$cid/README | ");
	while (<MYEXE2>){
	    $label = $_;
	}
	close MYEXE2;
	
	$this_version = "";

	open (MYEXE2, "head -1 $run_dir/$uid/$cid/version | ");
	while (<MYEXE2>){
	    $this_version = $_;
	}
	close MYEXE2;
	
        # zebra stripe the output
        if($j%2 == 0) {
	   print "<tr bgcolor=\"dfdfef\">";
        } else {
	   print "<tr bgcolor=\"efefff\">";
        }

	if ($octal eq "dr-xr-xr-x") {
	    print "<td><img src=\"/mendel/images/famfamfam.com/lock.png\"></td>";
	} else {
	    print "<td></td>";
	}
    }
 
    # use uid/cid form if (1) showing all user cases, or
    # (2) user has clicked onto another users id 
    # e.g. list_cases.cgi?cuid=john link
    #if($show_all_users_cases==1 || $cuid || $options eq "use_filter") {
    if($show_all_users_cases==1 || $cuid) {
       $cuidflag = 1;
    } else {
       $cuidflag = 0;
    }

    if ($j <= $num_cases || $os eq "linux") {
        if(!$show_users) {
	   print "<td>$space<input type=\"checkbox\" name=\"selected_cases\" value=\"$uid_cid:\" accesskey=\"$j\" onclick=\"fxn_set_caseid($j,$cuidflag)\">$space</td>";
        }

	if($show_all_users_cases) { 
           print "<td><a href=\"list_cases.cgi?cuid=$uid\">$uid</a>$space</td>"; 
        } elsif ($show_users) {
           if($cid eq "case.log") {
              print "<td><a href=\"$url_dir/$cid\">$cid</a>$space</td>"; 
           } else {
              print "<td><a href=\"list_cases.cgi?cuid=$cid\">$cid</a>$space</td>"; 
           }
        }

	if ($cid=~/tgz/ or $cid=~/zip/) {
	    print "<td><a href=\"$url_dir/$uid/$cid\">$cid</a></td>"; 
        } elsif ($show_users) {
            ($dir_size) = split(' ',`du -hs $run_dir/$cid`);
            print "<td>$dir_size</td>";
	} elsif ($cid ne "." and $cid ne ".." and $cid ne "/") { 
	    print "<td>$cid</td>"; 
	} else {
	    print "<td>ERROR</td>"; 
	}
	print "<td style=\"height:30px\" width=50>".$month." ".$day."</td>";
	print "<td align=left>$time$space</td>";

	#if ($j < 20 and $cid !~ /tgz/ and $cid !~ /zip/ and !$show_users) {
	if ($cid !~ /tgz/ and $cid !~ /zip/ and !$show_users) {
 
           # These are sparklines
           #print "<td style=\"height:50px\" align=center><span class=\"inlinesparkline\">";
           #open(FH,"$run_dir/$uid/$cid/$cid.000.hst");
           #while (<FH>) {
           #   ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
           #   if ($col1%1==0 && $col1 ne "#") {print "$col2,";}
           #}
           #print "</span></td>";
           #close FH;


           #print "<td style=\"height:50px\" align=center><span class=\"inlinesparkline\">";
           #open(FH,"$run_dir/$uid/$cid/$cid.000.dst");
           #while (<FH>) {
           #    ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
           #    #$x = -(log($col1+1.e-8)+12)/10;
           #    $x = -log($col1+1.e-8);
           #    if ($. <= 53 && $col1 ne "#") {print "$col3,";}
           #}
           #print "</span></td>";
           #close FH;

           #print "<td style=\"height:50px\" align=center><span class=\"inlinesparkline\">";
           #open(FH,"$run_dir/$uid/$cid/$cid.000.dst");
           #while (<FH>) {
           #   ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
           #   $x = -log($col1+1.e-8);
           #   if ($. >= 56 && $col1 ne "#") {print "$col3, ";}
           #}
           #print "</span></td>";
           #close FH;
	} else {
	    print "<td></td>";
	    print "<td></td>";
	}
        print "<td>$this_version</td>";
        print "<td>$label</td>";

	print "<input type=\"hidden\" name=\"case_id\" value=\"$cid\">";
        print "</tr>";
    }
    $j++;
}

# add extra blue line on bottom for looks
#print "<tr bgcolor=blue><td>$space</td><td>$space</td><td>$space</td><td>$space</td><td>$space</td><td>$space</td><td>$space</td><td>$space</td></tr>";

# there needs to be at least two instances of input for selected_cases
# for HTML to treat it as an array.  if the following statement is not here
# and only a single case existst in the list_cases dialogue, 
# when the user clicks the checkbox, it will not show up in
# the CaseID box on the CONTROL PANEL
print "<input type=\"hidden\" name=\"selected_cases\">";

print "</table>";
#print "</fieldset>";
print "</form>";
close MYEXE;

print "<table><tr><td>";

if ($recursion_level > 1 and !$show_users) {
   print "<form name=\"previous_form\" method=\"post\" action=\"list_cases.cgi\">";
   print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
   print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
   print "<input type=\"hidden\" name=\"num_cases\" value=\"$num_cases\">";
   print "<input type=\"hidden\" name=\"case_id\" value=\"previous\">";
   print "<input type=\"hidden\" name=\"head\"    value=\"$head\">";
   print "<input type=\"hidden\" name=\"filter\"  value=\"$filter\">";
   print "<input type=\"hidden\" name=\"version\" value=\"$version\">";
   print "<input type=\"hidden\" name=\"recursion_level\" value=\"-$recursion_level\">";
   print "<input type=\"hidden\" name=\"show_all_users_cases\" value=\"$show_all_users_cases\">";
   print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
   print "<input type=\"hidden\" name=\"admin\" value=\"$admin\">";
   print "<input type=\"submit\" value=\"<< Previous\" title=\"Pre(v)ious $num_cases cases\" accesskey=\"V\" style=\"width:7em\">";
   print "</form>";
   print "</td>";
}

if ($recursion_level < $total_cases/$num_cases and !$show_users) {
   print "<td>";
   print "<form name=\"next_form\" method=\"post\" action=\"list_cases.cgi\">";
   print "<input type=\"text\" name=\"num_cases\" value=\"$num_cases\" style=\"width:3em\">";
   print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
   print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
   print "<input type=\"hidden\" name=\"case_id\" value=\"next\">";
   print "<input type=\"hidden\" name=\"head\" value=\"$head\">";
   print "<input type=\"hidden\" name=\"filter\"  value=\"$filter\">";
   print "<input type=\"hidden\" name=\"version\" value=\"$version\">";
   print "<input type=\"hidden\" name=\"recursion_level\" value=\"$recursion_level\">";
   print "<input type=\"hidden\" name=\"show_all_users_cases\" value=\"$show_all_users_cases\">";
   print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
   print "<input type=\"hidden\" name=\"admin\" value=\"$admin\">";
   print "<input type=\"submit\" value=\"Next >>\" title=\"(N)ext $num_cases cases\" accesskey=\"N\" style=\"width:7em\">";
   print "</form>";
   print "</td>";
}

if($admin and $show_all_users_cases ne "1" and !$show_users) {
    print "<td>";
    print "<form name=\"show_all_data_form\" method=\"post\" action=\"list_cases.cgi\">";
    print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
    print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
    print "<input type=\"hidden\" name=\"head\" value=\"$head\">";
    print "<input type=\"hidden\" name=\"filter\"  value=\"$filter\">";
    print "<input type=\"hidden\" name=\"version\" value=\"$version\">";
    print "<input type=\"hidden\" name=\"recursion_level\" value=\"0\">";
    print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
    print "<input type=\"hidden\" name=\"admin\" value=\"$admin\">";
    print "<input type=\"hidden\" name=\"show_all_users_cases\" value=\"1\">";
    print "<input type=\"submit\" value=\"Show all user's cases\" title=\"Show All Cases\" style=\"width:12em\">";
    print "</form>";
    print "</td>";
}

if($admin and !$show_users) {
    print "<td>";
    print "<form name=\"show_users_form\" method=\"post\" action=\"list_cases.cgi\">";
    print "<input type=\"hidden\" name=\"url_dir\" value=\"$url_dir\">";
    print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
    print "<input type=\"hidden\" name=\"head\" value=\"$head\">";
    print "<input type=\"hidden\" name=\"filter\"  value=\"$filter\">";
    print "<input type=\"hidden\" name=\"version\" value=\"$version\">";
    print "<input type=\"hidden\" name=\"recursion_level\" value=\"0\">";
    #print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
    print "<input type=\"hidden\" name=\"admin\" value=\"$admin\">";
    print "<input type=\"hidden\" name=\"show_users\" value=\"1\">";
    print "<input type=\"submit\" value=\"Show users\" title=\"Show Users Directories\" style=\"width:12em\">";
    print "</form>";
    print "</td>";
}

print "</td></tr></table>";
print "</body>";

