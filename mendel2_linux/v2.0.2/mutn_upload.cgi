#!/usr/bin/perl
require "./parse.inc";

print "Content-type:text/html\n\n";
#$run_dir=$formdata{'run_dir'};
$user_id=$formdata{'user_id'};
$case_id=$formdata{'case_id'};
$case_dir="$run_dir/$user_id/$case_id";
#$mutn_file_id=$formdata{'mutn_file_id'};
$mutn_file_id="${case_id}_mutn.in";

#print "run_dir is: $run_dir<br>";
#print "user_id is: $user_id<br>";
#print "case_id is: $case_id<br>";
#print "mutn_file_id is: $mutn_file_id<br>";
#print "case_dir is: $case_dir<br>";

if($case_id eq "") {
    print "<h2>ERROR: case_id missing.</h2>";
    print "Solution: Set case_id before uploading mutations.";
    die;
}

print <<zZzZ;
<html>
<head>
<style>
table {
  margin: 1em 1em 1em 2em;
  background: whitesmoke;
  border-collapse: collapse;
}
table th, table td {
  border: 1px silver solid;
  padding: 0.2em;
}
table th {
  background: gainsboro;
  text-align: left;
}
table caption {
  margin-left: inherit;
  margin-right: inherit;
}
</style>
</head>

<body>
<h2>Paste in mutations in the following area:</h2>

<p> Note: the mutation table should have the following form:</p>

<table>
<tr>
<th><label title="1 to pop_size">individual</label></th>
<th><label title="1 to num_linkage_blocks">linkage_block</label></th>
<th><label title="1 or 2">hap_id</label></th>
<th><label title="0.00001~1\n+ beneficial\n- deleterious">fitness</label></th>
<th><label title="+1:dominant\n-1:recessive">dominance</label></th>
<tr><td>1 to pop_size</td><td>1 to num_linkage_blocks</td> <td>1 or 2</td> <td>+/-0.000001 to +/-1<br>-: deleterious<br>+:favorable</td><td>-1 or 1<br>1:dominant<br>-1:recessive</td></tr>
</tr>
</table>

<p>Also, there should <u>not</u> be a header row. So, for example:</p>

<table>
<tr><td>56</td> <td>407</td> <td>2</td> <td>-0.000117976</td><td>1</td></tr>
</table>


   <form name="upload_mutations_form" method=post action="./mutn_parse_write.cgi">
      <textarea name="mutn_table" rows="15" cols="55"></textarea><BR><BR>
      <input type="hidden" name="run_dir" value="$run_dir">
      <input type="hidden" name="user_id" value="$user_id">
      <input type="hidden" name="case_id" value="$case_id">
      <input type="hidden" name="mutn_file_id" value="$mutn_file_id">
      <input type="submit" onClick="window.opener.document.forms['mendel_input'].mutn_file_id.value = this.form.mutn_file_id.value;" value="Upload Mutations"> 
      <!-- <input type="submit" onClick="myfile='<a href=test.html>$mutn_file_id</a>'; window.opener.document.getElementById("mutn_file_id_label").innerHTML = myfile;" value="Upload Mutations"> -->
      <input type="reset">
   </form>
</body>
</html>
zZzZ
