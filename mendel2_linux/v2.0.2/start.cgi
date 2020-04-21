#!/usr/bin/perl
##############################################################################
#
# toc.php -> this_file -> input_file_writer.pl
#
# This file creates a form for the user to input the biological
# parameters and then passes them to input_file.cgi which
# creates the mendel.in file required to run the program.
#
# If no case_id is given, the file reads in the default mendel.in
# file located in the same directory.  If a case_id is provided,
# that mendel.in file is used instead.
#
# Special hidden functions are built-in to run the Crow case
# if case_id is set to "crow" when the start button is pressed.
#
##############################################################################

#require ".//usr/lib/perl5/vendor_perl/5.6.1/HTTP/BrowserDetect.pm";
#my $mybrowser = new HTTP::BrowserDetect($user_agent_string);
#$browser = $mybrowser->browser_string();

require "./parse.inc";
require "./config.inc";

# this is for starting a case from list_cases.cgi
if ($case_id eq "") { 
   $case_id=$formdata{'case_id'}; 
   $user_id=$formdata{'user_id'};
   # in case case is in uid/cid form (e.g. john/test01)
   if($case_id =~ /%2F/) {
     ($case_user_id,$case_id)=split(/%2F/,$case_id);
   } else {
      $case_user_id = $user_id;
   }
   $version=$formdata{'version'};
   $quota=$formdata{'quota'};
   # ensure users have at least 512 MB
   if($quota eq "" or $quota < 512) { $quota = 512; }
   print "Content-type:text/html\n\n";
   #print "quota is $quota<br>";
} else {
   $case_user_id = $user_id;
}
$browser=$formdata{'browser'};
$screenresx=$formdata{'screenresx'};
$screenresy=$formdata{'screenresy'};
$template=$formdata{'template'};
$tribe_id=$formdata{'tribe_id'};

if($user_id eq "" && $os eq "linux") {
   print "<h1>ERROR: you must login first.</h1>";
   print "<h1><a href=\"/mendel/login/index.php\" target=\"_top\">Go to login page</a></h1>";
   die;
}

## Uncomment following line to test interface 
## as if it was running under Windows
#$os = "windows";

# turn buffering off for correct display order
$| = 1;

print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\">\n";
print "<html lang=en>\n";
print "<head>\n";
print "<title>Mendel - web interface</title>\n";

print <<ZzZzZz;
<script type="text/javascript" src="/mendel/js/tabpane.js"></script>
<script type="text/javascript" src="/mendel/js/general.js"></script>
<link type="text/css" rel="StyleSheet" href="/mendel/css/tab.webfx.css" />
<link type="text/css" rel="StyleSheet" href="/mendel/css/style2.css" />

<script type="text/javascript">
function fxn_init() {
   fxn_tribes($max_tribes);
   fxn_fitness_distrib_type_init();
   //fxn_selection_init();
   // assign values that were parsed from input file to JS vars
   // we need to store these, in case we need access them later
   tracking_threshold = dmi.tracking_threshold.value;
   compute_u();

   // properly grey out items
   fxn_allocate_memory();
   fxn_combine_mutns_able();
   fxn_dynamic_linkage_able();
   fxn_bottleneck_able();
   fxn_restart_case_able();
   fxn_is_parallel();
   fxn_migration();
   fxn_clone();
   fxn_fraction_neutral();
   fxn_track_neutrals();
   fxn_track_all_mutn();
   fxn_init_tracking_threshold();
   show_hide_mutation_upload_form();
   //document.getElementById("tribediv").style.display = "none";
   dmi.case_id.focus();
   // this is in tabpane.js
   setupAllTabs();
}

function fxn_set_caseid() {
        parent.frames.contents.caseidform.case_id.value = 
           dmi.case_id.value;
}

function set_random_caseid() {
        var c; var n;
        //var s=65; n=25; //for all caps
        var s=97; n=25;//for all lowercase
        c = String.fromCharCode(s + Math.round(Math.random() * n));
        c += String.fromCharCode(s + Math.round(Math.random() * n));
        c += String.fromCharCode(s + Math.round(Math.random() * n));
        c += String.fromCharCode(s + Math.round(Math.random() * n));
        c += String.fromCharCode(s + Math.round(Math.random() * n));
        c += String.fromCharCode(s + Math.round(Math.random() * n));
        dmi.case_id.value = c;
}

function fxn_set_this_caseid() {
	dmi.case_id.focus();
        // get string from control panel
        var a = parent.frames.contents.caseidform.case_id.value;
        // get just the case_id (in case of format uid/caseid)
        var b = a.substring(a.length-6);
        // get the last three characters
        var c = b.substring(3);
        c = String.fromCharCode(97 + Math.round(Math.random() * 25));
        c += String.fromCharCode(97 + Math.round(Math.random() * 25));
        c += String.fromCharCode(97 + Math.round(Math.random() * 25));
        var d = b.substring(0,3); 
        var e = d + c;
        if(dmi.caseid_cb.checked) {
           if(dmi.case_id.value == "") {
              set_random_caseid();
              dmi.case_id.select();
           } else {
              dmi.case_id.value = e;
           }          
        } else {
           dmi.case_id.value = "";
        }
}

function fxn_opf(x, min, max) {
   var opf = 2*x;
   status("offspring_per_female = " + opf);
   check_value(x, min, max);
}

function alpha_warning() {
   status("WARNING: this function is experimental and largely untested.");
}

function check_value(x, min, max) {
   // make sure values are numbers not strings
   min *= 1;
   max *= 1;
   if(x < min || x > max || isNaN(x)) {
      alert("WARNING: Value must be between " + min + " and " + max);
      // status("WARNING: Value must be between " + min + " and " + max );
   }
}

function fxn_synergistic_epistasis() {
        fxn_synergistic_epistasis_able();
        if(dmi.synergistic_epistasis.checked) {
	   if (dmi.se_nonlinked_scaling.value = "0.0"){
              dmi.se_nonlinked_scaling.value = "0.1";
           }
        }
}

function fxn_synergistic_epistasis_able() {
	if(dmi.synergistic_epistasis.checked) {
           dmi.se_nonlinked_scaling.disabled = false;
           dmi.se_linked_scaling.disabled = false;
	} else {
	   dmi.se_nonlinked_scaling.disabled = true;
	   dmi.se_linked_scaling.disabled = true;
	}
}
function fxn_synergistic_epistasis_disable() {
        dmi.se_nonlinked_scaling.disabled = true;
        dmi.se_linked_scaling.disabled = true;
}

function fxn_combine_mutns() {
        fxn_combine_mutns_able();
	if (dmi.combine_mutns.checked) {
	    dmi.multiplicative_weighting.value = 0.5;
	    dmi.multiplicative_weighting.select();
            window.scrollBy(0,50);
	} else {
	    dmi.multiplicative_weighting.value = 0.0;
	}
}
function fxn_combine_mutns_able() {
   if (dmi.combine_mutns.checked) {
	document.getElementById("mwdiv").style.display = "block";
   } else {
	document.getElementById("mwdiv").style.display = "none";
   }
}

function fxn_dynamic_linkage() {
        fxn_dynamic_linkage_able();
	if (dmi.dynamic_linkage.checked) {
		//mendel_input.num_linkage_subunits.value = 1000;
                if (dmi.haploid_chromosome_number.value = "0")
	           dmi.haploid_chromosome_number.value = "23";
	} else {
		//dmi.num_linkage_subunits.value = 1000;
	}
}
function fxn_dynamic_linkage_able() {
	if (dmi.dynamic_linkage.checked) {
	   dmi.haploid_chromosome_number.disabled = false;
           document.getElementById("link_num").innerText = 
			":: number of linkage subunits:";
	} else {
	   dmi.haploid_chromosome_number.disabled = true;
	   document.getElementById("link_num").innerText = 
			":: fixed block linkage number:";
	}
}

function fxn_haploid() {
   if (dmi.clonal_haploid.checked) {
      dmi.fraction_recessive.value = 0.0; 
      dmi.dominant_hetero_expression.value = 1.0; 
      status("Setting fraction_recessive to 0 and dominant_hetero_expression to 1");
   } else {
      dmi.dominant_hetero_expression.value = 0.5; 
      status("Setting dominant_hetero_expression back to 0.5");
   }
}

function fxn_is_parallel() {
   if (dmi.is_parallel.checked) {
      document.getElementById("psdiv").style.display = "block";
      window.scrollBy(0,500);
      //document.getElementById("engine").selectedIndex = 1;
      //status("NOTE: Changed engine to C");
      //dmi.fraction_neutral.value = 0;
      //status("Setting fraction_neutral to 0. Neutral mutations not supported in parallel runs.");
   } else {
      document.getElementById("psdiv").style.display = "none";
      status("");
   }
}

function status(msg) {
      //omsg = document.getElementById("note_to_user").innerText;
      //mymsg = omsg + msg;
      mymsg = msg;
      document.getElementById("note_to_user").innerText = mymsg;
}

function fxn_restart_case() {
        fxn_restart_case_able();
	if (dmi.restart_case.checked) {
            if (dmi.restart_dump_number.value = "0") {
                dmi.restart_dump_number.value = "1";
            } 
	}
}

function fxn_restart_case_able() {
   if (dmi.restart_case.checked) {
      document.getElementById("rddiv").style.display = "block";
   } else {
      document.getElementById("rddiv").style.display = "none";
   }
}

function fxn_bottleneck() {
        fxn_bottleneck_able();
	if (dmi.bottleneck_yes.checked) {
                if (dmi.bottleneck_generation.value = "0") {
                    dmi.bottleneck_generation.value = "1000";
                    window.scrollBy(0,500);
                }
                if (dmi.bottleneck_pop_size.value = "0") {
                    dmi.bottleneck_pop_size.value = "100";
                }
                if (dmi.num_bottleneck_generations.value = "0") {
                    dmi.num_bottleneck_generations.value = "500";
                }
	}
}
function fxn_bottleneck_able() {
   if (dmi.bottleneck_yes.checked) {
      document.getElementById("bydiv").style.display = "block";
   } else {
      document.getElementById("bydiv").style.display = "none";
   }
}

