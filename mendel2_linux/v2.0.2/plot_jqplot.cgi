#!/usr/bin/perl

require "parse.inc";
require "config.inc";

$case_id=$formdata{'case_id'};
$user_id=$formdata{'user_id'};

$plot_width = 640;

print "Content-type:text/html\n\n";

# Require input_file_parser at line 174... should be here in future
# but there is some problem with it.

#print "case_id is $case_id<br>";
#print "user_id is $user_id<br>";
#print "$run_dir/$user_id/$case_id/$case_id.000.hst";

# Get the generation number use this in the image tag as image.png?$gen
# this forces the browser to not use the cached images

open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst") or
  die "ERROR: $case_id.000.hst does not exist<br>";
while (<FH>) {
  ($gen,$fitness,$fitness_sd,$num_dmutns,$num_fmutns) = split(' ', $_, 9999);
}
close FH;

$num_dmutns = sprintf("%.1f",$num_dmutns);
$num_fmutns = sprintf("%.1f",$num_fmutns);

print <<END_HTML;

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<html><head>
<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
<title>Output Case $case_id User $user_id</title>

<link rel="stylesheet" type="text/css" href="jquery.jqplot.css" />
<!--[if IE]><script language="javascript" type="text/javascript" src="excanvas.js"></script><![endif]-->
<script language="javascript" type="text/javascript" src="/mendel/js/jqplot/jquery.min.js"></script>
<script language="javascript" type="text/javascript" src="/mendel/js/jqplot/jquery.jqplot.min.js"></script>
<script language="javascript" type="text/javascript" src="/mendel/js/jqplot/jqplot.logAxisRenderer.js"></script>
<script type="text/javascript" src="/mendel/js/jqplot/jqplot.canvasTextRenderer.min.js"></script>
<script type="text/javascript" src="/mendel/js/jqplot/jqplot.canvasAxisLabelRenderer.min.js"></script>

<script type="text/javascript" src="/mendel/js/tabpane.js"></script>
<link type="text/css" rel="StyleSheet" href="/mendel/css/tab.webfx.css">
<link type="text/css" rel="StyleSheet" href="/mendel/css/form.css" />
</head>
<body>

<div class="tab-pane" id="tab-pane-1">

<!-- ############ MUTATIONS ####################################### -->
<div class="tab-page">

   <h2 class="tab">mutations</h2>

   <center>
   <h3>1a: Average mutations/individual</h3>
   <i>updated every generation</i>
   </center>

   <div id="mutations" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%1==0 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%1==0 && $col1 ne "#") {print "[$col1, $col5], ";}
      }
      close FH;
      print "];";

print <<END_HTML;
      //\$.jqplot(\$("#mutations"), [{ label: "<< deleterious", data: d1, 
      //                             color: "rgb(200,0,0)"}, 
      //                           { label: ">> favorable", data: d2, 
      //                             color: "rgb(0,200,0)", yaxis: 2}],
      //                           { legend: { position: 'nw' } } );
      });
    \$(document).ready(function(){
      \$.jqplot('mutations',  [[[1, 2],[3,5.12],[5,13.1],[7,33.6],[9,85.9],[11,219.9]]], {
   // Give the plot a title.
      title: 'Plot With Options',
      axesDefaults: {
        labelRenderer: \$.jqplot.CanvasAxisLabelRenderer
      },
      axes: {
        xaxis: {
          label: "Number of Generations",
          pad: 0
        },
        yaxis: {
          label: "Deleterious and Neutral Mutations"
        }
      }
    }); 
   });

   </script>

   <center> <h4>Number of generations</h4> </center>

   <center>
   <form name="mutn_form" method="post" action="more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.hst">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>
   </center>

</div>


<!-- ############ FITNESS ####################################### -->
<div class="tab-page">

   <h2 class="tab">fitness</h2>

   <center>
   <h3>1b: Fitness and Standard Deviation</h3>
   <i>updated every generation</i>
   </center>

   <div id="fitness" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%1==0 && $col1 ne "#") {print "[$col1, $col2], ";}
      }
      close FH;
      print "];";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%1==0 && $col1 ne "#") {print "[$col1, $col3], ";}
      }
      close FH;
      print "];";

      print "var d3 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5,$col6) = split(' ', $_, 9999);
         if ($col1%1==0 && $col1 ne "#") {print "[$col1, $col6], ";}
      }
      close FH;
      print "];";

print <<END_HTML;
      \$.jqplot(\$("#fitness"), [{ label: "<< fitness", data: d1, 
                                 color: "rgb(200,0,0)"}, 
                               { label: "<< standard deviation", data: d2, 
                                 color: "rgb(0,200,0)", yaxis: 1},
                               { label: ">> population size", data: d3, 
                                 color: "rgb(0,0,200)", yaxis: 2}],
                               { legend: { position: 'se' } } );
      });
   </script>

   <center> <h4>Number of generations</h4> </center>

   <center>
   <form name="fit_form" method="post" action="more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.hst">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>
   </center>

