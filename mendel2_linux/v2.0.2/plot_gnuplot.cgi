#!/usr/bin/perl
##############################################################################
#
# list_cases.cgi -> with_selected.cgi -> this_file -> display results
#       toc.html ->                      this_file -> display results
#
# This file plots the results of the simulation by create PNG images
# and displaying the PNG images in HTML.
#
##############################################################################

require "./parse.inc";

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

require "./config.inc";

$selected_cases=$formdata{'selected_cases'};
@case = split(/:/,$selected_cases);

# turn buffering off for correct display order
#$| = 1;

print "<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML//EN\">\n";
print "<html> <head>\n";
print "<META HTTP-EQUIV=\"CACHE-CONTROL\" CONTENT=\"NO-CACHE\">\n";
print "<title>Mendel run parameters</title>\n";

# for tab pane
print "<script type=\"text/javascript\" src=\"/mendel/js/tabpane.js\"></script>";
print "<link type=\"text/css\" rel=\"StyleSheet\" href=\"/mendel/css/tab.webfx.css\">";

print "</head>\n";
print "<body>\n";

#print "selected_cases: $selected_cases<br>";

#for ( $i = 0; $i <= $#case; ++$i ) {
#   print "$i $case[$i]<br>";
#}

#$plot_when_mutns = 400;
$plot_when_mutns = 0;

print "<table><tr><td>";
if ($os eq "windows") {
   print "<em>If plots are incomplete, refresh browser (press F5 in IE).</em></p>";
}


print "<table><tr>";

if ($#cases eq "-1") {
   $ncases = 0;
} else {
   $ncases = $#cases;
}

$plot_width = 640;
$font_size = 4;

