#!/usr/bin/perl
##############################################################################
# start.cgi -> this_file -> ...
##############################################################################

require "config.inc";

read(STDIN, $buffer,$ENV{'CONTENT_LENGTH'});

$buffer =~ s/%([a-fA-F0-9][a-fA-F0-9])/ /g;

print "Content-type:text/html\n\n";
print <<zZzZ;
<head>
<style>
table {
  margin: 1em 1em 1em 2em;
  background: whitesmoke;
  border-collapse: collapse;
}
table th, table td {
  border: 1px silver solid;
  padding: 0.2em;
}
table th {
  background: gainsboro;
  text-align: left;
}
table caption {
  margin-left: inherit;
  margin-right: inherit;
}
</style>
</head>

<body onload="setTimeout('self.close()',3);self.focus();">
zZzZ

@pairs = split(/&/,$buffer);
foreach $pair(@pairs){
  ($key,$value)=split(/=/,$pair);
  $formdata{$key}.="$value";
}

$user_id=$formdata{'user_id'};
$case_id=$formdata{'case_id'};
$mutn_file_id=$formdata{'mutn_file_id'};

#print "mutn_file_id is: $mutn_file_id<br>";
#print "run_dir is: $run_dir<br>";
#print "user_id is: $user_id<br>";
#print "case_id is: $case_id<br>";

$case_dir="$run_dir/$user_id/$case_id";

system("mkdir -p $case_dir");

@mutn = split(/ /,$formdata{'mutn_table'});

$num_mutn = int($#mutn + 2)/6;

print "<h1>$num_mutn mutations written</h1>";

#print "$num_mutn mutations written to: $user_id/$case_id/$mutn_file_id<br>";

print "<p><center><a href=\"javascript:self.close();\">Close window<br></a></center></p>";

print "This window will automatically close in 0 seconds.<br>";

open(FILEWRITE, "> $case_dir/$mutn_file_id");
print FILEWRITE "$num_mutn\n";
print FILEWRITE "# individual linkage_block hap_id fitness          dominance\n";

#print "<table>";
#print "<tr><th>individual</th><th>linkage block</th><th>hap_id</th><th>fitness</th><th>dominance</th></tr>";

for ($i=0; $i<=$#mutn; $i+=6) {

#   print sprintf("<tr><td>%10d</td>",$mutn[$i]);
#   print sprintf("<td>%10d</td>",$mutn[$i+1]);
#   print sprintf("<td>%10d</td>",$mutn[$i+2]);
#   print sprintf("<td>%12.8f</td>",$mutn[$i+3]);
#   print sprintf("<td>%10d</td>",$mutn[$i+4]);
#   print "</tr>";

   print FILEWRITE sprintf("%10d %10d %10d %12.8f %10d\n",
         $mutn[$i],$mutn[$i+1],$mutn[$i+2],$mutn[$i+3],$mutn[$i+4]);
}
close FILEWRITE;

print "</table>";

