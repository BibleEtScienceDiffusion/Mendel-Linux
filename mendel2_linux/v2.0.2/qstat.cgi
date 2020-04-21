#!/usr/bin/perl
##############################################################################
#
# toc.php -> qstat.cgi -> qdel.cgi
#
# This file runs the "qstat -a" command and displays the results in a table.
# 
##############################################################################

require "./config.inc";
require "./parse.inc";

$user_id=$formdata{'user_id'};

# turn buffering off for correct display order
$| = 1;

print "Content-type:text/html\n\n";
print <<zZzZz;
<meta http-equiv="refresh" content="20;URL=qstat.cgi?user_id=$user_id">
<script language="javascript">
function fxn_set_caseid(i) {
   parent.frames.contents.caseidform.case_id.value = 
	     stop_form.selected_jids[i-1].value.substring(0,6);
}
</script>
</head>
<html>
<body>
zZzZz

if($disable_pbs) {
   print "<b>PBS has been disabled for this system.</b>  To enable PBS on a Linux machine requires installing the PBS/Torque queueing system.  Then reconfiguring Mendel's Accountant by running \"./configure --with-torque\" and reinstalling using \"make install\".";   
   exit;   
}

if($os eq "windows") {
   open (MYEXE, "tasklist | find \"mendel\" |");
   while(<MYEXE>) {
      ($exe,$jid,$buf,$buf,$mem,$buf) = split(' ', $_, 9999);
      print "<table>";
      print "<tr>";
      print "<td>$exe</td>";
      print "<td>$jid</td>";
      print "<td>$mem</td>";
      print "<td><form name=\"demo\" method=\"POST\" action=\"qdel.cgi\">";
      print "<input type=\"hidden\" name=\"jid\" value=\"$jid\">";
      print "<input type=\"hidden\" name=\"case_id\" value=\"$case_id\">";
      print "</tr>";
      print "<tr>";
      print "<td><input type=\"submit\" value=\"Stop $jid\"></form></td>";
      print "<td><font color=FFFFFF>---</font></td>";
      print "<td><font color=FFFFFF>---</font></td></tr>";
      print "<tr></table>";
   }
   close MYEXE;
   exit;
}


$num_pbs_jobs=$qstat_num_jobs; # b/c qstat_num_jobs is defined in config.inc
$num_atq_jobs = `atq | wc -l`;

#print $user_id;
#print $num_pbs_jobs;
#print $run_dir;
#print $qstat_num_jobs;
#print $qstat_cmd;

### read the case.log file and associate the case_id to the user_id
if($os ne "windows") {
   open(FH,"$run_dir/case.log") or
     die "ERROR: case.log does not exist<br>";
   @caselog = <FH>;
   close FH;
}

### report out qstat results
if ($num_pbs_jobs < 1 && !$disabled_pbs && $os eq "linux") {
   print "<a href=\"qstat_main.cgi\" style=\"text-decoration: none\" target=\"right\">No PBS jobs running.</a>";
   #print "<td valign=\"top\"><form method=\"get\" action=\"qstat_main.cgi\" target=\"right\"><input type=\"submit\" value=\"More >\" accesskey=\"E\" style=\"width:5em\" title=\"More (e)xtensive job information\"></form></td>";

   open (MYEXE, "export HOME=/var/www; /usr/local/bin/mpdtrace |");
   print "<pre>";
    
    while (<MYEXE>){ 
       print "mpdtrace: $_"; 
       if ($_ =~ m/MPICH/) {
          print "<form method=\"post\" action=\"qmpd.cgi\" target=\"right\">";
          print "<input type=\"hidden\" name=\"action\" value=\"mpdboot\">";
          print "<input type=\"submit\" value=\"mpdboot\" title=\"start a ring of daemons (on head node only)\">";
          print "</form>";
       }
    } close MYEXE;
    print "</pre>";
} else {
   if($run_queue eq "atq") {
      open (MYEXE, "atq |");
   } else {
      open (MYEXE, $qstat_cmd);
   }
   $i=1;
   print "<table><tr>";
   print "<td valign=\"top\"><form method=\"get\" action=\"qstat_main.cgi\" target=\"right\"><input type=\"submit\" value=\"More >\" accesskey=\"E\" style=\"width:5em\" title=\"More (e)xtensive job information\"></form></td>";
   print "<td valign=\"top\"><form name=\"stop_form\" method=\"post\" action=\"qdel.cgi\">";
   print "<input type=\"submit\" value=\"Stop\" style=\"width:5em\">";
   #print "<input type=\"checkbox\" name=\"write_restart\" title=\"Check this box to write restart file before shutting down\">";
   print "</td></tr></table>";
}

