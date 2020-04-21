#!/usr/bin/perl

require "./parse.inc";
require "./config.inc";

$plot_width = 640;
$max_gens = 5000;

# if posting from control panel 
if ($case_id eq "") {
   $case_id=$formdata{'case_id'};
   $user_id=$formdata{'user_id'};
   $version=$formdata{'version'};
   if($case_id =~ /%2F/) {
     ($user_id,$case_id)=split(/%2F/,$case_id);
   }
   print "Content-type:text/html\n\n";
   #print "cid: $case_id uid: $user_id cuid: $cuid<p>";
   if ($case_id eq "") {
      print "ERROR: Case_ID missing<br>";
      die;
   }
}

# Read the parameters from the input file to get fitness_distrib_type
$path = "$run_dir/$user_id/$case_id/mendel.in";
require "./input_file_parser.inc";

#print "case_id is $case_id<br>";
#print "user_id is $user_id<br>";
#print "$run_dir/$user_id/$case_id/$case_id.000.hst";

# Get the generation number use this in the image tag as image.png?$gen
# this forces the browser to not use the cached images

open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst") or
  die "ERROR: $case_id.000.hst does not exist<br>";
while (<FH>) {
  ($gen,$fitness,$fitness_sd,$num_dmutns,$num_fmutns,$num_nmutns) = split(' ', $_, 9999);
}
close FH;

$num_dmutns = sprintf("%.1f",$num_dmutns);
$num_fmutns = sprintf("%.1f",$num_fmutns);
$num_nmutns = sprintf("%.1f",$num_nmutns);

print <<END_HTML;

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<html><head>
<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
<title>Output Case $case_id User $user_id</title>
<script language="javascript" type="text/javascript" src="/mendel/js/flot/excanvas.pack.js"></script> 
<script language="javascript" type="text/javascript" src="/mendel/js/flot/jquery.js"></script>
<script language="javascript" type="text/javascript" src="/mendel/js/flot/jquery.flot.js"></script>
<script language="javascript" type="text/javascript" src="/mendel/js/flot/jquery.flot.axislabels.js"></script>
<script language="javascript" type="text/javascript" src="/mendel/js/flot/jquery.flot.selection.js"></script>
<script language="javascript" type="text/javascript" src="/mendel/js/flot/jquery.flot.fillbetween.js"></script>
<script type="text/javascript" src="/mendel/js/tabpane.js"></script>
<link type="text/css" rel="StyleSheet" href="/mendel/css/tab.webfx.css">
<link type="text/css" rel="StyleSheet" href="/mendel/css/form.css" />

<script>
   function fxn_init() {
   }
</script>
</head>

<body onload="fxn_init()">

<div class="tab-pane" id="tab-pane-1">

<!-- ############ MUTATIONS ####################################### -->
<div class="tab-page">

   <h2 class="tab">mutations</h2>

   <h3>1: Average mutations/individual ($case_id)</h3>
   <p><i>updated every generation</i></p>

   <div id="mutations" style="width:600px;height:370px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      # get number of lines in file
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      my $lines = @f = <FH>;
      close FH;
      $modulo = int($lines/100);

      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%$modulo==0 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%$modulo==0 && $col1 ne "#") {print "[$col1, $col5], ";}
      }
      close FH;
      print "];";

      print "var d3 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5,$col6) = split(' ', $_, 9999);
         if ($col1%$modulo==0 && $col1 ne "#") {print "[$col1, $col6], ";}
      }
      close FH;
      print "];";

