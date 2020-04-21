# This file will parse the mendel input file line by line, trying
# match string tokens in the input file to the proper variable names.
# By parsing the file like this, it can handle older mendel.in files.
# Since v1.9.3 the order of the string and value was reversed, so I have
# included a switch (omendelin) that can be set to 1 to indicate that
# this file is reading an old format type of file.

#$debug = 1;

if(-e $path) {
   open(SOURCE, "< $path");
} else { 
   print "ERROR: Couldn't open $path for reading.\n";
   die;
}

# for mendel.in file which have less than 70 lines, assume old v1.9.2 format
# for mendel.in files greater than 70 lines, assume it is namelist format

($wcl) = split(' ',`wc -l $path`);
$wcl *= 1;
#if($wcl < 70) {
#   $omendelin = 1;
#   #print "using old style<br>";
#} else {
   $omendelin = 0;
   #print "using namelist style<br>";
#}

while(<SOURCE>) {
   my $record = $_;
   chomp($record);

   #$record = <SOURCE>; 
   if ($omendelin) {
      #print $record;
      ($value,$label) = split(' ', $record);
   } else {
      ($label,$value) = split('=', $record);
      # following statement gets rid of comments after values
      # e.g. selection_scheme = 1 ! truncation_selection
      ($value,$comment) = split('!', $value);
      $value =~ s/,//g; # get rid of commas
      $value =~ s/'//g; # get rid of single quotes
      $value =~ s/ //g; # get rid of any spaces in strings
   }
   #print "$label = $value<br>";
   # convert anything that looks like a number from a string to a number
   # this tends to get rid of all the additional 0000's after the decimal
   if($value =~ /[0-9]/) { $value *= 1 };

   # older input files used Fortran .true. and .false. logicals
   # we must convert these to 1 and 0's respectively
   $value =~ s/\.true\./1/;
   $value =~ s/\.false\./0/;
   #print "$label = $value<br>"; 
   #$debug = true;

   if($label eq "") {
      $old_path = $value; 
      #print "label is nothing<br>";
   } elsif($label =~ /bottleneck_pop_size/) {
      $bottleneck_pop_size = $value;
      if($debug) { print "bottleneck_pop_size = $bottleneck_pop_size<br>"; }
   } elsif($label =~ /pop_size/) {
      $pop_size = $value;
      if($debug) { print "pop_size = $pop_size<br>"; }
   } elsif($label =~ /num_generations/) {
      $num_generations = $value;
      if($debug) { print "num_generations = $num_generations<br>"; }
   } elsif($label =~ /fitness_distrib_type/) {
      $fitness_distrib_type = $value;
      if($debug) { print "fitness_distrib_type = $fitness_distrib_type<br>"; }
   } elsif($label =~ /selection_scheme/) {
      $selection_scheme = $value;
      if($debug) { print "selection_scheme = $selection_scheme<br>"; }
   } elsif($label =~ /haploid_chromosome_number/) {
      $haploid_chromosome_number = $value;
      if($debug) { print "haploid_chromosome_number = $haploid_chromosome_number<br>"; }
   } elsif($label =~ /num_linkage_subunits/) {
      $num_linkage_subunits = $value;
      if($debug) { print "num_linkage_subunits = $num_linkage_subunits<br>"; }
   } elsif($label =~ /pop_growth_rate/) {
      $pop_growth_rate = $value;
      if($debug) { print "pop_growth_rate = $pop_growth_rate<br>"; }
   } elsif($label =~ /pop_growth_model/) {
      $pop_growth_model = $value;
      if($debug) { print "pop_growth_model = $pop_growth_model<br>"; }
   } elsif($label =~ /pop_growth_model/) {
      $pop_growth_model = $value;
      if($debug) { print "pop_growth_model = $pop_growth_model<br>"; }
   } elsif($label =~ /fraction_neutral/) {
      $fraction_neutral = $value;
      if($debug) { print "fraction_neutral = $fraction_neutral<br>"; }
   } elsif($label =~ /genome_size/) {
      $genome_size = sprintf("%.3e",$value);
      if($debug) { print "genome_size = $genome_size<br>"; }
   } elsif($label =~ /reproductive_rate/) {
      $reproductive_rate = $value;
      if($debug) { print "reproductive_rate = $reproductive_rate<br>"; }
   } elsif($label =~ /fraction_random_death/) {
      if($debug) { print "label = $label<br>"; }
      $fraction_random_death = $value;
   } elsif($label =~ /fraction_random_death/) {
      if($debug) { print "label = $label<br>"; }
      $fraction_random_death = $value;
      if($debug) { print "fraction_random_death = $fraction_random_death<br>"; }
   } elsif($label =~ /fraction_self_fertilization/) {
      $fraction_self_fertilization = $value;
      if($debug) { print "fraction_self_fertilization = $fraction_self_fertilization<br>"; }
   } elsif($label =~ /mutn_rate/) {
      $mutn_rate = $value;
      if($debug) { print "mutn_rate = $mutn_rate<br>"; }
   } elsif($label =~ /high_impact_mutn_fraction/) {
      $high_impact_mutn_fraction = $value;
      if($debug) { print "high_impact_mutn_fraction = $high_impact_mutn_fraction<br>"; }
   } elsif($label =~ /high_impact_mutn_threshold/) {
      $high_impact_mutn_threshold = $value;
      if($debug) { print "high_impact_mutn_threshold = $high_impact_mutn_threshold<br>"; }
   } elsif($label =~ /uniform_fitness_effect_del/) {
      $uniform_fitness_effect_del = $value;
      if($debug) { print "uniform_fitness_effect_del = $uniform_fitness_effect_del<br>"; }
   } elsif($label =~ /uniform_fitness_effect_fav/) {
      $uniform_fitness_effect_fav = $value;
      if($debug) { print "uniform_fitness_effect_fav = $uniform_fitness_effect_fav<br>"; }
   } elsif($label =~ /multiplicative_weighting/) {
      $multiplicative_weighting = $value;
      if($debug) { print "multiplicative_weighting = $multiplicative_weighting<br>"; }
   } elsif($label =~ /tracking_threshold/) {
      $tracking_threshold = $value;
      if($debug) { print "tracking_threshold = $tracking_threshold<br>"; }
   } elsif($label =~ /extinction_threshold/) {
      $extinction_threshold = $value;
      if($debug) { print "extinction_threshold = $extinction_threshold<br>"; }
   } elsif($label =~ /fraction_recessive/) {
      $fraction_recessive = $value;
      if($debug) { print "fraction_recessive = $fraction_recessive<br>"; }
   } elsif($label =~ /recessive_hetero_expression/) {
      $recessive_hetero_expression = $value;
      if($debug) { print "recessive_hetero_expression = $recessive_hetero_expression<br>"; }
   } elsif($label =~ /dominant_hetero_expression/) {
      $dominant_hetero_expression = $value;
      if($debug) { print "dominant_hetero_expression = $dominant_hetero_expression<br>"; }
   } elsif($label =~ /frac_fav_mutn/) {
      $frac_fav_mutn = $value;
      if($debug) { print "frac_fav_mutn = $frac_fav_mutn<br>"; }
   } elsif($label =~ /max_fav_fitness_gain/) {
      $max_fav_fitness_gain = $value;
      if($debug) { print "max_fav_fitness_gain = $max_fav_fitness_gain<br>"; }
   } elsif($label =~ /group_heritability/) {
      $group_heritability = $value;
      if($debug) { print "group_heritability = $group_heritability<br>"; }
   } elsif($label =~ /heritability/) {
      $heritability = $value;
      if($debug) { print "heritability = $heritability<br>"; }
   } elsif($label =~ /non_scaling_noise/) {
      $non_scaling_noise = $value;
      if($debug) { print "non_scaling_noise = $non_scaling_noise<br>"; }
   } elsif($label =~ /partial_truncation_value/) {
      $partial_truncation_value = $value;
      if($debug) { print "partial_truncation_value = $partial_truncation_value<br>"; }
   } elsif($label =~ /num_contrasting_alleles/) {
      $num_contrasting_alleles = $value;
      if($debug) { print "num_contrasting_alleles = $num_contrasting_alleles<br>"; }
   } elsif($label =~ /initial_contrasting_alleles/) {
      $num_contrasting_alleles = int($initial_contrasting_alleles);
      if($debug) { print "initial_contrasting_alleles = $initial_contrasting_alleles<br>"; }
   } elsif($label =~ /max_total_fitness_increase/) {
      $max_total_fitness_increase = $value;
      if($debug) { print "max_total_fitness_increase = $max_total_fitness_increase<br>"; }
   } elsif($label =~ /se_nonlinked_scaling/) {
      $se_nonlinked_scaling = $value;
      if($debug) { print "se_nonlinked_scaling = $se_nonlinked_scaling<br>"; }
   } elsif($label =~ /se_linked_scaling/) {
      $se_linked_scaling = $value;
      if($debug) { print "se_linked_scaling = $se_linked_scaling<br>"; }
   } elsif($label =~ /synergistic_epistasis/) {
      $synergistic_epistasis = $value;
      if($debug) { print "synergistic_epistasis = $synergistic_epistasis<br>"; }
   } elsif($label =~ /upload_mutations/) {
      $upload_mutations = $value;
      if($debug) { print "upload_mutations = $upload_mutations<br>"; }
   } elsif($label =~ /allow_back_mutn/) {
      $allow_back_mutn = $value;
      if($debug) { print "allow_back_mutn = $allow_back_mutn<br>"; }
   } elsif($label =~ /altruistic/) {
      $altruistic = $value;
      if($debug) { print "altruistic = $altruistic<br>"; }
   } elsif($label =~ /social_bonus_factor/) {
      $social_bonus_factor = $value;
      if($debug) { print "social_bonus_factor = $social_bonus_factor<br>"; }
   } elsif($label =~ /clonal_reproduction/) {
      $clonal_reproduction = $value;
      if($debug) { print "clonal_reproduction = $clonal_reproduction<br>"; }
   } elsif($label =~ /clonal_haploid/) {
      $clonal_haploid = $value;
      if($debug) { print "clonal_haploid = $clonal_haploid<br>"; }
   } elsif($label =~ /dynamic_linkage/) {
      $dynamic_linkage = $value;
      if($debug) { print "dynamic_linkage = $dynamic_linkage<br>"; }
   } elsif($label =~ /fitness_dependent_fertility/) {
      $fitness_dependent_fertility = $value;
      if($debug) { print "fitness_dependent_fertility = $fitness_dependent_fertility<br>"; }
   } elsif($label =~ /is_parallel/) {
      $is_parallel = $value;
      if($debug) { print "is_parallel = $is_parallel<br>"; }
   } elsif($label =~ /bottleneck_yes/) {
      $bottleneck_yes = $value;
      if($debug) { print "bottleneck_yes = $bottleneck_yes<br>"; }
   } elsif($label =~ /num_bottleneck_generations/) {
      $num_bottleneck_generations = $value;
      if($debug) { print "num_bottleneck_generations = $num_bottleneck_generations<br>"; }
   } elsif($label =~ /bottleneck_generation/) {
      $bottleneck_generation = $value;
      if($debug) { print "bottleneck_generation = $bottleneck_generation<br>"; }
   } elsif($label =~ /num_initial_fav_mutn/) {
      $num_initial_fav_mutn = $value;
      if($debug) { print "num_initial_fav_mutn = $num_initial_fav_mutn<br>"; }
   } elsif($label =~ /num_indiv_exchanged/) {
      $num_indiv_exchanged = $value;
      if($debug) { print "num_indiv_exchanged = $num_indiv_exchanged<br>"; }
   } elsif($label =~ /migration_generations/) {
      $migration_generations = $value;
      if($debug) { print "migration_generations = $migration_generations<br>"; }
   } elsif($label =~ /migration_model/) {
      $migration_model = $value;
      if($debug) { print "migration_model = $migration_model<br>"; }
   } elsif($label =~ /homogenous_tribes/) {
      $homogenous_tribes = $value;
      if($debug) { print "homogenous_tribes = $homogenous_tribes<br>"; }
   } elsif($label =~ /tribal_competition/) {
      $tribal_competition = $value;
      if($debug) { print "tribal_competition = $tribal_competition<br>"; }
   } elsif($label =~ /tc_scaling_factor/) {
      $tc_scaling_factor = $value;
      if($debug) { print "tc_scaling_factor = $tc_scaling_factor<br>"; }
   } elsif($label =~ /max_del_mutn_per_indiv/) {
      $max_del_mutn_per_indiv = $value;
      if($debug) { print "max_del_mutn_per_indiv = $max_del_mutn_per_indiv<br>"; }
   } elsif($label =~ /max_fav_mutn_per_indiv/) {
      $max_fav_mutn_per_indiv = $value;
      if($debug) { print "max_fav_mutn_per_indiv = $max_fav_mutn_per_indiv<br>"; }
   } elsif($label =~ /random_number_seed/) {
      $random_number_seed = $value;
      if($debug) { print "random_number_seed = $random_number_seed<br>"; }
   } elsif($label =~ /track_neutrals/) {
      $track_neutrals = $value;
      if($debug) { print "track_neutrals = $track_neutrals<br>"; }
   } elsif($label =~ /write_dump/) {
      $write_dump = $value;
      if($debug) { print "write_dump = $write_dump<br>"; }
   } elsif($label =~ /restart_case_id/) {
      $restart_case_id = $value;
      if($debug) { print "restart_case_id = $restart_case_id<br>"; }
   } elsif($label =~ /restart_case/) {
      $restart_case = $value;
      if($debug) { print "restart_case = $restart_case<br>"; }
   } elsif($label =~ /restart_dump_number/) {
      $restart_dump_number = $value;
      if($debug) { print "restart_dump_number = $restart_dump_number<br>"; }
   } elsif($label =~ /case_id/) {
      # if we name the following case_id, it may change the value
      # that is currently being used in some scripts which include
      # this file (e.g. plot_gnuplot.cgi)
      $my_case_id = $value;
      if($debug) { print "case_id = $case_id<br>"; }
   } elsif($label =~ /data_file_path/) {
      $data_file_path = $value;
      if($debug) { print "data_file_path = $data_file_path<br>"; }
   } elsif($label =~ /num_tribes/) {
      $num_tribes = $value;
      if($debug) { print "num_tribes = $num_tribes<br>"; }
   } elsif($label =~ /auto_malloc/) {
      $auto_malloc = $value;
      if($debug) { print "auto_malloc = $auto_malloc<br>"; }
   } elsif($label =~ /num_procs/) {
      $num_procs = $value;
      if($debug) { print "num_procs = $num_procs<br>"; }
   } elsif($label =~ /plot_avg_data/) {
      $plot_avg_data = $value;
      if($debug) { print "plot_avg_data = $plot_avg_data<br>"; }
   } elsif($label =~ /plot_allele_gens/) {
      $plot_allele_gens = $value;
      if($debug) { print "plot_allele_gens = $plot_allele_gens<br>"; }
   } elsif($label =~ /restart_append/) {
      $restart_append = $value;
      if($debug) { print "restart_append = $restart_append<br>"; }
   } elsif($label =~ /run_queue/) {
      $run_queue = $value;
      if($debug) { print "run_queue = $run_queue<br>"; }
   } elsif($label =~ /engine/) {
      $engine = $value;
      if($debug) { print "engine = $engine<br>"; }

###### DEPRECATED PARAMETERS ##################################################
   } elsif($label =~ /max_tracked_mutn_per_indiv/) {
      $max_del_mutn_per_indiv = $value;
      $max_fav_mutn_per_indiv = $value;
      if($debug) { print "max_del_mutn_per_indiv = $max_del_mutn_per_indiv<br>"; }
      if($debug) { print "max_fav_mutn_per_indiv = $max_fav_mutn_per_indiv<br>"; }
   } elsif($label =~ /new_mutn_per_offspring/) {
      $mutn_rate = $value;
      if($debug) { print "mutn_rate = $mutn_rate<br>"; }
   } elsif($label =~ /initial_alleles_mean_effect/) {
      $initial_alleles_mean_effect = $value;
      if($debug) { print "initial_alleles_mean_effect = $initial_alleles_mean_effect<br>"; }
      if ($initial_alleles_mean_effect > 0 ) {
         $max_total_fitness_increase = 
             ($initial_alleles_mean_effect - 
              $num_contrasting_alleles)*$num_contrasting_alleles;
      } else {
         $max_total_fitness_increase = 0;
      }
      if($debug) { print "max_total_fitness_increase = $max_total_fitness_increase<br>"; }
   } elsif($label =~ /uniform_fitness_effect/) {
      $uniform_fitness_effect_del = $value;
      if($debug) { print "uniform_fitness_effect_del = $uniform_fitness_effect_del<br>"; }
   } elsif($label =~ /organism_type/) {
      $organism_type = $value;
      if($debug) { print "organism_type = $organism_type<br>"; }
   } elsif($label =~ /linked_mutn_se_fraction/) {
      $se_nonlinked_scaling = $value;
      if($debug) { print "linked_mutn_se_fraction = $linked_mutn_se_fraction<br>"; } 
      print "WARNING: this value has changed meaning please check its value<br>";
   } elsif($label =~ /se_scaling_factor/) {
      $se_linked_scaling = $value;
      if($debug) { print "se_scaling_factor = $se_scaling_factor<br>"; }
      print "WARNING: this value has changed meaning please check its value<br>";
   } elsif($label =~ /offspring_per_female/) {
      $offspring_per_female = $value;
      $reproductive_rate = $offspring_per_female/2.;
      if($debug) { print "reproductive_rate = $reproductive_rate (converted from offspring_per_female)<br>"; }
   } elsif($label =~ /tc_scaling_exponent/) {
      $tc_scaling_exponent = $value;
      if($debug) { print "tc_scaling_exponent = $tc_scaling_exponent (this value no longer used)<br>"; }
   } elsif($label =~ /random_death_exponent/) {
      $random_death_exponent = $value;
      if($debug) { print "random_death_exponent = $random_death_exponent (this value is no longer used)<br>"; }
   } elsif($label =~ /mean_fitness_degradation/ ) {
      $uniform_fitness_effect = $value;
      if($debug) { 
         print "<font color=ref>deprecated value mean_fitness_degradation, converting to:</font><br>";
         print "&nbsp;&nbsp;&nbsp;--> uniform_fitness_effect = $uniform_fitness_effect<br>"; 
      }
   } elsif($label =~ /uniform_fitness_degradation/) {
      $uniform_fitness_effect = $value;
      if($debug) { 
         print "<font color=red>deprecated value uniform_fitness_degradation, converting to:</font><br>";
         print "&nbsp;&nbsp;&nbsp;--> uniform_fitness_effect = $uniform_fitness_effect<br>"; 
      }
   } elsif($label =~ /starting_haplotype_std_dev/) {
      $initial_contrasting_alleles = $value; 
      if($debug) { 
         print "<font color=red>deprecated value starting_haplotype_std_dev, converting to:</font><br>";
         print "&nbsp;&nbsp;&nbsp;--> initial_contrasting_alleles = $initial_contrasting_alleles<br>"; 
      }
   } else {
      #print "<font color=red>matching new label not found for $label</font><br>";
   }
}

