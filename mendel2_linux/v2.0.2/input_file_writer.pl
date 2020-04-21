#!/usr/bin/perl
##############################################################################
#
# start.cgi -> this_file -> qsub.pl
#
# This file takes the Mendel inputs from the start.cgi page and             
# writes the mendel.in file.  It then allows the user to start
# the job via the qsub.pl script.  It also estimates the amount
# of memory which will be required to run the case.
#
##############################################################################

read(STDIN, $buffer,$ENV{'CONTENT_LENGTH'});
$buffer =~ tr/+/ /;
$buffer =~ s/\r/ /g;
$buffer =~ s/\n/ /g;
$buffer =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
$buffer =~ s/<!--(.|\n)*-->/ /g;
# following line will strip the \\ from windows $run_dir
#$buffer =~ tr/\\|[|]|<|!|"|$|{|}|*|#|'|>|||;|%/ /; 
#$unsupported = "\\|[|]|<|!|\"|$|{|}|*|#|'|>|||;|%/ /"; 

@pairs = split(/&/,$buffer);
foreach $pair(@pairs){
  ($key,$value)=split(/=/,$pair);
  $formdata{$key}.="$value";
}

require "./config.inc";

#######################################################################
# Assign parsed parameters to parameters
#######################################################################

# basic parameters
$case_id=$formdata{'case_id'};
$mutn_rate=$formdata{'mutn_rate'};
$frac_fav_mutn=$formdata{'frac_fav_mutn'};
$reproductive_rate=$formdata{'reproductive_rate'};
$pop_size=$formdata{'pop_size'};
$num_generations=$formdata{'num_generations'};

# mutations
$fitness_distrib_type=$formdata{'fitness_distrib_type'};
$fraction_neutral=$formdata{'fraction_neutral'};
$genome_size=$formdata{'genome_size'};
$high_impact_mutn_fraction=$formdata{'high_impact_mutn_fraction'};
$high_impact_mutn_threshold=$formdata{'high_impact_mutn_threshold'};
$max_fav_fitness_gain=$formdata{'max_fav_fitness_gain'};
$num_initial_fav_mutn=$formdata{'num_initial_fav_mutn'};
$uniform_fitness_effect_del=$formdata{'uniform_fitness_effect_del'};
$uniform_fitness_effect_fav=$formdata{'uniform_fitness_effect_fav'};

$fraction_recessive=$formdata{'fraction_recessive'};
$recessive_hetero_expression=$formdata{'recessive_hetero_expression'};
$dominant_hetero_expression=$formdata{'dominant_hetero_expression'};

$multiplicative_weighting=$formdata{'multiplicative_weighting'};
$synergistic_epistasis=$formdata{'synergistic_epistasis'};
$se_linked_scaling=$formdata{'se_linked_scaling'};
$se_nonlinked_scaling=$formdata{'se_nonlinked_scaling'};

$upload_mutations=$formdata{'upload_mutations'};
$allow_back_mutn=$formdata{'allow_back_mutn'};
$altruistic=$formdata{'altruistic'};
$social_bonus_factor=$formdata{'social_bonus_factor'};
$mutn_file_id=$formdata{'mutn_file_id'};

# selection
$fraction_random_death=$formdata{'fraction_random_death'};
$heritability=$formdata{'heritability'};
$non_scaling_noise=$formdata{'non_scaling_noise'};
$fitness_dependent_fertility=$formdata{'fitness_dependent_fertility'};
$selection_scheme=$formdata{'selection_scheme'};
$partial_truncation_value=$formdata{'partial_truncation_value'};

# population
$clonal_reproduction=$formdata{'clonal_reproduction'};
$clonal_haploid=$formdata{'clonal_haploid'};
$fraction_self_fertilization=$formdata{'fraction_self_fertilization'};

$num_contrasting_alleles=$formdata{'num_contrasting_alleles'};
$max_total_fitness_increase=$formdata{'max_total_fitness_increase'};

$dynamic_linkage=$formdata{'dynamic_linkage'};
$haploid_chromosome_number=$formdata{'haploid_chromosome_number'};
$num_linkage_subunits=$formdata{'num_linkage_subunits'};

$pop_growth_model=$formdata{'pop_growth_model'};
$pop_growth_rate=$formdata{'pop_growth_rate'};

