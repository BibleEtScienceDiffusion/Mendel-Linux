#!/usr/bin/perl
##############################################################################
#
# input_file_writer.pl  -> this_file -> output *.gnu files in $run_dir
# plot_gnuplot_modify.cgi       -> this_file -> output *.gnu files in $run_dir
# plot_gnuplot_combine.cgi     -> this_file -> output *.gnu files in $run_dir
#
# This file writes the Gnuplot recipe files *.gnu into the Case directory
#
# Note: this file is unique in that it can be called three ways:
# (1) posted to from form, (2) included/required from another Perl file
# (3) called directly from Linux command line:
#     e.g.  /var/www/cgi-bin/v1.4.3/plot_recipes.cgi mytest
# if the file mendel.in exists in the directory, it will use
# that name as the case_id. Otherwise it will use "mytest".
# But it is important that the case_id is specified whether or
# not there is a mendel.in file. It is the argument that tells the
# script that this is being called from the command line.
#
##############################################################################

#following line has problems when combining plots
#require "./parse.inc";

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

$caller=$formdata{'caller'};

$plot=$formdata{'plot'};
$xmin=$formdata{'xmin'};
$xmax=$formdata{'xmax'};
$ymin=$formdata{'ymin'};
$ymax=$formdata{'ymax'};
$y2min=$formdata{'y2min'};
$y2max=$formdata{'y2max'};

$grayscale=$formdata{'grayscale'};
$fill_boxes=$formdata{'fill_boxes'};

$format=$formdata{'format'};
if($format eq "") { $format = "png"; }

$labels=$formdata{'labels'};
$lines=$formdata{'lines'};
$grid=$formdata{'grid'};
$user_id=$formdata{'user_id'};

if ($lines eq "on") { 
   $lorb="lines";
} else {
   $lorb="boxes";
}

# in case not calling from plot_gnuplot_combine.cgi
if ($plot eq "") { $plot = "all"; }

# check if this is being called from Linux command-line
# if so, write files to the cwd (current working directory)
$numArgs = $#ARGV + 1;
if ($numArgs >= 1) {
   $this_dir = `dirname $0`;
   chop($this_dir);
   $run_dir = ".";
   $case_dir = ".";
   $path="$case_dir/mendel.in";
   if(-f $path) {
      require "./$this_dir/input_file_parser.inc";
   } else {
      $case_id = $ARGV[0];
   }

## if posting to this file from another form 
## rather than requiring it
} elsif ($case_id eq "") {
   require "./config.inc";
   $case_id=$formdata{'case_id'};

   #$run_dir=$formdata{'run_dir'};
   $case_dir="$run_dir/$case_id";
   $plot_avg_data=$formdata{'plot_avg_data'};
   if (lc($plot_avg_data) eq "on") { $plot_avg_data = 1; }
   else { $plot_avg_data = 0; }
   $mod_plot_avg_data = $plot_avg_data;
   print "Content-type:text/html\n\n";
   #print "buffer is: $buffer<br>";
   #print "case_id is: $case_id<br>";
   #print "run_dir is: $run_dir<br>";
   #print "user_id is: $user_id<br>";
   #print "plot type is: $plot<br>";
   #print "plot_avg_data is:",$plot_avg_data,"<br>";

   #require "./plot.cgi";

   $combine_plots=0;
   ########################################
   # COMBINE PLOTS
   # if called from plot_gnuplot_combine.cgi
   if ($caller eq "combine") {
      $combine_plots=1;

      $ccid=$formdata{'ccid'};
      $case_id=$ccid;

      $case_id_length=length($case_id);

      if ($case_id =~ /,/) {
         print "<h2>ERROR: case_id cannot contain ,</h2>";
         die;
      } elsif ($case_id =~ /\!/) {
         print "<h2>ERROR: case_id cannot contain !</h2>";
         die;
      } elsif ($case_id  eq "") {
         print "<h1>ERROR: must enter Case ID!</h1>";
         die;
      }

      #$case_dir="$run_dir/$user_id/$case_id";
      $case_dir="$run_dir/$user_id/$ccid";

      system("mkdir -p $case_dir");
      system("echo combo-plot > $case_dir/version");

      $selected_cases=$formdata{'selected_cases'};
      @cases = split(/:/,$selected_cases);
      ($cfuid,$cfcid) = split('/',$cases[0]);

      $copyf = "$run_dir/$cfuid/$cfcid/$cfcid";
      $copyt = "$run_dir/$user_id/$case_id/$case_id";

      #print "case_dir is $case_dir<br>";
      #print "cases[0] is $cases[0]<br>";
      #print "copyf is $copyf<br>";
      #print "copyt is $copyt<br>";

      system("cp $run_dir/$cfuid/$cfcid/mendel.in $run_dir/$user_id/$case_id");
      system("cp $copyf.000.hst $copyt.000.hst");
      system("cp $copyf.000.dst $copyt.000.dst");
      system("cp $copyf.000.thr $copyt.000.thr");
      system("cp $copyf.000.plm $copyt.000.plm");
      system("cp $copyf.000.hap $copyt.000.hap");
      system("cp $copyf.000.sel $copyt.000.sel");

      #$run_dir=$run_dir."/".$case_id;

      print("<script language=\"Javascript\">parent.frames.contents.caseidform.case_id.value = \"$case_id\";</script>\n");
      print "<h1>CLICK PLOT (or Alt-G) TO CONTINUE.</h1>";
      print "<meta http-equiv=\"refresh\" content=\"0;URL=plot_gnuplot.cgi?case_id=$case_id&user_id=$user_id\">\n";
   }
}

