#!/usr/bin/perl
##############################################################################
#
# qstat.cgi -> this_file -> ...
#
# This file processes inputs from an array of checked nodes (or files)
# and redirects to another Perl script for operation.
#
##############################################################################

require "parse.inc";

$action=$formdata{'action'};
$selected_nodes=$formdata{'selected_nodes'};
@nodes = split(/:/,$selected_nodes);

# turn buffering off for correct display order
$| = 1;

print "Content-type:text/html\n\n";

#print "action is $action<br>";

if ($action eq "mpdboot") {
   ### write mpd2.hosts file
   open(FILEWRITE, "> /tmp/mpd2.hosts_apache");
   print FILEWRITE "localhost\n";
   for ( $i = 0; $i <= $nn; ++$i ) {
      print FILEWRITE $nodes[$i]."\n";
   }
   close FILEWRITE;   

   ### start MPD
   print "executing command: ";
   print "/usr/local/bin/mpdboot<br><br>";
   system("export HOME=/var/www; /usr/local/bin/mpdboot > /tmp/mpd2.err");
   open(FILEREAD, "< /tmp/mpd2.err");
   while (<FILEREAD>){
       print "$_<br>";
   }
   close FILEREAD;

   print "<h2>Current MPD ring:</h2>";

   open (MYEXE, "export HOME=/var/www; /usr/local/bin/mpdtrace |");
   while (<MYEXE>){
      print "$_<br>";
   }   
   close MYEXE;

   print "<meta http-equiv=\"refresh\" content=\"5;";
   print "URL=qstat_main.cgi\">\n";

  } elsif ($action eq "kill") {
    for ( $i = 0; $i <= $nn-2; ++$i ) {
      print "rsh $nodes[$i] kill -9 -1<br>";
      system("/usr/kerberos/bin/rsh $nodes[$i] kill -9 -1 >>& /tmp/mpd2.killog");
    }
    open(FILEREAD, "< /tmp/mpd2.killog");
    while (<FILEREAD>){
       print "$_<br>";
    }
    close FILEREAD;
    system("rm /tmp/mpd2.killog");

    print "<meta http-equiv=\"refresh\" content=\"5;";
    print "URL=/admin/mpd.html\">\n";

  } elsif ($action eq "mpdallexit") {
   system("/usr/local/bin/mpdallexit >& /tmp/mpd2exit.err");
   open(FILEREAD, "< /tmp/mpd2exit.err");
   while (<FILEREAD>){
       print "$_<br>";
   }
   close FILEREAD;
   system("rm /tmp/mpd2.hosts_apache");

   print "<meta http-equiv=\"refresh\" content=\"1;";
   print "URL=/admin/mpd.html\">\n";

  } elsif ($action eq "mpdtrace") {
   print "<meta http-equiv=\"refresh\" content=\"3;";
   print "URL=/admin/mpd.html\">\n";

   open (MYEXE, "/usr/local/bin/mpdtrace |");
   while (<MYEXE>){
      print "$_<br>";
   }   
   close MYEXE;

  } elsif ($action eq "ping_cluster") {
   print "<meta http-equiv=\"refresh\" content=\"10;";
   print "URL=/admin/mpd.html\">\n";

   open (MYEXE, "/usr/local/sbin/ping_cluster |");
   while (<MYEXE>){
      print "$_<br>";
   }   
   close MYEXE;

  } elsif ($action eq "shutdown") {
    for ( $i = 0; $i <= $nn; ++$i ) {
      print "rsh $nodes[$i] shutdown -h now<br>";
      system("/usr/kerberos/bin/rsh $nodes[$i] shutdown -h now >>& /tmp/mpd2.shutdown");
    }
    open(FILEREAD, "< /tmp/mpd2.shutdown");
    while (<FILEREAD>){
       print "$_<br>";
    }
    close FILEREAD;
    system("rm /tmp/mpd2.shutdown");

    print "<meta http-equiv=\"refresh\" content=\"2;";
    print "URL=/admin/mpd.html\">\n";

  } else {
     print "action not supported<br>";
  }