$is_parallel=$formdata{'is_parallel'};
$num_indiv_exchanged=$formdata{'num_indiv_exchanged'};
$migration_generations=$formdata{'migration_generations'};
$migration_model=$formdata{'migration_model'};

$homogenous_tribes=$formdata{'homogenous_tribes'};
$tribal_competition=$formdata{'tribal_competition'};
$tc_scaling_factor=$formdata{'tc_scaling_factor'};
$random_death_exponent=$formdata{'random_death_exponent'};
$group_heritability=$formdata{'group_heritability'};

$bottleneck_yes=$formdata{'bottleneck_yes'};
$bottleneck_generation=$formdata{'bottleneck_generation'};
$bottleneck_pop_size=$formdata{'bottleneck_pop_size'};
$num_bottleneck_generations=$formdata{'num_bottleneck_generations'};

# computation
$max_del_mutn_per_indiv=$formdata{'max_del_mutn_per_indiv'};
$max_fav_mutn_per_indiv=$formdata{'max_fav_mutn_per_indiv'};
$track_neutrals=$formdata{'track_neutrals'};
$tracking_threshold=$formdata{'tracking_threshold'};
$extinction_threshold=$formdata{'extinction_threshold'};
$random_number_seed=$formdata{'random_number_seed'};
$write_dump=$formdata{'write_dump'};
$restart_case=$formdata{'restart_case'};
$restart_dump_number=$formdata{'restart_dump_number'};
$restart_case_id=$formdata{'restart_case_id'};
$restart_append=$formdata{'restart_append'};
$run_queue=$formdata{'run_queue'};
$engine=$formdata{'engine'};
$plot_avg_data=$formdata{'plot_avg_data'};
$plot_allele_gens=$formdata{'plot_allele_gens'};

# other
$description=$formdata{'description'};
$user_id=$formdata{'user_id'};
$quota=$formdata{'quota'};
$compute_node=$formdata{'compute_node'};
$auto_malloc=$formdata{'auto_malloc'};
#$num_procs=$formdata{'num_procs'};
$num_tribes=$formdata{'num_tribes'};
$version=$formdata{'version'};
$tribe_id=$formdata{'tribe_id'};

if ($os eq "windows") {
   $base_dir=$run_dir;
   $case_dir="$base_dir\\$case_id";
} else {
   $base_dir=$formdata{'run_dir'};
   $case_dir="$base_dir/$user_id/$case_id";
}

# correct a few parameters
if($migration_generations==0) {$migration_generations = 1;}
#$partial_truncation_value=$partial_truncation_value**0.25;
if ($dominant_hetero_expression eq "") {
   $dominant_hetero_expression = "1.0";
}
$num_procs=$num_tribes;


print "Content-type:text/html\n\n";

#print "$buffer";

#print "user_id=".$formdata{'user_id'}.", user_id=$user_id<br>";

#print "run_dir is $run_dir";

$run_dir_permissions = `ls -ld $run_dir`;
($run_dir_permissions) = split(' ', $run_dir_permissions);
$run_dir_permissions =~ s/\.//;

## ERROR checking
if(! -e $run_dir && $os eq "linux") { 
  print "<h2>ERROR: $run_dir does not exist.</h2>";
  print "<em>Contact the system administrator and request that they create the directory<br> and set the permissions to 777 (e.g. chmod 777 $run_dir)</em>";
  exit -1;
}

#if($run_dir_permissions ne "drwxrwxrwx" && $os eq "linux") {
#  print "<h2>ERROR: $run_dir is not set with the correct permissions.</h2>";
#  print "current setting is: $run_dir_permissions<br>";
#  print "<em>Contact the system administrator and request that they run the command:</em><p>";
#  print "<b>chmod 777 $run_dir</b>";
#  exit -1;
#}

if (lc($bottleneck_yes) eq "on") {
	$bottleneck_yes = "T";
} else {
	$bottleneck_yes = "F";
}

if (lc($homogenous_tribes) eq "on") {
	$homogenous_tribes = "T";
} else {
	$homogenous_tribes = "F";
}

if (lc($tribal_competition) eq "on") {
	$tribal_competition = "T";
} else {
	$tribal_competition = "F";
}