print <<END_HTML;
      var data = [ { label: "deleterious", data: d1, color: "rgb(200,0,0)" },
                   { label: "favorable",   data: d2, color: "rgb(0,200,0)" },
                   { label: "neutrals",    data: d3, color: "rgb(0,0,200)" } ];

      var options = {
         legend: { position: 'nw' },
         xaxis:  { axisLabel: 'Generations', axisLabelFontSizePixels: 12 },
         yaxis:  { axisLabel: 'Mutations', axisLabelOffset: -30, 
                   axisLabelFontSizePixels: 12 },
         grid:   { hoverable: true, clickable: true },
         selection: { mode: "xy" }
      };

      var placeholder = \$("#mutations");

      //myplot = new plotter(placeholder, data, options)
      //myplot.showPlot();

      // attach an event handler directly to the plot
      placeholder.bind("plotselected", function (event, ranges) {
        \$("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));

        var zoom = \$("#zoom").attr("checked");

        if (zoom)
            plot = \$.plot(placeholder, data,
                   \$.extend(true, {}, options, {
                      xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
                      yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
                   }));
        else 
           var plot = \$.plot(placeholder, data, options);
      });

      placeholder.bind("plothover", function (event, pos, item) {
        \$("#x").text(pos.x.toFixed(2));
        \$("#y").text(pos.y.toFixed(2));
      });

      placeholder.dblclick(function() {
         var plot = \$.plot(placeholder, data, options);
      });

      var plot = \$.plot(placeholder, data, options);

   });
   </script>

   <form name="mutn_form" method="post" action="./more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.hst">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>

</div>

<!-- ############ FITNESS ####################################### -->
<div class="tab-page">

   <h2 class="tab">fitness</h2>

   <h3>2: Population, Fitness and Standard Deviation ($case_id)</h3>
   <p><i>updated every generation</i></p>

   <div id="fitness" style="width:600px;height:370px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = {'mean': [
END_HTML
      
      # Mean fitness
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%$modulo==0 && $col1 ne "#") {print "[$col1, $col2], ";}
         $fit[$col1] = $col2;
      }
      close FH;
      print "], ";

      # Fitness plus one standard deviation 
      print "'upper': [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         $y = $fit[$col1]+$col3;
         if ($col1%$modulo==0 && $col1 ne "#") {print "[$col1, $y], ";}
      }
      close FH;
      print "],";
      
      # Fitness minus one standard deviation 
      print "'lower': [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         $y = $fit[$col1]-$col3;
         if ($col1%$modulo==0 && $col1 ne "#") {print "[$col1, $y], ";}
      }
      close FH;
      print "]};\n";

      # Population size
      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5,$col6,$col7) = split(' ', $_, 9999);
         if ($col1%$modulo==0 && $col1 ne "#") {print "[$col1, $col7], ";}
      }
      close FH;
      print "];\n";

print <<END_HTML;
      var data = [ { label: "fitness", data: d1['mean'], 
     		     color: "rgb(255,50,50)" },
	           { label: "+/-1 standard dev.", id: 'fl', data: d1['lower'], 
		     lines: { show: true, lineWidth: 0, fill: false }, 
		     color: "rgb(0,0,0)"},
	           { id: 'fu', data: d1['upper'], 
		     lines: { show: true, lineWidth: 0, fill: 0.2 }, 
		     color: "rgb(0,0,0)", fillBetween: 'fl'},
	           { label: "pop size", data: d2, 
		     color: "rgb(0,0,255)", yaxis: 2 } ];

      var options = {
	 legend: { position: 'sw' },
	 xaxis:  { axisLabel: 'Generations', axisLabelFontSizePixels: 12 }, 
	 yaxis:  { min: 0, axisLabel: 'Fitness & Population size', 
		   axisLabelOffset: -150, axisLabelFontSizePixels: 12 },
	 grid:   { hoverable: true, clickable: true },
	 selection: { mode: "xy" }
      };

      var placeholder = \$("#fitness");

      // attach an event handler directly to the plot
      placeholder.bind("plotselected", function (event, ranges) {
        \$("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));

        var zoom = \$("#zoom").attr("checked");

        if (zoom)
            plot = \$.plot(placeholder, data,
                   \$.extend(true, {}, options, {
                      xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
                      yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
                   }));
        else 
           var plot = \$.plot(placeholder, data, options);
      });

      placeholder.bind("plothover", function (event, pos, item) {
        \$("#x").text(pos.x.toFixed(2));
        \$("#y").text(pos.y.toFixed(2));
      });

      placeholder.dblclick(function() {
         var plot = \$.plot(placeholder, data, options);
      });

      var plot = \$.plot(placeholder, data, options);

      });
   </script>

   <form name="fit_form" method="post" action="./more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.hst">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>

</div>
END_HTML

