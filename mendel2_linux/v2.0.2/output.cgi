#!/usr/bin/perl
##############################################################################
#
# toc.php -> this_file -> to screen
#
# This file provides a snapshot output of the running mendel output
# by using the "tail" command.
#
##############################################################################

require "config.inc";
require "parse.inc";

# if being posted from control panel
if ($case_id eq "") {
   $case_id=$formdata{'case_id'};
   $user_id=$formdata{'user_id'};
   # in case case is in uid/cid form (e.g. john/test01)
   if($case_id =~ /%2F/) {
     ($user_id,$case_id)=split(/%2F/,$case_id);
   }
   $num_lines=$formdata{'num_lines'};
   $ajax=$formdata{'ajax'};
   if($num_lines eq "") { $num_lines = 36; }
   $auto=$formdata{'auto'};
   print "Content-type:text/html\n\n";
}

# turn buffering off for correct display order
$| = 1;

#print "cases is $#cases<br>";
#print "run_dir is $run_dir<br>";
#print "case_id is $case_id<br>";
#print "user_id is $user_id<br>";
#print "num_lines is $num_lines<br>";
#print "$ENV{'REQUEST_METHOD'}<br>";

if ($#cases eq "-1") {
   $ncases = 0;
} else {
   $ncases = $#cases;
}

for ( $i = 0; $i <= $ncases; $i++ ) {

        if ($#cases ne "-1") {
           $case_id = $cases[$j];
        }

        ### the following uses an IFRAME buffer 
        #$ofile = "$url_dir/$case_id/$case_id.out";
        #print "<iframe src =\"$ofile\" STYLE=\"background-color:#efefef;\" width=\"100%\" height=\"80%\">";
        #print "<p>Your browser does not support iframes.</p>";
        #print "</iframe>";

        #print "<td>";
	if(!$ajax) {print "<h1>Output for $case_id ";}
        if ($auto eq "1") {
           print "(auto-updating)</h1>";
           print "<em>click \"Output\" to switch to manual updating</em>";
        } else {
           print "</h1>";
        }
	print "<table bgcolor=efefef border=1 cellpadding=10><tr><td>";
	print "<pre>";

	if ($num_lines eq "1000") {
           if ($os eq "windows") {
	      open (MYEXE, "< $run_dir\\$case_id\\$case_id.000.out");
           } else {
              open (MYEXE, "/bin/cat $run_dir/$user_id/$case_id/$case_id.out | sed -e 's/^generation.*/<b><font color=blue>&<\\/font><\\/b>/' -e 's/BOTTLENECK.*/<b><font color=red>&<\\/font><\\/b>/' |");
           }
	} else {
           # automatically update the output every 3 seconds:
           if($auto eq "1") {
              print "<META HTTP-EQUIV=\"refresh\" CONTENT=\"3;URL=output.cgi?case_id=$case_id&user_id=$user_id&auto=1\"/>";
           }
           if ($os eq "windows") {
              open(MYEXE, "< $run_dir\\$case_id\\$case_id.000.out") or die "can't open $file: $!";
              $count++ while <MYEXE>;
              $start=$count-$num_lines;
              seek(MYEXE,0,0); # rewind file
           } else {
              open (MYEXE, "/usr/bin/tail -$num_lines $run_dir/$user_id/$case_id/$case_id.out | sed -e 's/^generation.*/<b><font color=blue>&<\\/font><\\/b>/' -e 's/BOTTLENECK.*/<b><font color=red>&<\\/font><\\/b>/' -e 's/.*SHUTDOWN.*/<b><font color=red>&<\\/font><\\/b>/' -e 's/.*SIGSEGV.*/<b><font color=red>&<\\/font><\\/b>/' |");
           }
	}

        $count = 0;
	while (<MYEXE>){
                $count++;
                if ($os eq "windows") {
                   if ($count > $start) { print $_; }
                } else {
                   if ($_ =~ m/AUXILIARY ROUTINES/ && $auto eq "1") {
                      print "<META HTTP-EQUIV=\"Refresh\" CONTENT=\"1;URL=plot_gnuplot.cgi?case_id=$case_id&user_id=$user_id\"/>";
                   }
		   print "$_";
                }
	}
	close MYEXE;

	print "</td></tr></table><p>";

	print "</pre>";

   if(!$ajax) {
        print "<table><tr><td>";

	print "<form name=\"advanced\" method=POST action=\"output.cgi\">";
	print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
	print "<input type=\"hidden\" name=\"case_id\" value=\"$case_id\">";
	print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
	print "<input type=\"hidden\" name=\"num_lines\" value=\"1000\">";
	print "<INPUT type=\"submit\" value=\"More >>\" accesskey=\"M\">";
	print "</form>";

        print "</td><td>";

	print "<form method=post action=\"monitor.cgi\">";
	print "<input type=\"hidden\" name=\"case_id\" value=\"$case_id\">";
	print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
	print "<input type=\"submit\" value=\"Monitor data in real-time\">";
	print "</form>";

        print "</td><td>";

        if($auto ne "1" && $os ne "windows") {
	   print "<form name=\"advanced\" method=POST action=\"output.cgi\">";
	   print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
	   print "<input type=\"hidden\" name=\"case_id\" value=\"$case_id\">";
	   print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
	   print "<input type=\"hidden\" name=\"auto\" value=\"1\">";
	   print "<INPUT type=\"submit\" value=\"Turn on auto-update\" accesskey=\"M\">";
	   print "</form>";
        }
        print "</td></tr></table>";
    }
}