if (lc($dynamic_linkage) eq "on") {
	$dynamic_linkage = "T";
        $num_linkage_subunits = int($num_linkage_subunits/$haploid_chromosome_number)*
                      $haploid_chromosome_number;
        if($num_contrasting_alleles > $num_linkage_subunits) {
           $num_contrasting_alleles = $num_linkage_subunits;
           print "<em>WARNING: num_contrasting_alleles cannot be greater than ";
           print "num_linkage_subunits.<br>  num_contrasting_alleles has been ";
           print "adjusted to $num_contrasting_alleles.</em><br>"; 
        }
        if($num_linkage_subunits < 50) {
           print "<em>WARNING: dynamic linkage will most likely give unstable results ";
           print "for a low number of linkage blocks.  Please either: increase ";
           print "the number of linkage blocks, or turn dynamic linkage off.</em><br>";
        }
} else {
	$dynamic_linkage = "F";
}

if ($pop_size <= 50) {
   print "<em>WARNING: population size is too small for polymorphism analysis.</em><br>";
}

if (lc($synergistic_epistasis) eq "on") {
	$synergistic_epistasis = "T";
} else {
	$synergistic_epistasis = "F";
}

if (lc($upload_mutations) eq "on") {
	$upload_mutations = "T";
} else {
	$upload_mutations = "F";
}

if (lc($allow_back_mutn) eq "on") {
	$allow_back_mutn = "T";
} else {
	$allow_back_mutn = "F";
}

if (lc($altruistic) eq "on") {
	$altruistic = "T";
} else {
	$altruistic = "F";
}

if (lc($auto_malloc) eq "on") {
	$auto_malloc = 1;
} else {
	$auto_malloc = 0;
}

if($upload_mutations eq "T" && ! -e "$case_dir/${case_id}_mutn.in") {
   print "<h2>ERROR: upload_mutations checked but mutations file does not exist.</h2>";
   die;
}

if (lc($clonal_reproduction) eq "on") {
	$clonal_reproduction = "T";
} else {
	$clonal_reproduction = "F";
}
if (lc($clonal_haploid) eq "on") {
	$clonal_haploid = "T";
} else {
	$clonal_haploid = "F";
}

if (lc($is_parallel) eq "on") {
        $is_parallel = "T";
        if ($migration_generations > 0) {
           $migration_exchange_rate=$num_indiv_exchanged/$migration_generations;
        }
} else {
        $is_parallel = "F";
}

if (lc($fitness_dependent_fertility) eq "on") {
	$fitness_dependent_fertility = "T";
} else {
	$fitness_dependent_fertility = "F";
}

if (lc($track_neutrals) eq "on") {
	$track_neutrals = "T";
} else {
	$track_neutrals = "F";
}

if (lc($write_dump) eq "on") {
	$write_dump = "T";
} else {
	$write_dump = "F";
}

if (lc($restart_case) eq "on") {
	$restart_case = "T";
} else {
	$restart_case = "F";
}

if (lc($restart_append) eq "on") {
	$restart_append = "T";
} else {
	$restart_append = "F";
}

if (lc($plot_avg_data) eq "on") {
	$plot_avg_data = 1;
} else {
	$plot_avg_data = 0;
}

$version = "$version.$engine";

$case_id_length=length($case_id);

# qsub queue name requires first character to be alphabetic 
$case_id_first_char = substr($case_id,0,1);
if ($case_id_first_char =~ /[0-9]/ ) {
   print "<h2>ERROR: first character of Case ID cannot be integer.</h2>";
   die;
}

if ($case_id =~ /,/) {
   print "<h2>ERROR: case_id cannot contain ,</h2>";
   die;
} elsif ($case_id =~ /\!/) {
   print "<h2>ERROR: case_id cannot contain !</h2>";
   die;
}

if ($case_id_length != 6) {
#     print "Content-type:text/html\n\n";
     print "<h1>ERROR: Case ID must only be 6 characters!</h1>";
     exit(-1);
}

# don't let users start an old job - JCS request
# note: if ever undoing this make sure to uncomment
# section at bottom of qsub.pl which deletes old .png files
if (-e "$case_dir/mendel.in" && $homogenous_tribes eq "T") {
    print "<h1>ERROR: case $case_id already exists.</h1>";
    print "<h1><em>please use a new case_id</em></h1>";
    if ($os eq "linux") {
       system("touch $case_dir");
    }
    $case_already_exists = true;
    exit(-1); 
}

