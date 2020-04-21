#!/usr/bin/perl
##############################################################################
#
# list_cases.cgi -> with_selected.cgi -> this_file -> plot_gnuplot.cgi
#
# This file displays a form to ask user about casename for 
# combined data, then calls plot_gnuplot.cgi
#
##############################################################################

require "parse.inc";
require "config.inc";

$file_name=$formdata{'file_name'};
$case_id=$formdata{'cid'};
$run_dir=$formdata{'run_dir'};
$url_dir=$formdata{'url_dir'};
$user_id=$formdata{'user_id'};
$plot=$formdata{'plot'};

# turn buffering off for correct display order
$| = 1;

print "Content-type:text/html\n\n";
#print "<meta http-equiv=\"refresh\" content=\"10;";
#print "URL=list_cases.cgi\">\n";
print "<html><body>";
print "<table width=500><tr><td>";

print "<h1>Modify $plot plot for Case $case_id</h1>";

#print "<h2>$case_id archived</h2><br>";
#print "url_dir is $url_dir<br>";
#print "case_id is $case_id<br>";
#print "run_dir is $run_dir<br>";
#print "user_id is $user_id<br>";
#print "plot is $plot<br>";

$run_dir =~ s/%2F/\//g;

$cid = $case_id;
$path="$run_dir/$user_id/$case_id/mendel.in";
require "input_file_parser.inc";

if($plot_avg_data) { $checkpad = "CHECKED" }

#if($plot eq "ddst") { $plot = "dst"; }

open(FH,"$run_dir/$user_id/$cid/${cid}_$plot.gnu");
while (<FH>) {
  #print $_."<br>";
  if($_ =~ /xrange/) { ($xmin,$xmax) = split(':',$_); } 
  $xmin =~ s/set.*xrange.*\[//;
  $xmax =~ s/\]//;

  if($_ =~ /yrange/) { ($ymin,$ymax) = split(':',$_); } 
  $ymin =~ s/set.*yrange.*\[//;
  $ymax =~ s/\]//;

  if($_ =~ /y2range/) { ($y2min,$y2max) = split(':',$_); } 
  $y2min =~ s/set.*y2range.*\[//;
  $y2max =~ s/\]//;
}
close FH;

print <<zZzZz;
<form method="post" action="plot_gnuplot_recipes.cgi">
   <table>

     <tr>
          <td>Output format<sup>(1)</sup>: </td>
          <td>
             <select name="format">
             <option selected VALUE="png">PNG
             <option VALUE="eps">EPS
             </select>
          </td>

     </tr>

     <tr>
        <td> Plot data in grayscale <em>(only works for PNG format)</em>?</td>
        <td> <input type="checkbox" name="grayscale" value="on"></td>
     </tr>

<!-- this will affect every graph and sometime undesirably;
     we should not enable unless we absolutely need it
        <tr>
           <td> Draw grid?</td>
           <td> <input type="checkbox" name="grid" value="on"></td>
        </tr>
-->

        <tr>
           <td> Hide input parameters?</td>
           <td> <input type="checkbox" name="labels" value="off"></td>
        </tr>

        <tr>
           <td> Plot using lines <em>(instead of boxes)</em>?</td>
           <td> <input type="checkbox" name="lines" value="on"></td>
        </tr>

        <tr>
           <td> Average/Aggregate tribal data <em>(for parallel cases)</em>?</td>
           <td> <input type="checkbox" name="plot_avg_data" value="on" $checkpad></td>
        </tr>

zZzZz
       #if($plot eq "ddst" or
       #   $plot eq "fdst" or
       #   $plot eq "dmutn" or 
       #   $plot eq "fmutn") {
       #   print "<tr>";
       #   print "<td>Only plot dominant mutations?</td>";
       #   print "<td> <input type=\"checkbox\" name=\"dominant_only\" value=\"1\"></td>";
       #   print "</tr>";
       #}

       if($plot eq "fit_hst") {
          print "<tr>";
          print "  <td> Plot dynamic population size</td>";
          print "  <td> <input type=\"checkbox\" name=\"pgm\" value=\"on\"></td>";
          print "</tr>";
       }
      
       if($plot eq "ddst" or 
          $plot eq "fdst" or 
          $plot eq "dmutn" or 
          $plot eq "fmutn" or
          $plot eq "plm") {
          print "<tr>";
          print "<td>Fill histograms with solid color?</td>";
          print "<td> <input type=\"checkbox\" name=\"fill_boxes\" value=\"1\"></td>";
          print "</tr>";
      }
print <<zZzZz;

          <tr><td>Annotation</td><td> <input type="text" name="annotation"></td></tr>
        </table>

        <table>
        <tr> <th></th> <th align=left>min</th> 
                       <th align=left>max</th> </tr>
       
        <tr>
        <td align=right>xrange<sup>(2)</sup></td> 
        <td><input type="text" name="xmin" value=$xmin></td>
        <td><input type="text" name="xmax" value=$xmax></td>
        </tr>
        <tr>
        <td align=right>yrange<sup>(2)</sup></td> 
        <td><input type="text" name="ymin" value=$ymin></td>
	<td><input type="text" name="ymax" value=$ymax></td>
        </tr>
        <tr>
        <td align=right>y2range<sup>(2)</sup></td> 
        <td><input type="text" name="y2min" value=$y2min></td>
	<td><input type="text" name="y2max" value=$y2max></td>
        </tr>
        
        <tr>
        <td> </td>
        <td> <input type="submit" value="Modify plot"> </td>
        </tr>
        </table>

       <hr>

       <input type="hidden" name="plot" value="$plot">
       <input type="hidden" name="case_id" value="$cid">
       <input type="hidden" name="run_dir" value="$run_dir">
       <input type="hidden" name="user_id" value="$user_id">
       <input type="hidden" name="caller" value="modify">
</form>

<em>Notes: 
<ol>
<li> Only PNG output will be able to be viewed by clicking "Plots" button, others will create files which can be accessed by clicking "Files" button.
<li> Leave values blank which you do not want to modify. Explanation: if both min and max are blank, MENDEL default values will be used.  If just min is specified (but not max), Gnuplot will automatically determine the best value for max (and vice-versa, e.g. max is specified but not min).
<li> When modifying the plots, the plot parameters will not appear on the combined plots.
</em> 
</ol>

</td></tr></table>

zZzZz