#################################
# if called by plot_modify.cgi
if($caller eq "modify") {
   $dominant_only=$formdata{'dominant_only'};
   $annotation=$formdata{'annotation'};

   $pgm=$formdata{'pgm'};
   if($pgm eq "on") { $pop_growth_model="1"; }

   #$run_dir=$formdata{'run_dir'};
   #$run_dir=$run_dir."/".$case_id;
   $case_dir="$run_dir/$user_id/$case_id";
   print "<h1>Plot recipe has been modified.<br>";
   print "CLICK PLOT (or Alt-G) TO CONTINUE.</h1>";
   print "<meta http-equiv=\"refresh\" content=\"1;URL=plot_gnuplot.cgi?case_id=$case_id&user_id=$user_id\">\n";

   $path=$case_dir."/mendel.in";
   require "./input_file_parser.inc";
   # reading the mendel.in file will overwrite the plot_avg_data option
   # specified in the Modify plots dialogue, so set it back to 
   $plot_avg_data = $mod_plot_avg_data;
}

#print "case_dir is: $case_dir<p>";
#print "dominant_only is: $dominant_only<p>";
#print "is_parallel is: $is_parallel<br>";
#print "fill_boxes is: $fill_boxes<br>";

# if case_id not specified by this point
# do not proceed to write files
if($case_id eq "") {
   print "ERROR: case_id is empty\n";
   die; 
}
if($run_dir eq "") {
   print "ERROR: run_dir is empty\n";
   die; 
}

#################################

# delete old plot figures
#system("cd $run_dir;/bin/rm *.$format");

### write plot_mutn_hst 
if($plot eq "mutn_hst" || $plot eq "all") {

    $myXLabel="Number of generations";
    $myYLabel="Deleterious and Neutral Mutations";
    $myTitle=sprintf("Average mutations per individual (%s)",$case_id);
    open(FILEWRITE, "> $case_dir/${case_id}_mutn_hst.gnu");
    $ofn=sprintf("%s_mutn_hst.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);
    printParameters(*FILEWRITE,0.4,0.375);

    # can set y2max to this value... currently unused
    $max_num_fav_mutn = 1+$num_generations*$mutn_rate*$frac_fav_mutn;

    if($xmin ne "" || $xmax ne "") {
       print FILEWRITE sprintf("set xrange [$xmin : $xmax]\n");
    } else {
       #print FILEWRITE sprintf("set xrange [0.0 : ]\n");
    }
    if($ymax ne "") {
       print FILEWRITE sprintf("set yrange [$ymin : $ymax]\n");
    }
    print FILEWRITE sprintf("set ytics nomirror\n");

    if($y2min ne "" || $y2max ne "") {
       print FILEWRITE sprintf("set y2range [$y2min : $y2max]\n");
    } else {
       print FILEWRITE sprintf("set y2range [0.0 : $max_num_fav_mutn]\n");
       #print FILEWRITE sprintf("set y2range [0.0 : ]\n");
    }
    print FILEWRITE sprintf("set y2label \"Favorable mutations\"\n");
    print FILEWRITE sprintf("set y2tics \n");

    print FILEWRITE sprintf("set key left\n");
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"$case_id.%03d.hst\" using 1:4 title \"Deleterious (tribe $i)\", \"$case_id.%03d.hst\" using 1:5 title \"Favorable (tribe $i)\", \"$case_id.%03d.hst\" using 1:6 title \"Neutral (tribe $i)\"",$i,$i,$i);
	    if ( $i != $num_tribes ) { print FILEWRITE sprintf(", "); }
	}
	print FILEWRITE sprintf("\n");
    } elsif($combine_plots) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.hst\" using 1:4 title \"Deleterious: $cases[$i]\" axis x1y1, \"../$cid/$cid.000.hst\" using 1:5 title \"Favorable: $cases[$i]\" axis x1y2, \"../$cid/$cid.000.hst\" using 1:6 title \"Neutral: $cases[$i]\" axis x1y1");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } else {
	print FILEWRITE sprintf("plot \"%s.000.hst\" using 1:4 title \"Deleterious\" axis x1y1, \"%s.000.hst\" using 1:5 title \"Favorable\" axis x1y2, \"%s.000.hst\" using 1:6 title \"Neutral\" axis x1y1\n",$case_id,$case_id,$case_id);
    }
    close FILEWRITE;
}
    