if($is_parallel eq "T" && $homogenous_tribes eq "F") {
   $file_name="mendel.in".$tribe_id;   
} else {
   $file_name="mendel.in";
}

# create run directory before any files are written
if ($os eq "windows") {
   system("mkdir $case_dir");
} else {
   system("mkdir -p $case_dir");
}

open(FILEWRITE, "> $case_dir/$file_name")
or print "ERROR: Cannot open $case_dir/$file_name"; 

# copy dump file from restart_case_id to current run directory

if ($restart_case eq "T") {
   if ($is_parallel eq "F") {
      $num_tribes = 1; 
   }
   
   for ($i=1; $i<=$num_tribes; $i++) {

      if($is_parallel eq "F") {
         # when not parallel there is only one restart file: caseid.000.dmp.1
         $ext = sprintf("%.3d",0); 
      } else {
         # when parallel, caseid.001.dmp.1 ~ caseid.NNN.dmp.1 (NNN = num_tribes)
         $ext = sprintf("%.3d",$i);
      }

      if ($os eq "windows") {
         $cpcmd="copy";
         $restart_file="$base_dir\\$restart_case_id\\$restart_case_id.$ext.dmp.$restart_dump_number";
         $hst_file="$base_dir\\$restart_case_id\\$restart_case_id.$ext.hst";
      } else {
         $cpcmd="cp";
         $restart_file="$base_dir/$user_id/$restart_case_id/$restart_case_id.$ext.dmp.$restart_dump_number";
         $hst_file="$base_dir/$user_id/$restart_case_id/$restart_case_id.$ext.hst";
      }

      if (-e "$restart_file") { 
         system("$cpcmd $restart_file $case_dir$slash$case_id.$ext.dmp.$restart_dump_number");
         if ($os eq "linux") {
            system("chmod 644 $case_dir/$case_id.$ext.dmp.$restart_dump_number");
         }
      } else {
         print "<em><b>ERROR: restart file $restart_file does not exist.</b></em><br>";
      }

      if ($restart_append) {
         if (-e "$hst_file") { 
            system("$cpcmd $hst_file $case_dir$slash$case_id.$ext.hst");
            if ($os eq "linux") {
               system("chmod 644 $case_dir/$case_id.$ext.hst");
            }
         }
      }
   }
} else {
  $restart_case_id = "test00";
}

# compute estimate of memory requirements for current run
# if auto_malloc is turned on, compute max_del_mutn_per_indiv
# and max_fav_mutn_per_indiv
if($auto_malloc) {
   require "./memory.inc";
}

### write description to file
if ($description ne "") {
   system("echo $description > $case_dir/README");
}

### write inputs to mendel.in file

# basic namelist
print FILEWRITE "&basic\n";
print FILEWRITE "\tcase_id = '$case_id'\n";
print FILEWRITE sprintf("\tmutn_rate = %f\n",$mutn_rate);
print FILEWRITE sprintf("\tfrac_fav_mutn = %f\n",$frac_fav_mutn);
print FILEWRITE sprintf("\treproductive_rate = %f\n",$reproductive_rate);
if ($pop_growth_model > 0) {
   print FILEWRITE sprintf("\tpop_size = %d ! starting pop_size\n",$pop_size);
   print FILEWRITE sprintf("\tnum_generations = %d ! max pop_size\n",$num_generations);
} else {
   print FILEWRITE sprintf("\tpop_size = %d\n",$pop_size);
   print FILEWRITE sprintf("\tnum_generations = %d\n",$num_generations);
}
print FILEWRITE "/\n\n";