# fill in settings not found in input file
if ($fraction_neutral eq "") { $fraction_neutral = 0.9; }
if ($genome_size eq "") { $genome_size = sprintf("%.3e",3.0e+08); }
if ($high_impact_mutn_fraction eq "") { $high_impact_mutn_fraction = 0.001; }
if ($high_impact_mutn_threshold eq "") { $high_impact_mutn_threshold = 0.1; }
if ($max_fav_fitness_gain eq "")   { $max_fav_fitness_gain = 0.001; }

if ($num_initial_fav_mutn eq "") { $num_initial_fav_mutn = 0; }

if ($uniform_fitness_effect_del eq "") { $uniform_fitness_effect_del = 0.001; }
if ($uniform_fitness_effect_fav eq "") { $uniform_fitness_effect_fav = 0.0001; }

if ($se_nonlinked_scaling eq "") { $se_nonlinked_scaling = 0.1; }
if ($se_linked_scaling eq "") { $se_linked_scaling = 100.; }

if ($partial_truncation_value eq "") { $partial_truncation_value = 0.5; }

if ($haploid_chromosome_number eq "") { $haploid_chromosome_number = 23; }
if ($bottleneck_generation eq "") { $bottleneck_generation = 1000; }
if ($bottleneck_pop_size eq "")   { $bottleneck_pop_size = 100; }
if ($num_bottleneck_generations eq "") { $num_bottleneck_generations = 500; }

