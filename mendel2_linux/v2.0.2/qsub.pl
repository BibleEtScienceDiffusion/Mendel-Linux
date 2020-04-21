#!/usr/bin/perl
##############################################################################
#
# input_file_writer.pl -> this_file -> (auto-refresh to) qstat.cgi
#
# This file creates a pbs.script or batch.in and then submits the job to the
# Queuing system via either the qsub, at, batch command.  After 1 second, 
# the page is automatically forwarded to qstat.cgi
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

$user_id=$formdata{'user_id'};
$case_id=$formdata{'case_id'};
$run_dir=$formdata{'run_dir'};
if($os eq "windows") {
   $case_dir="..\\..\\htdocs\\$case_id";
} else {
   $case_dir="$run_dir/$user_id/$case_id";
}
$pop_size=$formdata{'pop_size'};
$num_generations=$formdata{'num_generations'};
$offspring_per_female=$formdata{'offspring_per_female'};
$fraction_fav_mutn=$formdata{'fraction_fav_mutn'};
$mutn_rate=$formdata{'mutn_rate'};
$selection_noise_std_dev=$formdata{'selection_noise_std_dev'};
$is_parallel=$formdata{'is_parallel'};
$version=$formdata{'version'};
$num_procs=$formdata{'num_procs'};
$run_queue = $formdata{'run_queue'};
$num_tribes=$formdata{'num_tribes'};
$mem_reqd=$formdata{'mem_reqd'};
$mem_available=$formdata{'mem_available'};
if($num_nodes > 1) { 
   $num_nodes = int($num_tribes/$procs_per_node + .5); 
}
$restart_case = $formdata{'restart_case'};
$case_exists = $formdata{'case_exists'};
$engine = $formdata{'engine'};

# turn buffering off for correct display order
$| = 1;

# Write version information
system("echo $version >> $case_dir/version");
system("echo `hostname` >> $case_dir/version");

# Write real mendel.in file
#system("mv $run_dir/mendel.in.new $run_dir/mendel.in");

### start web output here
print "Content-type:text/html\n\n";
print "<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML//EN\">\n";
print "<html> <head>\n";
print "<meta http-equiv=\"refresh\" content=\"2;";
#print "URL=output.cgi?case_id=$case_id&user_id=$user_id&auto=1\">\n";
print "URL=monitor.cgi?case_id=$case_id&user_id=$user_id\">\n";
print "<title>Mendel run parameters</title>\n";
print "</head>\n";
print "<body>\n";

if($os eq "windows") {
   $cgivdir=`chdir`;
} else {
   $cgivdir=`pwd`;
}
chomp($cgivdir);

if($engine eq "c") {
   $exe = "cmendel.exe";
} elsif($engine eq "j") {
   $exe = "jmendel.exe";
} elsif($run_queue eq "himem") {
   $exe = "fmc101.exe";
} else {
   $exe = "fmendel.exe";
}

#print "exe is $exe<br>";

# procs_per_node should be defined in config.inc
#if ($is_parallel && $procs_per_node) {
#   $ppn = $procs_per_node;
#} elsif ($is_parallel) {
#   $ppn = 2;
if ($is_parallel eq "T") {
   $ppn = $num_procs;
} else {
   $num_nodes = 1;
   $num_procs = 1;
   $num_tribes = 1;
   $ppn = 1;
}

if($run_queue eq "pbs") {
   ### create pbs.script
   open(FILEWRITE, "> $case_dir/pbs.script");
   print FILEWRITE sprintf("#!/bin/sh\n");
   # this is another way to relate user_id and case_id
   # (instead of using case.log.  However, the problem is
   # that qstat -a limits the characters of the names to
   # nine characters. Must be consistent with qstat.cgi
   #print FILEWRITE sprintf("#PBS -N $user_id.$case_id\n");
   print FILEWRITE sprintf("#PBS -N $case_id\n");
   print FILEWRITE sprintf("#PBS -e pbs.err\n");
   print FILEWRITE sprintf("#PBS -o pbs.log\n");
   if ($run_queue eq "himem") {
      print FILEWRITE sprintf("#PBS -q batch\@c101\n");
      print FILEWRITE sprintf("#PBS -l nodes=$num_nodes:ppn=$ppn\n\n");
   } else {
      print FILEWRITE sprintf("#PBS -q batch\n");
      print FILEWRITE sprintf("#PBS -l nodes=$num_nodes:ppn=$ppn\n\n");
   }
   print FILEWRITE sprintf("cd \$PBS_O_WORKDIR\n\n");

   print FILEWRITE sprintf("echo Running on host `hostname`\n");
   print FILEWRITE sprintf("echo Time is `date`\n");
   print FILEWRITE sprintf("echo Directory is `pwd`\n");
   print FILEWRITE sprintf("echo This jobs runs on the following processors:\n");
   print FILEWRITE sprintf("echo `cat \$PBS_NODEFILE`\n\n");

   print FILEWRITE sprintf("NPROCS=`wc -l < \$PBS_NODEFILE`\n");
   print FILEWRITE sprintf("echo This job has allocated $NPROCS nodes\n");

   print FILEWRITE sprintf("$mpiexec -n $num_tribes $cgivdir/$exe $case_id >& $case_id.out\n");
   close FILEWRITE;
} elsif($run_queue eq "atq" || $run_queue eq "batch") {
   ### create batch.in file
   open(FILEWRITE, "> $case_dir/batch.in");
   if($is_parallel eq "T") {
      print FILEWRITE sprintf("$mpiexec -n $num_tribes $cgivdir/$exe $case_id >& $case_id.out\n");
   } else {
      print FILEWRITE sprintf("$cgivdir/$exe $case_id >& $case_id.out\n");
   }
   close FILEWRITE;
}