# mutations namelist
print FILEWRITE "&mutations\n";
if ($fitness_distrib_type == 0) {
   print FILEWRITE sprintf("\tfitness_distrib_type = %d ! equal_mutation_effect\n",$fitness_distrib_type);
   print FILEWRITE sprintf("\tuniform_fitness_effect_del = %f\n",$uniform_fitness_effect_del);
   print FILEWRITE sprintf("\tuniform_fitness_effect_fav = %f\n\n",$uniform_fitness_effect_fav);
} elsif ($fitness_distrib_type == 1) {
   print FILEWRITE sprintf("\tfitness_distrib_type = %d ! exponential_mutation_effect\n",$fitness_distrib_type);
   print FILEWRITE sprintf("\tfraction_neutral = %f\n",$fraction_neutral);
   print FILEWRITE sprintf("\tgenome_size = %e\n",$genome_size);
   print FILEWRITE sprintf("\thigh_impact_mutn_fraction = %f\n",$high_impact_mutn_fraction);
   print FILEWRITE sprintf("\thigh_impact_mutn_threshold = %f\n",$high_impact_mutn_threshold);
   print FILEWRITE sprintf("\tmax_fav_fitness_gain = %f\n\n",$max_fav_fitness_gain);
} elsif ($fitness_distrib_type == 2) {
   print FILEWRITE sprintf("\tfitness_distrib_type = %d ! all_mutn_neutral\n",$fitness_distrib_type);
} elsif ($fitness_distrib_type == 3) {
   print FILEWRITE sprintf("\tfitness_distrib_type = %d ! bimodal\n",$fitness_distrib_type);
} else {
   print FILEWRITE sprintf("\tfitness_distrib_type = %d\n",$fitness_distrib_type);
}

#print FILEWRITE sprintf("\tnum_initial_fav_mutn = %d\n\n",$num_initial_fav_mutn);

print FILEWRITE sprintf("\tfraction_recessive = %f\n",$fraction_recessive);
print FILEWRITE sprintf("\trecessive_hetero_expression = %f\n",$recessive_hetero_expression);
print FILEWRITE sprintf("\tdominant_hetero_expression = %f\n\n",$dominant_hetero_expression);

print FILEWRITE sprintf("\tmultiplicative_weighting = %f\n",$multiplicative_weighting);

print FILEWRITE sprintf("\tsynergistic_epistasis = %s\n",$synergistic_epistasis);
if ($synergistic_epistasis eq "T") {
   print FILEWRITE sprintf("\tse_nonlinked_scaling = %e\n",$se_nonlinked_scaling);
   print FILEWRITE sprintf("\tse_linked_scaling = %e\n\n",$se_linked_scaling);
}

print FILEWRITE sprintf("\tupload_mutations = %s\n",$upload_mutations);
print FILEWRITE sprintf("\tallow_back_mutn = %s\n",$allow_back_mutn);

print FILEWRITE "/\n\n";

# selection namelist
print FILEWRITE "&selection\n";
print FILEWRITE sprintf("\tfraction_random_death = %f\n",$fraction_random_death);
print FILEWRITE sprintf("\theritability = %f\n",$heritability);
print FILEWRITE sprintf("\tnon_scaling_noise = %f\n",$non_scaling_noise);
print FILEWRITE sprintf("\tfitness_dependent_fertility = %s\n",$fitness_dependent_fertility);
if ($selection_scheme == 1) {
   print FILEWRITE sprintf("\tselection_scheme = %d ! truncation selection\n",$selection_scheme);
} elsif ($selection_scheme == 2) {
   print FILEWRITE sprintf("\tselection_scheme = %d ! unrestricted probability selection\n",$selection_scheme);
} elsif ($selection_scheme == 3) {
   print FILEWRITE sprintf("\tselection_scheme = %d ! strict proportional probability selection\n",$selection_scheme);
} elsif ($selection_scheme == 4) {
   print FILEWRITE sprintf("\tselection_scheme = %d ! partial truncation selection\n",$selection_scheme);
   print FILEWRITE sprintf("\tpartial_truncation_value = %f\n",$partial_truncation_value);
} else {
   print FILEWRITE sprintf("\tselection_scheme = %d ! not supported\n",$selection_scheme);
}
print FILEWRITE "/\n\n";

# population namelist
print FILEWRITE "&population\n";
print FILEWRITE sprintf("\tclonal_reproduction = %s\n",$clonal_reproduction);
print FILEWRITE sprintf("\tclonal_haploid = %s\n",$clonal_haploid);
print FILEWRITE sprintf("\tfraction_self_fertilization = %f\n\n",$fraction_self_fertilization);

print FILEWRITE sprintf("\tnum_contrasting_alleles = %d\n",$num_contrasting_alleles);
print FILEWRITE sprintf("\tmax_total_fitness_increase = %f\n\n",$max_total_fitness_increase);

print FILEWRITE sprintf("\tdynamic_linkage = %s\n",$dynamic_linkage);
if($dynamic_linkage eq "T") {
   print FILEWRITE sprintf("\thaploid_chromosome_number = %d\n",$haploid_chromosome_number);
}
print FILEWRITE sprintf("\tnum_linkage_subunits = %d\n\n",$num_linkage_subunits);