### write plot_fit_hst
if($plot eq "fit_hst" || $plot eq "all") {
    
    # originally we plotted standard deviation on y2 axis
    # but with dynamic populations we want to change this to instead
    # plot population size on y2 axis
    my $plot_pop_size = true;

    # in case we comment out above line we always want to plot
    # population size on y2 when there dynamic population growth is on
    if($pop_growth_model) { $plot_pop_size = true; }

    $myXLabel="Number of generations";
    $myYLabel="Fitness";
    if($plot_pop_size) {
       $myTitle=sprintf("Fitness and Population size (%s)",$case_id);
    } else {
       $myTitle=sprintf("Population fitness and fitness standard deviation (%s)", $case_id);
    }
    open(FILEWRITE, "> $case_dir/${case_id}_fit_hst.gnu");

    $ofn=sprintf("%s_fit_hst.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);

    printParameters(*FILEWRITE,0.4,0.47);

    if($xmin ne "" || $xmax ne "") {
       print FILEWRITE sprintf("set xrange [$xmin : $xmax]\n");
    } else {
       #print FILEWRITE sprintf("set xrange [0.0 : ]\n");
    }
    if($ymin ne "" || $ymax ne "") {
       print FILEWRITE sprintf("set yrange [$ymin : $ymax]\n");
    } else {
       print FILEWRITE sprintf("set yrange [0.0 : ]\n");
    }

    print FILEWRITE sprintf("set ytics nomirror\n");

    if(!$combine_plots) {
       if($y2min ne "" || $y2max ne "") {
          print FILEWRITE sprintf("set y2range [$y2min : $y2max]\n");
       } elsif($tribal_competition) {
          print FILEWRITE sprintf("set y2range [0.0 : 100.0]\n");
       } else {
          print FILEWRITE sprintf("set y2range [0.0 : ]\n");
       }
       if($tribal_competition) {
          print FILEWRITE sprintf("set y2label \"Tribal size relative to global pop. size (%)\"\n");
       } elsif($plot_pop_size) {
          print FILEWRITE sprintf("set y2label \"Population size\"\n");
       } else {
          print FILEWRITE sprintf("set y2label \"Standard Deviation\"\n");
       }
       print FILEWRITE sprintf("set y2tics \n");
    }

    print FILEWRITE sprintf("set key left bottom\n");
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    #print FILEWRITE sprintf("set y2range [0.0 : $num_generations]\n");

    $extinction_threshold = 0.1;
    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot ");
        print FILEWRITE sprintf("$extinction_threshold title \"Extinction threshold\" lw 3, ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"$case_id.%03d.hst\" using 1:2 title \"Fitness (tribe $i)\", \"$case_id.%03d.hst\" using 1:7 title \"Population size (tribe $i)\" axis x1y2 with lines lw 3",$i,$i);
	    if ( $i != $num_tribes ) { print FILEWRITE sprintf(", "); }
	}
        #print FILEWRITE sprintf("\"%s.%03d.hst\" using 1:(\$6*0.1) title \"Meltdown threshold\"",$case_id,$i);
	print FILEWRITE sprintf("\n");
    } elsif($combine_plots) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.hst\" using 1:2 title \"$cases[$i]\"");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } else {
       if($plot_pop_size) {
  	  print FILEWRITE sprintf("plot \"%s.000.hst\" using 1:2 title \"Fitness\", \"%s.000.hst\" using 1:7 title \"Population size\" axis x1y2 \n",$case_id,$case_id);
       } else {
          print FILEWRITE sprintf("plot $extinction_threshold title \"Extinction threshold\" lw 3, \"%s.000.hst\" using 1:2 title \"Fitness\"       , \"%s.000.hst\" using 1:3 title \"Standard Deviation\" axis x1y2 \n",$case_id,$case_id);
       }
    }
    close FILEWRITE;
}    

### write plot_dst
if($plot eq "ddst" || $plot eq "all") {
    $myXLabel="Mutational Fitness Degradation";
    $myYLabel="Fraction of Mutations Retained in Genome";
    $myTitle=sprintf("Distribution of accumulated deleterious mutations (%s)",$case_id);
    open(FILEWRITE, "> $case_dir/${case_id}_dst.gnu");

    $ofn=sprintf("%s_dst.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);

    printParameters(*FILEWRITE,0.15,0.76);

    if($xmin ne "" || $xmax ne "") {
       print FILEWRITE sprintf("set xrange [$xmin : $xmax] reverse\n");
    } else {
       if($is_parallel eq "T" && !$plot_avg_data) {
          $xmin = $tracking_threshold;
          # will not plot if xmin = 0 because of logscale
          if($xmin eq "0") { $xmin = 1.e-8; }
          if($xmin eq "" ) { $xmin = 1.e-8; }
          print FILEWRITE sprintf("set xrange [$xmin : 1.0] reverse\n");
       } else {
          print FILEWRITE sprintf("set xrange [ : 1.0] reverse\n");
       }
    }
    if($ymin ne "" || $ymax ne "") {
       print FILEWRITE sprintf("set yrange [$ymin : $ymax]\n");
    } else {
       print FILEWRITE sprintf("set autoscale y\n");
    }
    if($y2min ne "" || $y2max ne "") {
       print FILEWRITE sprintf("set y2range [$y2min : $y2max]\n");
    }

    if($caller eq "modify") {
       print FILEWRITE sprintf("set ytics auto\n");
    } else {
       print FILEWRITE sprintf("set ytics 0.1\n");
    }
    print FILEWRITE sprintf("set xtics scale 2.0\n");
    print FILEWRITE sprintf("set logscale x\n");
    print FILEWRITE sprintf("set key left\n");
    if($fill_boxes) {
       print FILEWRITE sprintf("set style fill solid 0.5\n");
    }
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot 0 title \"\", ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"%s.%03d.dst\" every ::1::50 using 1:3:4 title \"Dominant (tribe $i)\" with $lorb lw 3, \"%s.%03d.dst\" every ::1::50 using 1:2:4 title \"Recessive (tribe $i)\" with $lorb lw 3, ",$case_id,$i,$case_id,$i);
	}
	print FILEWRITE sprintf(" 1 lw 3\n");
    } elsif($combine_plots) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.dst\" every ::1::50 using 1:3:4 title \"$cid\" with $lorb lw 3");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } elsif($dominant_only || $fraction_recessive == 0) {
	print FILEWRITE sprintf("plot 0.5 title \"\" ls 0, \"%s.000.dst\" every ::0::49 using 1:3:4 title \"Dominant\" with $lorb lw 3\n",$case_id);
    } else {
	print FILEWRITE sprintf("plot 0.5 title \"\" ls 0, \"%s.000.dst\" every ::0::49 using 1:3:4 title \"Dominant\" with $lorb lw 3, \'%s.000.dst\' every ::0::49 using 1:2:4 title \"Recessive\" with $lorb lw 3\n",$case_id,$case_id);
    }
    close FILEWRITE;
}    