function check_bottleneck() {
   bgen = dmi.bottleneck_generation.value;
   if(bgen < 0) {
     status("Cyclic bottlenecking turned on");
     if(dmi.num_bottleneck_generations.value > -bgen ) {
         dmi.num_bottleneck_generations.value = -bgen - 1; 
     }
   } else {
     status("Cyclic bottlenecking turned off");
   }
}

function fxn_allocate_memory() {
	if (dmi.auto_malloc.checked) {
           dmi.max_del_mutn_per_indiv.disabled = true;
           dmi.max_fav_mutn_per_indiv.disabled = true;
           status("");
        } else {
           dmi.max_del_mutn_per_indiv.disabled = false;
           dmi.max_fav_mutn_per_indiv.disabled = false;
           dmi.max_del_mutn_per_indiv.select();
        }
}

function compute_u() {
   u = dmi.mutn_rate.value;
   uneu = dmi.uneu.value = u*dmi.fraction_neutral.value;
   dmi.uben.value = (u-uneu)*dmi.frac_fav_mutn.value;
   dmi.udel.value = (u-uneu)*(1-dmi.frac_fav_mutn.value);
}

function fxn_fraction_neutral() {
   if(dmi.fraction_neutral.value>0) {
      dmi.track_neutrals.checked = true;
      //status("tracking all mutations");
   } else {
      dmi.track_neutrals.checked = false;
      //status("not tracking all mutations");
   }      
   compute_u();
}

function fxn_track_neutrals() {
   if(dmi.track_neutrals.checked) {
      dmi.fraction_neutral.disabled = false;
      dmi.fraction_neutral.value = 0.9;
      // Modify mutation rate -- divide by fraction_neutrals
      //dmi.mutn_rate.value = Math.round(dmi.mutn_rate.value/(1-dmi.fraction_neutral.value));
      dmi.fraction_neutral.select();
      dmi.track_all_mutn.checked = true;
      fxn_track_all_mutn();
      document.getElementById("mutn_rate").innerText = "Total mutation rate per individual per generation:";
      status("including neutrals in analysis will require more memory and will slow run, and all mutations will be tracked");
   } else {
      // Modify mutation rate -- multiply by fraction_neutrals
      //dmi.mutn_rate.value = Math.round(dmi.mutn_rate.value*(1-dmi.fraction_neutral.value));
      document.getElementById("mutn_rate").innerText = "Total non-neutral mutation rate per individual per generation:";
      dmi.fraction_neutral.value = 0.0;
      dmi.fraction_neutral.disabled = true;
      status("");
   }
   compute_u();
}

function fxn_track_all_mutn() {
   if(dmi.track_all_mutn.checked) {
      dmi.tracking_threshold.value = 0;
      dmi.tracking_threshold.disabled = true;
   } else {
      dmi.tracking_threshold.disabled = false;
      dmi.tracking_threshold.value = tracking_threshold;
      dmi.tracking_threshold.select();
      dmi.track_neutrals.checked = false;
   }
}

function fxn_init_tracking_threshold() {
   if(dmi.tracking_threshold.value == 0) {
      dmi.track_all_mutn.checked = true;
   } else {
      dmi.track_all_mutn.checked = false;
   } 
   // set a default tracking_threshold value, in case user
   // is not restarting from a file that has a specified tracking 
   // threshold value.
   if(tracking_threshold == 0) { tracking_threshold = 1.e-5; }
}

function fxn_fitness_distrib_type_init() {
   fdt = dmi.fitness_distrib_type.value;
   // equal effect distribution
   if (fdt == 0) {
      document.getElementById("ufe_div").style.display = "block";
      document.getElementById("weibull_div").style.display = "none";
      document.getElementById("crdiv").style.display = "block";
      dmi.combine_mutns.disabled = false;
      dmi.synergistic_epistasis.disabled = false;
      window.scrollBy(0,500);
   // Weibull distribution
   } else if (fdt == 1) {
      document.getElementById("ufe_div").style.display = "none";
      document.getElementById("weibull_div").style.display = "block";
      document.getElementById("crdiv").style.display = "block";
      dmi.combine_mutns.disabled = false;
      dmi.synergistic_epistasis.disabled = false;
      window.scrollBy(0,500);
   // All Neutral
   } else if (fdt == 2) {
      document.getElementById("ufe_div").style.display = "none";
      document.getElementById("weibull_div").style.display = "none";
      document.getElementById("crdiv").style.display = "none";
      dmi.combine_mutns.disabled = true;
      dmi.synergistic_epistasis.disabled = true;
      fxn_disable_synergistic_epistasis();
      window.scrollBy(0,500);
   // Bi-modal
   } else if (fdt == 3) {
      document.getElementById("ufe_div").style.display = "block";
      document.getElementById("weibull_div").style.display = "block";
      document.getElementById("crdiv").style.display = "block";
      dmi.combine_mutns.disabled = false;
      dmi.synergistic_epistasis.disabled = false;
      window.scrollBy(0,500);
   } else {
      document.getElementById("ufe_div").style.display = "none";
      document.getElementById("weibull_div").style.display = "block";
      document.getElementById("crdiv").style.display = "block";
      dmi.combine_mutns.disabled = false;
      dmi.synergistic_epistasis.disabled = false;
   }
}

function fxn_fitness_distrib_type_change() {
   fxn_fitness_distrib_type_init();
   fdt = dmi.fitness_distrib_type.value;
   if (fdt == 0) {
      dmi.dominant_hetero_expression.value = 1.0;
   } else {
      dmi.dominant_hetero_expression.value = 0.5;
   }
}

function show_hide_advanced() {
	if (dmi.advsel.checked) {
           document.getElementById("tab-pane-1").style.display = "block";
           window.scrollBy(0,500);
        } else {
           document.getElementById("tab-pane-1").style.display = "none";
        }
}

function show_hide_parser() {
	if (document.parsed_data.show_data.checked) {
           document.getElementById("parser").style.display = "block";
           //window.scrollBy(0,500);
        } else {
           document.getElementById("parser").style.display = "none";
        }
}

function show_hide_mutation_upload_form(i) {
        // if user checks upload mutations on the mutation pane
        // then automatically also check the upload mutations box
        // under population substructure, and vice-versa
        if(i==2) {
           if (dmi.altruistic.checked) {
              dmi.upload_mutations.checked = true;
           } else {
              dmi.upload_mutations.checked = false;
           }
        }

        // if user checks upload mutations on the mutation pane
        // then automatically also check the upload mutations box 
        // under population substructure, and vice-versa
	if (dmi.upload_mutations.checked) {
           document.getElementById("upload_mutations_div").style.display = "block";
           //dmi.mutn_file_id.disabled = false;
           window.scrollBy(0,500);
        } else if (dmi.altruistic.checked) {
           document.getElementById("upload_mutations_div").style.display = "block";
        } else {
          document.getElementById("upload_mutations_div").style.display = "none";
          //dmi.mutn_file_id.disabled = true;
        }
}

function fxn_migration() {
   x = 1*dmi.num_indiv_exchanged.value;
   max = 1*dmi.pop_size.value;
   if(x == 0) {
      dmi.migration_generations.disabled = true;
   } else {
      dmi.migration_generations.disabled = false;
      //dmi.migration_generations.value = 1;
      if(x > max || x < 0) alert("Value must be between 0 and " + max);
   }
}

function fxn_tribes(max_tribes) {
   myobject = dmi.num_tribes;
   num_tribes = myobject.value;

   // set max number of tribes for server from setting in config.inc
   if(num_tribes > max_tribes) { 
      myobject.value = max_tribes;
      num_tribes = max_tribes;
   }
   // set min number of tribes 
   if(num_tribes < 2) {
      myobject.value = 2; 
      num_tribes = 2;
   }

   if (dmi.homogenous_tribes.checked) {
      document.getElementById("tribediv").style.display = "none";
   } else {
      document.getElementById("tribediv").style.display = "block";
   }

   if (dmi.tribal_competition.checked) {
      dmi.tc_scaling_factor.disabled = false;
      dmi.group_heritability.disabled = false;
      dmi.tc_scaling_factor.select();
      status("Group competition is still under development. Proceed with caution.");
   } else {
      dmi.tc_scaling_factor.disabled = true;
      dmi.group_heritability.disabled = true;
      status("");
   }

   dmi.num_tribes.title = "2 - " + max_tribes;
   // Add options to tribe_id select statement
   dmi.tribe_id.options.length=0;
   for (i = 0; i < num_tribes; i++) {
      a = (i+1)/1000 + ''; // compute number of tribe as a string
      b = a.substring(1);  // remove the leading 0 from 0.001, 0.002, etc.
      if((i+1)%10==0) b += '0'; // every 10 tribes: 0.01->0.010, 0.02->0.020, etc.
      dmi.tribe_id.options[i]=new Option(b, b, true, false);
   }
}

function fxn_clone() {
   if (dmi.clonal_reproduction.checked) {
      dmi.fraction_self_fertilization.disabled = true;
      dmi.num_contrasting_alleles.disabled = true;
      dmi.max_total_fitness_increase.disabled = true;
      dmi.dynamic_linkage.disabled = true;
      dmi.haploid_chromosome_number.disabled = true;
      dmi.num_linkage_subunits.value = 1;
   } else {
      dmi.fraction_self_fertilization.disabled = false;
      dmi.num_contrasting_alleles.disabled = false;
      dmi.max_total_fitness_increase.disabled = false;
      dmi.dynamic_linkage.disabled = false;
      dmi.haploid_chromosome_number.disabled = false;
      //dmi.num_linkage_subunits.value = 1000;
   }
}

function fxn_selection_init() {
  i = dmi.selection_scheme.value;
  if (i == 1 || i == 2 || i == 4) {
     dmi.non_scaling_noise.value = 0.05;
     //status("Setting non_scaling_noise to 0.05");
  } else {
     dmi.non_scaling_noise.value = 0.0;
     //status("Setting non_scaling_noise to 0.0");
  } 
}

