##############################################################################
#
# compute memory requirements in bytes
#
##############################################################################

if ( $pop_growth_model > 0 ) {
   # pass in max_pop_size through num_generations
   $my_pop_size = $num_generations;
} else {
   $my_pop_size = $pop_size;
}

$offspring_per_female = 2*$reproductive_rate;
$max_size = 0.55*$offspring_per_female*(1.-fraction_random_death)*$my_pop_size;
$n = $offspring_per_female*(1. - $fraction_random_death) + 0.999;

$mtmpi = $num_generations*$mutn_rate;

# compute static memory requirements

$base_mem = (42020 + 1630)*4;

if ( $is_parallel eq "T" ) {
   #$tpp = int($num_tribes/$num_procs);
   $num_nodes_reqd = int($num_tribes/$procs_per_node);
   $tpn = $procs_per_node;
   $mem_reqd = $tpn*$mtmpi*$num_indiv_exchanged*(1-$frac_fav_mutn)* 4; #dbuff
   $mem_reqd += $tpn*$mtmpi*$num_indiv_exchanged*$frac_fav_mutn   * 4; #fbuff
   $mem_reqd += $tpn*2*$num_linkage_subunits*$num_indiv_exchanged * 4; #cbuff1
   $mem_reqd += $tpn*2*$num_linkage_subunits*$num_indiv_exchanged * 4; #cbuff2
   $mem_reqd += $tpn*2*$num_linkage_subunits*$num_indiv_exchanged * 8; #lbuff
   $mem_reqd += $num_procs*$base_mem; # base static memory required
   #print sprintf("mem_reqd for parallel is: %7.1f MB<br>",$mem_reqd/1024/1024);
} else {
   $mem_reqd = $base_mem;            # base static memory required
}

$mem_reqd += $num_linkage_subunits*4*$max_size * 4; #lb_mutn_count
$mem_reqd += $num_linkage_subunits*4*$n * 4; #offsprng_lb_mutn_count
$mem_reqd += $num_linkage_subunits*2*$max_size * 8; #lb_fitness
$mem_reqd += $num_linkage_subunits*2*$n * 8; #offsprng_lb_fitness
$mem_reqd += $max_size * 8; #fitness
$mem_reqd += $max_size * 8; #fitness_score
$mem_reqd += $max_size * 4; #sorted_score
$mem_reqd += $max_size * 4; #available
$mem_reqd += $my_pop_size * 4; #replaced_by_offspring

# for polymorphism analysis
$mem_reqd += 1000000*4;

# compute dynamic memory requirements
$dyn_mem_reqd =  $max_size * 4 * (1-$frac_fav_mutn); #dmutn
$dyn_mem_reqd += $max_size * 4 * $frac_fav_mutn;     #fmutn
$dyn_mem_reqd += $n * 4 * (1-$frac_fav_mutn); #dmutn_offsprng
$dyn_mem_reqd += $n * 4 * $frac_fav_mutn;     #fmutn_offsprng

$mem_est = ($mtmpi*$dyn_mem_reqd + $mem_reqd)/1024/1024;

# compute memory available 

if ($os eq "windows") {

   open(MH,"systeminfo |");
   while(<MH>) {
      if($_ =~ "Available Physical Memory") {
         #print $_."<br>";
         ($buf1,$buf2) = split(/:/,$_);
         #print "buf1 = $buf1 . buf2 = $buf2<br>";
	 $buf2 =~ s/MB//;
	 $buf2 =~ s/,//;
         #print "buf2 = $buf2<br>";
	 $mem_available = ($buf2 - 50)*1024*1024;
	 #print "mem_available = $mem_available<br>";
      }
   }
   # in case systeminfo command fails use 256MB
   if(not $mem_available > 0) { 
      $mem_available = 256*1024*1024;
   }
} else {
   if ($is_parallel eq "T" ) {
      if ($tribal_competition) {
         # having problems allocating memory for tribal competition cases
         # one, because tribal competition over-allocates memory for each tribe
         $mem_available = $max_ram_per_node/$num_tribes/$num_tribes*1024*1024/10;
      } else {
         $mem_available = $max_ram_per_node/$num_tribes*1024*1024;
      }
   } else {
      $mem_available = $ram_per_job*1024*1024; # MB/processor
   }
}

# the c-engine uses 32% more RAM than the Fortran version
# so adjust mem_available accordingly
if ($engine eq "c") {
   $mem_available = int (0.68*$mem_available);
}

$total_allowed_memory = $mem_available;
if($os eq "windows") {
   $max_del_mutn_per_indiv = 1.2*$mtmpi;
   if ($max_del_mutn_per_indiv < 10000) {
      $max_del_mutn_per_indiv = 10000;
   }
} else {
   $max_tracked_mutn_per_indiv = ($total_allowed_memory - $mem_reqd)/$dyn_mem_reqd;
   $max_del_mutn_per_indiv = (1-$frac_fav_mutn)*$max_tracked_mutn_per_indiv+1000;
}

$max_fav_mutn_per_indiv = $frac_fav_mutn*$max_tracked_mutn_per_indiv+1000;

if($max_del_mutn_per_indiv < 0) {
   print "<em>WARNING: max_del_mutn_per_indiv < 0. Setting max_tracked_mutn_per_indiv = 20000.  This may cause unstable results.</em><br>";
   $max_del_mutn_per_indiv = 20000;
}

if($max_fav_mutn_per_indiv < 0) {
   print "<em>WARNING: max_fav_mutn_per_indiv < 0. Setting max_tracked_mutn_per_indiv = 20000.  This may cause unstable results.</em><br>";
   $max_fav_mutn_per_indiv = 20000;
}

# this is a bit of a hack for now
if($is_parallel eq "T" ) {
   $max_del_mutn_per_indiv = 10000;
   $max_fav_mutn_per_indiv = 10000;
}

if ($mem_reqd > $total_allowed_memory) {
   print "<font size=+2 color=red><hr>WARNING: there is not enough memory to run your case. To reduce required memory, do one or more of the following:<br> <ol><li>set tracking threshold (under \"computation\" tab) to a value greater than zero, but less than or equal to one <li> reduce population size <li> reduce mutation rate <li> reduce the number of generations <li> reduce the number of linkage blocks <li> uncheck \"track neutrals\" <li> reduce reproductive rate </ol> <hr> </font><br>";
   #die;
}

if ($os eq "windows") {
   print sprintf("estimated memory required: %d MB<br>", $mem_est);
   print sprintf("memory available: %d MB<br>",$mem_available/1024/1024);
   if($mem_est > $mem_available/1024/1024) {
      print "<p><font size=+2 color=red>WARNING: there may not be enough memory to complete your case.</font><br>";
      print "<font color=red><em>Try reducing the population size, offspring/female, generations, # linkage blocks, or increasing tracking threshold.</em></font><br>";
   }
}

$mem_reqd = $total_allowed_memory;

$mem_reqd=$mem_reqd/1024/1024;