### write plot_fdst
if($plot eq "fdst" || $plot eq "all") {
    
    $myXLabel="Mutational Fitness Increase";
    $myYLabel="Fractional Mutation Accumulation\\nRelative to No Selection";
    $myTitle=sprintf("Distribution of accumulated mutations\\nAccumulated beneficial mutations (%s)",$case_id);
    open(FILEWRITE, "> $case_dir/${case_id}_fdst.gnu");

    $ofn=sprintf("%s_fdst.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);

    printParameters(*FILEWRITE,0.15,0.86);

    if ($num_linkage_subunits ne "") {
	$lb_modulo=(2**32-2)/$num_linkage_subunits;
	$rand_modulo=714025;
	$lb_modulo=$rand_modulo/($rand_modulo/$lb_modulo + 1);
	$inv_range=1/$lb_modulo;
	$expn_scale=log($genome_size);
	$fav_threshold=log(100*$pop_size)/($expn_scale*$inv_range);
	$inv_fav_threshold=1/$fav_threshold;
        if($xmin ne "" || $xmax ne "") {
           printf FILEWRITE sprintf("set xrange [$xmin : $xmax]\n");
        } else {
           $half_tracking_threshold = 0.5*$tracking_threshold;
	   #print FILEWRITE sprintf("set autoscale x\n");
	   print FILEWRITE sprintf("set xrange [$half_tracking_threshold : $max_fav_fitness_gain ] \n");
	   #print FILEWRITE sprintf("set xrange [$inv_fav_threshold : $max_fav_fitness_gain ] \n");
        }
    }
    print FILEWRITE sprintf("set logscale x\n");

    if($xmin ne "" || $xmax ne "") {
       printf FILEWRITE sprintf("set xrange [$xmin : $xmax]\n");
    }
    
    if ($ymin ne "" || $ymax ne "") {
       print FILEWRITE sprintf("set yrange [$ymin : $ymax]\n");
    } else {
       #print FILEWRITE sprintf("set autoscale y\n");
       print FILEWRITE sprintf("set yrange [ : 10.0]\n");
    }

    if($fill_boxes) {
       print FILEWRITE sprintf("set style fill solid 0.5\n");
    }

    print FILEWRITE sprintf("set xtics scale 2.0\n");
    #print FILEWRITE sprintf("set key left bottom\n");
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot 0 title \"\", ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"%s.%03d.dst\" every ::50::100 using 1:3 title \"Dominant (tribe $i)\" with $lorb lw 3, \"%s.%03d.dst\" every ::50::100 using 1:2 title \"Recessive (tribe $i)\" with $lorb lw 3, ",$case_id,$i,$case_id,$i);
	}
	print FILEWRITE sprintf(" 1 lw 3\n");
    } elsif($combine_plots) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.dst\" every ::50::101 using 1:3 title \"$cid\" with $lorb lw 3",$cases[$i]);
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } elsif($dominant_only || $fraction_recessive == 0) {
	print FILEWRITE sprintf("plot 2.0 title \"\" ls 0, \"%s.000.dst\" every ::50::101 using 1:3 title \"Dominant\" with $lorb lw 3\n",$case_id);
    } else {
	print FILEWRITE sprintf("plot 2.0 title \"\" ls 0, \"%s.000.dst\" every ::50::101 using 1:3 title \"Dominant\" with $lorb lw 3, \'%s.000.dst\' every ::50::101 using 1:2 title \"Recessive\" with $lorb lw 3\n",$case_id,$case_id);
    }
    close FILEWRITE;
}

### write plot_thr
if($plot eq "thr" || $plot eq "all") {

    $ext="thr";
    $myXLabel="Generations";
    $myYLabel="Selection threshold";
    $myTitle=sprintf("Selection threshold history (%s)",$case_id);
    open(FILEWRITE, "> $case_dir/${case_id}_$ext.gnu");

    $ofn=sprintf("%s_$ext.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);

    printParameters(*FILEWRITE,0.55,0.76);

    if($xmin ne "" || $xmax ne "") {
       print FILEWRITE sprintf("set xrange [$xmin : $xmax]\n");
    } else {
       print FILEWRITE sprintf("set autoscale x\n");
    }
    if($ymin ne "" || $ymax ne "") {
       print FILEWRITE sprintf("set yrange [$ymin : $ymax]\n");
    } else {
       print FILEWRITE sprintf("set yrange [0.0 : ]\n");
       #print FILEWRITE sprintf("set autoscale y\n");
    }
    if($y2min ne "" || $y2max ne "") {
       print FILEWRITE sprintf("set y2range [$y2min : $y2max]\n");
    }

    #print FILEWRITE sprintf("set y2label \"Beneficial selection threshold\"\n");
    #print FILEWRITE sprintf("set ytics nomirror \n");
    #print FILEWRITE sprintf("set y2tics \n");

    #print FILEWRITE sprintf("set logscale y\n");
    print FILEWRITE sprintf("set key left\n");
    print FILEWRITE sprintf("set pointsize 1\n");
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot 0 title \"\", ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"$case_id.%03d.$ext\" with linespoints title \"Tribe $i\"",$i);
            if ( $i != $num_tribes ) { print FILEWRITE sprintf(", "); }
	}
	print FILEWRITE sprintf(" \n");
    } elsif($combine_plots) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.$ext\" using 1:2 title \"Deleterious: $cid\" with linespoints lw 3, \"../$cid/$cid.000.$ext\" using 1:4 title \"Favorable: $cid\" with linespoints lw 3");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } else {
	print FILEWRITE sprintf("plot \"%s.000.$ext\" using 1:2 title \"Deleterious\" with linespoints lw 3, \"%s.000.$ext\" using 1:4 title \"Favorable\" with linespoints lw 3\n",$case_id,$case_id);
    }
    close FILEWRITE;
}