function fxn_selection(i) {
  fxn_selection_init();
  if (i == 4) {
     document.getElementById("ptv").style.display = "block";
     dmi.partial_truncation_value.select();
  } else {
     document.getElementById("ptv").style.display = "none";
  } 
}

function check_back_mutn() {
   if(dmi.allow_back_mutn.checked) {
      tt = dmi.tracking_threshold.value;
      dmi.tracking_threshold.value = "0.0";
      status("NOTE: Changed tracking threshold to 0.0 so that all mutations will be tracked");
   } else {
      if(tt<=0) tt = 1.e-5; 
      dmi.tracking_threshold.value = tt;
      status("NOTE: Changed tracking threshold back to " + tt );
   }
}

function fxn_pop_growth_model(i) {
  // the Fortran engine does not support dynamic population sizes
  // so change the engine if dynamic population is turned on
  //if(i == 1 || i == 2) {
  //   document.getElementById("engine").selectedIndex = 1;
  //   status("NOTE: Changed simulation engine to C");
  //}
  if (i == 0) {
     dmi.pop_growth_rate.disabled = true;
     document.getElementById("gen").innerText =
                        "Generations:";
     document.getElementById("pop").innerText =
                        "Population size (per subpopulation):";
     status("");
  } else if (i == 1) {
     dmi.pop_growth_rate.disabled = false;
     document.getElementById("pgr").innerText =
                        "    :: intrinsic growth rate:";
     document.getElementById("gen").innerText =
                        "Max population size:";
     document.getElementById("pop").innerText =
                        "Starting population size (per subpopulation):";
     dmi.pop_size.value = "2"; 
     dmi.num_generations.value = "2000"; 
     dmi.pop_growth_rate.value = "1.01"; 
     dmi.pop_growth_rate.title = "1.00 - 1.26"; 
     status("WARNING: dynamic populations are experimental and largely untested");
  } else if (i == 2) {
     dmi.pop_growth_rate.disabled = false;
     document.getElementById("pgr").innerText =
                        "    :: maximum reproductive rate of an individual:";
     document.getElementById("gen").innerText =
                        "Carrying capacity:";
     document.getElementById("pop").innerText =
                        "Starting population size (per subpopulation):";
     dmi.pop_size.value = "2"; 
     dmi.num_generations.value = "1000"; 
     dmi.pop_growth_rate.value = "0.1"; 
     dmi.pop_growth_rate.title = "0.0 - 1.0"; 
     status("WARNING: dynamic populations are experimental and largely untested");
  } else {
     dmi.pop_growth_rate.disabled = false;
     status("");
  }
}

</script>
ZzZzZz

print "</head>\n";
print "<body onload=\"fxn_init()\" bgcolor=ffffff>\n";
#print "screen resolution is: $screenresx x $screenresy<br>";
#print "browser is: $browser<br>";
#print "Run_dir: $run_dir<br>";
#print "user_id: $user_id<br>";
#print "template is $template<br>";
#print "tribe_id is $tribe_id<br>";
#print "Version: $version $os<br>";

if($browser eq "Microsoft+Internet+Explorer") {
   print "<h2>ERROR: Microsoft Internet Explorer not supported.</h2>";
   print "<p>Solution: please try using another browser such as Google Chrome</p>";
   die;
}

$tempfn = "./templates/mendel.in$template";

if ($tribe_id ne "") {
   $tribe_note = "mendel.in$tribe_id";
}

print "<table width=550><tr><td valign=top>";

$mytemplate = $template;
$mytemplate =~ s/\.//;

if ($case_id eq "") {
   if ($template ne "") {
      print "<em>Note: using default $mytemplate parameters<br> $tribe_note</em><br>";
   } else {
      print "<em>Note: using default parameters<br> $tribe_note</em><br>";
   }
   $path = $tempfn;
} else {
   if ($template ne "") {
      $path = $tempfn;
      print "<em>Note: using default $mytemplate parameters<br> $tribe_note</em><br>";
   }
   $path = "$run_dir/$case_user_id/$case_id/mendel.in";
   if (-e $path || $os eq "windows") {
      print "<em>Note: using parameters from $case_id<br> $tribe_note</em><br>\n";
      $new_case_id = $case_id;
   } else {
      $new_case_id = $case_id;
      $path = $tempfn;
      print "<em>Note: creating new case $case_id with $mytemplate params<br> $tribe_note</em><br>\n";
      #print "<b>ERROR</b>: Case does not exist.<br>\n";
      #print "<b>SOLUTION</b>: Either clear the CaseID, or insert a valid CaseID.<br>\n";
   }
}

print "</td>";

### Read input parameters from mendel.in ######################################
#if ($os eq "linux") {
#   print "<td>";
#   print "<form method=post action=\"import.cgi\">";
#   print "<input type=hidden name=\"version\" value=\"$version\">";
#   print "<input type=hidden name=\"case_id\" value=\"$case_id\">";
#   print "<input type=submit title=\"Import $case_id parameters from another MENDEL server\" value=\"Import Case\">";
#   print "</form>";
#   print "</td>";
#}

if($os eq "linux") {
   ($wcl) = split(' ',`wc -l $path`);
   if($wcl eq "0") {
      print "<h2>ERROR: mendel.in exists but is empty.</h2>";
      die;
   }
}

# Read the parameters from the input file
require "./input_file_parser.inc";
$case_id = $my_case_id;
print "<font color=red>$done</font>";

### End read input parameters #################################################

        if ($os eq "windows") {
           $disable_parallel   = "disabled=true";
           $disable_synergistic_epistasis ="disabled=true";
           $disable_dynamic_populations = "disabled=true";
           $disable_bottlenecks = "disabled=true";
           $disable_queuing_system = "disabled=true";
           $disable_engines = "disabled=true";
           $readonly = "READONLY";
        }

	if($multiplicative_weighting > 0) {
	   $combine_mutns = "CHECKED";
	}

	if($dynamic_linkage eq "T") {
	   $dynamic_linkage = "CHECKED";
	} else {
	   $dynamic_linkage = "";
	}
	if($bottleneck_yes eq "T") {
	   $bottleneck_yes = "CHECKED";
	} else {
	   $bottleneck_yes = "";
	}
	if($homogenous_tribes eq "T") {
	   $homogenous_tribes = "CHECKED";
	} else {
	   $homogenous_tribes = "";
	}
	if($synergistic_epistasis eq "T") {
	   $synergistic_epistasis = "CHECKED";
	} else {
	   $synergistic_epistasis = "";
	}
	if($upload_mutations eq "T") {
	   $upload_mutations = "CHECKED";
	} else {
	   $upload_mutations = "";
	}
	if($allow_back_mutn eq "T") {
	   $allow_back_mutn = "CHECKED";
	} else {
	   $allow_back_mutn = "";
	}
	if($altruistic eq "T") {
	   $altruistic = "CHECKED";
	} else {
	   $altruistic = "";
	}
	if($clonal_reproduction eq "T") {
	   $clonal_reproduction = "CHECKED";
	} else {
	   $clonal_reproduction = "";
	}
	if($clonal_haploid eq "T") {
	   $clonal_haploid = "CHECKED";
	} else {
	   $clonal_haploid = "";
	}

        if($tribal_competition eq "T") {
           $tribal_competition = "CHECKED";
        } else {
           $tribal_competition = "";
        }

	if($fitness_dependent_fertility eq "T") {
	   $fitness_dependent_fertility = "CHECKED";
	} else {
	   $fitness_dependent_fertility = "";
	}
	if ($track_neutrals eq "T") {
	   $track_neutrals = "CHECKED";
	} else {
	   $track_neutrals = "";
	}
	if ($write_dump eq "T") {
	   $write_dump = "CHECKED";
	} else {
	   $write_dump = "";
	}
	if ($restart_case eq "T") {
	   $restart_case = "CHECKED";
	} else {
	   $restart_case = "";
	}
	if ($plot_avg_data) {
	   $plot_avg_data = "CHECKED";
	} else {
	   $plot_avg_data = "";
	}
	if ($is_parallel eq "T") {
	   $is_parallel = "CHECKED";
	} else {
	   $is_parallel = "";
	}

	if ($restart_append eq "T") {
	   $restart_append = "CHECKED";
	} else {
	   $restart_append = "";
	}

	if ($auto_malloc) {
	   $auto_malloc = "CHECKED";
	} else {
	   $auto_malloc = "";
	}

#print "<h1><font color=red>ALERT: currently changing interface, you may experience unstable results</font></h1>";

$pop_growth_number = $pop_growth_model;

if ($pop_growth_model eq "0") {
    $pop_growth_model= "<option SELECTED VALUE=\"0\">Off (fixed population size) <option VALUE=\"1\">Exponential growth <option VALUE=\"2\">Carrying capacity model";
} elsif ($pop_growth_model eq "1") {
    $pop_growth_model = "<option VALUE=\"0\">Off (fixed population size) <option SELECTED VALUE=\"1\">Exponential growth <option VALUE=\"2\">Carrying capacity model";
} else {
    $pop_growth_model = "<option VALUE=\"0\">Off (fixed population size) <option VALUE=\"1\">Exponential growth <option SELECTED VALUE=\"2\">Carrying capacity model";
} 

if ($migration_model eq "1") {
    $migration_model = "<option SELECTED VALUE=\"1\">One-way stepping stone model <option VALUE=\"2\">Two-way stepping stone model <option VALUE=\"3\">Island model";
} elsif ($migration_model eq "2") {
    $migration_model = "<option VALUE=\"1\">One-way stepping stone model <option SELECTED VALUE=\"2\">Two-way stepping stone model <option VALUE=\"3\">Island model";
} elsif ($migration_model eq "3") {
    $migration_model = "<option VALUE=\"1\">One-way stepping stone model <option VALUE=\"2\">Two-way stepping stone model <option SELECTED VALUE=\"3\">Island model";
} else {
    $migration_model = "<option SELECTED VALUE=\"1\">One-way stepping stone model <option VALUE=\"2\">Two-way stepping stone model <option VALUE=\"3\">Island model";
}

$selection_scheme_number = $selection_scheme;

