include version
include make.in

RM	= rm
ECHO	= echo
DIRS	= cgi-bin/cmendel cgi-bin/fmendel
EXE	= mendel
OBJS	= main.o
OBJLIBS = 
LIBS    = 

$(EXE) : main.o $(OBJLIBS)
	$(ECHO) $(LD) -o $(EXE) $(OBJS) $(LIBS)
	$(LD) -o $(EXE) $(OBJS) $(LIBS)

cmendel : force_look
	$(ECHO) looking into cmendel : $(MAKE) $(MFLAGS)
	cd cgi-bin/cmendel; $(MAKE) $(MFLAGS)

fmendel : force_look
	$(ECHO) looking into fmendel : $(MAKE) $(MFLAGS)
	cd cgi-bin/fmendel; $(MAKE) $(MFLAGS)

clean :
	$(ECHO) cleaning up in .
	-$(RM) -f $(EXE) $(OBJS) $(OBJLIBS)
	-for d in $(DIRS); do (cd $$d; $(MAKE) clean ); done

force_look :
	true

install: install-html install-css install-js install-cgi \
	install-images install-cmendel post-install

install-html:
	@echo You must be root to install
	install -d $(HTMLD)/v$(VERSION)
	install -m 644 index.php $(HTMLD)
	install -m 644 favicon.ico $(HTMLD)
	install -m 644 html/account.html $(HTMLD)/v$(VERSION)
	install -m 644 html/other.html $(HTMLD)/v$(VERSION)
	install -m 644 html/index.php $(HTMLD)/v$(VERSION)
	install -m 644 html/intro.html $(HTMLD)/v$(VERSION)
	install -m 644 html/tips.html  $(HTMLD)/v$(VERSION)
	install -m 644 html/tips.js    $(HTMLD)/v$(VERSION)
	install -m 644 html/toc.php    $(HTMLD)/v$(VERSION)
	install -d $(HTMLD)/v$(VERSION)/images
	install -m 644 html/images/logo.png   $(HTMLD)/v$(VERSION)/images
	install -m 644 html/images/mendel.png $(HTMLD)/v$(VERSION)/images
	install -m 644 help.html $(HTMLD)

install-images:
	install -d $(HTMLD)/images
	install -m 644 images/button.gif $(HTMLD)/images
	install -m 644 images/logo.png $(HTMLD)/images
	install -m 644 images/mendel.png $(HTMLD)/images
	install -m 644 images/nodata.png $(HTMLD)/images
	install -d $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/lock.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/application_go.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/application_double.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/arrow_branch.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/chart_curve.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/comment.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/compress.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/cross.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/delete.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/folder_explore.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/folder_page.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/information.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/lock_open.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/lock.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/page_white_get.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/page_white_put.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/textfield_rename.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/tick.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/time_add.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/user.png $(HTMLD)/images/famfamfam.com
	install -m 644 images/famfamfam.com/world_link.png $(HTMLD)/images/famfamfam.com

install-css:
	install -d $(HTMLD)/css
	install -m 644 css/form.css $(HTMLD)/css
	install -m 644 css/style1.css $(HTMLD)/css
	install -m 644 css/style2.css $(HTMLD)/css
	install -m 644 css/tab.webfx.css $(HTMLD)/css

install-js:
	install -d $(HTMLD)/js
	install -m 644 js/jquery.js $(HTMLD)/js
	install -m 644 js/general.js $(HTMLD)/js
	install -m 644 js/stylize_buttons.js $(HTMLD)/js
	install -m 644 js/tabpane.js $(HTMLD)/js
	install -d $(HTMLD)/js/flot
	install -m 644 js/flot/excanvas.js $(HTMLD)/js/flot
	install -m 644 js/flot/excanvas.pack.js $(HTMLD)/js/flot
	install -m 644 js/flot/index.html $(HTMLD)/js/flot
	install -m 644 js/flot/jquery.flot.js $(HTMLD)/js/flot
	install -m 644 js/flot/jquery.flot.pack.js $(HTMLD)/js/flot
	install -m 644 js/flot/jquery.js $(HTMLD)/js/flot
	install -m 644 js/flot/README.txt $(HTMLD)/js/flot

install-cgi:
	install -d $(CGID)/v$(VERSION)
	install -m 644 cgi-bin/config.inc $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/delete.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/diff.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/input_file_writer.pl $(CGID)/v$(VERSION)
	install -m 644 cgi-bin/input_file_parser.inc $(CGID)/v$(VERSION)
	install -m 644 cgi-bin/input_file_reader.inc $(CGID)/v$(VERSION)
	install -m 644 cgi-bin/label_form.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/label_post.pl $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/list_cases.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/list_files.cgi $(CGID)/v$(VERSION)
	install -m 644 cgi-bin/memory.inc $(CGID)/v$(VERSION)
	install -m 644 cgi-bin/mendel.in $(CGID)/v$(VERSION)
	install -m 644 cgi-bin/mendel.in.yeast $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/monitor.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/monitor.ajax $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/more.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/output.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/parse.inc $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/plot_gnuplot_modify.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/plot_gnuplot_recipes.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/plot_gnuplot.cgi $(CGID)/v$(VERSION)
	install -m 644 cgi-bin/plot_gnuplot_combine.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/qdel.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/qmpd.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/qstat.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/qstat_main.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/qsub.pl $(CGID)/v$(VERSION)
	install -m 644 cgi-bin/readme $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/rename.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/start.cgi $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/with_selected.cgi $(CGID)/v$(VERSION)

install-cmendel:
	install -d $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/cmendel/mendel $(CGID)/v$(VERSION)/cmendel.exe

install-fmendel:
	install -d $(CGID)/v$(VERSION)
	install -m 755 cgi-bin/fmendel/mendel $(CGID)/v$(VERSION)/mendel.exe

post-install:
	install -m 777 -d $(MUD)
	@echo Now open the URL http://localhost/mendel/v$(VERSION)/index.php

testdeps:
	$(PERL) ./sbin/test-dependencies --verbose 

distclean:
	\rm -rf win/cgi-bin win/cmendel win/htdocs win/installer.nsi
	rm wmendel-$(VERSION).tgz
uninstall:
	rm -rf $(HTMLD)/v$(VERSION)
	rm -rf $(CGID)/v$(VERSION)
	rm -rf $(HTMLD)/help.html
	rm -rf $(HTMLD)/js
	rm -rf $(HTMLD)/css
	rm -rf $(HTMLD)/images