### write plot_indep_dmutn
if($plot eq "dmutn" || $plot eq "all") {
    
    $myXLabel="Fitness effect";
    $myYLabel="Frequency";
    $myTitle=sprintf("Distribution of minor and near-neutral mutation effects (%s)\\nDeleterious mutations -- actual versus theoretical (without selection)",$case_id);
    open(FILEWRITE, "> $case_dir/${case_id}_indep_dmutn.gnu");

    $ofn=sprintf("%s_indep_dmutn.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);
    
    printParameters(*FILEWRITE,0.15,0.42);

    print FILEWRITE sprintf("set xtics 0.001\n");

    if ($xmin ne "" || $xmax ne "") {
       print FILEWRITE sprintf("set xrange [$xmin : $xmax]\n");
    } else {
       print FILEWRITE sprintf("set xrange [-0.01 : 0.0]\n");
    }
    if ($ymin ne "" || $ymax ne "") {
       print FILEWRITE sprintf("set yrange [ $ymin : $ymax]\n");
    } else {
       print FILEWRITE sprintf("set yrange [ 1.e-6 : 0.01]\n");
    }

    if($fill_boxes) {
       print FILEWRITE sprintf("set style fill solid 0.5\n");
    }
    print FILEWRITE sprintf("set key left\n");
    #print FILEWRITE sprintf("set logscale y\n");
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"$case_id.%03d.hap\" using 1:2 title \"Theoretical (tribe $i)\" with $lorb lw 3, \"$case_id.%03d.hap\" using 1:4 title \"Dominant (tribe $i)\" with $lorb lw 3, \"$case_id.%03d.hap\" using 1:5 title \"Recessive (tribe $i)\" with $lorb lw 3",$i,$i,$i);
	    if ( $i != $num_tribes ) { print FILEWRITE sprintf(", "); }
	}
	print FILEWRITE sprintf("\n");
    } elsif($combine_plots) {
        ($uid,$cid) = split('/',$cases[0]);
	print FILEWRITE sprintf("plot \"../$cid/$cid.000.hap\" using 1:2 title \"Theoretical\" with $lorb lw 3, ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.hap\" using 1:4 title \"$cid\" with $lorb lw 3");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } elsif($dominant_only || $fraction_recessive == 0) {
	print FILEWRITE sprintf("plot \"%s.000.hap\" using 1:2 title \"Theoretical\" with $lorb lw 3, \"%s.000.hap\" using 1:4 title \"Dominant\" with $lorb lw 3\n",$case_id,$case_id);
    } else {
	print FILEWRITE sprintf("plot \"%s.000.hap\" using 1:2 title \"Theoretical\" with $lorb lw 3, \"%s.000.hap\" using 1:4 title \"Dominant\" with $lorb lw 3, \"%s.000.hap\" using 1:5 title \"Recessive\" with $lorb lw 3\n",$case_id,$case_id,$case_id);
    }
    close FILEWRITE;
}

### write plot_indep_fmutn
if($plot eq "fmutn" || $plot eq "all") {
    
    $myXLabel="Fitness effect";
    $myYLabel="Frequency";
    $myTitle=sprintf("Distribution of minor and near-neutral mutation effects (%s)\\nBeneficial mutations -- actual versus theoretical (without selection)",$case_id);
    open(FILEWRITE, "> $case_dir/${case_id}_indep_fmutn.gnu");

    $ofn=sprintf("%s_indep_fmutn.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);

    printParameters(*FILEWRITE,0.15,0.86);

    print FILEWRITE sprintf("set xtics 0.001\n");
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    if($xmin ne "" || $xmax ne "") {
       printf FILEWRITE sprintf("set xrange [$xmin : $xmax]\n");
    } else {
       print FILEWRITE sprintf("set xrange [ 0.0 : 0.01]\n");
    }
    if($ymin ne "" || $ymax ne "") {
       printf FILEWRITE sprintf("set yrange [$ymin : $ymax]\n");
    } else {
       print FILEWRITE sprintf("set yrange [ 1.e-6 : 0.01]\n");
    }

    #print FILEWRITE sprintf("set logscale y\n");

    if($fill_boxes) {
       print FILEWRITE sprintf("set style fill solid 0.5\n");
    }

    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"%s.%03d.hap\" using 1:2 title \"Theoretical\" with $lorb lw 3, \"%s.%03d.hap\" using 1:4 title \"Dominant\" with $lorb lw 3, \"%s.%03d.hap\" using 1:5 title \"Recessive\" with $lorb lw 3",$case_id,$i,$case_id,$i,$case_id,$i);
	    if ( $i != $num_tribes ) { print FILEWRITE sprintf(", "); }
	}
	print FILEWRITE sprintf("\n");
    } elsif($combine_plots) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.hap\" using 1:2 title \"$cid\" with $lorb lw 3");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } elsif($dominant_only || $fraction_recessive == 0) {
	print FILEWRITE sprintf("plot \"%s.000.hap\" using 1:2 title \"Theoretical\" with $lorb lw 3, \"%s.000.hap\" using 1:4 title \"Dominant\" with $lorb lw 3\n",$case_id,$case_id);
    } else {
	print FILEWRITE sprintf("plot \"%s.000.hap\" using 1:2 title \"Theoretical\" with $lorb lw 3, \"%s.000.hap\" using 1:4 title \"Dominant\" with $lorb lw 3, \"%s.000.hap\" using 1:5 title \"Recessive\" with $lorb lw 3\n",$case_id,$case_id,$case_id);
    }
    close FILEWRITE;
}