if ($selection_scheme eq "1") {
    $selection_scheme = "<option SELECTED VALUE=\"1\">Truncation selection<option VALUE=\"2\">Unrestricted probability selection <option VALUE=\"3\">Strict proportionality probability selection <option VALUE=\"4\">Partial truncation selection";
} elsif ($selection_scheme eq "2") {
    $selection_scheme = "<option VALUE=\"1\">Truncation selection<option SELECTED VALUE=\"2\">Unrestricted probability selection <option VALUE=\"3\">Strict proportionality probability selection <option VALUE=\"4\">Partial truncation selection";
} elsif ($selection_scheme eq "3") {
    $selection_scheme = "<option VALUE=\"1\">Truncation selection<option VALUE=\"2\">Unrestricted probability selection <option SELECTED VALUE=\"3\">Strict proportionality probability selection <option VALUE=\"4\">Partial truncation selection";
} elsif ($selection_scheme eq "4") {
    $selection_scheme = "<option VALUE=\"1\">Truncation selection<option VALUE=\"2\">Unrestricted probability selection <option VALUE=\"3\">Strict proportionality probability selection <option SELECTED VALUE=\"4\">Partial truncation selection";
} else {
    $selection_scheme = "<option SELECTED VALUE=\"1\">Truncation selection<option VALUE=\"2\">Unrestricted probability selection <option VALUE=\"3\">Strict proportionality probability selection <option VALUE=\"4\">Partial truncation selection";
}

if ($fitness_distrib_type eq 0) {
    $dist_options = "<option VALUE=\"1\">Natural distribution \(Weibull\)<option SELECTED VALUE=\"0\">All mutations equal<option VALUE=\"2\" disabled=true>All mutations neutral<option VALUE=\"3\" disabled=true>Weibull + second mode";
} elsif ($fitness_distrib_type eq 1) {
    $dist_options = "<option SELECTED VALUE=\"1\">Natural distribution \(Weibull\)<option VALUE=\"0\">All mutations equal<option VALUE=\"2\" disabled=true>All mutations neutral<option VALUE=\"3\" disabled=true>Weibull + second mode";
} elsif ($fitness_distrib_type eq 2) {
    $dist_options = "<option VALUE=\"1\">Natural distribution \(Weibull\)<option VALUE=\"0\">All mutations equal<option SELECTED VALUE=\"2\" disabled=true>All mutations neutral<option VALUE=\"3\" disabled=true>Weibull + second mode";
} elsif ($fitness_distrib_type eq 3) {
    $dist_options = "<option VALUE=\"1\">Natural distribution \(Weibull\)<option VALUE=\"0\">All mutations equal<option VALUE=\"2\" disabled=true>All mutations neutral<option SELECTED VALUE=\"3\" disabled=true>Weibull + second mode";
} else {
    $dist_options = "<option SELECTED VALUE=\"1\">Natural distribution \(Weibull\)<option VALUE=\"0\">All mutations equal<option VALUE=\"2\" disabled=true>All mutations neutral<option VALUE=\"3\" disabled=true>Weibull + second mode";
}

if ($template eq ".human") { 
   $template_options = "<option VALUE=\"\">Choose parameter template... <option SELECTED VALUE=\".human\">Human and similar<option VALUE=\".mito\">Human Mitochondria<option VALUE=\".yeast\">Yeast and similar<option VALUE=\".hiv\">HIV and similar<option VALUE=\".flu\">Influenza and similar";
} elsif ($template eq ".mito") {
   $template_options = "<option VALUE=\"\">Choose parameter template...  <option VALUE=\".human\">Human and similar<option SELECTED VALUE=\".mito\">Human Mitochondria<option VALUE=\".yeast\">Yeast and similar<option VALUE=\".hiv\">HIV and similar<option VALUE=\".flu\">Influenza and similar";
} elsif ($template eq ".hiv") { 
   $template_options = "<option VALUE=\"\">Choose parameter template...  <option VALUE=\".human\">Human and similar<option VALUE=\".mito\">Human Mitochondria<option VALUE=\".yeast\">Yeast and similar<option SELECTED VALUE=\".hiv\">HIV and similar<option VALUE=\".flu\">Influenza and similar";
} elsif ($template eq ".yeast") {
   $template_options = "<option VALUE=\"\">Choose parameter template...  <option VALUE=\".human\">Human and similar<option SELECTED VALUE=\".yeast\">Yeast and similar<option VALUE=\".hiv\">HIV and similar<option VALUE=\".flu\">Influenza and similar";
} elsif ($template eq ".flu") {
   $template_options = "<option VALUE=\"\">Choose parameter template...  <option VALUE=\".human\">Human and similar<option VALUE=\".mito\">Human Mitochondria<option VALUE=\".yeast\">Yeast and similar<option VALUE=\".hiv\">HIV and similar<option SELECTED VALUE=\".flu\">Influenza and similar";
} else {
   $template_options = "<option SELECTED VALUE=\"\">Choose parameter template...  <option VALUE=\".human\">Human and similar<option VALUE=\".mito\">Human Mitochondria<option VALUE=\".yeast\">Yeast and similar<option VALUE=\".hiv\">HIV and similar<option VALUE=\".flu\">Influenza and similar";
}

if ($run_queue eq "noq" || $disable_pbs) {
    $my_run_queue = "<option SELECTED VALUE=\"noq\" $disable_noq>No queue<option VALUE=\"atq\" $disable_atq>ATQ<option VALUE=\"pbs\" $disable_pbs>PBS<option VALUE=\"himem\" $disable_himem>HI-MEM";
} elsif ($run_queue eq "atq") {
    $my_run_queue = "<option VALUE=\"noq\" $disable_noq>No queue<option SELECTED VALUE=\"atq\" $disable_atq>ATQ<option VALUE=\"pbs\" $disable_pbs>PBS<option VALUE=\"himem\" $disable_himem>HI-MEM";
} elsif ($run_queue eq "himem" || $run_queue eq "single_job") {
    $my_run_queue = "<option VALUE=\"noq\" $disable_noq>No queue<option VALUE=\"atq\" $disable_atq>ATQ<option VALUE=\"pbs\" $disable_pbs>PBS<option SELECTED VALUE=\"himem\" $disable_himem>HI-MEM";
} else {
    $my_run_queue = "<option VALUE=\"noq\" $disable_noq>No queue<option VALUE=\"atq\" $disable_atq>ATQ<option SELECTED VALUE=\"pbs\" $disable_pbs>PBS<option VALUE=\"himem\" $disable_himem>HI-MEM";
}

if ($engine eq "j" || $engine eq "2") {
    $my_engine = "<option VALUE=\"f\" $disable_fortran>Fortran<option VALUE=\"c\" $disable_c>C<option SELECTED VALUE=\"j\" disabled=true>Java";
} elsif ($engine eq "c" || $engine eq "1" || $disable_fortran ) {
    $my_engine = "<option VALUE=\"f\" $disable_fortran>Fortran<option SELECTED VALUE=\"c\" $disable_c>C<option VALUE=\"j\" disabled=true>Java";
} else { 
    $my_engine = "<option SELECTED VALUE=\"f\" $disable_fortran>Fortran<option VALUE=\"c\" $disable_c>C<option VALUE=\"j\" disabled=true>Java";
}

print <<ZzZz;
<!-- 
<td align=right valign=bottom>
<form name="template_form" method=post action="./start.cgi">
<select name="template" onChange="template_form.submit()">
$template_options
</select>
-->
<input type="hidden" name="browser" value="$browser">
<input type="hidden" name="version" value="$version">
<input type="hidden" name="quota" value="$quota">
<input type="hidden" name="user_id" value="$user_id">
</form>
</td>
</tr>
</table>
ZzZz

print "<hr>";
print "<form name=\"mendel_input\" method=post action=\"input_file_writer.pl\" onsubmit=\"fxn_set_caseid()\">";

# if new case but case_id is given
if ($new_case_id ne "") {
   if ($new_case_id eq "crow") {
     print "<h1>NO LONGER SUPPORTED</h1>";
   } else {
     $case_id = $new_case_id;
   }
} elsif($homogenous_tribes eq "") {
   print "<font color=red><em>Note: using non-homogenous tribes</em></font>";
   $case_id = $case_id;
#} elsif($template eq ".hiv") {
#   $case_id = "hiv000";
#} elsif($template eq ".yeast") {
#   $case_id = "yst000";
} else {
   $case_id = "";
}

print <<End_of_Doc;
<input type="hidden" name="user_id" value="$user_id">

