--------------------------------------------------------------------------
MENDELS ACCOUNTANT LINUX VERSION
--------------------------------------------------------------------------

To get the latest Linux version (v2.5), one can install SPC & MENDEL as follows:

1. install SPC
> git clone https://github.com/whbrewer/spc.git && cd spc

2. install python
> sudo apt-get install python python-pip; sudo pip install virtualenv pathlib2

3. create database and config file
> ./spc init 

4. install Mendel
> ./spc install https://github.com/whbrewer/fmendel-spc-linux/archive/master.zip

5. start server (must always be running in order to use Mendel's Accountant)
> ./spc run 

6. Open browser to http://localhost:8580 to access Mendel's Accountant

--------------------
MENDEL ON CHROMEBOOK
--------------------

The latest version of Mendel's Accountant can also run on a Google Chromebook.  To 
install on a Chromebook first requires putting the Chromebook in developer mode by
following the instructions here:

http://lifehacker.com/how-to-install-linux-on-a-chromebook-and-unlock-its-ful-509039343

Next, bring up shell by clicking Ctrl+Alt+T, and enter the command "shell" at the "crosh>" prompt.  
Then, enter "sudo enter-chroot".  Then enter commands 1-5 above at the command prompt
to install and use Mendel's Accountant.

-------
v2.0.2
-------

The LINUX version of Mendels Accountant has been tested on the following
Linux distros: Ubuntu, SuSE, Fedora, and Debian. It should also work on
similar variants such as CentOS and Redhat.

This version has pre-compiled binaries included, so no compilation needs
to be done.  However, this is a 32-bit binary version, so if you are 
running a 64-bit version of Linux and do not have the libraries installed 
to run 32-bit binaries, you will need to install the 32-bit libraries 
using a command such as:

    * sudo apt-get install ia32-libs

NOTE: There is a bug in the Flot plotting system which causes the plots
not to work correctly on a few Linux distributions.  If this is a problem, 
you may want to try using a different browser, or a different version of 
Linux.  We are working to fix this and release an updated version ASAP.

- The Mendels Accountant Development Team

---------------------------------------------------------------------------
INSTALLATION INSTRUCTIONS
---------------------------------------------------------------------------

  1. Download the distribution

  2. Unpack the distribution. For example:

> tar xvfz mendel_v2.0.2_linux.tgz 

  3. Run the install script:
 
> ./install

---------------------------------------------------------------------------
HOW TO START USING MENDELS ACCOUNTANT
---------------------------------------------------------------------------

  To start using Mendels Accountant, point your web browser to the 
  following URL:

     http://localhost/mendel/v2.0.2/index.html

---------------------------------------------------------------------------
ADDITIONAL NOTES
---------------------------------------------------------------------------

1. During installation, this version will ask you how much memory
you want to allow MENDEL to use. If you need to change the amount
of memory which Mendel uses, edit the file:
/Library/WebServer/CGI-Executables/v2.0/config.inc
and the value of the variable $ram_per_job to the amount of RAM you
have available.  More RAM means larger population sizes, more linkage
blocks, etc.

2. If you already have Mendel installed, you may want to uninstall
before installing a new version.  If you uninstall Mendel, your
data will still remain on your system and you will have access
with the newer version.
