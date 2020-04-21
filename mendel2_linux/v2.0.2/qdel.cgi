#!/usr/bin/perl
##############################################################################
#
# qstat.cgi -> this_file -> (auto-refresh to) qstat.cgi
#
# This file deletes a case from the PBS queue using the qdel command.
# It then auto-refreshes back to qstat.cgi
#
##############################################################################

require "./config.inc";

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

print "Content-type:text/html\n\n";
print "<html><body>";

# turn buffering off for correct display order
$| = 1;

if ($os eq "windows") {
   $case_id=$formdata{'case_id'};
   $jid=$formdata{'jid'};
   system("taskkill/PID $jid /F");
   #print "<h2>Running taskkill/PID $jid</h2>";
   exit;
} else {
   $selected_jids=$formdata{'selected_jids'};
   @jids = split(/:/,$selected_jids);
   ($case_id, $jid) = split(/,/,$selected_jids);
   $jid =~ s/null//;
   $write_restart=$formdata{'write_restart'};
}
#print "write_restart is $write_restart";

if ($write_restart eq "on") {
   print "<meta http-equiv=\"refresh\" content=\"3;";
   print "URL=qstat.cgi\">\n";
   system("echo 1 > $run_dir/$case_id/$case_id.st8");
   if ($jid == "null"){
     print "Please select which case you want to stop, then press stop.";
   } else {
     print "<h2>Writing restart file $case_id.st8 and shutting down.</h2>";
     print "Please allow some time for job to shutdown properly.";
   }
} else {
   print "<meta http-equiv=\"refresh\" content=\"1;";
   print "URL=qstat.cgi\">\n";

   # extract number only from JID b/c sometimes the server name 
   # gets truncated when listing qstat, so the job will not stop
   # properly
   ($jid)=split('\.',$jid);  

   if ($jid eq "") {
      print "<h2>Nothing to stop.</h2>";
      print "make sure radio button is selected before clicking stop";
      die;
   } else {
      system("$qdel $jid");
      print "<h2>Stopping Case $case_id (JID=$jid)</h2>";

      #$result = `atrm $jid 2>&1`;
      #print "<h2>Stopping Case $case_id (JID=$jid)</h2>";
      #print $result;
   }
}
print "</body></html>";