### write plot_hap
if($plot eq "hap" || $plot eq "all") {
    
    $myXLabel="Fitness effect";
    $myYLabel="Frequency";
    $myTitle=sprintf("Haplotype fitness distribution all linkage blocks (%s)",$case_id);
    open(FILEWRITE, "> $case_dir/${case_id}_hap.gnu");

    $ofn=sprintf("%s_hap.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);
    
    printParameters(*FILEWRITE,0.15,0.86);

    print FILEWRITE sprintf("set xtics 0.002\n");
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    if ($xmin ne "" || $xmax ne "") {
       print FILEWRITE sprintf("set xrange [$xmin : $xmax]\n");
    } else {
       #print FILEWRITE sprintf("set xrange [-0.01 : 0.01]\n");
    }
    if ($ymin ne "" || $ymax ne "") {
       print FILEWRITE sprintf("set yrange [ $ymin : $ymax]\n");
    } else {
       print FILEWRITE sprintf("set yrange [ : 0.01]\n");
    }

    #print FILEWRITE sprintf("set logscale y\n");

    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"$case_id.%03d.hap\" every ::1::99 using 1:3 title \"Net-deleterious effect blocks (tribe $i)\" with $lorb lw 3, \"$case_id.%03d.hap\" every ::102::200 using 1:3 title \"Net-beneficial effect blocks (tribe $i)\" with $lorb lw 3",$i,$i);
	    if ( $i != $num_tribes ) { print FILEWRITE sprintf(", "); }
	}
	print FILEWRITE sprintf("\n");
    } elsif($combine_plots) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.hap\" every ::1::99 using 1:3 title \"$cid\" with $lorb lw 3");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } else {
	print FILEWRITE sprintf("plot \"%s.000.hap\" every ::1::99 using 1:3 title \"Net-deleterious effect blocks\" with $lorb lw 3, \"%s.000.hap\" every ::102::200 using 1:3 title \"Net-beneficial effect blocks\" with $lorb lw 3\n",$case_id,$case_id);
    }
    close FILEWRITE;
}
    
### write plot_plm
if($plot eq "plm" || $plot eq "all") {
    
    $myXLabel="Allele frequency";
    $myYLabel="Number of Alleles";
    if ( $is_parallel eq "T" && !$plot_avg_data ) {
       $myTitle=sprintf("Tribal allele frequency distribution (%s)",$case_id);
    } elsif ( $is_parallel eq "T" && $plot_avg_data ) {
       $myTitle=sprintf("Global allele frequency distribution (%s)",$case_id);
    } else {
       $myTitle=sprintf("Allele Frequency (%s)",$case_id);
    }
    open(FILEWRITE, "> $case_dir/${case_id}_plm.gnu");

    $ofn=sprintf("%s_plm.$format",$case_id);
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);

    printParameters(*FILEWRITE,0.15,0.86);

    #if ($xmin ne "" || $xmax ne "") {
    if ($caller eq "modify") {
       print FILEWRITE sprintf("set xrange [ $xmin : $xmax]\n");
    } else {
       print FILEWRITE sprintf("set xrange [0.0 : 100.0 ]\n");
    }
    if ($ymin ne "" || $ymax ne "") {
       print FILEWRITE sprintf("set yrange [ $ymin : $ymax]\n");
    } else {
       print FILEWRITE sprintf("set yrange [0.0 : ]\n");
    }

    if($fill_boxes) {
       print FILEWRITE sprintf("set style fill solid 0.5\n");
    }

    # Since there is more than one snapshot of data in the plm file,
    # we need to tail the last 110 lines to plot only the most
    # recent data.  $nl is the number of lines from the bottom
    # of the file to the first bin, for the most recent set of data.
    $nl = -110; 
    # I am disabling the following statement because John Sanford said
    # he has no interest in relative allele frequency distributions.
    # If this ever becomes of interest in the future, just change the 0
    # to a 1 in the next line
    if ( $is_parallel eq "T" && !$plot_avg_data && 0 ) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"< tail $nl $case_id.%03d.plm\" using 1:4 title \"Deleterious (tribe $i)\" with $lorb lw 3, \"< tail $nl $case_id.%03d.plm\" using 1:5 title \"Favorable (tribe $i)\" with $lorb lw 3, \"< tail $nl $case_id.%03d.plm\" using 1:7 title \"Neutrals (tribe $i)\" with $lorb lw 3",$i,$i,$i);
	    if ( $i != $num_tribes ) { print FILEWRITE sprintf(", "); }
	}
	print FILEWRITE sprintf("\n");
    } elsif($combine_plots) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"< tail $nl ../$cid/$cid.000.plm\" using 1:4 title \"< tail $nl $cid\" with $lorb lw 3");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } else {
        if($os eq "windows") {
	   print FILEWRITE sprintf("plot \"%s.000.pls\" using 1:4 title \"Deleterious\" with $lorb lw 3, \"%s.000.pls\" using 1:5 title \"Favorable\" with $lorb lw 3, \"%s.000.plm\" using 1:7 title \"Neutrals\" with $lorb lw 3\n",$case_id,$case_id,$case_id);
        } else {
	   print FILEWRITE sprintf("plot \"< tail $nl %s.000.plm\" using 1:4 title \"Deleterious\" with $lorb lw 3, \"< tail $nl %s.000.plm\" using 1:5 title \"Favorable\" with $lorb lw 3, \"< tail $nl %s.000.plm\" using 1:7 title \"Neutrals\" with $lorb lw 3\n",$case_id,$case_id,$case_id);
        }
    }
    close FILEWRITE;
}
    
