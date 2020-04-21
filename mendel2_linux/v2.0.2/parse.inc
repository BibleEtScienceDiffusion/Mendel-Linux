##############################################################################
# parse the input string sent via forms to the perl script
# added this file because it supports the "GET" mehod
# in other .cgi scripts the GET method is not supported
# so I have "required" this file in those cgi scripts
# where the "GET" method might be used.
##############################################################################

# following borrowed from http://spruce.flint.umich.edu/~jalarie/jaa_kdb.htm
if ($ENV{'REQUEST_METHOD'} eq 'GET') {            # get from URL
   @pairs = split(/[&;]/, $ENV{'QUERY_STRING'});   # split on "&" and ";"
} elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
  read (STDIN, $buffer, $ENV{'CONTENT_LENGTH'});  # read STDIN
  if ($ENV{'QUERY_STRING'} ne "") {               # something on URL
    $buffer = $ENV{'QUERY_STRING'}."&".$buffer;   # ...use as prefix
  }
  @pairs = split(/[&;]/, $buffer);                # split on "&" and ";"
} else {
  print "Content-type: text/html\n\n";            # error!
  print "<p>You must use Post or Get</p>";
}

# Convert + signs to spaces:
$buffer =~ tr/+/ /;
$buffer =~ s/\r/ /g;
$buffer =~ s/\n/ /g;
# Convert hex pairs (%HH) to ASCII characters:
$buffer =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
$buffer =~ s/<!--(.|\n)*-->/ /g;
$buffer =~ tr/\\|[|]|<|!|"|$|{|}|*|#|'|>|||;|%/ /;

foreach $pair(@pairs){
  ($key,$value)=split(/=/,$pair);
  $formdata{$key}.="$value";
}

1;