# Only plot mutation and fitness plots for equal effect mutation distribution
# This is not working right now... parsing the input file is failing,
# and thus causing the rest of the script to fail, so comment it out for now.
if($fitness_distrib_type==0 || $fitness_distrib_type == 2) {
   print "NOTE: Only mutation and fitness plots can be generated when using <u>equal effect mutation</u> or <u>all neutral</u> mutation distributions.<br>";
} else {
print <<END_HTML;

<!--
<center>
<form method="post" action="./plot_gnuplot.cgi">
<input type="hidden" name="case_id" value="$case_id">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="user_id" value="$user_id">
<input type="submit" value="GNUPLOT">
</form>
</center>
-->

<!-- ############ DISTRIBUTION ####################################### -->
<div class="tab-page">

   <h2 class="tab">distribution</h2>

   <h3>3: Log-scale distribution of accumulated mutations ($case_id)</h3>
   <i>updated every 20 generations</i>

   <h3>DELETERIOUS</h3>

   <div id="ddst" style="width:600px;height:370px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.dst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         #$x = -(log($col1+1.e-8)+12)/10;
         $x = $col1;
         if ($. <= 53 && $col1 ne "#") {print "[$x, $col3], ";}
      }
      close FH;
      print "];";
      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.dst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         $x = $col1;
         if ($. <= 53 && $col1 ne "#") {print "[$x, $col2], ";}
      }
      close FH;
      print "];";
print <<END_HTML;
      var data = [ { label: "Dominant", data: d1, 
                     bars: { show: true, barWidth: 0 }, 
                     color: "rgb(0,200,0)" },
                   { label: "Recessive", data: d2, 
                     bars: { show: true, barWidth: 0 },
                     color: "rgb(200,0,0)"} ];

      // Line annotation at 0.5 -- selection threshold point
      var markings = [
        { color: '#000', lineWidth: 1, yaxis: { from: 0.5, to: 0.5 } },
      ];

      var options = {
         xaxis: { axisLabel: 'Mutational Fitness Degradation', 
                  axisLabelFontSizePixels: 12,
                  transform: function (x) { return -Math.log(x); },
                  inverseTransform: function (x) { return -Math.exp(x); },
                  ticks: [[1.0,"1"],[0.1,"1e-1"],[0.01,"1e-2"],[1e-3,"1e-3"],
                          [1e-4,"1e-4"],[1e-5,"1e-5"],[1e-6,"1e-6"],
                          [1e-7,"1e-7"], [1e-8,"1e-8"]], 
                          tickDecimals: 6, max: 1.0 },
         yaxis: { axisLabelOffset: -220, 
                  axisLabel: 'Fraction of Mutations Retained in Genome',
                  axisLabelFontSizePixels: 12 },
	 legend: { position: 'nw' }, 
         grid: { markings: markings }
      };

      var placeholder = \$("#ddst");

      // attach an event handler directly to the plot
      placeholder.bind("plotselected", function (event, ranges) {
        \$("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));

        var zoom = \$("#zoom").attr("checked");

        // this doesn't work for this plot b/c of logarithmic x-axis
        if (zoom)
            plot = \$.plot(placeholder, data,
                   \$.extend(true, {}, options, {
                      xaxis: { min: -Math.logx(ranges.xaxis.from), 
                               max: -Math.logx(ranges.xaxis.to) },
                      yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
                   }));
        else 
           var plot = \$.plot(placeholder, data, options);
      });

      placeholder.bind("plothover", function (event, pos, item) {
        \$("#x").text(pos.x.toFixed(2));
        \$("#y").text(pos.y.toFixed(2));
      });

      placeholder.dblclick(function() {
         var plot = \$.plot(placeholder, data, options);
      });

      var plot = \$.plot(placeholder, data, options);

      }); // close function
   </script>

   <form name="dst_form" method="post" action="./more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.dst">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>

<h3>BENEFICIALS</h3>

   <div id="fdst" style="width:600px;height:370px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.dst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         #$x = -log($col1+1.e-8);
         $x = $col1;
         if ($. >= 56 && $col1 ne "#") {print "[$x, $col3], ";}
      }
      close FH;
      print "];";
      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.dst");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         #$x = -log($col1+1.e-8);
         $x = $col1;
         if ($. >= 56 && $col1 ne "#") {print "[$x, $col2], ";}
      }
      close FH;
      print "];";