</div>
END_HTML

# Read the parameters from the input file to get fitness_distrib_type
# For some reason, the input_file_parser does not work correctly 
# when fitness_distrib_type = 0
$path = "$run_dir/$user_id/$case_id/mendel.in";
#require "input_file_parser.inc";

# Only plot mutation and fitness plots for equal effect mutation distribution
# This is not working right now... parsing the input file is failing,
# and thus causing the rest of the script to fail, so comment it out for now.
#if($fitness_distrib_type==0) {
#   print "NOTE: Only mutation and fitness plots can be generated when using <u>equal effect mutation</u> distribution.<br>";
#} else {
print <<END_HTML;
<center>
<form method="post" action="plot_gnuplot.cgi">
<input type="hidden" name="case_id" value="$case_id">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="user_id" value="$user_id">
<input type="submit" value="GNUPLOT">
</form>
</center>
<!-- ############ DISTRIBUTION ####################################### -->
<div class="tab-page">

   <h2 class="tab">distribution</h2>

   <center>
   <h3>2: Distribution of accumulated mutations</h3>
   <i>updated every 20 generation</i>
   </center>

   <h3>DELETERIOUS</h3>

   <div id="ddst" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.dst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         #$x = -(log($col1+1.e-8)+12)/10;
         $x = -log($col1+1.e-8);
         if ($. <= 53 && $col1 ne "#") {print "[$x, $col3], ";}
      }
      close FH;
      print "];";
      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.dst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         $x = -log($col1+1.e-8);
         if ($. <= 53 && $col1 ne "#") {print "[$x, $col2], ";}
      }
      close FH;
      print "];";
print <<END_HTML;
      \$.jqplot(\$("#ddst"), [ { label: "Dominant", data: d1, 
                               bars: { show: true, barWidth: 0.2 },
                               color: "rgb(0,200,0)"},
                             { label: "Recessive", data: d2,
                               bars: { show: true, barWidth: 0.2 },
                               color: "rgb(200,0,0)"} ],
                             { legend: { position: 'nw' } });
                         //, { xaxis: { ticks: 10, min: -1.0, max: -0.1} });
      });
   </script>

   <center> <h4> Mutational Fitness Degradation</h4> </center>

   <center>
   <form name="dst_form" method="post" action="more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.dst">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>
   </center>

<h3>BENEFICIALS</h3>

   <div id="fdst" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.dst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         $x = -log($col1+1.e-8);
         if ($. >= 56 && $col1 ne "#") {print "[$x, $col3], ";}
      }
      close FH;
      print "];";
      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.dst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         $x = -log($col1+1.e-8);
         if ($. >= 56 && $col1 ne "#") {print "[$x, $col2], ";}
      }
      close FH;
      print "];";
print <<END_HTML;
      \$.jqplot(\$("#fdst"), [ { label: "Dominant", data: d1, 
                               bars: { show: true, barWidth: 0.2 },
                               color: "rgb(0,200,0)"},
                             { label: "Recessive", data: d2,
                               bars: { show: true, barWidth: 0.2 },
                               color: "rgb(200,0,0)"} ],
                             { legend: { position: 'ne' } });
      });
   </script>

   <center> <h4> Mutational Fitness Degradation</h4> </center>

</div>

<!-- ############ THRESHOLD ####################################### -->
<div class="tab-page">

   <h2 class="tab">threshold</h2>

   <center>
   <h3>3: Selection threshold history</h3>
   <i>updated every 20 generation</i>
   </center>

   <div id="thr" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.thr");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%1==0 && $col1 ne "#") {print "[$col1, $col2], ";}
      }
      close FH;
      print "];";
      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.thr");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= 100 && $col1 ne "#") {print "[$col1, $col3], ";}
      }
      close FH;
      print "];";
print <<END_HTML;
      \$.jqplot(\$("#thr"), [ { label: "Deleterious threshold", 
                              data: d1, color: "rgb(200,0,0)"},
                            { label: "Favorable threshold",
                              data: d2, color: "rgb(0,200,0)"} ]);
      });
   </script>
   <center> <h4>Number of Generations</h4> </center>

   <center>
   <form method="post" action="more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.thr">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>
   </center>


</div>

<!-- ############ NEAR-NEUTRAL ####################################### -->
<div class="tab-page">

   <h2 class="tab">near-neutrals</h2>

   <center>
   <h3>4: Distribution of minor and near-neutral effects</h3>
   <i>updated every 20 generation</i>
   </center>

   <h3>DELETERIOUS</h3>

   <div id="dmutn" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1 <= 102 && $col1 ne "#") {print "[$col1, $col2], ";}
      }
      close FH;
      print "];";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1 <= 102 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];";

      print "var d3 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1 <= 102 && $col1 ne "#") {print "[$col1, $col5], ";}
      }
      close FH;
      print "];";