<br>
<table>
<tr> <td>
<font size="+1">Basic parameters</font> 
<table>
     <tr>
	<td width=350> <LABEL for="case_id">
        1. <a class="plain" href="/mendel/$version/help.html#caseid" target="status"
            title="case_id" tabindex="100"> <u>C</u>ase ID:</a> </LABEL></td>
	<td> 
	    <input type="text" name="case_id" value="$case_id"  
                   style="width:4em;"
                   title="Case ID must be 6 characters" accesskey="C">
            <input type="text" style="width:6em" name="description"
                   title="Label or description (optional)">
            <input type="checkbox" name="caseid_cb" 
                   title="Generate a new random Case ID (U)"
                   onclick="fxn_set_this_caseid()" accesskey="U" tabindex="101">
            <div id="tribediv" style="display:none">
                Tribe:
	        <select name="tribe_id">
                   <option VALUE=".001">.001</option>
                   <option VALUE=".002">.002</option>
	        </select>
            </div> 
        </td>
     </tr>
     <tr>
	<td><LABEL for="mutn_rate">
	   2. <a class="plain" href="/mendel/$version/help.html#nmpo" 
                 id="mutn_rate" target="status" 
                 title="mutn_rate" tabindex="102">
              Total non-neutral mutation rate:<br>
              &nbsp;&nbsp;&nbsp;
              (per individual per generation)</a> </LABEL></td>
	<td><INPUT type="text" name="mutn_rate" accesskey="1" 
                   value="$mutn_rate" 
                   onchange="compute_u()"
                   title="0 - 10,000; can be  fraction e.g. 0.5"></td>
        <td></td>
     </tr>
     <tr>
	<td><LABEL for="frac_fav_mutn">
	   3. <a class="plain" href="/mendel/$version/help.html#fomb" target="status"
               title="frac_fav_mutn" tabindex="103">
              Beneficial/deleterious ratio within non-neutral mutations:</</a> </LABEL></td>
	<td><INPUT type="text" name="frac_fav_mutn" accesskey="3" 
                   value="$frac_fav_mutn" 
                   onchange="compute_u();check_value(this.value,0,1)"
                   title="0.0 - 1.0 (e.g. if 1:1000, enter 0.001)"></td>
        <td></td>
     </tr>
     <tr>
	<td><LABEL for="uben">
	   &nbsp;&nbsp;&nbsp; <a class="plain" href="/mendel/$version/help.html#fomb" target="status">
              <font color="grey">beneficial mutation rate:</font></</a> </LABEL></td>
	<td><INPUT name="uben" type="text" disabled=true></td>
        <td></td>
     </tr>
     <tr>
	<td><LABEL for="udel">
	   &nbsp;&nbsp;&nbsp; <a class="plain" href="/mendel/$version/help.html#fomb" target="status">
              <font color="grey">deleterious mutation rate:</font></</a> </LABEL></td>
	<td><INPUT name="udel" type="text" disabled=true></td>
        <td></td>
     </tr>
     <tr>
	<td><LABEL for="reproductive_rate">
	   4. <a class="plain" href="/mendel/$version/help.html#opf" target="status"
               id="opf" title="reproductive_rate" tabindex="104">
               Reproduction rate:</a> </LABEL></td>
	<td><INPUT type="text" name="reproductive_rate" accesskey="4" 
                   onchange="fxn_opf(this.value,1,6)"
                   value="$reproductive_rate" title="1 - 6"></td>
        <td></td>
     </tr>
     <tr>
	<td><LABEL for="pop_size">
	   5. <a class="plain" href="/mendel/$version/help.html#popsize" target="status"
               id="pop" title="pop_size" tabindex="105">
              Population size (per subpopulation):</a> </LABEL></td>
	<td><INPUT type="text" name="pop_size" value="$pop_size" accesskey="5" 
                   onchange="check_value(this.value,2,50000)"
                   title="2 - 50,000"></td>
        <td></td>
     </tr>
     <tr>
	<td><LABEL for="num_generations">
	   6. <a class="plain" href="/mendel/$version/help.html#ngen" target="status"
              id="gen" title="num_generations" tabindex="106">
              Generations:</a> </LABEL></td>
	<td><INPUT type="text" name="num_generations" accesskey="6" 
                   onchange="check_value(this.value,1,100000)"
                   value="$num_generations" title="1 - 100,000"></td>
        <td></td>
     </tr>

     <tr><td><a class="plain" href="/mendel/$version/help.html#adv" target="status"
                <u>A</u>dvanced settings?</a> </td>
         <td>
              <table><tr><td width=80>
              <input type="checkbox" name="advsel" id="advsel" 
                onclick="show_hide_advanced()" accesskey="A"
                title="Show/hide advanced parameters"></td>
             <td align=right><INPUT type="submit" value="Submit" accesskey="X"></td> 
     <td></td>
     </tr></table>
</td></tr>
</table>
</td><td valign=top>
<!--
<font size="+1">Computed Parameters</font> 
<table>
<tr><td><font color="grey">Neutral mutation rate:<font></td><td></td></tr>
<tr><td><font color="grey">Beneficial mutation rate:</font></td><td></td></tr>
<tr><td><font color="grey">Deleterious mutation rate:</font></td><td></td></tr>
</table>
-->
</td></tr></table>

<!--*************************** ADVANCED PANE *******************************-->
<div class="tab-pane" id="tab-pane-1" style="display:none">
    
<div class="tab-page">
<h2 class="tab">mutation</h2>

    <table>
       <tr>
          <td width=350>1. Distribution type:</td>
          <td>
		<select name="fitness_distrib_type" 
                        onchange="fxn_fitness_distrib_type_change()">
		$dist_options
		</select>
          </td>
       </tr>
    </table>

     <div id="ufe_div" style="display:none">
     <table>
     <tr>
        <td width=350><LABEL for="uniform_fitness_effect_del">
           <a class="plain" href="/mendel/$version/help.html#fdt" 
            title="uniform_fitness_effect_del" target="status">
	     &nbsp;&nbsp;&nbsp;
	     a. equal effect for each deleterious mutation:</a></LABEL></td>
        <td><input type="text" name="uniform_fitness_effect_del"
		   value="$uniform_fitness_effect_del"></td>
     </tr>	   
     <tr>
        <td width=350><LABEL for="uniform_fitness_effect_fav">
           <a class="plain" href="/mendel/$version/help.html#fdt" 
            title="uniform_fitness_effect_fav" target="status">
	     &nbsp;&nbsp;&nbsp;
	     b. equal effect for each beneficial mutation:</a></LABEL></td>
        <td><input type="text" name="uniform_fitness_effect_fav"
	           value="$uniform_fitness_effect_fav"></td>
     </tr>	   
     </table>	   
     </div>
     
<div id="weibull_div" style="display:none">
    <a class="plain" href="/mendel/$version/help.html#psddme" target="status"
                tabindex="107">
     &nbsp;&nbsp;&nbsp;
      Parameters shaping Weibull distribution of mutation effects:</a>
     <table>		
     
     <tr>
        <td width=350><LABEL for="genome_size">
	     &nbsp;&nbsp;&nbsp;
	           a. <a class="plain" href="/mendel/$version/help.html#hgs" 
                         target="status" title="genome_size" tabindex="108">
                   functional genome size:</a><br> 
	     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
             <font size="-2">&rarr; G<sub>functional</sub> = G<sub>actual</sub> - G<sub>junk</sub></font> </LABEL> </td>
        <td><INPUT type="text" name="genome_size" id="hgs" accesskey="1"
                   value="$genome_size" 
                   onchange="check_value(this.value,100,1e11)"
                   title="100 - 100 billion"></td>
     </tr>	   
     
     <tr>
        <td><LABEL for="high_impact_mutn_fraction">
	        &nbsp;&nbsp;&nbsp;
		   b. <a class="plain" href="/mendel/$version/help.html#himf"
		         target="status" title="high_impact_mutn_fraction"
                         tabindex="109">
	    fraction of del. mutations with "major effect": </a></LABEL></td>
        <td><input type="text" name="high_impact_mutn_fraction"
                   value="$high_impact_mutn_fraction" 
                   onchange="check_value(this.value,0.0001,0.9)"
                   title="0.0001 - 0.9"></td>
     </tr>	   
     
     <tr>
        <td><LABEL for="high_impact_mutn_threshold">
	       &nbsp;&nbsp;&nbsp;
	    c. <a class="plain" href="/mendel/$version/help.html#himt" 
               target="status" title="high_impact_mutn_threshold" 
               tabindex="110">
               minimum del. effect defined as "major":</a></LABEL></td>
        <td><input type="text" name="high_impact_mutn_threshold"
	 	   value="$high_impact_mutn_threshold" 
                   onchange="check_value(this.value,0.01,0.9)"
                   title="0.01 - 0.9"></td>
     </tr>	   
     <tr><td>	   
       &nbsp;&nbsp;&nbsp;
        <a class="plain" href="/mendel/$version/help.html#rdbm" target="status"
        tabindex="111" title="max_fav_fitness_gain">
            d. maximum beneficial fitness effect:</a></td>
        <td><input type="text" name="max_fav_fitness_gain" accesskey="2"
		   value="$max_fav_fitness_gain" title="0.000001 - 0.01"></td>
     </tr>
     
<!--
     <tr>
        <td width=350><LABEL for="max_fav_fitness_gain">
	        &nbsp;&nbsp;&nbsp;
     &bull;		<a class="plain" href="/mendel/$version/help.html#mffg" tabindex="112"
        target="status" title="max_fav_fitness_gain">maximal
           beneficial effect per mutation:</a></LABEL></td>
     </tr>	   
-->
     
<!--
     <tr>
        <td><LABEL for="num_initial_fav_mutn">
	        &nbsp;&nbsp;&nbsp;
		  &bull; <a class="plain" href="/mendel/$version/help.html#nifm"
			         tabindex="113"
                      target="status" title="num_initial_fav_mutn">
                      number of initial beneficial loci:</a></LABEL></td>
        <td><input type="text" name="num_initial_fav_mutn"
                   value="$num_initial_fav_mutn" title="0 - 10,000"></td>
     </tr>	   
-->
     
   </table>
</div>

<hr>

     <!-- Note: the value specified for a checkbox is sent
                     only if box is checked -->
		     
     <table><tr><td width=350>
        <a class="plain" href="/mendel/$version/help.html#cr" target="status"
           tabindex="115">2. Mutations &mdash; dominant vs. recessive?</a> </td>
          <td></td>
     </tr></table>
     
     
     <div id="crdiv">
     <table>
     <tr>
        <td width=350><LABEL for="fraction_recessive">
	        &nbsp;&nbsp;&nbsp;
		a. <a class="plain" href="/mendel/$version/help.html#fr"
		      target="status" title="fraction_recessive"
                      tabindex="116">fraction recessive (rest dominant):</a></LABEL></td>
        <td><input type="text" name="fraction_recessive"
                   value="$fraction_recessive"
                   onchange="check_value(this.value,0,1)"
                   id="fraction_recessive"
                   title="0.0 - 1.0" accesskey="3"></td>
     </tr>	   
     <tr>
        <td><LABEL for="recessive_hetero_expression">
	     &nbsp;&nbsp;&nbsp;
             b. <a class="plain" href="/mendel/$version/help.html#rhe" 
                   tabindex="117" target="status" 
                   title="recessive_hetero_expression">
               expression of recessive mutations (in heterozygote):</a>
            </LABEL></td>
        <td><input type="text" name="recessive_hetero_expression"
                value="$recessive_hetero_expression"
                onchange="check_value(this.value,0,0.5)"
                title="0.0 - 0.5"></td>
     </tr>	
     <tr>
        <td><LABEL for="dominant_hetero_expression">
	     &nbsp;&nbsp;&nbsp;
	     c. <a class="plain" href="/mendel/$version/help.html#dhe"
	           tabindex="118"
	           target="status" title="dominant_hetero_expression">
                   expression of dominant mutations (in heterozygote):</a>
            </LABEL></td>
        <td><input type="text" name="dominant_hetero_expression"
                value="$dominant_hetero_expression"
                onchange="check_value(this.value,0.5,1.0)"
                title="0.5 - 1.0"></td>
     </tr>	
     </table>	
     </div>
     