print <<END_HTML;
      var data = [ { label: "Dominant", data: d1, 
                     bars: { show: true, barWidth: 0 },
                     color: "rgb(0,200,0)"},
                   { label: "Recessive", data: d2,
                     bars: { show: true, barWidth: 0 },
                     color: "rgb(200,0,0)"} ];

      // Line annotation at 2 -- selection threshold point
      var markings = [
        { color: '#000', lineWidth: 1, yaxis: { from: 2, to: 2 } },
      ];

      var options = { 
         xaxis: { axisLabel: 'Mutational Fitness Enhancement',
                  axisLabelFontSizePixels: 12,
         // following two lines are needed for log axis
         transform: function (x) { return Math.log(x); }, 
         inverseTransform: function (x) { return Math.exp(x);},
         ticks: [[1.0,"1"],[0.1,"1e-1"],[0.01,"1e-2"],[1e-3,"1e-3"],
                 [1e-4,"1e-4"],[1e-5,"1e-5"],[1e-6,"1e-6"],[1e-7,"1e-7"],
                 [1e-8,"1e-8"]], tickDecimals: 6, max: $max_fav_fitness_gain },
         yaxis: { axisLabel: 'Fraction of Mutations Retained in Genome', axisLabelOffset: -220, axisLabelFontSizePixels: 12, max: 10},
         legend: { position: 'nw' },
         grid: { markings: markings }
      };

      var placeholder = \$("#fdst");

      var plot = \$.plot(placeholder, data, options);

      }); // close function

   </script>

</div>

<!-- ############ THRESHOLD ####################################### -->
<div class="tab-page">

   <h2 class="tab">threshold</h2>

   <h3>4: Selection threshold history ($case_id)</h3>
   <p><i>updated every 20 generations</i></p>

   <div id="thr" style="width:600px;height:370px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.thr");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%$modulo==0 && $col1 ne "#") {print "[$col1, $col2], ";}
      }
      close FH;
      print "];";
      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.thr");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1%$modulo==0 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];";
print <<END_HTML;
      var data = [ { label: "Deleterious threshold", 
                     data: d1, color: "rgb(200,0,0)"},
                   { label: "Favorable threshold",
                     data: d2, color: "rgb(0,200,0)"} ];
      var options = {
         xaxis: { axisLabel: 'Generations', axisLabelFontSizePixels: 12 },
         yaxis: { axisLabel: 'Selection Threshold', axisLabelOffset: -120, 
                  axisLabelFontSizePixels: 12 },
         grid: { hoverable: true, clickable: true },
         selection: { mode: "xy" } 
      };

      var placeholder = \$("#thr");

      // attach an event handler directly to the plot
      placeholder.bind("plotselected", function (event, ranges) {
        \$("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));

        var zoom = \$("#zoom").attr("checked");

        if (zoom)
            plot = \$.plot(placeholder, data,
                   \$.extend(true, {}, options, {
                      xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
                      yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
                   }));
        else 
           var plot = \$.plot(placeholder, data, options);
      });

      placeholder.bind("plothover", function (event, pos, item) {
        \$("#x").text(pos.x.toFixed(2));
        \$("#y").text(pos.y.toFixed(3));
      });

      placeholder.dblclick(function() {
         var plot = \$.plot(placeholder, data, options);
      });

     
      var plot = \$.plot(placeholder, data, options);

   });
   </script>

   <form method="post" action="./more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.thr">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>

</div>

<!-- ############ NEAR-NEUTRAL ####################################### -->
<div class="tab-page">

   <h2 class="tab">near-neutrals</h2>

   <h3>5: Linear-scale distribution of minor and near-neutral effects ($case_id)</h3>
   <p><i>updated every 20 generations</i></p>

   <h3>DELETERIOUS</h3>

   <div id="dmutn" style="width:600px;height:370px;"></div> 
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
      print "];\n\n";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1 <= 102 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];\n\n";

      print "var d3 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($col1 <= 102 && $col1 ne "#") {print "[$col1, $col5], ";}
      }
      close FH;
      print "];\n\n";