print <<END_HTML;
      \$.jqplot(\$("#dmutn"), [ { label: "Theoretical", 
                                //lines: { show: true, fill: true },
                                //bars: { show: true, barWidth: 0.0001 },
                                data: d1, color: "rgb(200,0,0)" },
                              { label: "Dominant",
                                bars:  { show: true, barWidth: 0.0001 },
                                data: d2, color: "rgb(0,200,0)" },
                              { label: "Recessive",
                                bars:  { show: true, barWidth: 0.0001 },
                                data: d3, color: "rgb(0,0,200)" } ],
                              { xaxis: { ticks: 10, min: -0.01, max: 0.0},
                                yaxis: { ticks: 10, min: 0.0,   max: 0.01}, 
                                legend: { position: 'nw' } });
      });
   </script>

   <center><h4>Fitness Effect</h4></center>

   <center>
   <form method="post" action="more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.hap">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>
   </center>

   <h3>BENEFICIALS</h3>

   <div id="fmutn" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= 103 && $col1 ne "#") {print "[$col1, $col2], ";}
      }
      close FH;
      print "];";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= 103 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];";

      print "var d3 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1 >= 103 && $col1 ne "#") {print "[$col1, $col5], ";}
      }
      close FH;
      print "];";

print <<END_HTML;
      \$.jqplot(\$("#fmutn"), [ { label: "Theoretical", 
                                //lines: { show: true, fill: true },
                                data: d1, color: "rgb(200,0,0)" },
                              { label: "Dominant",
                                bars:  { show: true, barWidth: 0.0001 },
                                data: d2, color: "rgb(0,200,0)" },
                              { label: "Recessive",
                                bars:  { show: true, barWidth: 0.0001 },
                                data: d3, color: "rgb(0,0,200)" } ],
                              { xaxis: { ticks: 10, min: 0.0, max: 0.01},
                                yaxis: { ticks: 10, min: 0.0 }, 
                                legend: { position: 'nw' } });
      });
   </script>

   <center><h4>Fitness Effect</h4></center>

</div>

<!-- ############ LINKAGE ####################################### -->
<div class="tab-page">

   <h2 class="tab">linkage</h2>

   <center>
   <h3>5: Linkage block effects</h3>
   <i>updated every 20 generation</i>
   </center>

   <div id="hap" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. <= 99 && $col1 ne "#") {print "[$col1, $col3], ";}
         else {
            if (/avg_linkage_block_effect/) {
               ($buf,$buf,$buf,$avg_lb_effect) = split(' ', $_); } 
            if (/lb_fitness_percent_positive/) {
               ($buf,$buf,$buf,$lb_fitness_percent_positive) = split(' ', $_); }
         }
      }
      $avg_lb_effect= sprintf("%.3e",$avg_lb_effect);
      $lb_fitness_percent_positive = 
         sprintf("%.2f",$lb_fitness_percent_positive);
      close FH;
      print "];";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= 100 && $col1 ne "#") {print "[$col1, $col3], ";}
      }
      close FH;
      print "];";
print <<END_HTML;
      \$.jqplot(\$("#hap"), [ { label: "Net-deleterious effect blocks", 
                              bars:  { show: true, barWidth: 0.0001 },
                              data: d1, color: "rgb(200,0,0)" },
                            { label: "Net-beneficial effect blocks",
                              bars:  { show: true, barWidth: 0.0001 },
                              data: d2, color: "rgb(0,200,0)" } ],
                            { xaxis: { ticks: 10, min: -0.01, max: 0.01},
                              yaxis: { ticks: 10, min: 0.0,   max: 0.01} });
      });
   </script>

   <center><h4>Fitness Effect</h4></center>

   <center>
   <form method="post" action="more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.hap">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>
   </center>

<hr>
Average linkage block effect = $avg_lb_effect<br>
Linkage blocks which have a positive fitness value = $lb_fitness_percent_positive% <br>


</div>

<!-- ############ SELECTION ####################################### -->
<div class="tab-page">

   <h2 class="tab">selection</h2>

   <center>
   <h3>6: Selection effects</h3>
   <i>updated every 20 generations</i>
   </center>

   <div id="sel" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.sel");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col2 > 0 && $col1 ne "#") {print "[$col1, $col2], ";}
      }
      close FH;
      print "];";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.sel");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col2 > 0 && $col1 ne "#") {print "[$col1, $col3], ";}
         else {
            if (/pre.*selection.fitness/)  { $pre_selection_fitness  = $_; }
            if (/post.*selection.fitness/) { $post_selection_fitness = $_; }
         }
      }
      close FH;
      print "];";

      print "var d3 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.sel");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if($col4 eq "?") { $col4 = ""; }
         if ($col2 > 0 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];";
