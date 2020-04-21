chop($thisos=`uname`);
chop($hostname=`hostname`);

$det = "disabled=true";

$disable_pbs = $disable_himem = $det;
$disable_parallel = $det;

$url_dir="/mendel_user_data";
$run_dir="XYZ$url_dir";
$this_server="Linux";
$ram_per_job=256;

# only for parallel 
$max_ram_per_node=256;
$max_tribes = 1;
$procs_per_node = 1;
$num_nodes = 1;