print <<END_HTML;
      var data = [ { label: "Theoretical", 
		     data: d1, color: "rgb(200,0,0)" },
		   { label: "Dominant",
	    	     bars:  { show: true, barWidth: 0.0001 },
		     data: d2, color: "rgb(0,200,0)" },
		   { label: "Recessive",
		     bars:  { show: true, barWidth: 0.0001 },
		     data: d3, color: "rgb(0,0,200)" } ];

      var options = {
         xaxis: { axisLabel: 'Fitness Effect', axisLabelFontSizePixels: 12, 
                  ticks: 10, min: -0.01, max: 0.0},
	 yaxis: { axisLabel: 'Frequency', axisLabelOffset: -50, 
                  axisLabelFontSizePixels: 12, ticks: 10, min: 0.0, max: 0.01}, 
	 legend: { position: 'nw' },
         grid: { hoverable: true, clickable: true },
         selection: { mode: "xy" } 
      };

      var placeholder = \$("#dmutn");

      // attach an event handler directly to the plot
      placeholder.bind("plotselected", function (event, ranges) {
        \$("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));

        var zoom = \$("#zoom").attr("checked");

        if (zoom)
            plot = \$.plot(placeholder, data,
                   \$.extend(true, {}, options, {
                      xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
                      yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
                   }));
        else 
           var plot = \$.plot(placeholder, data, options);
      });

      placeholder.bind("plothover", function (event, pos, item) {
        \$("#x").text(pos.x.toFixed(4));
        \$("#y").text(pos.y.toFixed(4));
      });

      placeholder.dblclick(function() {
         var plot = \$.plot(placeholder, data, options);
      });


      var plot = \$.plot(placeholder, data, options);

   });
   </script>

   <form method="post" action="./more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.hap">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>

   <h3>BENEFICIALS</h3>

   <div id="fmutn" style="width:600px;height:370px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= 102 && $col1 ne "#") {print "[$col1, $col2], ";}
      }
      close FH;
      print "];\n\n";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= 102 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];\n\n";

      print "var d3 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= 102 && $col1 ne "#") {print "[$col1, $col5], ";}
      }
      close FH;
      print "];\n\n";

print <<END_HTML;
      var data = [{ label: "Theoretical", data: d1, color: "rgb(200,0,0)" },
	          { label: "Dominant", bars:  { show: true, barWidth: 0.0001 },
		    data: d2, color: "rgb(0,200,0)" },
	          { label: "Recessive", bars: { show: true, barWidth: 0.0001 },
		    data: d3, color: "rgb(0,0,200)" } ];

      var options = {
         xaxis: { axisLabel: 'Fitness Effect', axisLabelFontSizePixels: 12,
                  ticks: 10, min: 0.0, max: 0.01},
	 yaxis: { axisLabel: 'Frequency', axisLabelOffset: -50, 
                  axisLabelFontSizePixels: 12, ticks: 10, min: 0.0, max: 0.01 },
	 legend: { position: 'ne' },
         grid: { hoverable: true, clickable: true },
         selection: { mode: "xy" } 
      };

      var placeholder = \$("#fmutn");

      // attach an event handler directly to the plot
      placeholder.bind("plotselected", function (event, ranges) {
        \$("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));

        var zoom = \$("#zoom").attr("checked");

        if (zoom)
            plot = \$.plot(placeholder, data,
                   \$.extend(true, {}, options, {
                      xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
                      yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
                   }));
        else 
           var plot = \$.plot(placeholder, data, options);
      });

      placeholder.bind("plothover", function (event, pos, item) {
        \$("#x").text(pos.x.toFixed(4));
        \$("#y").text(pos.y.toFixed(4));
      });

      placeholder.dblclick(function() {
         var plot = \$.plot(placeholder, data, options);
      });

      var plot = \$.plot(placeholder, data, options); 

   });
   </script>

</div>

<!-- ############ LINKAGE ####################################### -->
<div class="tab-page">

   <h2 class="tab">linkage</h2>

   <h3>6: Linkage block effects ($case_id)</h3>
   <p><i>updated every 20 generations</i></p>

   <div id="hap" style="width:600px;height:370px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.hap");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. < 102 && $col1 ne "#") {print "[$col1, $col3], ";}
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
         if ($. >= 103 && $col1 ne "#") {print "[$col1, $col3], ";}
      }
      close FH;
      print "];";