### write plot_tim
if($plot eq "tim" || $plot eq "all") {
    
    $myXLabel="Generation";
    $myYLabel="Time (s)";
    $myTitle=sprintf("Timing information per processor (%s)",$case_id);
    open(FILEWRITE, "> $case_dir/${case_id}_tim.gnu");

    $ofn=sprintf("%s_tim.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);

    printParameters(*FILEWRITE,0.15,0.86);

    print FILEWRITE sprintf("set y2range [0.0 : ]\n");

    print FILEWRITE sprintf("set y2label \"Offspring time (s)\"\n");
    print FILEWRITE sprintf("set y2tics \n");
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"$case_id.%03d.tim\" using 1:2 title \"Total (tribe $i)\" lw 3, \"$case_id.%03d.tim\" using 1:3 title \"Offspring (tribe $i)\" axis x1y2 lw 3, \"$case_id.$03d.tim\" using 1:4 title \"Selection (tribe $i)\" lw 3",$i,$i,$i);
	    if ( $i != $num_tribes ) { print FILEWRITE sprintf(", "); }
	}
	print FILEWRITE sprintf("\n");
    } elsif($combine_plots) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.tim\" using 1:2 title \"$cid\" with $lorb lw 3");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } else {
	print FILEWRITE sprintf("plot \"%s.000.tim\" using 1:2 title \"Total\" lw 3, \"%s.000.tim\" using 1:3 title \"Offspring\" axis x1y2 lw 3, \"%s.000.tim\" using 1:4 title \"Selection\" lw 3\n",$case_id,$case_id,$case_id);
    }
    close FILEWRITE;
}
    