<hr>
     <table><tr>
     <td width=350>
        <a class="plain" href="/mendel/$version/help.html#cmenam" target="status"
	      tabindex="118">
	      3. Combine mutations effects non-additively?</a> </td>
     <td> <input type="checkbox" name="combine_mutns"
	       onclick="fxn_combine_mutns()" value="on" $combine_mutns>
     </td></tr ></table>
    <div id="mwdiv" style="display:none">
     <table>
     <tr>
        <td width=350><LABEL for="multiplicative_weighting">
     &nbsp;&nbsp;&nbsp;
     :: <a class="plain" href="/mendel/$version/help.html#mw" target="status"
	   title="multiplicative_weighting" tabindex="119">
	          fraction multiplicative effect:</a></LABEL></td>
        <td><input type="text" name="multiplicative_weighting"
                id="multiplicative_weighting"
                value="$multiplicative_weighting"
                onchange="check_value(this.value,0,1)"
                title="0.0 - 1.0" accesskey="4"></td>
     </tr>	
     </table>	
     </div>
     
<div>
<hr>
<table>
     <tr>
        <td width=350><LABEL FOR="synergistic_epistasis">
	              4. <a class="plain" href="/mendel/$version/help.html#se"
		            tabindex="120"
			    target="status" title="synergistic_epistasis">
      Include mutation-mutation interactions (synergistic epistasis)?</a></LABEL></td>
        <td><input type="checkbox" name="synergistic_epistasis"
                   value="on" onclick="fxn_synergistic_epistasis()"
                   $synergistic_epistasis $disable_synergistic_epistasis></td>
        <td></td>  
     </tr>
     <tr>
        <td><LABEL for="se_nonlinked_scaling">
	 &nbsp;&nbsp;&nbsp;
         a. scaling factor for non-linked SE interactions:</LABEL></td>
        <td><input type="text" name="se_nonlinked_scaling"
		   value="$se_nonlinked_scaling"
                   onchange="check_value(this.value,0.0,1.0)"
		   title="0.0 - 1.0" $disable_synergistic_epistasis></td>
     </tr>	      
     <tr>
        <td><LABEL for="se_linked_scaling">
	 &nbsp;&nbsp;&nbsp;
         b. scaling factor for linked SE interactions: </LABEL></td>
        <td><input type="text" name="se_linked_scaling"
		   value="$se_linked_scaling"
                   onchange="check_value(this.value,0.0,1.0)"
		   title="0.0 - 1.0" $disable_synergistic_epistasis></td>
     </tr>	   
</table>
<hr>
<table>
     <tr>
        <td width=350><LABEL FOR="upload_mutations">
         5. <a class="plain" href="/mendel/$version/help.html#upload"
               tabindex="120" target="status" title="upload_mutations">
	Upload set of custom mutations?</a> </LABEL></td>
        <td><input type="checkbox" name="upload_mutations"
                   value="on" onclick="show_hide_mutation_upload_form(1)" $upload_mutations></td>
        <td></td>  
     </tr>
</table>
<hr>
<table>
     <tr>
        <td width=350><LABEL FOR="allow_back_mutn">
	              6. <a class="plain" href="/mendel/$version/help.html#abm"
		            tabindex="120"
			    target="status" title="allow_back_mutn">
	Allow back mutations?</a> </LABEL></td>
        <td><input type="checkbox" name="allow_back_mutn"
                   value="on" onclick="check_back_mutn()" $allow_back_mutn></td>
        <td></td>  
     </tr>
     </table>

</div>

</ol>
</div>
<!--*************************** SELECTION TAB *******************************-->
<div class="tab-page">
<h2 class="tab">selection</h2>
     <table>
     <tr>
        <td width=380><LABEL for="fraction_random_death">
	       <ol><li><a class="plain" href="/mendel/$version/help.html#frd"
	                 target="status" title="fraction_random_death" tabindex="126">
            Fraction of offspring lost apart from selection ("random death"):</a></ol>
            </LABEL></td>
        <td><INPUT type="text" name="fraction_random_death"
                   value="$fraction_random_death" accesskey="1"
                   onchange="check_value(this.value,0,0.99)"
                   title="0.0 - 0.99"></td>
     </tr>
     <tr>
        <td><LABEL for="heritability">
	    <ol start=2><li><a class="plain" href="/mendel/$version/help.html#h"
	                       target="status" title="heritability" tabindex="127">
			       Heritability:</a></ol> </LABEL></td>
        <td><INPUT type="text" name="heritability" title="0 - 1"
                   onchange="check_value(this.value,0,1)"
                   accesskey="2" value="$heritability"></td>
     </tr>	   
     <tr>
        <td><LABEL for="non_scaling_noise">
	    <ol start=3><li><a class="plain" href="/mendel/$version/help.html#nsn"
	                     target="status" title="non_scaling_noise"
	                     tabindex="128">Non-scaling noise:</a></ol> 
            </LABEL></td>
        <td><input type="text" name="non_scaling_noise" title="0 - 1"
                   onchange="check_value(this.value,0,1)"
                   accesskey="3" value="$non_scaling_noise"></td>
     </tr>	   
     <tr>
        <td><LABEL for="fitness_dependent_fertility">
	    <ol start=4><li><a class="plain" href="/mendel/$version/help.html#fdf"
			     target="status" tabindex="128"
			     title="fitness_dependent_fertility">
                             Fitness-dependent fecundity decline?</a>
            </ol></LABEL></td> 
        <td><input type="checkbox" name="fitness_dependent_fertility"
                   accesskey="4" value="on" $fitness_dependent_fertility></td>
     </tr>	   
     <tr>
        <td><LABEL for="selection_scheme">
	    <ol start=5><li><a class="plain" href="/mendel/$version/help.html#ss"
	                       target="status" title="selection_scheme"
			       tabindex="128">Selection scheme:</a>
            </ol></LABEL></td>			     
        <td><select NAME="selection_scheme" accesskey="5"
             onchange="fxn_selection(this.value)" >
             $selection_scheme </select></td>
     </tr>   
     </table>
     
     <div id="ptv">
        <table>
	   <tr>
	      <td width=380> <LABEL for="partial_truncation_value">
	          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
		   :: <a class="plain" href="/mendel/$version/help.html#ptv"
		      target="status" title="partial_truncation_value">
		        partial truncation parameter, k</a></LABEL>
           <td> <input type="text" name="partial_truncation_value"
               value="$partial_truncation_value" title="0.0 - 1.0"> </td>
        </tr>  
        </table>
     </div>
</div>
<!--*************************** POPULATION TAB ******************************-->
<div class="tab-page">
<h2 class="tab">population</h2>
     <table>
     
     <tr>
        <td width=380> <LABEL for="clonal_reproduction">
	           1. <a class="plain" href="/mendel/$version/help.html#clonal"
		         target="status" tabindex="129"
			 title="clonal_reproduction">
                      Clonal reproduction?</a></LABEL> </td>
        <td> <input type="checkbox" name="clonal_reproduction"
                    value="on" onclick="fxn_clone()"
                    $clonal_reproduction></td>
     </tr>	    
     </table>	    
     
     <table>
     <tr>
        <td width=380> <LABEL for="clonal_haploid">
	           2. <a class="plain" href="/mendel/$version/help.html#ch"
		                 target="status" tabindex="129"
				    title="clonal_haploid">
                      Haploid?</a> </LABEL> </td>
        <td> <input type="checkbox" name="clonal_haploid"
                    value="on" onchange="fxn_haploid()" $clonal_haploid></td>
     </tr>	    
     </table>	    
     <table>
     <tr>
        <td width=380> <LABEL for="fraction_self_fertilization">
	        3. <a class="plain" href="/mendel/$version/help.html#fsf"
		             target="status" tabindex="129"
			           title="fraction_self_fertilization">
                      Fraction self fertilization:</a></LABEL> </td>
        <td> <input type="text" name="fraction_self_fertilization" title="0 - 1"
                    accesskey="1" value="$fraction_self_fertilization"
                    onchange="check_value(this.value,0,1)"
                    style="width:5em"></td>
     </tr></table><br>
     
     <table>
     <tr>
        <td width=380> <LABEL for="dynamic_linkage">
	 4. <a class="plain" href="/mendel/$version/help.html#dl" target="status"
	     title="dynamic_linkage" tabindex="130">
	        Dynamic linkage?</a></LABEL> </td>
        <td> <input type="checkbox" name="dynamic_linkage" accesskey="2"
		    value="on" onclick="fxn_dynamic_linkage()"
	            $dynamic_linkage> </td>
     </tr>		
     <tr>
        <td><LABEL for="haploid_chromosome_number">
	     &nbsp;&nbsp;&nbsp;
	         :: haploid chromosome number:</LABEL> </td>
        <td><INPUT type="text" name="haploid_chromosome_number"
		   value="$haploid_chromosome_number"></td>
     </tr>	   
     <tr>
        <td>&nbsp;&nbsp;&nbsp;
	        <LABEL id="link_num" for="num_linkage_subunits">
		          :: number of linkage subunits:</LABEL></td>
        <td><INPUT type="text" name="num_linkage_subunits" title="1 - 10,000"
                   onchange="check_value(this.value,1,10000)"
                   value="$num_linkage_subunits"></td>
     </tr>	   
     </table><br>  
     
     <table>
     <tr>
        <td width=380> 
	 5. <a class="plain" href="/mendel/$version/help.html#pgm"
	   target="status">Dynamic population size:</a><p></td>
     </tr>
     <tr>  
        <td><LABEL for="pop_growth_model">
	     &nbsp;&nbsp;&nbsp;
	       :: <a class="plain" href="/mendel/$version/help.html#pgm"
	             target="status" title="pop_growth_model">
		      population growth model:</a></LABEL> </td>
        <td><select NAME="pop_growth_model" accesskey="5"
             onchange="fxn_pop_growth_model(this.value)"  i
             $disable_dynamic_populations >
             $pop_growth_model</select></td>
     </tr>   
     <tr>
        <td><LABEL for="pop_growth_rate">
	    &nbsp;&nbsp;&nbsp;
	       <a id="pgr" class="plain" href="/mendel/$version/help.html#pgr"
	       target="status" title="pop_growth_rate" tabindex="130">
            :: population growth rate:</a></LABEL> </td>
        <td><INPUT type="text" name="pop_growth_rate"
                   onchange="check_value(this.value,1,1.26)"
	           value="$pop_growth_rate"></td>
     </tr>	   
     </table><br>  
     
     <table>
     <tr>
        <td width=380> <LABEL for="bottleneck_yes">
	 6. <a class="plain" href="/mendel/$version/help.html#by" 
	       target="status" title="bottleneck_yes" tabindex="132">
			    Bottleneck?</a></LABEL> </td>
        <td> <input type="checkbox" name="bottleneck_yes" value="on"
                    accesskey="4"
                    onclick="fxn_bottleneck()" $bottleneck_yes
                    $disable_bottlenecks> </td>
     </tr></table>  
     
     <div id="bydiv" style="display:none">
     <table>
     <tr>
        <td width=380><LABEL for="bottleneck_generation" 
                             title="bottleneck_generation">
	              &nbsp;&nbsp;&nbsp;
		      :: generation when bottleneck starts<br>
	              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                      <font size="-2"><em>note: negative values enable cyclic 
                                          bottlenecking</em></font></LABEL></td>
        <td><INPUT type="text" name="bottleneck_generation"
                   value="$bottleneck_generation" onchange="check_bottleneck()"
                   title="2 - 50,000"></td>
     </tr>	   
     <tr>
        <td><LABEL for="bottleneck_pop_size" title="bottleneck_pop_size">
	           &nbsp;&nbsp;&nbsp;
	           :: population size during bottleneck:</LABEL></td>
        <td><INPUT type="text" name="bottleneck_pop_size"
		   value="$bottleneck_pop_size"  title="2 - 1,000"></td>
     </tr>	   
     <tr>
        <td><LABEL for="num_bottleneck_generations" 
                   title="num_bottleneck_generations">
	           &nbsp;&nbsp;&nbsp;
	           :: duration of bottleneck - generations: </LABEL></td>
        <td><INPUT type="text" name="num_bottleneck_generations"
		   value="$num_bottleneck_generations" title="1 - 5,000"></td>
     </tr>	   
     </table>	   
     </div>
     