for ( $i = 0; $i <= $ncases; $i++ ) {

if ($#cases eq "-1") {
   $my_run_dir=$run_dir.$slash.$user_id.$slash.$case_id;
   $my_url_dir=$url_dir."/".$user_id."/".$case_id;
} else {
   ($user_id,$case_id) = split('/',$cases[$i]);
   $uidcid = $cases[$i];
   $my_run_dir=$run_dir.$slash.$uidcid;
   $my_url_dir=$url_dir."/".$uidcid;
}

#print "case_id is: $case_id<br>";
#print "run_dir is: $run_dir<br>";
#print "user_id is: $user_id<br>";

# Get the generation number use this in the image tag as image.png?$gen
# this forces the browser to not use the cached images

$cid = $case_id;
# the following fixes a problem in parallel cases when tribes die,
# however it seems to break the combine plots function
$path="$run_dir/$user_id/$case_id/mendel.in";
# problem with input_file_parser since new style of input file v1.9.3 
# following will set case_id to value in mendel.in... may cause problem
require "./input_file_parser.inc";

#if($is_parallel) {
#   $tribe = "001";  # if tribes die 000 will stop reporting
#} else {
#   $tribe = "000";
#}

open(FH,"$run_dir/$user_id/$cid/$cid.000.hst") or 
  die "ERROR: $cid.000.hst does not exist<br>";
while (<FH>) {
  ($gen,$fitness,$fitness_sd,$num_dmutns,$num_fmutns,$num_nmutns) = split(' ', $_, 9999);
}
close FH;

$num_dmutns = sprintf("%.1f",$num_dmutns);
$num_fmutns = sprintf("%.1f",$num_fmutns);
$num_nmutns = sprintf("%.1f",$num_nmutns);

if ($num_dmutns > $plot_when_mutns || $gen eq "#") {
   $dst="<a href=\"$my_url_dir/${cid}_dst.png?$gen\"> <img src=\"$my_url_dir/${cid}_dst.png?$gen\" width=$plot_width></a>";
   $dmutn="<a href=\"$my_url_dir/${cid}_indep_dmutn.png?$gen\"> <img src=\"$my_url_dir/${cid}_indep_dmutn.png?$gen\" width=$plot_width></a>";
} else {
   $dst="<a href=\"/mendel/images/nodata.html\" target=\"status\"><img src=\"/mendel/images/nodata.png\" width=$plot_width></a>";
   $dmutn="<a href=\"/mendel/images/nodata.html\" target=\"status\"><img src=\"/mendel/images/nodata.png\" width=$plot_width></a>";
}

if ($num_fmutns > $plot_when_mutns || $gen eq "#") {
   $fdst="<a href=\"$my_url_dir/${cid}_fdst.png?$gen\"> <img src=\"$my_url_dir/${cid}_fdst.png?$gen\" width=$plot_width></a>";
   $fmutn="<a href=\"$my_url_dir/${cid}_indep_fmutn.png?$gen\"> <img src=\"$my_url_dir/${cid}_indep_fmutn.png?$gen\" width=$plot_width></a>";
} else {
   $fdst="<a href=\"/mendel/images/nodata.html\" target=\"status\"><img src=\"/mendel/images/nodata.png\" width=$plot_width></a>";
   $fmutn="<a href=\"/mendel/images/nodata.html\" target=\"status\"><img src=\"/mendel/images/nodata.png\" width=$plot_width></a>";
}

if (-e "$run_dir/$user_id/$cid/$cid.000.dst") {
   open(MYEXE, "< $run_dir/$user_id/$cid/$cid.000.dst") 
        or die "can't open $file: $!";
   while (<MYEXE>){
      if (/deleterious$/) {
      ($buf,$expected_dmutn_recessive,$expected_dmutn_dominant) = split(' ', $_);
      }
      if (/favorable$/) {
      ($buf,$expected_fmutn_recessive,$expected_fmutn_dominant) = split(' ', $_);
      }
   }
   close MYEXE;
} else {
   print "ERROR: $cid.000.dst does not exist<br>";
}

$expected_dmutn_recessive = sprintf("%d",$expected_dmutn_recessive);
$expected_dmutn_dominant = sprintf("%d",$expected_dmutn_dominant);

if ($expected_fmutn_dominant < 1) {
   $expected_fmutn_recessive = sprintf("%.4f",$expected_fmutn_recessive);
   $expected_fmutn_dominant = sprintf("%.4f",$expected_fmutn_dominant);
} else {
   $expected_fmutn_recessive = sprintf("%d",$expected_fmutn_recessive);
   $expected_fmutn_dominant = sprintf("%d",$expected_fmutn_dominant);
}

# Get polymorphism statistics

if ($gen >= 1) {

  if (-e "$run_dir/$user_id/$cid/$cid.000.plm") {
     open(MYEXE, "< $run_dir/$user_id/$cid/$cid.000.plm") or die "can't open $file: $!";
     while (<MYEXE>) {
        if (/deleterious$/) {
           ($buf,$num_drare,$num_dpolymorphic,$num_dfixed) = split(' ', $_);
        }
        if (/favorable$/) {
           ($buf,$num_frare,$num_fpolymorphic,$num_ffixed) = split(' ', $_);
        }
        if (/neutral$/) {
           ($buf,$num_nrare,$num_npolymorphic,$num_nfixed) = split(' ', $_);
        }
     }
     close MYEXE;
  } else {
     print "ERROR: $cid.000.plm does not exist<br>";
  }

  $num_drare = sprintf("%d",$num_drare);
  $num_dpolymorphic = sprintf("%d",$num_dpolymorphic);
  $num_dfixed = sprintf("%d",$num_dfixed);

  $num_frare = sprintf("%d",$num_frare);
  $num_fpolymorphic = sprintf("%d",$num_fpolymorphic);
  $num_ffixed = sprintf("%d",$num_ffixed);

  $num_nrare = sprintf("%d",$num_nrare);
  $num_npolymorphic = sprintf("%d",$num_npolymorphic);
  $num_nfixed = sprintf("%d",$num_nfixed);
}

# Get the average linkage block effect
if (-e "$run_dir/$user_id/$cid/$cid.000.hap") {
   open(MYEXE, "< $run_dir/$user_id/$cid/$cid.000.hap") 
     or die "can't open $file: $!";
   while (<MYEXE>) {
      if (/avg_linkage_block_effect/) {
        ($buf,$buf,$buf,$avg_lb_effect) = split(' ', $_);
      }
      if (/lb_fitness_percent_positive/) {
        ($buf,$buf,$buf,$lb_fitness_percent_positive) = split(' ', $_);
      }
   }
   close MYEXE;
   } else {
      print "ERROR: $cid.000.hap does not exist<br>";
}

$avg_lb_effect= sprintf("%.3e",$avg_lb_effect);
$lb_fitness_percent_positive = sprintf("%.2f",$lb_fitness_percent_positive);

# Get the final selection threshold

if (-e "$run_dir/$user_id/$cid/$cid.000.thr") {
   open (MYEXE, "tail -1 $run_dir/$user_id/$cid/$cid.000.thr |");
   while (<MYEXE>){
      ($sgen,$dstd,$dstr,$fst) = split(' ', $_);
   }
   close MYEXE;
} else {
   print "ERROR: $cid.000.thr does not exist<br>";
}

# Get the selection effects

if (-e "$run_dir/$user_id/$cid/$cid.000.sel") {
   open(MYEXE, "< $run_dir/$user_id/$cid/$cid.000.sel") 
          or die "can't open $file: $!";
   while (<MYEXE>) {
     if (/pre.*selection.fitness/) {
        $pre_selection_fitness = $_;
     }
     if (/post.*selection.fitness/) {
        $post_selection_fitness = $_;
     }
   }
   close MYEXE;
   } else {
      print "ERROR: $cid.000.sel does not exist<br>";
}



#
# Run Gnuplot in batch mode to generate the plot images
#

$sed_cmd = "sed -i 's/Generations = [0-9].*[0-9]\"/Generations = $gen\"/'";

chdir $my_run_dir;
system("$sed_cmd ${cid}_fit_hst.gnu");
system("$gnuplot ${cid}_fit_hst.gnu");
system("$sed_cmd ${cid}_mutn_hst.gnu");
system("$gnuplot ${cid}_mutn_hst.gnu");
system("$sed_cmd ${cid}_tim.gnu");
system("$gnuplot ${cid}_tim.gnu");
system("$sed_cmd ${cid}_sel.gnu");
system("$gnuplot ${cid}_sel.gnu");
system("$sed_cmd ${cid}_thr.gnu");
system("$gnuplot ${cid}_thr.gnu");

# for PLM file, first read the generation from the first line of the
# *.plm file and change the plot to reflect that generation number
open (MYEXE, "<$cid.000.plm");
while (<MYEXE>){
   ($buf1,$buf2,$buf3,$generation) = split(' ', $_);
   if($buf2 =~ /generation/) { $plm_gen = $generation; }
}
close MYEXE;

$sed_plm_cmd = "sed -i 's/Generation.*\"/Generation = $plm_gen\"/'";
system("$sed_plm_cmd ${cid}_plm.gnu");
system("$gnuplot ${cid}_plm.gnu");

if ($num_dmutns > $plot_when_mutns) {
   system("$sed_cmd ${cid}_dst.gnu");
   system("$gnuplot ${cid}_dst.gnu");
}

if ($num_fmutns > $plot_when_mutns) {
   system("$sed_cmd ${cid}_fdst.gnu");
   system("$gnuplot ${cid}_fdst.gnu");
}

if ($num_dmutns > $plot_when_mutns) {
   system("$sed_cmd ${cid}_indep_dmutn.gnu");
   system("$gnuplot ${cid}_indep_dmutn.gnu");
}

if ($num_fmutns > $plot_when_mutns) {
   system("$sed_cmd ${cid}_indep_fmutn.gnu");
   system("$gnuplot ${cid}_indep_fmutn.gnu");
}

system("$sed_cmd ${cid}_hap.gnu");
system("$gnuplot ${cid}_hap.gnu");

#if ($num_dmutns < $plot_when_mutns || $num_fmutns < $plot_when_mutns) {
#  print "<em>Plots 2 & 3 will appear when mutations exceed $plot_when_mutns.</em><br>";
#}

#print "Run directory is: $my_run_dir<br>";
#print "URL directory is: $my_url_dir<br>";

# Limit the number of cases that can be plotted to 5
if($ncases > 4) {
   print "<h1>ERROR: too many cases.</h1>";
   exit;
}

#
# Output the plots to screen
#

print "<td width=$plot_width valign=top>";
#print "<h1>$cid</h1>";

print <<End_Print;
<div class="tab-pane" id="tab-pane-1">

<div class="tab-page">
<h2 class="tab">mutations</h2>

<font size="$font_size">
<a class="plain" href="/mendel/$version/help.html#plot1" target="status">
   1. Generational History: average mutations</a></font>
<table>
<tr>
<td width=$plot_width><center><em>updated every generation</em></center></td>
<td align=right>
<form method="post" action="./plot_gnuplot_modify.cgi">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="cid" value="$cid">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="plot" value="mutn_hst">
<input type="submit" value="Modify plot">
</form>
</td><td>
<form name="list_files" method="post" action="./more.cgi" target="_blank">
<input type="hidden" name="case_id" value="$cid">
<input type="hidden" name="file_name" value="${cid}.000.hst">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="user_id" value="$user_id">
<input type="submit" value="Show Data">
</form>
</td>
</tr>
</table>

<a href="$my_url_dir/${cid}_mutn_hst.png?$gen"> <img src="$my_url_dir/${cid}_mutn_hst.png?gen" width=$plot_width></a>
</div>

<div class="tab-page">
<h2 class="tab">fitness</h2>
<font size="$font_size">
<a class="plain" href="/mendel/$version/help.html#plot2" target="status">
   2. Generational History: fitness </a></font><br>

<table>
<tr>
<td width=$plot_width><center><em>updated every generation</em></center></td>
<td align=right>
<form method="post" action="./plot_gnuplot_modify.cgi">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="cid" value="$cid">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="plot" value="fit_hst">
<input type="submit" value="Modify plot">
</form>
</td><td>
<form name="list_files" method="post" action="./more.cgi" target="_blank">
<input type="hidden" name="case_id" value="$cid">
<input type="hidden" name="file_name" value="${cid}.000.hst">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="user_id" value="$user_id">
<input type="submit" value="Show Data">
</form>
</td>
</tr>
</table>

<a href="$my_url_dir/${cid}_fit_hst.png?$gen"> <img src="$my_url_dir/${cid}_fit_hst.png?gen" width=$plot_width></a> 
</div>
End_Print

#if($num_dmutns >= $plot_when_mutns || $num_fmutns >= $plot_when_mutns) {
if($fitness_distrib_type > 0) {
print <<End_Print;
<div class="tab-page">
<h2 class="tab">distribution</h2>
<font size="$font_size">
<a class="plain" href="/mendel/$version/help.html#plot3" target="status">
   3. Distribution of accumulated mutations</a></font>
<table><tr>
<td width=$plot_width><center><em>updated every 20 generations</em></center></td>
<td align=right>
<form method="post" action="./plot_gnuplot_modify.cgi">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="cid" value="$cid">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="plot" value="ddst">
<input type="submit" value="Modify Deleterious plot">
</form>
</td><td>
<form method="post" action="./plot_gnuplot_modify.cgi">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="cid" value="$cid">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="plot" value="fdst">
<input type="submit" value="Modify Favorable plot">
</form>
</td><td>
<form name="list_files" method="post" action="./more.cgi" target="_blank">
<input type="hidden" name="case_id" value="$cid">
<input type="hidden" name="file_name" value="${cid}.000.dst">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="user_id" value="$user_id">
<input type="submit" value="Show Data">
</form>
</td>
</tr></table>
<!--
$expected_dmutn_dominant *
$expected_fmutn_dominant *
-->
<font size="$font_size">
<a class="plain" href="/mendel/$version/help.html#plot3" target="status">Deleterious</a>
$dst <br>
<a class="plain" href="/mendel/$version/help.html#plot3b" target="status">Beneficial</a>
<br>
$fdst
</font>
</div>

<div class="tab-page">
<h2 class="tab">threshold</h2>
<font size="$font_size">
<a class="plain" href="/mendel/$version/help.html#plot4" target="status">
   4. Selection threshold history</a></font>
<table><tr>
<td width=$plot_width><center><em>updated every 20 generations</em></center></td>
<td>
<form method="post" action="./plot_gnuplot_modify.cgi">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="cid" value="$cid">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="plot" value="thr">
<input type="submit" value="Modify plot">
</form>
</td><td>
<form name="list_files" method="post" action="./more.cgi" target="_blank">
<input type="hidden" name="case_id" value="$cid">
<input type="hidden" name="file_name" value="${cid}.000.thr">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="user_id" value="$user_id">
<input type="submit" value="Show Data">
</form>
</td>
</tr></table>

Deleterious threshold at generation $sgen = $dstd<br>
Favorable threshold at generation $sgen = $fst<br>

<a href="$my_url_dir/${cid}_thr.png?$gen"> <img src="$my_url_dir/${cid}_thr.png?$gen" width=$plot_width></a><br>

</div>

<div class="tab-page">
<h2 class="tab">near-neutrals</h2>
<font size="$font_size">
<a class="plain" href="/mendel/$version/help.html#plot5" target="status">
5. Distribution of near-neutrals</a></font>

<table><tr>
<td width=$plot_width><center><em>updated every 20 generations</em></center></td>
<td>
<form method="post" action="./plot_gnuplot_modify.cgi">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="cid" value="$cid">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="plot" value="dmutn">
<input type="submit" value="Modify deleterious plot">
</form>
</td><td>
<form method="post" action="./plot_gnuplot_modify.cgi">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="cid" value="$cid">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="plot" value="fmutn">
<input type="submit" value="Modify beneficial plot">
</form>
</td><td>
<form name="list_files" method="post" action="./more.cgi" target="_blank">
<input type="hidden" name="case_id" value="$cid">
<input type="hidden" name="file_name" value="${cid}.000.hap">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="user_id" value="$user_id">
<input type="submit" value="Data">
</form>
</td></tr></table>

<h2>Deleterious</h2>
 $dmutn <br> 
<h2>Beneficial</h2>
 $fmutn
</div>

<div class="tab-page">
<h2 class="tab">linkage</h2>
<font size="$font_size">
<a class="plain" href="/mendel/$version/help.html#plot6" target="status">
   6. Linkage block effects</a></font>
<table>
<tr>
<td width=$plot_width><center><em>updated every 20 generations</em></center></td>
<td>
<form method="post" action="./plot_gnuplot_modify.cgi">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="cid" value="$cid">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="plot" value="hap">
<input type="submit" value="Modify plot">
</form>
</td><td>
<form name="list_files" method="post" action="./more.cgi" target="_blank">
<input type="hidden" name="case_id" value="$cid">
<input type="hidden" name="file_name" value="${cid}.000.hap">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="cols" value="1:3">
<input type="submit" value="Data">
</form>
</td>
</tr>
</table>

Average linkage block effect = $avg_lb_effect<br>
Linkage blocks which have a positive fitness value = $lb_fitness_percent_positive% <br>

<a href="$my_url_dir/${cid}_hap.png?$gen"> <img src="$my_url_dir/${cid}_hap.png?$gen" width=$plot_width></a><br>
</div>

<div class="tab-page">
<h2 class="tab">selection</h2>
<font size="$font_size">
<a class="plain" href="/mendel/$version/help.html#plot7" target="status">
   7. Selection effects</a></font>
<table>
<tr>
<td width=$plot_width><center><em>updated every 20 generations</em></center></td>
<td>
<form method="post" action="./plot_gnuplot_modify.cgi">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="cid" value="$cid">
<input type="hidden" name="user_id" value="$user_id">
<input type="hidden" name="plot" value="sel">
<input type="submit" value="Modify plot">
</form>
</td><td>
<form name="list_files" method="post" action="./more.cgi" target="_blank">
<input type="hidden" name="case_id" value="$cid">
<input type="hidden" name="file_name" value="${cid}.000.sel">
<input type="hidden" name="run_dir" value="$run_dir">
<input type="hidden" name="user_id" value="$user_id">
<input type="submit" value="Data">
</form>
</td>
</tr>
</table>

$pre_selection_fitness<br>
$post_selection_fitness<br>

<a href="$my_url_dir/${cid}_sel.png?$gen"> <img src="$my_url_dir/${cid}_sel.png?$gen" width=$plot_width></a><br>

</div>
End_Print
}

#print "<h2>track_neutrals: $track_neutrals</h2>";

#if($track_neutrals eq "T" && $fitness_distrib_type > 0) {
if($fitness_distrib_type > 0) {
   if($gen >= 1 && 
     ($num_dmutns > $plot_when_mutns || $num_fmutns > $plot_when_mutns)) {
      print "<div class=\"tab-page\">";
      print "<h2 class=\"tab\">alleles</h2>";
      if($upload_mutations eq "T") {
         print "<legend><font size=\"$font_size\"><a class=\"plain\" href=\"/mendel/$version/help.html#plot8\" target=\"status\">8. Allele Frequency of Uploaded Mutations</a></font></legend>";
      } else {
         print "<legend><font size=\"$font_size\"><a class=\"plain\" href=\"/mendel/$version/help.html#plot8\" target=\"status\">8. Allele Frequency</a></font></legend>";
      }
      print "<table><tr><td valign=top width=$plot_width>";
      print "<em>updated as specified by user in interface<br> (default every 1000 generations)</em><br>";
      print "</td><td>";
      print "<form method=\"post\" action=\"plot_gnuplot_modify.cgi\">";
      print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
      print "<input type=\"hidden\" name=\"case_id\" value=\"$cid\">";
      print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
      print "<input type=\"hidden\" name=\"plot\" value=\"plm\">";
      print "<input type=\"submit\" value=\"Modify plot\">";
      print "</form>";
      print "</td><td>";
      print "<form name=\"list_files\" method=\"post\" action=\"more.cgi\" target=\"_blank\">";
      print "<input type=\"hidden\" name=\"case_id\" value=\"$cid\">";
      print "<input type=\"hidden\" name=\"file_name\" value=\"${cid}.000.plm\">";
      print "<input type=\"hidden\" name=\"run_dir\" value=\"$run_dir\">";
      print "<input type=\"hidden\" name=\"user_id\" value=\"$user_id\">";
      print "<input type=\"submit\" value=\"Data\">";
      print "</form>";
      print "</td>";
      print "</tr></table>";

      print "<table>";
      print "<tr><th align=left>Number of alleles</th> <th width=150>Deleterious</th> <th width=150>Favorables</th> <th align=center>Neutrals</th> </tr>";
      print "<tr><td>very rare (0-1%)</td> <td align=center>$num_drare</td> <td align=center>$num_frare</td> <td align=center>$num_nrare</td> </tr>";
      print "<tr><td>polymorphic (1-99%)</td> <td align=center>$num_dpolymorphic</td> <td align=center>$num_fpolymorphic</td> <td align=center>$num_npolymorphic</td> </tr>";
      print "<tr><td>fixed or very nearly fixed (99-100%)</td> <td align=center>$num_dfixed</td> <td align=center>$num_ffixed</td> <td align=center>$num_nfixed</td> </tr>";
      print "</table>";
      $mnp = 1000000;
      if($num_drare >= $mnp || $num_frare >= $mnp) { 
	 print "<center><font color=red>WARNING: exceeded limit for polymorphism analysis. Data is not complete.</font></center>"; 
      }

      print "<a href=\"$my_url_dir/${cid}_plm.png?$gen\"> <img src=\"$my_url_dir/${cid}_plm.png?$gen\" width=$plot_width></a><br>";
      print "</div>";
   }
   print "</div>";
   print "</td>";
   print "</tr>";
   }
}
print "<script type=\"text/javascript\">";
print "setupAllTabs();";
print "</script>";

print "<table border=0 width=$plot_width>";
print "<tr bgcolor=dfdfdf> <td>Generation</td> <td>Fitness</td> <td>avg # del mutns</th> <td>avg # fav mutns</td> <td>avg # neu mutns</td> </tr>";
print "<tr> <td>$gen</td> <td>$fitness</td> <td>$num_dmutns</th> <td>$num_fmutns</td> <td>$num_nmutns</td> </tr>";
print "</table>";
print "<br>";

print <<End_of_Doc;
</tr></table>
</html>
</body>
End_of_Doc