print <<END_HTML;
      var data = [ { label: "Net-deleterious effect blocks", 
		     bars:  { show: true, barWidth: 0.0001 },
		     data: d1, color: "rgb(200,0,0)" },
		   { label: "Net-beneficial effect blocks",
		     bars:  { show: true, barWidth: 0.0001 },
		     data: d2, color: "rgb(0,200,0)" } ];

      var options = { 
         xaxis: { axisLabel: 'Fitness effect', axisLabelFontSizePixels: 12, 
                  ticks: 10, min: -0.01, max: 0.01},
         yaxis: { axisLabel: 'Frequency', axisLabelOffset: -50, 
                  axisLabelFontSizePixels: 12, ticks: 10, min: 0.0, max: 0.01},
         grid: { hoverable: true, clickable: true },
         selection: { mode: "xy" } 
      };

      var placeholder = \$("#hap");

      // attach an event handler directly to the plot
      placeholder.bind("plotselected", function (event, ranges) {
        \$("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));

        var zoom = \$("#zoom").attr("checked");

        if (zoom)
            plot = \$.plot(placeholder, data,
                   \$.extend(true, {}, options, {
                      xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
                      yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
                   }));
        else 
           var plot = \$.plot(placeholder, data, options);
      });

      placeholder.bind("plothover", function (event, pos, item) {
        \$("#x").text(pos.x.toFixed(4));
        \$("#y").text(pos.y.toFixed(4));
      });

      placeholder.dblclick(function() {
         var plot = \$.plot(placeholder, data, options);
      });

      var plot = \$.plot(placeholder, data, options);

   });
   </script>

   <form method="post" action="./more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.hap">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>

<hr>
Average linkage block effect = $avg_lb_effect<br>
Linkage blocks which have a positive fitness value = $lb_fitness_percent_positive% <br>


</div>

<!-- ############ SELECTION ####################################### -->
<div class="tab-page">

   <h2 class="tab">selection</h2>

   <h3>7: Selection effects ($case_id)</h3>
   <p><i>updated every 20 generations</i></p>

   <div id="sel" style="width:600px;height:370px;"></div> 
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
      var data = [ { label: "<< Before selection", 
                     bars:  { show: true, barWidth: 0.01 },
                     data: d1, color: "rgb(200,0,0)" },
                   { label: "<< After selection",
                     bars:  { show: true, barWidth: 0.01 },
                     data: d2, color: "rgb(0,200,0)" },
                   { label: ">> After/before ratio",
                     data: d3, color: "rgb(0,0,200)", yaxis: 2 } ];

      var options = { 
         xaxis: { axisLabel: 'Fitness', axisLabelFontSizePixels: 12 },
         yaxis: { axisLabel: 'Number of Individuals', axisLabelOffset: -120, 
                  axisLabelFontSizePixels: 12, ticks: 10, min: 0.0 },
         y2axis: { ticks: 5, min: 0.0, max: 1.0 },
         grid: { hoverable: true, clickable: true },
         selection: { mode: "xy" } 
      };
           
      var placeholder = \$("#sel");

      // attach an event handler directly to the plot
      placeholder.bind("plotselected", function (event, ranges) {
        \$("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));

        var zoom = \$("#zoom").attr("checked");

        if (zoom)
            plot = \$.plot(placeholder, data,
                   \$.extend(true, {}, options, {
                      xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
                      yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
                   }));
        else 
           var plot = \$.plot(placeholder, data, options);
      });

      placeholder.bind("plothover", function (event, pos, item) {
        \$("#x").text(pos.x.toFixed(2));
        \$("#y").text(pos.y.toFixed(2));
      });

      placeholder.dblclick(function() {
         var plot = \$.plot(placeholder, data, options);
      });

      var plot = \$.plot(placeholder, data, options);
   });
   </script>

   <form method="post" action="./more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.sel">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>