print "<table cellpadding=3 border=0>";
while (<MYEXE>){
        #print $_."<br>";
        if($run_queue eq "atq") {
           ($jid,$date,$time,$status,$apache) = split(' ', $_, 9999);
            # otherwise, get user_id from case_id by grepping case.log file
            @lines = grep (/atq.job.$jid/, @caselog);
            ($date,$time,$cuid,$cid,$this_jid) = split(' ', $lines[$#lines]);
            $case_id = $cid;
        } else {
           ($jid,$user,$queue,$case_id,$sid,
            $nnodes,$fld7,$fld8,$fld9,$status,$etime) = split(' ', $_, 9999);
           ### there are two ways to relate user_id to case_id
           #if in qsub.cgi set PBS name as uid.cid, then decode on following line
           #($cuid,$case_id) = split('\.',$case_id);
           # otherwise, get user_id from case_id by grepping case.log file
           @lines = grep (/$case_id/, @caselog);
           ($date,$time,$cuid,$cid,$this_jid) = split(' ', $lines[$#lines]);
        }
        ($etime1,$etime2) = split(':',$etime);
        $etime_minutes = $etime1*60 + $etime2;

	print "<tr><td bgcolor=dfdfdf><b>$cuid</b></td><td bgcolor=dfdfdf><b>$case_id</b>";
        # only let person stop cases if they are owner of case
        if($cuid eq $user_id) {
           print "<input type=\"radio\" name=\"selected_jids\"";
           print "       value=\"$case_id,$jid\" onclick=\"fxn_set_caseid($i)\"";
           print "       style=\"width:5em\">";
        }
        print "</td></tr>";

        $path="$run_dir/$cuid/$case_id/mendel.in";

        require "./input_file_parser.inc";
        #print "path: $path<br>";
        #print "case_id: $case_id<br>";
        #print "num_gen: $num_generations<br>";

        $num_gens = $num_generations;
        if($is_parallel) { 
           $tribe = "001";  # if tribes die 000 will stop reporting
        } else {
           $tribe = "000"; 
        }

        # since the time/generation becomes slower over time, it does not
        # make sense to average the entire file of times, each time
        # so just average the last 10 values to get an estimate
        #$rate = `awk '{t+=\$2;c+=1}; END {print t/c}' \
        #         $run_dir/$cuid/$case_id/$case_id.$tribe.tim`;
        $rate = `tail -10 $run_dir/$cuid/$case_id/$case_id.$tribe.tim | \ 
                 awk '{t+=\$2;c+=1}; END {print t/c}'`;

	open (MYEXE2, "tail -1 $run_dir/$cuid/$case_id/$case_id.$tribe.hst |");
	while (<MYEXE2>){
	   ($gen,$fit,$fitness_sd,$num_dmutns,$num_fmutns) = split(' ', $_);
	   $fit = sprintf("%12.7f",$fit);
	   $num_dmutns = sprintf("%d",$num_dmutns);
	   $num_fmutns = sprintf("%d",$num_fmutns);
           if ($gen == "") { $gen="N/A"; $fit="N/A";}
	}

        # for restart cases
        if ($gen > $num_gens) {
           $num_gens = $num_gens + $gen;
        }

        #$total_run_time = $num_gens*$rate/60;
      
        $gens_left = $num_gens - $gen;
        
        ## COMPLEX TIME ESTIMATE 
        ## if we really want to get a good time estimate for the run jobs
        ## we should use the following formula: m*N^2/2 + b*N
        ## m is the rate of deceleration of the time/generation vs. generations
        ## b is the value of the time/generation for generation = 1
        ## when tracking threshold is zero, m = 0, and the first
        ## term drops out

        #$rate0 = `head -10 $run_dir/$cuid/$case_id/$case_id.$tribe.tim | \
        #          awk '{t+=\$2;c+=1}; END {print t/c}'`;
        #$deceleration_rate = ($rate - $rate0) / $gen;
        #$etf1 = ($deceleration_rate*$num_gens**2/2 + $rate0*$num_gens)/60;
        #$etf2 = ($deceleration_rate*$gens_left**2/2 + $rate0*$gens_left)/60;
        #$etf = $etf1 - $etf2;

        ## SIMPLE TIME ESTIMATE 
        ## This does not include deceleration rate but 
        ## gives good estimate when tracking threshold is off (=1)
        $etf = $rate*$gens_left/60;

        if ($etf < 1) {
           $etf = $etf*60;
           $etf = sprintf("%12.1f seconds",$etf);
        } elsif ($etf < 60) {
           $etf = sprintf("%12.1f minutes",$etf);
        } elsif ($etf < 1440) {
           $etf = $etf/60;
           $etf = sprintf("%12.1f hours",$etf);
        } else {
           $etf = $etf/60/24;
           $etf = sprintf("%12.1f days",$etf);
        }

           if ($status eq "R") {
              if($num_gens > 0) {
                 $percent_complete = 100*$gen/$num_gens;
	         $percent_complete = sprintf("%12.1f%",$percent_complete);
                 if($user_id eq $cuid) {
                    print "<tr><td>Gen </td><td>$gen ($percent_complete)</td></tr>";
                    print "<tr><td>Fit </td><td>$fit</td></tr>";
                    print "<tr><td>Mutns</td><td>$num_dmutns D / $num_fmutns F</td></tr>";
                 }
                 print "<tr><td>Time left</td><td>$etf</td></tr>";
              }
           } elsif($status eq "H") {
              print "<tr><td>Status</td><td>Held</td></tr>";
           } elsif($status eq "C") {
              print "<tr><td>Status</td><td>Completed</td></tr>";
           } elsif($status eq "E") {
              print "<tr><td>Status</td><td>Exiting</td></tr>";
           } elsif($status eq "Q") {
              print "<tr><td>Status</td><td>Queued</td></tr>";
           } elsif($status eq "W") {
              print "<tr><td>Status</td><td>Waiting</td></tr>";
           } else {
              print "<tr><td>Status</td><td>Please wait...</td></tr>";
           }
	close MYEXE2;

        $i++;
}

#if ($i <= 1) {
#   print "no jobs running";
#}

# was having problems with javascript when just one job was running
if ($i==2) {
print "<input type=\"hidden\" name=\"selected_jids\" value=\"null\">";
}

print "</table>";
print "</form>";
close MYEXE;

print "<br><br><br>";
print "</body>";
print "</html>";