</div>
<!--*************************** SUBSTRUCTURE TAB ****************************-->
<div class="tab-page">
<h2 class="tab">substructure</h2>

     <table>
     <tr>
        <td width=380> 
           <LABEL for="is_parallel">
	      <a class="plain" href="/mendel/$version/help.html#ip" 
                 target="status" title="is_parallel" tabindex="131">
	      Population substructure?</a>
           </LABEL></td>
        <td> <input type="checkbox" name="is_parallel" accesskey="3"
                    onclick="fxn_is_parallel()" value="on"
                    $is_parallel $disable_parallel></td>
     </tr>	    
     </table>	    

     <div id="psdiv" style="display:none">

     <table>
     <tr>
        <td width=380> &nbsp;&nbsp;&nbsp;
	     1. <a class="plain" href="/mendel/$version/help.html#ht"
	               title="homogenous_tribes" target="status">
	 	              Homogeneous subpopulations?</a></td>
        <td> <input type="checkbox" name="homogenous_tribes"
                    onclick="fxn_tribes($max_tribes)" value="on" 
                    $homogenous_tribes></td>
     </tr>	    
     <tr>
        <td> <LABEL for="num_tribes">
	     &nbsp;&nbsp;&nbsp;
	     2. <a class="plain" href="/mendel/$version/help.html#nt"
	           target="status" title="num_tribes">
	           Number of subpopulations:</a> </LABEL></td>
        <td><input type="text" name="num_tribes" value="$num_tribes" 
                   onChange="fxn_tribes($max_tribes)"
        </td>
     </tr>	   
     <tr>
        <td><LABEL for="migration_model">
            &nbsp;&nbsp;&nbsp; 
            3. <a class="plain" href="/mendel/$version/help.html#mm"
	       target="status" title="migration_model">
	       Migration model:</a></LABEL></td>
        <td><select NAME="migration_model" id="migration_model">
               $migration_model
            </select>
        </td>
     </tr>

     <tr>
        <td width=380> &nbsp;&nbsp;&nbsp;
	     4. <a class="plain" href="/mendel/$version/help.html#mr"
	               title="migration_rate" target="status">
		Migrate
                <input type="text" name="num_indiv_exchanged"
                       title="1 to Pop Size" 
                       onchange="fxn_migration()";
                       size=2 value="$num_indiv_exchanged">
                individual(s) <br> 
                &nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; &nbsp;
               
                every
                    <input type="text" name="migration_generations"
                     size=2 value="$migration_generations">
                generations(s)</a></td>
     </tr>  
     
     <tr>
        <td>&nbsp;&nbsp;&nbsp; 
            5. <a class="plain" href="/mendel/$version/help.html#tc"
	          target="status" title="tribal_competition">
	           Competition between subpopulations?</a></LABEL></td>
        <td><input type="checkbox" name="tribal_competition" 
                    id="tribal_competition" onchange="fxn_tribes($max_tribes)"
                    value="on" $tribal_competition>
        </td>
     </tr>

     <tr>
        <td>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
          a. <label id="tcsf_label">
                <a class="plain" href="/mendel/$version/help.html#gssf"
                  target="status" title="tc_scaling_factor">
                  group selection scaling factor:</a></label>
        </td>
        <td> <input type="text" name="tc_scaling_factor" 
                    id="tc_scaling_factor"
                    value="$tc_scaling_factor"
                    title="0 - 1." disabled=true></td>
     </tr>

     <tr>
        <td> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
          b. <label>
                <a class="plain" href="/mendel/$version/help.html#gh"
                   target="status" title="group_heritability">
                   group heritability:</a> </label></td>
        <td> <input type="text" name="group_heritability" 
                    title="0 - 1\n0: max noise\n1: no noise"
                    onchange="check_value(this.value,0,1)"
                    value="$group_heritability"
                    title=""></td>
     </tr>
     </table>

     <table>
     <tr>
        <td width=350> &nbsp;&nbsp;&nbsp;
          <LABEL FOR="altruistic">
	      <a class="plain" href="/mendel/$version/help.html#alt"
	         tabindex="120" target="status" title="altruistic">
	      6. Upload altruistic mutations?</a>
          </LABEL>
        </td>
        <td><input type="checkbox" name="altruistic" value="on" 
             onclick="show_hide_mutation_upload_form(2)" $altruistic></td>
        <td></td>  
     </tr>

     <tr>
        <td width=350><LABEL FOR="social_bonus_factor">
	              <a class="plain" href="/mendel/$version/help.html#sbf" 
		         target="status" title="social_bonus_factor">
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
	a. social bonus scaling factor:</a> </LABEL></td>
        <td><input type="text" style="width:7em;" name="social_bonus_factor"
                   value="$social_bonus_factor" title="0 - 1"></td>
        <td></td>  
     </tr>

     <tr>
        <td width=350> <LABEL for="plot_avg_data">
	              <a class="plain" href="/mendel/$version/help.html#pad" 
		         target="status" title="plot_avg_data">
           &nbsp;&nbsp;&nbsp;
	         7. Average subpopulation data when plotting?
		       </LABEL></td>
        <td> <input type="checkbox" name="plot_avg_data"
                    value="on" $plot_avg_data $disable_parallel></td>
     </tr>	    
     </table>

     </div>