if($pop_growth_model == 0) {
  print FILEWRITE sprintf("\tpop_growth_model = %d ! fixed population\n",$pop_growth_model);
} elsif($pop_growth_model == 1) {
  print FILEWRITE sprintf("\tpop_growth_model = %d ! exponential\n",$pop_growth_model);
} elsif($pop_growth_model == 2) {
  print FILEWRITE sprintf("\tpop_growth_model = %d ! carrying capacity\n",$pop_growth_model);
} else {
  print FILEWRITE sprintf("\tpop_growth_model = %d\n",$pop_growth_model);
}

if($pop_growth_rate > 0) {
  print FILEWRITE sprintf("\tpop_growth_rate = %f\n\n",$pop_growth_rate);
}

print FILEWRITE sprintf("\tbottleneck_yes = %s\n",$bottleneck_yes);
if($bottleneck_yes eq "T") {
   print FILEWRITE sprintf("\tbottleneck_generation = %d\n",$bottleneck_generation);
   print FILEWRITE sprintf("\tbottleneck_pop_size = %d\n",$bottleneck_pop_size);
   print FILEWRITE sprintf("\tnum_bottleneck_generations = %d\n",$num_bottleneck_generations);
}
print FILEWRITE "/\n\n";

# substructure namelist
print FILEWRITE "&substructure\n";
print FILEWRITE sprintf("\tis_parallel = %s\n",$is_parallel);
if($is_parallel eq "T") {
   print FILEWRITE sprintf("\thomogenous_tribes = %s\n",$homogenous_tribes);
   print FILEWRITE sprintf("\tnum_indiv_exchanged = %d\n",$num_indiv_exchanged);
   print FILEWRITE sprintf("\tmigration_generations = %d\n",$migration_generations);
   print FILEWRITE sprintf("\tmigration_model = %d\n\n",$migration_model);

   print FILEWRITE sprintf("\ttribal_competition = %s\n",$tribal_competition);
   if($tribal_competition) {
      print FILEWRITE sprintf("\ttc_scaling_factor = %f\n",$tc_scaling_factor);
      print FILEWRITE sprintf("\tgroup_heritability = %f\n\n",$group_heritability);
   }

   print FILEWRITE sprintf("\taltruistic = %s\n",$altruistic);
   print FILEWRITE sprintf("\tsocial_bonus_factor = %f\n",$social_bonus_factor);
}
print FILEWRITE "/\n\n";

# computation namelist
print FILEWRITE "&computation\n";
print FILEWRITE sprintf("\tmax_del_mutn_per_indiv = %d\n",$max_del_mutn_per_indiv);
print FILEWRITE sprintf("\tmax_fav_mutn_per_indiv = %d\n",$max_fav_mutn_per_indiv);
print FILEWRITE sprintf("\ttrack_neutrals = %s\n",$track_neutrals);
print FILEWRITE sprintf("\ttracking_threshold = %e\n",$tracking_threshold);
print FILEWRITE sprintf("\textinction_threshold = %f\n",$extinction_threshold);
print FILEWRITE sprintf("\trandom_number_seed = %d\n",$random_number_seed);
print FILEWRITE sprintf("\twrite_dump = %s\n",$write_dump);
print FILEWRITE sprintf("\trestart_case = %s\n",$restart_case);
if($restart_case eq "T") {
   print FILEWRITE sprintf("\trestart_dump_number = %d\n",$restart_dump_number);
}
print FILEWRITE sprintf("\tplot_allele_gens = %d\n",$plot_allele_gens);

if ($os eq "windows") {
   print FILEWRITE sprintf("\tdata_file_path = '.\\'\n");
} else {
   print FILEWRITE sprintf("\tdata_file_path = '%s/'\n",$case_dir);
}
print FILEWRITE "/\n\n";

# misc parametters