print <<END_HTML;
      //\$.jqplot(\$("#sel"), [d1]);
      \$.jqplot(\$("#sel"), [ { label: "<< Before selection", 
                              bars:  { show: true, barWidth: 0.01 },
                              data: d1, color: "rgb(200,0,0)" },
                            { label: "<< After selection",
                              bars:  { show: true, barWidth: 0.01 },
                              data: d2, color: "rgb(0,200,0)" },
                            { label: ">> After/before ratio",
                              data: d3, color: "rgb(0,0,200)", yaxis: 2 } ],
                            { //xaxis: { ticks: 10, min: 0.5, max: 1.5 },
                              yaxis: { ticks: 10, min: 0.0 },
                              y2axis: { ticks: 5, min: 0.0, max: 1.0 } });
      });
   </script>

   <center><h4>Fitness</h4></center>

   <center>
   <form method="post" action="more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.sel">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>
   </center>

<hr>
$pre_selection_fitness<br>
$post_selection_fitness<br>

</div>

<!-- ############ ALLELES ####################################### -->
END_HTML
if(1) {
   if(1) {
#if($track_neutrals) {
#   if($gen >= 1 &&
#     ($num_dmutns > $plot_when_mutns || $num_fmutns > $plot_when_mutns)) {
print <<END_HTML;

<div class="tab-page">

   <h2 class="tab">alleles</h2>

   <center>
   <h3>7: Allele frequency</h3>
   <i>updated at generation 200, every 1000 generations<br>
      starting from generation 0, and at end of run</i>
   </center>

   <div id="plm" style="width:600px;height:300px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.plm");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= 103 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.plm");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= 103 && $col1 ne "#") {print "[$col1, $col5], ";}
         else {
            if (/deleterious$/) 
            {($buf,$num_drare,$num_dpolymorphic,$num_dfixed) = split(' ', $_);}
            if (/favorable$/) 
            {($buf,$num_frare,$num_fpolymorphic,$num_ffixed) = split(' ', $_);}
            if (/neutral$/) 
            {($buf,$num_nrare,$num_npolymorphic,$num_nfixed) = split(' ', $_);}
         }
      }
      close FH;
      print "];";
print <<END_HTML;
      //\$.jqplot(\$("#plm"), [d1]);
      \$.jqplot(\$("#plm"), [ { label: "Deleterious", 
                              data: d1, bars: { show: true },
                              color: "rgb(200,0,0)"},
                            { label: "Favorable",
                              data: d2, bars: { show: true },
                              color: "rgb(0,200,0)"} ]);
      });
   </script>

   <center><h4>Allele Frequency</h4></center>

   <center>
   <form method="post" action="more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.plm">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>
   </center>

   <hr>
   <table>
   <tr><th align=left>Number of alleles</th> <th width=150>Deleterious</th> <th width=150>Favorables</th> <th align=center>Neutrals</th> </tr>
   <tr><td>very rare (0-1%)</td> <td align=center>$num_drare</td> <td align=center>$num_frare</td> <td align=center>$num_nrare</td> </tr>
   <tr><td>polymorphic (1-99%)</td> <td align=center>$num_dpolymorphic</td> <td align=center>$num_fpolymorphic</td> <td align=center>$num_npolymorphic</td> </tr>
   <tr><td>fixed or very nearly fixed (99-100%)</td> <td align=center>$num_dfixed</td> <td align=center>$num_ffixed</td> <td align=center>$num_nfixed</td> </tr>
   </table>

</div>
END_HTML
}}
#} # if(fitness_distrib_type > 0)

print <<END_HTML;
<table border=0 width=$plot_width>
<tr bgcolor=dfdfdf> <td>Generation</td> <td>Fitness</td> <td># del mutns</th> <td># fav mutns</td> </tr>
<tr> <td>$gen</td> <td>$fitness</td> <td>$num_dmutns</th> <td>$num_fmutns</td> </tr>
</table>
<br>

<hr>
To save an image of the plots:<br>
<ul>
<li>On Mac OS X, click Shift+Command+4, and click and drag the mouse to create a box which envelopes the plot you wish you save as an image.
<li>On Linux, hit the PrtSc button, and a window should come up asking where to save file.
<li>On Windows, select the Alt+PrtSc button (some computers may require using Fn key as well). This copies the window to the clipboard.  In Microsoft PowerPoint, the Paste function can be used to paste the image.  Modify and crop the image as desired.  Then, right click on the image and select \"Save As...\" to save the image to a file.
</li>
  
</body>
</html>

END_HTML