</div>
<!--*************************** COMPUTATION TAB *****************************-->
<div class="tab-page">
<h2 class="tab">computation</h2>
     
     <table>
     <tr>
        <td width=350> <LABEL for="auto_malloc">
             <a class="plain" href="/mendel/$version/help.html#malloc" 
                target="status" title="auto_malloc">
               1. Automatically allocate memory? </td>
        <td>      <input type="checkbox" name="auto_malloc" value="on"
                   onclick="fxn_allocate_memory()" $auto_malloc> </a></td>
     </tr>

     <tr>
        <td align=right> 
             <a class="plain" href="/mendel/$version/help.html#mtmpi" 
                target="status" title="max_del_mutn_per_indiv">
            &nbsp;&nbsp;&nbsp;  
	    :: maximum deleterious mutations per individual:</a> </LABEL></td>
        <td><input type="text" name="max_del_mutn_per_indiv" accesskey="0"
	           onchange="check_value(this.value,1000,5000000)" 
                   value="$max_del_mutn_per_indiv"></td>
     </tr>	   

     <tr>
        <td align=right> 
             <a class="plain" href="/mendel/$version/help.html#mtmpi" 
                target="status" title="max_fav_mutn_per_indiv">
            &nbsp;&nbsp;&nbsp;  
	    :: maximum favorable mutations per individual:</a> </LABEL></td>
        <td><input type="text" name="max_fav_mutn_per_indiv" accesskey="0"
	           onchange="check_value(this.value,1000,5000000)" 
                   value="$max_fav_mutn_per_indiv"></td>
     </tr>	   

     <tr>
        <td width=350> <LABEL for="track_neutrals">
	      2. <a class="plain" href="/mendel/$version/help.html#tnm" 
                    target="status" title="track_all_mutn" tabindex="133">
                  Track all mutations? </a><br>
                  &nbsp;&nbsp;&nbsp;
                  <font size="-2">(must be checked if allele statistics 
                                   are needed)</font></td> </label>
        <td>      <input type="checkbox" name="track_all_mutn" value="on"
                   onclick="fxn_track_all_mutn()" $track_all_mutn> </td>
     </tr>
     
     <tr>
        <td width=380> <LABEL for="tracking_threshold">
	       <a class="plain" href="/mendel/$version/help.html#tt" 
                    target="status" title="tracking_threshold" tabindex="133">
                  &nbsp;&nbsp;&nbsp;
                    To conserve memory and speed up runs, <br>
                  &nbsp;&nbsp;&nbsp;
                    do not track mutations with fitness effects less than: </a>
             </LABEL></td>
        <td><input type="text" name="tracking_threshold" accesskey="1"
                   onchange="check_value(this.value,0,1)"
                   title="1e-4 ~ 1e-8" value="$tracking_threshold"></td>
     </tr>   

     <tr>
        <td width=380> <LABEL for="extinction_threshold">
	    <a class="plain" href="/mendel/$version/help.html#et" 
               target="status" title="extinction_threshold" tabindex="133">
             3. Go extinct when mean fitness reaches: </a>
             </LABEL></td>
        <td><input type="text" name="extinction_threshold" accesskey="1"
                   onchange="check_value(this.value,0,1)"
                   title="0-1" value="$extinction_threshold"></td>
     </tr>   

     <tr>
        <td width=380> <LABEL for="random_number_seed">
	 4. <a class="plain" href="/mendel/$version/help.html#rns" target="status" title="random_number_seed" tabindex="134">Random number seed:</a> </LABEL></td>
	 <td><input type="text" name="random_number_seed" title="1 - 1000"
	           accesskey="2" value="$random_number_seed"></td>
     </TR>
     
     <tr>
        <td width=380> <LABEL for="write_dump">
	 5. <a class="plain" href="/mendel/$version/help.html#wd" target="status" title="write_dump" tabindex="135">Allow this run to be later re-started with new parameters? (these restart files are very large ~1GB)</a></LABEL></td>
	      <td> <input type="checkbox" name="write_dump" accesskey="3"
	            value="on" $write_dump></td>
     </tr>	    
     
     <tr>
        <td width=350> <LABEL for="restart_case">
	 6. <a class="plain" href="/mendel/$version/help.html#restart" target="status" title="restart_case" tabindex="136">Restart second (third, fourth) phase of run
	            with these new parameters?</a></LABEL></td>
        <td> <input type="checkbox" name="restart_case" accesskey="4"
		    onclick="fxn_restart_case()" value="on" $restart_case></td>
     </tr>	    
     </table>	    
     
     <div id="rddiv" style="display:none">
     <table>
     <tr>
        <td width=350> <LABEL for="restart_dump_number">
	    &nbsp;&nbsp;&nbsp;   :: restart from which phase of run:</LABEL></td>
	    <td><input type="text" name="restart_dump_number" title="1 - 100"
	           value="$restart_dump_number"></td>
     </tr>	   
     
     <tr>
        <td width=350> <LABEL for="restart_case_id">
	    &nbsp;&nbsp;&nbsp;   :: restart from which case ID:</LABEL></td>
	    <td><input type="text" name="restart_case_id"
	           title="must be six letters"
		          value="$restart_case_id"></td>
     </tr>		  
     <tr>
        <td width=380> <LABEL for="restart_append">
	 &nbsp;&nbsp;&nbsp;   :: append data to previous case:</LABEL></td>
        <td> <input type="checkbox" name="restart_append"
	            value="on" $restart_append></td>
     </tr>
     </table>	    
     </div>
     
     <table>
     <tr>
        <td width=380> <LABEL for="run_queue">
	 7. <a class="plain" href="/mendel/$version/help.html#rq"
	       target="status" title="run_queue" tabindex="138">
	       Queuing system:</a></LABEL></td>
        <td><select NAME= "run_queue" style="width=10em" title="hi-mem option only works on epiphany" $disable_queuing_system>
            $my_run_queue 
        </td>
        </select>
     </tr>
     <tr>
        <td width=380> <LABEL for="engine">
	 8. <a class="plain" href="/mendel/$version/help.html#cv"
               target="status">Simulation Engine:</a></LABEL></td>
        <td>
           <select NAME="engine" id="engine" $disable_engines>
           $my_engine
           </select>   
        </td>
     </tr>
     <tr>
        <td width=380> <LABEL for="plot_allele_gens">
	 9. <a class="plain" href="/mendel/$version/help.html#pag"
               target="status">Compute allele frequencies every:</a></LABEL></td>
        <td> <input type="text" name="plot_allele_gens" accesskey="1" style="width:50px" 
                   onchange="check_value(this.value,0,10000)"
                   title="0-1" value="$plot_allele_gens"> generations</td>
     </tr>
     </table>
</div>

<div class="tab-page">
<h2 class="tab">locked</h2>

<table>
<tr>
<td width=380> <LABEL for="">
	      1. <a class="plain" href="/mendel/$version/help.html#iha"
			       target="status" tabindex="129"
				  title="initial_heterozygous_alleles">
		 Initial heterozygous alleles:</a></LABEL> </td>
</tr><tr>		 
<td><LABEL for="num_contrasting_alleles">
     &nbsp;&nbsp;&nbsp;
      :: <a class="plain" href="/mendel/$version/help.html#nca" 
	    target="status" title="num_contrasting_alleles">
	    number of initial contrasting alleles:</a></LABEL> </td>
<td> <input type="text" name="num_contrasting_alleles" title="0 - 1"
	    accesskey="1" value="$num_contrasting_alleles"
	    onchange="alpha_warning()"
	    style="width:5em" $readonly ></td>
</tr><tr>	    
<td><LABEL for="max_total_fitness_increase">
     &nbsp;&nbsp;&nbsp;
     :: <a class="plain" href="/mendel/$version/help.html#mtfi"
	   target="status" title="max_total_fitness_increase">
	   maximum total fitness increase:</a></LABEL> </td>
<td> <input type="text" name="max_total_fitness_increase" title="0 - 1"
	    accesskey="1" value="$max_total_fitness_increase"
	    onchange="check_value(this.value,0,1)"
	    style="width:5em" $readonly ></td>
</tr>	    
     <tr>
	<td><LABEL for="">
	   <a class="plain" href="/mendel/$version/help.html#fomb" target="status">
              2. Include neutrals in analysis:</a> 
            </LABEL></td>
        <td><input type="checkbox" name="track_neutrals" 
                   title="" onclick="fxn_track_neutrals()" $track_neutrals></td>
        <td></td>
     </tr>
     <tr>
        <td><LABEL for="fraction_neutral">
	   &nbsp;&nbsp;&nbsp;    
              <a class="plain" href="/mendel/$version/help.html#fmun" 
                 target="status" title="fraction_neutral" tabindex="">
              :: fraction of genome which is non-functional <em>junk</em>:</a> 
        </LABEL> </td>
        <td><INPUT type="text" name="fraction_neutral" id="fmun" accesskey="1"
                   value="$fraction_neutral"
                   onchange="compute_u();fxn_fraction_neutral()"
                   title="0 - 1"></td>
     </tr>	   
     <tr>
	<td><LABEL for="uneu">
	   &nbsp;&nbsp;&nbsp; <a class="plain" 
                                 href="/mendel/$version/help.html#fomb" 
                                 target="status">
            <font color="grey">:: neutral mutation rate:</font></a> 
            </LABEL></td>
	<td><INPUT name="uneu" type="text" disabled=true></td>
        <td></td>
     </tr>
</table>
</div>

</div>
</div>

<div id="upload_mutations_div" style="display:none" align="center">
<fieldset style="background-color: white">
<legend>Upload Mutations</legend>

     <table>
     <tr>
<!--
        <td width=350><LABEL FOR="mutn_file_id">
	              <a class="plain" href="/mendel/$version/help.html#mfid" 
		         id="mutn_file_id_label" tabindex="120"
		         target="status" title="mutn_file_id">
	File id of mutations file:</a> </LABEL></td>
-->
        <td><input type="hidden" name="mutn_file_id" style="width:7em;"
                   value="$mutn_file_id"
                   title="Currently this filename cannot be changed" 
                   disabled="true"></td>
        <td></td>  
     </tr>
     </table>

<font size="+1">
     <a href="/mendel/$version/upload_mutations.xlsx">download worksheet</a> ::
     <label name="upload_mutn_link"><a href="javascript:cid=dmi.case_id.value;popUp('mutn_upload.cgi?run_dir=$run_dir&user_id=$user_id&case_id=' + cid + '&mutn_file_id=$mutn_file_id',600,600);">upload mutations</a></label> ::
     <label name="upload_mutn_link"><a href="javascript:cid=dmi.case_id.value;mfid=dmi.mutn_file_id.value;popUp('more.cgi?user_id=$user_id&case_id='+cid+'&file_name='+mfid+'&nothing=$nothing',600,600);">view mutations</a></label> 
</font>
</fieldset>
</div>

<font color="red" size="+1"> <div align=center id="note_to_user"> </div> </font> 
<input type="hidden" name="version" value="$version">
<input type="hidden" name="quota" value="$quota">
<input type="hidden" name="run_dir" value="$run_dir">

</form>

End_of_Doc

# Now that all the user input parameters are known,
# initialize screen with all the proper settings
# Rest of initialization is done using the JS fxn_init() function
# Actually this code is done BEFORE fxn_init() called.
# fxn_init() is called on ready event.

$ojs = "<script language=\"Javascript\">";
$cjs = "</script>\n";

# This needs to be defined here first 
print $ojs."dmi = document.mendel_input".$cjs;

if($synergistic_epistasis eq "CHECKED") {
   print $ojs."fxn_synergistic_epistasis_able();".$cjs;
} else {
   print $ojs."fxn_synergistic_epistasis_disable();".$cjs;
}

# show or hide partial_truncation_value based on initial setting

if($selection_scheme_number eq "4") {
   print $ojs."document.getElementById(\"ptv\").style.display = \"block\";".$cjs;
} else {
   print $ojs."document.getElementById(\"ptv\").style.display = \"none\";".$cjs;
}

if($pop_growth_number eq "0") {
   print $ojs."dmi.pop_growth_rate.disabled = true;".$cjs;
} else {
   print $ojs."dmi.pop_growth_rate.disabled = false;".$cjs;
}

print "</body>";
print "</html>";