print FILEWRITE "&interface\n";
print FILEWRITE sprintf("\tauto_malloc = %d\n",$auto_malloc);
if($is_parallel eq "T") {
   print FILEWRITE sprintf("\tnum_tribes = %d\n",$num_tribes);
   print FILEWRITE sprintf("\tnum_procs = %d\n",$num_procs);
   print FILEWRITE sprintf("\tplot_avg_data = %d\n",$plot_avg_data);
}
if($restart_case eq "T") {
   print FILEWRITE sprintf("\trestart_case_id = '%s'\n",$restart_case_id);
   print FILEWRITE sprintf("\trestart_append = %d\n",$restart_append);
}
print FILEWRITE sprintf("\trun_queue = '%s'\n",$run_queue);
print FILEWRITE sprintf("\tengine = '%s'\n",$engine);
#print FILEWRITE sprintf("%s",$tribe_id)."\t\ttribe_id\n";
# Note to compute an integer of tribe_id just multiply it times 1000.
# since it is taken as an integer, e.g. .001 is the id, 1 is the tribe number
print FILEWRITE "/\n";

# We need all the newline characters to keep the number of lines in the 
# file greater than 70, which is the threshold which delineates in
# input_file_parser.inc whether the mendel.in file is of the old style 
# format (<70 lines) or the new style format (>70 lines)
# This is a temporary fix and should be removed in the future.
print FILEWRITE "\n\n\n\n\n\n\n";

close FILEWRITE;

# make backup of mendel.in file
if($os eq "linux") {
   system("cd $case_dir; cp mendel.in mendel.in.bak"); 
}

# check disk quota
($disk_usage) = split(' ',`du -ms $run_dir/$user_id`);
if($disk_usage > $quota) {
   print "<h2>ERROR: User usage disk usage, ${disk_usage}kb has exceeded quota of $quota kb</h2>";
   print "<em>please delete some cases and try to rerun</em><p>";
   print "<em>mendel.in file was written, so the parameters can be started later from this case.</em>";
   print "<p>A list of cases for user $user_id is shown ordered by size in MB:</p>";
   print "<table>";
   open (MYEXE, "cd $run_dir/$user_id; du -ms * | sort -rn |");
   while (<MYEXE>){
      ($cid_size,$this_cid) = split(' ',$_);
      print "<tr><td>$this_cid</td><td>$cid_size MB</td></tr>";
   }
   print "</table>";
   die;
   close MYEXE;
}

# write plot files
require "./plot_gnuplot_recipes.cgi";

# compute mean fitness effect

$expn_scale = log($genome_size);
$gamma = log(-log($high_impact_mutn_threshold)/$expn_scale)
            /log($high_impact_mutn_fraction);

$sum = 0.;
$d2  = 1.;
for ($i = 1; $i <= 1000; $i++)
{
   $d1 = $d2;
   $d2 = exp(-$expn_scale*(0.001*$i)**$gamma);
   $sum = $sum + 0.0005*($d1 + $d2);
}

### start web output
print "<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML//EN\">\n";
print "<html> <head>\n";
print "<title>Mendel run parameters</title>\n";
print "<script language=\"javascript\">\n";
print "	function saveFile() {\n";
print "		document.execCommand('SaveAs','1',null);\n";
print "	}\n";
print "</script>\n";
print "</head>\n";
print "<body>\n";

# error checks

if ($restart_case eq "T") {
  print "<em>WARNING: cannot change pop_size during restart. ";
  print "Please manually check that<br> the current pop_size is the same ";
  print "as the previous case from which you are restarting.</em><br>";
}

if($reproductive_rate*(1. - $fraction_random_death) < 1.) {
  printf sprintf("<b>WARNING:</b> Input value of fraction_random_death<br> ");
  printf sprintf("         implies a fertility of less than 2 per female.<p>");
}

if($is_parallel eq "T" && $num_tribes < $num_procs ) {
  printf sprintf("<b>ERROR:</b> num_tribes < num_procs.<br>");
  printf sprintf("       you need at least 1 tribe per processor.<p>");
}

if($is_parallel eq "F" && $num_tribes > 2) {
  printf sprintf("<b>WARNING:</b> num_tribes > 2; however, parallel button is not checked.<p>");
}

$num_tribal_input_files = 0;
if($is_parallel eq "T" && $homogenous_tribes eq "F" && $num_tribes > 1) {
   print "<h1>Wrote mendel.in$tribe_id</h1>";
   system("cd $case_dir; cp $file_name mendel.in");
   for ($i=1; $i<=$num_tribes; $i++) {
       $tribe_input_file = "mendel.in.".sprintf("%.3d",$i);
       $tribe_input_file_path = "$case_dir/$tribe_input_file";
       if (! -e $tribe_input_file_path) {
          #print "ERROR: $tribe_input_file does not exist<br>";
          print "<h2><em>Need to write $tribe_input_file (click start)</em></h2>";
       } else {
          $num_tribal_input_files++;
       }
   }
   #print "num_tribal_input_files = $num_tribal_input_files<br>";
   if($num_tribal_input_files < $num_tribes){
       die;
   }
}