### write plot_sel
if($plot eq "sel" || $plot eq "all") {
    
    $myXLabel="Fitness";
    $myYLabel="Number of Individuals";
    $myTitle=sprintf("Impact of Selection on Phenotypic Fitness (%s)",$case_id);
    open(FILEWRITE, "> $case_dir/${case_id}_sel.gnu");

    $ofn=sprintf("%s_sel.$format",$case_id);

    printInit(*FILEWRITE,$myTitle,$myXLabel,$myYLabel,$ofn);

    printParameters(*FILEWRITE,0.15,0.86);

    print FILEWRITE sprintf("set ytics nomirror\n");
    print FILEWRITE sprintf("set y2label \"After/before selection ratio\"\n");
    print FILEWRITE sprintf("set y2tics 0.1\n");
    #print FILEWRITE sprintf("set xtics 0.002\n");
    if($grid eq "on") { print FILEWRITE "set grid\n"; }

    if ($xmin ne "" || $xmax ne "") {
       print FILEWRITE sprintf("set xrange [ $xmin : $xmax]\n");
    } else {
       #print FILEWRITE sprintf("set xrange [-0.01 : 0.01]\n");
    }
    if ($ymin ne "" || $ymax ne "") {
       print FILEWRITE sprintf("set yrange [ $ymin : $ymax]\n");
    } else {
       #print FILEWRITE sprintf("set yrange [ : 0.1]\n");
    }
    if ($y2min ne "" || $y2max ne "") {
       print FILEWRITE sprintf("set y2range [ $ymin : $ymax]\n");
    } else {
       print FILEWRITE sprintf("set y2range [ 0.0 : 1.0 ]\n");
    }

    #print FILEWRITE sprintf("set logscale y\n");

    if ( $is_parallel eq "T" && !$plot_avg_data ) {
	print FILEWRITE sprintf("plot ");
	for ( $i = 1; $i <= $num_tribes; ++$i ) 
	{
	    print FILEWRITE sprintf("\"$case_id.%03d.sel\" using 1:2 title \"Before selection (tribe $i)\" with $lorb lw 3, \"$case_id.%03d.sel\" using 1:3 title \"After selection (tribe $i)\" with $lorb lw 3",$i,$i);
	    if ( $i != $num_tribes ) { print FILEWRITE sprintf(", "); }
	}
	print FILEWRITE sprintf("\n");
    } elsif($combine_plots) {
        ($uid,$cid) = split('/',$cases[0]);
	print FILEWRITE sprintf("plot \"../$cid/$cid.000.sel\" using 1:2 title \"Before selection\" with $lorb lw 3, ");
	for ( $i = 0; $i <= $#cases; ++$i )
	{
            ($uid,$cid) = split('/',$cases[$i]);
	    print FILEWRITE sprintf("\"../$cid/$cid.000.sel\" using 1:2 title \"After selection ($cid)\" with $lorb lw 3");
	    if ( $i != $#cases ) { print FILEWRITE sprintf(", "); }
	}
    } else {
	print FILEWRITE sprintf("plot \"%s.000.sel\" using 1:2 title \"Before selection\" with $lorb lw 3, \"%s.000.sel\" using 1:3 title \"After selection\" with $lorb lw 3, \"%s.000.sel\" using 1:4 title \"After/before ratio\" axis x1y2 with lines lw 3\n",$case_id,$case_id,$case_id);
    }
    close FILEWRITE;
}

sub printInit{

    my $fh = shift;
    my $myTitle = shift;
    my $myXLabel = shift;
    my $myYlabel = shift;
    my $ofn = shift;

    if ($format eq "eps") {
       $set_terminal="set terminal postscript eps color\n";
    } elsif ($os eq "windows") {
       $set_terminal="set terminal $format medium size 640 480\n";
    } elsif ($grayscale eq "on") {
       $set_terminal="set terminal $format transparent xffffff x000000 x202020 x404040 x606060 x808080 xA0A0A0 xC0C0C0 xE0E0E0\n";
    } else {
       $set_terminal="set terminal $format small\n";
    }

    print $fh sprintf($set_terminal);
    print $fh sprintf("set title \"%s\"\n",$myTitle);
    print $fh sprintf("set xlabel \"%s\"\n",$myXLabel);
    print $fh sprintf("set ylabel \"%s\"\n",$myYLabel);
    print $fh sprintf("set datafile missing \"NaN\"\n");
    print $fh sprintf("set output \"%s\"\n",$ofn);

}

sub printAnnotation{
    my $fh = shift;
    my $xp = shift;
    my $yp = shift;

    if($annotation) {
       print $fh sprintf("set label \"$annotation\" at screen %f,%f\n",$xp,$yp);
    }
}

sub printParameters{

    my $fh = shift;
    my $xp = shift;
    my $yp = shift;

    $dyp=0.04;

    printAnnotation($fh,$xp,0.9);

    if($pop_growth_model) {
       print $fh sprintf("set label \"Pop. growth rate = %f\" at screen %f,%f\n",$pop_growth_rate,$xp,$yp+$dyp);
    }
    if($pop_growth_model == 1) {
       print $fh sprintf("set label \"Starting pop. size = %d\" at screen %f,%f\n",$pop_size,$xp,$yp);
       print $fh sprintf("set label \"Max. pop size = %d\" at screen %f,%f\n",$num_generations,$xp,$yp-$dyp);
    } elsif($pop_growth_model == 2) {
       print $fh sprintf("set label \"Starting pop. size = %d\" at screen %f,%f\n",$pop_size,$xp,$yp);
       print $fh sprintf("set label \"Carrying capacity = %d\" at screen %f,%f\n",$num_generations,$xp,$yp-$dyp);
    } else {
       print $fh sprintf("set label \"Population size = %d\" at screen %f,%f\n",$pop_size,$xp,$yp);
       print $fh sprintf("set label \"Generations = %d\" at screen %f,%f\n",$num_generations,$xp,$yp-$dyp);
    }
    print $fh sprintf("set label \"Reproductive rate = %4.2f\" at screen %f,%f\n",$reproductive_rate,$xp,$yp-2*$dyp);
    print $fh sprintf("set label \"Mutation rate = %f\" at screen %f,%f\n",$mutn_rate,$xp,$yp-3*$dyp);
    print $fh sprintf("set label \"Fraction favorable = %f\" at screen %f,%f\n",$frac_fav_mutn,$xp,$yp-4*$dyp);
    print $fh sprintf("set label \"Heritability = %f\" at screen %f,%f\n",$heritability,$xp,$yp-5*$dyp);

    if ($selection_scheme == 1) {
        print $fh sprintf("set label \"Truncation selection\" at screen %f,%f\n",$xp,$yp-6*$dyp);
    } elsif ($selection_scheme == 2) {
        print $fh sprintf("set label \"Unrestricted probability selection\" at screen %f,%f\n",$xp,$yp-6*$dyp);
    } elsif ($selection_scheme == 3) {
        print $fh sprintf("set label \"Strict proportionality probibility selection\" at screen %f,%f\n",$xp,$yp-6*$dyp);
    } elsif ($selection_scheme == 4) {
        print $fh sprintf("set label \"Partial truncation selection\" at screen %f,%f\n",$xp,$yp-6*$dyp);
    } else {
        print $fh sprintf("set label \"Selection scheme not supported\" at screen %f,%f\n",$xp,$yp-6*$dyp);
    }

    if ( $is_parallel eq "T" ) {
        if ($migration_generations > 0) {
           $migration_exchange_rate=$num_indiv_exchanged/$migration_generations;
        }
        print $fh sprintf("set label \"Migration exchange rate = %f\" at screen %f,%f\n",$migration_exchange_rate,$xp,$yp-7*$dyp);
        if ( $plot_avg_data ) {
            print $fh sprintf("set label \"Note: data computed from %d tribes\" at screen %f,%f\n",$num_tribes,$xp,$yp-8*$dyp);
        }
    }

    if ($labels eq "off") { print $fh sprintf("unset label\n") };

}