<p><font color="red">NOTE: if no data appears, it means the data is off-scale during histogram binning process.</font></p>

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

   <h3>8: Allele frequencies ($case_id)</h3>
   <p><i>updated every $plot_allele_gens generations and at end of run</i></p>

   <div id="plm" style="width:600px;height:370px;"></div> 
   <script id="source" language="javascript" type="text/javascript"> 
      \$(function () {
      var d1 = [
END_HTML
      # Since the plm file has multiple snapshots of data for 
      # different generations, we need to get the number of lines in file, 
      # so we can plot only the last snapshot of allele frequencies
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.plm");
      my $lines = @f = <FH>;
      close FH;

      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.plm");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= $lines-109 && $col1 ne "#") {print "[$col1, $col4], ";}
      }
      close FH;
      print "];\n";

      print "var d2 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.plm");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5) = split(' ', $_, 9999);
         if ($. >= $lines-109 && $col1 ne "#") {print "[$col1, $col5], ";}
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
      print "];\n";

      print "var d3 = [";
      open(FH,"$run_dir/$user_id/$case_id/$case_id.000.plm");
      while (<FH>) {
         ($col1,$col2,$col3,$col4,$col5,$col6,$col7) = split(' ', $_, 9999);
         if ($. >= $lines-109 && $col1 ne "#") {print "[$col1, $col7], ";}
      }
      close FH;
      print "];\n";

print <<END_HTML;
      var data = [ { label: "Neutrals",    data: d3, bars: { show: true },
		     color: "rgb(0,0,200)"},
                   { label: "Deleterious", data: d1, bars: { show: true },
		     color: "rgb(200,0,0)"},
		   { label: "Favorable",   data: d2, bars: { show: true },
		     color: "rgb(0,200,0)"} ];

      var options = { 
         xaxis: { axisLabel: 'Allele Frequency', axisLabelFontSizePixels: 12 },
         yaxis: { axisLabel: 'Number of Alleles', axisLabelOffset: -100,
                  axisLabelFontSizePixels: 12 },
         grid: { hoverable: true, clickable: true },
         selection: { mode: "xy" } 
      };

      var placeholder = \$("#plm");

      // attach an event handler directly to the plot
      placeholder.bind("plotselected", function (event, ranges) {
        \$("#selection").text(ranges.xaxis.from.toFixed(1) + " to " + ranges.xaxis.to.toFixed(1));

        var zoom = \$("#zoom").attr("checked");

        if (zoom)
            plot = \$.plot(placeholder, data,
                   \$.extend(true, {}, options, {
                      xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
                      yaxis: { min: ranges.yaxis.from, max: ranges.yaxis.to }
                   }));
        else 
           var plot = \$.plot(placeholder, data, options);
      });

      placeholder.bind("plothover", function (event, pos, item) {
        \$("#x").text(pos.x.toFixed(2));
        \$("#y").text(pos.y.toFixed(2));
      });

      placeholder.dblclick(function() {
         var plot = \$.plot(placeholder, data, options);
      });


      var plot = \$.plot(placeholder, data, options);
   });
   </script>

   <form method="post" action="./more.cgi">
   <input type="hidden" name="case_id" value="$case_id">
   <input type="hidden" name="file_name" value="${case_id}.000.plm">
   <input type="hidden" name="run_dir" value="$run_dir">
   <input type="hidden" name="user_id" value="$user_id">
   <input type="submit" value="Data">
   </form>

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
} # if(fitness_distrib_type > 0)

print <<END_HTML;
 <p><label><input id="zoom" type="checkbox" CHECKED />Zoom to selection.</label> Double click to restore to original plot.</p>

<p id="hoverdata">Mouse hovers at
    (<span id="x">0</span>, <span id="y">0</span>). <span id="clickdata"></span></p>

<table border=0 width=$plot_width>
<tr bgcolor=dfdfdf> <td>Generation</td> <td>Fitness</td> <td>avg # del mutns</th> <td>avg # fav mutns</td> <td>avg # neu mutns</td> </tr>
<tr> <td>$gen</td> <td>$fitness</td> <td>$num_dmutns</th> <td>$num_fmutns</td> <td>$num_nmutns</td> </tr>
</table>
<br>

<hr>
To save an image of the plots:<br>
<ul>
<li>On Mac OS X, click Shift+Command+4, and click and drag the mouse to create a box which envelopes the plot you wish you save as an image.  The images should be saved on the Desktop.
<li>On Linux, hit the PrtSc button, and a window should come up asking where to save file.
<li>On Windows, select the Alt+PrtSc button (some computers may require using Fn key as well). This copies the window to the clipboard.  In Microsoft PowerPoint, the Paste function can be used to paste the image.  Modify and crop the image as desired.  Then, right click on the image and select \"Save As...\" to save the image to a file.
</li>
  
</body>
</html>

END_HTML
