#!/usr/bin/perl
##############################################################################
# This file shows real-time plots of the simulation while running
# by utilizing the Flot jQuery plotting library.  Data is updated
# about every 5 seconds, using ajax calls to monitor.ajax which
# extracts the data from the files and re-formats to a data that
# jQuery likes.
##############################################################################

require "./parse.inc";
require "./config.inc";

$case_id=$formdata{'case_id'};
$user_id=$formdata{'user_id'};

print "Content-type:text/html\n\n";
print <<End_of_Doc;
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<html><head>
<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
<title>Animated Output Case $case_id User $user_id</title>
<script language="javascript" type="text/javascript" src="/mendel/js/flot/excanvas.pack.js"></script>
<script language="javascript" type="text/javascript" src="/mendel/js/flot/jquery.js"></script>
<script language="javascript" type="text/javascript" src="/mendel/js/flot/jquery.flot.js"></script>
<script language="javascript" type="text/javascript" src="/mendel/js/flot/jquery.flot.axislabels.js"></script>
</head>
<body>

<table>
<tr>
<td><div id="dmutn" style="width:324px;height:200px;"></div> </td>
<td><div id="fmutn" style="width:324px;height:200px;"></div> </td>
</tr>
<tr>
<td><div id="fit" style="width:324px;height:200px;"></div> </td>
<td><div id="thr" style="width:324px;height:200px;"></div> </td>
</tr>
</table>

<div id="output" style="width:648px;height:200px;"></div>

<script language="Javascript" type="text/javascript">

var ajaxCall = function(cid, uid, ptype, placeholder, ylabel, interval){
	//id = id || 1;
	jQuery.ajax({
	url: 'monitor.ajax',
	data: {case_id: cid, user_id: uid, plot: ptype},
	type: "POST",
	complete: function(xhr){
		var plot_data = xhr.responseText;
		plot_data = eval(plot_data);
		//\$.plot(placeholder, [ plot_data ]);
                \$.plot(placeholder, [ { data: plot_data, 
                                               color: "rgb(0, 0, 255)" } ],
                                       { xaxis:  { axisLabel: 'Generations', 
                                                   axisLabelFontSizePixels: 12  },
                                         yaxis:  { axisLabel: ylabel, 
                                                   axisLabelOffset: -70,
                                                   axisLabelFontSizePixels: 12  } });
           	//console.log(arguments, plot_data);
		setTimeout(function(){
			ajaxCall(cid, uid, ptype, placeholder, ylabel, interval)
		}, interval)
	}})
}

showOutput = function(){
   jQuery('#output').load('output.cgi?case_id=$case_id&user_id=$user_id&num_lines=11&ajax=1', function(){
      setTimeout(showOutput, 5000);
   })
}

ajaxCall("$case_id", "$user_id", 'dmutn.hst', \$("#dmutn"), 'Del mutn/indiv', 5000);
ajaxCall("$case_id", "$user_id", 'fmutn.hst', \$("#fmutn"), 'Fav mutn/indiv', 5000);
ajaxCall("$case_id", "$user_id", 'fit.hst', \$("#fit"), 'Mean Fitness', 5000);
//ajaxCall("$case_id", "$user_id", 'ddst.dst', \$("#ddst"), 'Del Dist', 12000);
ajaxCall("$case_id", "$user_id", 'thr.thr', \$("#thr"), 'Del Sel Threshold', 13000);
showOutput();

</script>
End_of_Doc

#$auto = 1;
#$num_lines = 8;
#require "./output.cgi";


print "</body>";
print "</html>";