if ($pop_growth_rate eq "") { $pop_growth_rate = 1.01; }

if ($homogenous_tribes eq "")     { $homogenous_tribes = "T"; }
if ($migration_model eq "")       { $migration_model = 1; }
if ($migration_generations eq "") { $migration_generations = 1; }
if ($num_indiv_exchanged eq "")   { $num_indiv_exchanged = 1; }
if ($tribal_competition eq "")    { $tribal_competition = 0; }
if ($tc_scaling_factor eq "")     { $tc_scaling_factor = 1; }
if ($group_heritability eq "")    { $group_heritability = 0.2; }
if ($altruistic eq "")            { $altruistic = "F"; }
if ($social_bonus_factor eq "")   { $social_bonus_factor = 1.0; }
if ($num_tribes eq "")            { $num_tribes = 2; }
if ($num_procs eq "")             { $num_procs = 2; }
if ($plot_avg_data eq "")         { $plot_avg_data = 1; }
if ($extinction_threshold eq "")  { $extinction_threshold = 0.0; }

if ($tracking_threshold eq "")    { $tracking_threshold = 0; }
if ($max_del_mutn_per_indiv eq "") { $max_del_mutn_per_indiv = 10000; }
if ($max_fav_mutn_per_indiv eq "") { $max_fav_mutn_per_indiv = 10000; }
if ($restart_append eq "")        { $restart_append = 1; }
if ($restart_dump_number eq "")   { $restart_dump_number = 1; }
if ($restart_case_id eq "")       { $restart_case_id = $case_id; }

#print "num_tribes: $num_tribes<br>";
#print "num_procs: $num_procs<br>";

close SOURCE;

#$done = "input parameters read correctly";
