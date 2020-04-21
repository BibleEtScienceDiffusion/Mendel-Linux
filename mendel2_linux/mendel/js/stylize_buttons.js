/**

	this plugin converts ugly submit buttons to nice looking buttons
	see: http://www.oscaralexander.com/tutorials/how-to-make-sexy-buttons-with-css.html

	This jQuery plugin is created by Jankees van Woezik for www.base42.nl
	Date: October 3, 2008
 */

jQuery.fn.stylizeButton = function() {
  return this.each(function(){
  
   //value is the text in the button
   var value = this.value;
   var id = this.id;

   if($(this).attr("stylizeAction") == "submit"){

   	 $(this).css({ display:"none"});
   	 $(this).after("<a id='"+id+"' class='button' onclick=\"$(\'form\').submit();\"><span>"+value+"</span></a>");

   }else  if($(this).attr("stylizeAction") == "clean"){
	
   	 $(this).css({ display:"none"});
	 $(this).after("<a class='button'><span>"+value+"</span></a>");

   }else{
       	//sorry for now i only do submit buttons and clean buttons
	}
    
  });
};