### start job

if ($mem_reqd <= $mem_available) {
   if($num_nodes > 1) {
      print "<h1>Running on $num_nodes nodes</h1>\n";
   } else {
      print "<h1>Running...</h1>\n";
   }
   print "Case: $case_id<br>";
   print "Run directory is: $case_dir<br><hr>";

   if($os eq "windows") {
	# Write version information
	system("echo $version >> $case_id\\version");
        system("echo $version >> c:\\mendel\\apache\\htdocs\\runs\\$case_id\\version");

        # stop any currently running version of Mendel
        system("taskkill /F /IM fmendel.exe");
        #system("taskkill /F /IM cmendel.exe");

	### start job
	#print "<h1>Running on $num_procs processor(s)</h1>\n";
	print "Case: $case_id<br>";
	print "Run directory is: $run_dir<br><hr>";
	print "Exe directory is: $cgivdir<br>";
	print "Version is $version<br>";
	#chdir $case_id;
        chdir "c:\\mendel\\apache\\htdocs\\runs\\$case_id";
	system("$cgivdir\\fmendel.exe > $case_id.out 2>&1\n");
	#print "running in directory ".`chdir`."<br>";

	open(FILEREAD, "< $run_dir\\pbs.err");
	while (<FILEREAD>){
	   print "<h1>$_</h1><br>";
	}
	close FILEREAD;

	open(FILEWRITE, "> c:\\mendel\\apache\\htdocs\\runlog.txt");
	print FILEWRITE "$case_id\n";
	close FILEWRITE;
   } else {
      chdir($case_dir);
      if($run_queue eq "pbs") {
         $stdout = `$qsub pbs.script`;
      } elsif($run_queue eq "atq") {
         $stdout = `at -f batch.in now 2>&1`;
      } elsif($run_queue eq "batch") {
         $stdout = `batch -f batch.in 2>&1`;
      } elsif($run_queue eq "noq") {
         # if a second job is started without being managed by a queue
         # and if the memory is set to use 80% or more
         # then starting a second job will overload the memory
         # and basically bring it to a crawl.
         # to prevent this from happening, we must stop all other
         # jobs that user apache is running to make run for this run
         #system("killall cmendel.exe");
         #system("killall fmendel.exe");
         if ($is_parallel eq "T") {
            #$cmd = "$mpiexec -n $num_tribes $cgivdir/$exe $case_id < /dev/null > $case_id.out 2&>1 &";
            $cmd = "$mpiexec -n $num_tribes $cgivdir/$exe $case_id < /dev/null >& $case_id.out &";
            print "command is: $cmd";
            system($cmd);
         } else {
            # Ubuntu style shells (sh,dash):
            #$cmd = "$cgivdir/$exe $case_id > $case_id.out 2&>1 &";
            # Fedora
            #$cmd = "$cgivdir/$exe $case_id >& $case_id.out &";
            # will work on anything
            $cmd = "$cgivdir/$exe $case_id > $case_id.out &";
            print "command is: $cmd";
            system($cmd);
         }
         $stdout = "noq\n";
      } else {
         print "<h1>ERROR: queue $run_queue not supported</h1>"; 
         die;
      } 
      print $stdout;
      if ($run_queue eq "himem") {
         $stdout = "c101\n";
      }
   }
} else {
   print "<h1>ERROR: Job not submitted.</h1>";
   print "Reason: too much memory is required:<br>";
   print "mem_reqd = $mem_reqd, mem_available = $mem_available<br>";
   print "Also, make sure you have turned on the parallel switch.";
}

if ($os eq "windows") {
   open(FILEWRITE, "> c:\\mendel\\apache\\htdocs\\runlog.txt");
} else {
   ### create case log file which will be used as a lookup file by
   ### qstat.cgi to associate case_id's with user_id's
   my ($sec,$min,$hour,$mday,$mon,$year,
   	  $wday,$yday,$isdst) = localtime time;
   $year += 1900;
   $mon += 1;
   $min = sprintf("%.02d",$min);
   if($isdst) { $dst = "DST" } else { $dst = ""; }
   open (LOGFILE, ">> $run_dir/case.log");
   print LOGFILE sprintf("$year/$mon/$mday $hour:$min$dst $user_id $case_id $stdout");
   close LOGFILE;
}

print "</html>";
print "</body>";