print <<End_of_Doc;
<h1>Verify input for $case_id:</h1>

<p>Please check that the following inputs are correct,
then click Execute.</p>

<form name="demo" method="POST" action="qsub.pl">
        <input type="hidden" name="version" value="$version">
	<input type="hidden" name="user_id" value="$user_id">
	<input type="hidden" name="case_id" value="$case_id">
	<input type="hidden" name="run_dir" value="$run_dir">
	<input type="hidden" name="pop_size" value="$pop_size">
	<input type="hidden" name="num_generations" value="$num_generations">
	<input type="hidden" name="reproductive_rate" value="$reproductive_rate">
	<input type="hidden" name="frac_fav_mutn" value="$frac_fav_mutn">
	<input type="hidden" name="mutn_rate" value="$mutn_rate">
	<input type="hidden" name="heritability" value="$heritability">
	<input type="hidden" name="is_parallel" value="$is_parallel">
	<input type="hidden" name="num_procs" value="$num_procs">
	<input type="hidden" name="run_queue" value="$run_queue">
	<input type="hidden" name="num_tribes" value="$num_tribes">
	<input type="hidden" name="mem_reqd" value="$mem_reqd">
	<input type="hidden" name="mem_available" value="$mem_available">
        <input type="hidden" name="restart_case" value="$restart_case">
        <input type="hidden" name="case_exists" value="$case_exists">
        <input type="hidden" name="engine" value="$engine">
	<input type="submit" value="Execute Simulation" accesskey="X">
</form>

<hr width=400 align=left>
End_of_Doc

if ($mutn_rate > 0) {
   $estimated_shutdown_linear = ($max_del_mutn_per_indiv+$max_fav_mutn_per_indiv)/$mutn_rate;
   $estimated_shutdown_quadratic = $estimated_shutdown_linear**2;
} 

if ($os eq "linux") {
   if($auto_malloc) {
      print sprintf("<em> %12d deleterious mutations/individual and %12d favorable mutations/individual are allowed for this run based on available memory.</em><br>",$max_del_mutn_per_indiv,$max_fav_mutn_per_indiv);
      print sprintf("<em>It is estimated that this limitation will be reached in %d generations<br>(based on linear increase of mutations).  The memory required for this run is %d MB.<br> The memory allocated to this run is %d MB</em><br>",$estimated_shutdown_linear,$mem_est,$mem_available/1024/1024);
   } else {
      print "<em>User has manually specified $max_del_mutn_per_indiv deleterious mutations/individual and $max_fav_mutn_per_indiv beneficial mutations.  Users can check the amount of currently available memory while the job is running, by clicking \"Status\" and then \"More\" and looking for the value labeled MemFree.<br></em>";
   }
   print "<pre>Description: $description</pre>";
   # or %d generations (based on quadratic increase)</em><br>",$estimated_shutdown_linear,$estimated_shutdown_quadratic);
}

print "<p>";
print "<pre>";

#print sprintf("%12d     max_del_mutn_per_indiv<br>",$max_del_mutn_per_indiv);
#print sprintf("%12d     max_fav_mutn_per_indiv<br>",$max_fav_mutn_per_indiv);
#print sprintf("%12d     max_size - pop_size<br>",$max_size - $pop_size);

print sprintf("\tgamma = %12.7f<br>",$gamma);
print sprintf("\tmean_fitness_effect = %12.7f<br>",$sum);

#print sprintf("%12.3e    1/favorable_threshold<br>",$inv_fav_threshold);
#print sprintf("%16.12f   lb_modulo<br>",$lb_modulo);
#print sprintf("%16.12f   rand_modulo<br>",$rand_modulo);
#print sprintf("%16.12f   inv_range<br>",$inv_range);
#print sprintf("%16.12f   expn_scale<br>",$expn_scale);

print "<hr width=400 align=left>";

#
# Display mendel.in file to screen
#
require "./more.cgi";

print "<hr width=400 align=left>";
print "</pre>";

print "</html>";
print "</body>";


