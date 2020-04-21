#!/usr/bin/perl
##############################################################################
#
# toc.php -> qstat.cgi -> qdel.cgi
#
# This file gives the status of epiphany head node via 3 commands:
#   - CPU usage:    top
#   - Memory usage: from /proc/meminfo
#   - Disk usage:   df -k
#
# It also runs the "qstat -a" command and displays the results in a table.
# 
# Finally, it runs the "listmpdjobs" command to give specific information
# about the jobs running on the compute nodes.
#
##############################################################################

require "./config.inc";
if ($os eq "windows") {
   require "./qstatw.cgi";
   exit;
}

# turn buffering off for correct display order
$| = 1;

print "Content-type:text/html\n\n";
print "<html>";
print "<body>";
#print "<h1><u>system status</u></h1>";

#print "<h2>PBS Queue</h2>";
#print "<table cellpadding=3 border=1>";
#print "<tr><th>Case ID</th><th>Generation</th><th>Fitness</th><th>JID</th><th>SID</th><th>Nodes</th><th>Status</th>";
#print "<th>Elapsed Time</th></tr>";
#open (MYEXE, $qstat_cmd);
#$i=1;
#while (<MYEXE>){
#        ($jid,$user,$queue,$case_id,$sid,$nnodes,$fld7,$fld8,$fld9,$status,$etime) = split(' ', $_, 9999);
#	print "<tr>";
#	print "<td>$case_id</td>";
#        
#        open (MYEXE2, "grep gen $run_dir/$case_id/$case_id.out | tail -1 |");
#        while (<MYEXE2>){
#           ($f1,$f2,$gen,$f4,$f5,$f6,$f7,$f8,$f9,$f10,$fit) = split(' ', $_);
#           if ($gen == "") { $gen="N/A"; $fit="N/A";}
#           print "<td>$gen</td>";
#           print "<td>$fit</td>";
#        }
#        close MYEXE2;
# 
#	print "<td>$jid</td>";
#	print "<td>$sid</td>";
#	print "<td>$nnodes</td>";
#        print "<td>$status</td>";
#        print "<td>$etime</td>";
#	#print "<td><form name=\"demo\" method=\"POST\" action=\"qdel.cgi\"><input type=\"hidden\" name=\"jid\" value=\"$jid\"><input type=\"hidden\" name=\"case_id\" value=\"$case_id\"><input type=\"submit\" value=\"Stop\"></form></td>";
#	print "</tr>";
#        $i++;
#}
#close MYEXE;
#print "</table>";

print "<h2>System information:</h2>";

print "<font face=\"courier\">";
open (MYEXE, "/usr/bin/top -b -n 1 | awk '/cpu0/ {print \$1\":\",\$2}' | ");
while (<MYEXE>){
        print "$_<br>";
}
close MYEXE;
open (MYEXE, "cat /proc/meminfo | awk '/Mem[TF]/ {print \$1,\$2/1024/1024 \" GB\"}' | ");
while (<MYEXE>){
        print "$_<br>";
}
close MYEXE;

print "Disk: $disk_usage_cmd full";
print "</font>";

#print "<h2>Gnuplot jobs on head node:</h2>";

open (MYEXE, "ps -au apache | grep gnuplot |");
while (<MYEXE>){
        print "$_";
}
close MYEXE;

# Note: mpdtrace is no longer implemented since Torque 3.0
#print "<h2>MPDTRACE: show all mpd's in ring:</h2>";
#
#open (MYEXE, "export HOME=/var/www; /usr/local/bin/mpdtrace |");
#print "<pre>";
#
# while (<MYEXE>){
#    print "mpdtrace: $_";
#    if ($_ =~ m/MPICH/) {
#       print "<form method=\"post\" action=\"qmpd.cgi\" target=\"right\">";
#       print "<input type=\"hidden\" name=\"action\" value=\"mpdboot\">";
#       print "<input type=\"submit\" value=\"mpdboot\" title=\"start a ring of daemons (on head node only)\">";
#       print "</form>";
#    }
# } close MYEXE;
#print "</pre>";

#print "<h2>MPD job information:</h2>";
#open (MYEXE, "export HOME=/var/www; /usr/local/bin/mpdlistjobs |");
##open (MYEXE, "ls -l /var |");
##open (MYEXE, "env;ls -l /var/www/torque |");
#print "<pre>";
#while (<MYEXE>){
#	print "$_";
#}
#close MYEXE;

print "<h2>Qstat raw output:</h2>";
print "<pre>";
print `$qstat -a`;
print "</pre>";

print "</body>";
print "</html>";
