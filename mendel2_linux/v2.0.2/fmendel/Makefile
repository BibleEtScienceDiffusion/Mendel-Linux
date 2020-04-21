#FC = /opt/intel/fc/10.0.026/bin/ifort -vec-report0
FC = /opt/intel/bin/ifort
#FC = /opt/pgi/linux86-64/8.0-4/bin/pgf90 # c101
#FC = /usr/local/bin/mpif90
#FC = gfortran

# Following are needed for building parallel version
# Comment out if compiling with mpif90
# or if making serial version.
#LIBS = -lmpich -lpthread -lmpl

# Compiler flags
#FCFLAGS = -g # debug version
FCFLAGS = -O3 # release version

# Linker flags (gfortran on OSX)
#LDFLAGS = -static-libgfortran -static-libgcc

# executable name
TARGET = mendel

OBJECTS = sort.o random_pkg.o mendel.o mpi_mendel.o

##########################################
# build rules
##########################################

# target program
$(TARGET) : $(OBJECTS)
	$(FC) $(FCFLAGS) $(LDFLAGS) -o $(TARGET) $(OBJECTS) $(LIBS)

serial:
	cp -n mendel.f mendel_par.f
	cp -n mpi_mendel.f mpi_mendel_par.f
	sed -i '/START_MPI/,/END_MPI/d' mendel.f     
	sed -i '/START_MPI/,/END_MPI/d' mpi_mendel.f 

# make parallel should only be run if make serial has been previously run
# to restore the original files
parallel:
	mv -f mendel_par.f mendel.f
	mv -f mpi_mendel_par.f mpi_mendel.f
cln:
	\rm -f mendel.o mpi_mendel.o mendel

clean:
	\rm -f *.o *.mod $(TARGET) 

distclean:
	\rm -f $(OBJECTS) $(TARGET) $(DEPEND_FILES)


###########################################
# dependencies
###########################################

sort.o:		sort.f90
	$(FC) $(FCFLAGS) -c sort.f90

random_pkg.o:	random_pkg.f90
	$(FC) $(FCFLAGS) -c random_pkg.f90

mendel.o:       mendel.f common.h
	$(FC) $(FCFLAGS) -c mendel.f

mpi_mendel.o:	mpi_mendel.f common.h
	$(FC) $(FCFLAGS) -c mpi_mendel.f

