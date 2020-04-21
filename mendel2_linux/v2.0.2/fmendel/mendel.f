      program mendel

      use random_pkg
      include 'common.h'
      include '/usr/local/include/mpif.h'

      real*8,  allocatable, dimension(:,:,:)   :: linkage_block_fitness,
     &                                              offsprng_lb_fitness
      integer, allocatable, dimension(:,:,:)   :: dmutn, dmutn_offsprng,
     &                                            fmutn, fmutn_offsprng
      integer, allocatable, dimension(:,:,:,:) :: lb_mutn_count,
     &                                            offsprng_lb_mutn_count
      real,    allocatable, dimension(:) :: initial_allele_effects
      real*8,  allocatable, dimension(:) :: fitness, pheno_fitness
      real*8,  allocatable, dimension(:) :: work_fitness, sorted_score
      logical, allocatable, dimension(:) :: available,
     &                                      replaced_by_offspring
      integer i, j, k, lb, m, n, gen, dad, mom, child, mutn, slot
      integer npath, max_size, this_size, gen_0, shutdown_gen
      integer total_offspring, actual_offspring, gen_count, run_status
      integer other_run_status, bottleneck_modulo
      integer dest, status2(MPI_Status_size,2), requests(2)
      integer offspring_count, empty, replace, parent, red, green, blue
      integer ica_count(2), cumulative_offspring
      integer max_pop_size, pop_size_allocation, current_global_pop_size
      integer pop_lost, pop_lost_recvd
      integer global_pop, mean_pop, delta_pop, delta
      integer OLDGROUP,NEWGROUP,ranks(1),num_tribes_at_start
      integer, allocatable, dimension(:) :: global_run_status
      integer, allocatable, dimension(:) :: pop_size_array

      real*8 accum(50)
      real carrying_capacity, reproductive_advantage_factor, x
      real tribal_score, random_effects, genetic_effects, social_effects
      real fraction_elimination, fraction_selected_away
      real fertility_factor, random, num_offspring, fav_mutn_per_gen, d
      real fitness_adjusted_offspring
      real real_pop_size
      real tin_migration, tout_migration, tin_gen, tout_gen
      real tin_offspring, tout_offspring, tgen, par_tgen
      real tin_diagnostics, tout_diagnostics
      real total_time_offspring, time_offspring, time_selection
      real par_time_offspring, par_time_selection, tsub
      logical found, print_flag, am_parallel
      character*3 myid_str

      call second(tin)

      open (5, file='mendel.in', status='old')
c      open (5, file='namelist.input', status='old')

c...  Read input parameters from input file mendel.in.

      call read_parameters(5)

      close(5)

c...  Perform certain initializations including opening files.

      call initialize(myid_str)
      run_status = 0

      if(is_parallel) then 
c       Since we may turn off is_parallel in case a tribe dies,
c       remember the original state.
        am_parallel = .true.
        num_tribes_at_start = num_tribes
c       compute global population size
        call mpi_isum(pop_size,global_pop_size,1)
        call mpi_mybcasti(global_pop_size,1)
        allocate( global_run_status(num_tribes) )
        allocate( pop_size_array(num_tribes) )
      else
        am_parallel = .false.
      endif
 
      if(is_parallel .and. tribal_competition) then
         global_run_status = 0
         run_status = 0
         other_run_status = 0
         pop_size_array = pop_size
         pop_size_allocation = global_pop_size
         write(*,*) 'Allocating tribe ', myid, ' with max pop_size of:',
     &                pop_size_allocation
      elseif (pop_growth_model > 0) then
c..      Pass in max_pop_size through num_generations input parameter 
         max_pop_size = num_generations
         pop_size_allocation = max_pop_size       
      else
         pop_size_allocation = pop_size
      endif

      if(tribal_competition) then
         fraction_selected_away = 1. - 1./reproductive_rate
         tribal_fitness_factor = 1.0
         max_size = int(0.55*12.*pop_size_allocation
     &                      *(1. - fraction_random_death))
         n = 12.*(1. - fraction_random_death) + 0.999
c...     Limit the minimum value of heritability to be 10**-20.
         group_heritability = max(1.e-20, group_heritability)
      else
         max_size = int(1.1*reproductive_rate*pop_size_allocation
     &                     *(1. - fraction_random_death))
         n = 2.*reproductive_rate*(1. - fraction_random_death) + 0.999
      end if

c...  Allocate memory for large arrays.

      allocate(         dmutn(max_del_mutn_per_indiv/2,2,max_size),
     &                  fmutn(max_fav_mutn_per_indiv/2,2,max_size),
     &         dmutn_offsprng(max_del_mutn_per_indiv/2,2,n),
     &         fmutn_offsprng(max_fav_mutn_per_indiv/2,2,n),
     &                 lb_mutn_count(num_linkage_subunits,2,2,max_size),
     &        offsprng_lb_mutn_count(num_linkage_subunits,2,2,n),
     &         linkage_block_fitness(num_linkage_subunits,2,max_size),
     &           offsprng_lb_fitness(num_linkage_subunits,2,n),
     &        initial_allele_effects(num_linkage_subunits),
     &         pheno_fitness(max_size),      fitness(max_size),
     &          work_fitness(max_size), sorted_score(max_size), 
     &                        available(pop_size_allocation), 
     &            replaced_by_offspring(pop_size_allocation))

c...  If this is a restart case, read the restart dump file and
c...  set the current dump number to the restart dump number.
c...  Otherwise, set it to zero.  The variable gen_0 is the initial
c...  generation number, retrieved from the restart dump in a restart
c...  case and zero otherwise.

      if(restart_case) then
         call read_restart_dump(dmutn,fmutn,lb_mutn_count,
     &                          linkage_block_fitness,
     &                          initial_allele_effects,
     &                          gen_0,max_size,myid_str)
         dump_number = restart_dump_number
      else
         gen_0 = 0
         dump_number = 0
      end if

c...  If the bottleneck flag, bottleneck_yes, is false, set the value
c...  of bottleneck_generation beyond the generation range for this run.

      if(.not.bottleneck_yes) bottleneck_generation = 1 + gen_0
     &                                              + num_generations

c...  Initialize the population size to be equal to the parameter
c...  pop_size unless the parameter bottleneck_generation has the
c...  value zero.  In the latter case, initialize the population size 
c...  to bottleneck_pop_size.

      if(abs(bottleneck_generation) > 0) then
         current_pop_size = pop_size
      else
         current_pop_size = bottleneck_pop_size
      end if

c...  Setup cyclic bottlenecking

      if(bottleneck_yes.and.bottleneck_generation < 0) then
         if(num_bottleneck_generations >= abs(bottleneck_generation))
     &   then
            write(*,*) 'ERROR: num_bottleneck_generations ',
     &                 '>= cyclic bottleneck_generations'
            stop
         end if  
         bottleneck_modulo = abs(bottleneck_generation)
         bottleneck_generation = abs(bottleneck_generation)
         cyclic_bottlenecking = .true.
      end if

c...  If not a restart case, initialize entire population to have no 
c...  initial mutations.   

c...  Initialize the linkage block fitness such that all individuals
c...  in the population have identical haplotypes.  If initial 
c...  contrasting alleles are to be included, generate them here. 

      if(.not.restart_case) then
         dmutn = num_linkage_subunits*lb_modulo + 1
         fmutn = num_linkage_subunits*lb_modulo + 1
         dmutn(1,:,:)  = 0
         fmutn(1,:,:)  = 0
         lb_mutn_count = 0 
         linkage_block_fitness = 1.d0
         if(num_contrasting_alleles > 0) 
     &      call gen_initial_contrasting_alleles(dmutn, fmutn,
     &         linkage_block_fitness, initial_allele_effects, max_size)
      end if

c...  Read in a file containing a specific set of mutations.

      if(upload_mutations) then
         call read_mutn_file(dmutn,fmutn,lb_mutn_count,
     &                       linkage_block_fitness,max_size)
      end if

c...  Generate num_initial_fav_mutn random initial favorable mutations.

      do k=1,num_initial_fav_mutn
         call favorable_mutn(fmutn,lb_mutn_count,linkage_block_fitness)
      end do

      post_sel_fitness  = 1.d0 
      ica_count         = 0

c...  Step population through num_generations generations.

      call second(tout)
      sec(1) = sec(1) + tout - tin

      do gen=gen_0+1,gen_0+num_generations

         msg_num = 1

         call second(tin_gen)

c...     If the generation number lies within the bottleneck interval,
c...     set the current population size to bottleneck_pop_size.

         if(cyclic_bottlenecking.and.
     &      (mod(gen,bottleneck_modulo)==0
     &      .and.gen>gen_0+1+bottleneck_modulo)) then
            bottleneck_generation = bottleneck_generation + 
     &                              bottleneck_modulo
         end if

         if(bottleneck_yes .and. gen >= bottleneck_generation .and.
     &      gen <  bottleneck_generation + num_bottleneck_generations)
     &   then
            current_pop_size = bottleneck_pop_size
            write(6,'(/"BOTTLENECK down to ",
     &                i6," individual(s) at generation = ",i6)') 
     &                bottleneck_pop_size, gen
            write(9,'(/"BOTTLENECK down to ",
     &                i6," individual(s) at generation = ",i6)') 
     &                bottleneck_pop_size, gen
         end if

         fertility_factor = 1. - fraction_random_death

c...     For competing tribes compute tribal fertility factor.

         if(is_parallel .and. tribal_competition .and. 
     &      gen > gen_0+1) then
      
            reproductive_advantage_factor = tribal_fitness_factor-1.

c...        Compute the tribal fertility factor.

c...        Additive changes.

            fertility_factor = (1. - fraction_random_death)
     &                         *(1. + tc_scaling_factor
     &                         *reproductive_advantage_factor)

            if(mod(gen,10)==0) then
               write(*,'("myid =",i2," fertility_factor =",f7.4)')
     &               myid, fertility_factor
            end if

         endif

c...     Move individuals between tribes/processors.

         if (is_parallel.and.mod(gen,migration_generations)==0.and.
     &       num_indiv_exchanged > 0) then
            call second(tin_migration)
            if(mod(gen,10)==0 .and. myid==0) then
               write(6,'(/"migrating ",i4," individual(s) every",
     &             i4," generation(s) between",i4," tribe(s)")')
     &             num_indiv_exchanged, migration_generations,
     &             num_tribes
               if(tribal_competition) then
                  write(*,*) 'competing pop sizes:', pop_size_array
               endif
                   
            end if
            call mpi_migration(dmutn,fmutn,linkage_block_fitness,
     &           lb_mutn_count,gen,ierr,msg_num,available)
            call second(tout_migration)
            sec(3) = sec(3) + tout_migration - tin_migration
         end if

         call second(tin_offspring)

         available = .true.
         replaced_by_offspring = .false.
         post_sel_fitness = 1.d0
         total_offspring  = current_pop_size 
         offspring_count  = 0
         num_offspring    = 2.*reproductive_rate*fertility_factor

         if(mod(gen - gen_0, 10) == 1 .or. gen - gen_0 <= 10) then
            cumulative_offspring = 0
            new_mutn_count       = 0
         end if

c...     Re-initialize random number generator.

         d = randomnum(-abs(random_number_seed+myid+gen-gen_0))

         do i=1,current_pop_size/2

c...        Randomly mate one half of the population with members
c...        from the other half.

            dad = min(current_pop_size,
     &            1 + int(current_pop_size*randomnum(1)))

            do while(.not.available(dad))
               dad = mod(dad, current_pop_size) + 1
            end do
            available(dad) = .false.

            mom = min(current_pop_size, 
     &            1 + int(current_pop_size*randomnum(1)))
            do while(.not.available(mom))
               mom = mod(mom, current_pop_size) + 1
            end do
            available(mom) = .false.

c...        Generate an appropriate number offspring from
c...        the two parents. 

            if(fitness_dependent_fertility) then
               fitness_adjusted_offspring = num_offspring
     &            *sqrt(min(1.d0, post_sel_fitness))
               actual_offspring = int(fitness_adjusted_offspring)
               if(fitness_adjusted_offspring - actual_offspring >
     &            randomnum(1)) actual_offspring = actual_offspring + 1
            else
               actual_offspring = int(num_offspring)
               if(num_offspring - int(num_offspring) > randomnum(1))
     &            actual_offspring = actual_offspring + 1
            end if

            if(i == 1) actual_offspring = max(1, actual_offspring)

            actual_offspring = min(int(num_offspring) + 1,
     &                              actual_offspring)

c...        If the parameter fraction_self_fertilization is non-zero
c...        (as can be the case for many types of plants), implement
c...        self-fertilization for the appropriate portion of the
c...        population by calling routine offspring using 'dad' for
c...        both parents for half the offspring and 'mom' for both
c...        parents for the other half.

            time_offspring = 0

            do child=1,actual_offspring

               if(fraction_self_fertilization < randomnum(1)
     &            .and. .not.clonal_reproduction) then

c...              This call generates an offspring from a sexual
c...              union of the two individuals dad and mom.

                  call offspring(dmutn_offsprng(1,1,child),
     &                           fmutn_offsprng(1,1,child),
     &                 offsprng_lb_mutn_count(1,1,1,child),
     &                      offsprng_lb_fitness(1,1,child),
     &                           dmutn,fmutn,lb_mutn_count,
     &                  linkage_block_fitness,dad,mom,tsub)

               elseif(actual_offspring >= 2 .and. child == 1) then

c...              This call generates an offspring exclusively
c...              from the genetic makeup of individual -dad-.
c...              If the parameter clonal_reproduction is .true.,
c...              the offspring is a clone of -dad- except for
c...              possible new mutations.  If not, the genotype
c...              of the offspring is the product of gametic 
c...              shuffling of the chromosomes of -dad- via
c...              self-fertilization.

                  call offspring(dmutn_offsprng(1,1,child),
     &                           fmutn_offsprng(1,1,child),
     &                 offsprng_lb_mutn_count(1,1,1,child),
     &                      offsprng_lb_fitness(1,1,child),
     &                           dmutn,fmutn,lb_mutn_count,
     &                  linkage_block_fitness,dad,dad,tsub)

               elseif(actual_offspring >= 2 .and. child == 2) then

c...              This call generates an offspring exclusively
c...              from the genetic makeup of individual -mom-.
c...              If the parameter clonal_reproduction is .true.,
c...              the offspring is a clone of -mom- except for
c...              possible new mutations.  If not, the genotype
c...              of the offspring is the product of gametic 
c...              shuffling of the chromosomes of -mom- via
c...              self-fertilization.

                  call offspring(dmutn_offsprng(1,1,child),
     &                           fmutn_offsprng(1,1,child),
     &                 offsprng_lb_mutn_count(1,1,1,child),
     &                      offsprng_lb_fitness(1,1,child),
     &                           dmutn,fmutn,lb_mutn_count,
     &                  linkage_block_fitness,mom,mom,tsub)

               else

                  if(randomnum(1) < 0.5) then
                     parent = dad
                  else
                     parent = mom
                  end if

c...              This call generates an offspring exclusively
c...              from the genetic makeup of individual parent.
c...              If the parameter clonal_reproduction is .true.,
c...              the offspring is a clone of parent except for
c...              possible new mutations.  If not, the genotype
c...              of the offspring is the product of gametic 
c...              shuffling of the parent's chromosomes via
c...              self-fertilization.

                  call offspring(dmutn_offsprng(1,1,child),
     &                           fmutn_offsprng(1,1,child),
     &                 offsprng_lb_mutn_count(1,1,1,child),
     &                      offsprng_lb_fitness(1,1,child),
     &                           dmutn,fmutn,lb_mutn_count,
     &                  linkage_block_fitness,parent,parent,tsub) 

               end if

               time_offspring = time_offspring + tsub

            end do

            offspring_count = offspring_count + actual_offspring
           
c...        Copy mutation list arrays for each of the first two 
c...        offspring into locations of the two parents.  Update
c...        the linkage block mutation count and the linkage block
c...        fitness for these two offspring.

            if(actual_offspring >= 1) then
               k = dmutn_offsprng(1,1,1) + 1
               dmutn(1:k,1,dad) = dmutn_offsprng(1:k,1,1)
               k = dmutn_offsprng(1,2,1) + 1
               dmutn(1:k,2,dad) = dmutn_offsprng(1:k,2,1)
               k = fmutn_offsprng(1,1,1) + 1
               fmutn(1:k,1,dad) = fmutn_offsprng(1:k,1,1)
               k = fmutn_offsprng(1,2,1) + 1
               fmutn(1:k,2,dad) = fmutn_offsprng(1:k,2,1)
               lb_mutn_count(:,:,:,dad) = 
     &           offsprng_lb_mutn_count(:,:,:,1)
               linkage_block_fitness(:,:,dad) = 
     &           offsprng_lb_fitness(:,:,1)
               replaced_by_offspring(dad) = .true.
            end if
            if(actual_offspring >= 2) then
               k = dmutn_offsprng(1,1,2) + 1
               dmutn(1:k,1,mom) = dmutn_offsprng(1:k,1,2)
               k = dmutn_offsprng(1,2,2) + 1
               dmutn(1:k,2,mom) = dmutn_offsprng(1:k,2,2)
               k = fmutn_offsprng(1,1,2) + 1
               fmutn(1:k,1,mom) = fmutn_offsprng(1:k,1,2)
               k = fmutn_offsprng(1,2,2) + 1
               fmutn(1:k,2,mom) = fmutn_offsprng(1:k,2,2)
               lb_mutn_count(:,:,:,mom) = 
     &           offsprng_lb_mutn_count(:,:,:,2)
               linkage_block_fitness(:,:,mom) = 
     &           offsprng_lb_fitness(:,:,2)
               replaced_by_offspring(mom) = .true.
            end if

c...        Copy the mutation list for any other offspring into arrays
c...        dmutn and fmutn with an index greater than current_pop_size.
c...        Update array linkage_block_fitness appropriately.
         
            do slot=3,actual_offspring
               total_offspring = total_offspring + 1
               j = total_offspring 
               k = dmutn_offsprng(1,1,slot) + 1
               dmutn(1:k,1,j) = dmutn_offsprng(1:k,1,slot)
               k = dmutn_offsprng(1,2,slot) + 1
               dmutn(1:k,2,j) = dmutn_offsprng(1:k,2,slot)
               k = fmutn_offsprng(1,1,slot) + 1
               fmutn(1:k,1,j) = fmutn_offsprng(1:k,1,slot)
               k = fmutn_offsprng(1,2,slot) + 1
               fmutn(1:k,2,j) = fmutn_offsprng(1:k,2,slot)
               lb_mutn_count(:,:,:,j) = 
     &                              offsprng_lb_mutn_count(:,:,:,slot)
               linkage_block_fitness(:,:,j) = 
     &                                   offsprng_lb_fitness(:,:,slot)
            end do

         end do

c...     For slots not overwritten by new offspring, move data from
c...     offspring with higher index numbers to populate these slots.

         if(offspring_count < current_pop_size) then

            replace = current_pop_size
            empty   = 1

            do while(empty  <= offspring_count .and. 
     &               replace > offspring_count)

               do while(replaced_by_offspring(empty) .and.
     &                  empty < offspring_count)
                  empty = empty + 1
               end do

               do while(replace <= current_pop_size .and.
     &                  .not.replaced_by_offspring(replace))
                  replace = replace - 1
               end do

               if(empty <=  offspring_count .and. 
     &            replace > offspring_count) then
                  k = dmutn(1,1,replace) + 1
                  dmutn(1:k,1,empty) = dmutn(1:k,1,replace)
                  k = dmutn(1,2,replace) + 1
                  dmutn(1:k,2,empty) = dmutn(1:k,2,replace)
                  k = fmutn(1,1,replace) + 1
                  fmutn(1:k,1,empty) = fmutn(1:k,1,replace)
                  k = fmutn(1,2,replace) + 1
                  fmutn(1:k,2,empty) = fmutn(1:k,2,replace)
                  lb_mutn_count(:,:,:,empty) = 
     &            lb_mutn_count(:,:,:,replace)
                  linkage_block_fitness(:,:,empty) =
     &            linkage_block_fitness(:,:,replace)
                  replaced_by_offspring(empty) = .true.
                  replace = replace - 1
               end if

            end do

            total_offspring = offspring_count

         end if

c...     Because the Poisson random number generator does not yield
c...     the specified mean number of new mutations to sufficient
c...     accuracy, to improve accuracy make an adjustment to the value
c...     fed to the generator.

         cumulative_offspring = cumulative_offspring + offspring_count

         if((mod(gen - gen_0, 10) == 0 .or. gen - gen_0 < 10) .and.
     &      mutn_rate >= 1.) then 
            d = real(new_mutn_count)/real(cumulative_offspring)
            poisson_mean = poisson_mean + 0.3*(mutn_rate - d)
         end if

         if(is_parallel .and. tribal_competition) then

c...        Modify the tribal population size such that selection 
c...        intensity depends only on the default fertility.

            real_pop_size = offspring_count/(reproductive_rate
     &                      *(1. - fraction_random_death)) 
            if(fitness_dependent_fertility) real_pop_size = 
     &         real_pop_size/sqrt(min(1.d0, post_sel_fitness))
            current_pop_size = int(real_pop_size)
            if(real_pop_size - current_pop_size > randomnum(1))
     &         current_pop_size = current_pop_size + 1

c...        Modify the tribal population size to keep the global
c...        population size nearly constant.

            call mpi_mybarrier()

            call mpi_isum(current_pop_size,global_pop,1)
            call mpi_mybcasti(global_pop,1)

            mean_pop  = global_pop_size/num_tribes
            delta_pop = global_pop_size - global_pop
            delta     = 2*delta_pop/num_tribes

            if(delta_pop > 0 .and. current_pop_size > mean_pop) then
               k = min(delta, int(delta*randomnum(1) + 0.5))
               current_pop_size = current_pop_size + k
            elseif(delta_pop<0 .and. current_pop_size<mean_pop) then
               k = max(delta, int(delta*randomnum(1) - 0.5))
               current_pop_size = current_pop_size + k
            end if

c START_MPI
            call MPI_GATHER(current_pop_size,1,MPI_INTEGER,
     &                      pop_size_array,1,MPI_INTEGER,0,
     &                      MYCOMM,ierr)
c END_MPI

         end if
      
c...     If there is tribal competition and all tribes but one go
c...     extinct, let the remaining tribe grow to the maximum size.

         if(tribal_competition .and. .not.is_parallel) then
            k = real(global_pop_size - current_pop_size)*0.1 + 0.9
            current_pop_size = current_pop_size + k
         end if

         current_pop_size = min(current_pop_size, offspring_count)

         call second(tout_offspring)
         sec(5) = sec(5) + tout_offspring - tin_offspring

c...     Impose selection based on fitness to reduce the population 
c...     size to a value not to exceed the parameter pop_size.
          
         call selection(dmutn, fmutn, lb_mutn_count, 
     &        linkage_block_fitness, fitness, pheno_fitness, 
     &        work_fitness, sorted_score, initial_allele_effects,
     &        max_size, total_offspring, gen, time_selection)

c	 START_MPI
         if(tribal_competition) then
            call compute_tribal_fitness(dmutn, fmutn, pop_size_array,
     &           current_global_pop_size,gen)
         end if
c	 END_MPI

c        if(mod(gen,10)==0) write(*,*) "myid cps, offcnt =", myid,
c    &              current_pop_size, offspring_count

c...     If the population size or the mean fitness has collapsed,
c...     print message and shutdown all processors.

         if(post_sel_fitness < extinction_threshold) then

c           If one tribe goes extinct, set trigger for shutdown
            if(is_parallel) then
c              Must shutdown parallel before calling diagnostics_history_plot
c              otherwise will hang waiting for communications
               if(num_tribes == 2) is_parallel = .false.
               run_status = -1
            else 
               write(6,'(/"** SHUTDOWN DUE TO EXTINCTION **"/)')
               write(9,'(/"** SHUTDOWN DUE TO EXTINCTION **"/)')
               goto 20
            end if

            call diagnostics_history_plot(dmutn, fmutn, lb_mutn_count, 
     &           ica_count, gen, .true., current_global_pop_size)

            write(6,*)
            write(6,*)'*** SHUTDOWN TRIBE',myid+1,
     &                ' DUE TO EXTINCTION AT GEN:',gen
            write(9,*)'*** SHUTDOWN TRIBE',myid+1,
     &                ' DUE TO EXTINCTION AT GEN:',gen

         end if

c...     Since clonal cells such as bacteria can multiply from a single cell
c...     we need to provide some means to allow a population size of one
c...     to recover from a bottleneck. This is done by increasing it to
c...     a value of 2 just before the mutational check, which will cause
c...     it to rebound correctly. If it is left as 1, it will never rebound 
c...     correctly, but stay at a fixed value of 1 for the remainder of the 
c...     simulation.

         if(bottleneck_yes .and. bottleneck_pop_size == 1 .and.
     &      clonal_reproduction .and. current_pop_size == 1) then
            current_pop_size = 2
         end if

c...     Mutational meltdown scenario

         if((is_parallel .and. current_pop_size < 
     &      extinction_threshold*pop_size) .or.
     &      current_pop_size <= 1) then
            
c           If one tribe melts down, set trigger for shutdown
            if(is_parallel) then
               write(6,*)
               write(6,*)'*** SHUTDOWN TRIBE',myid+1,
     &                    'DUE TO MUTATIONAL MELTDOWN AT GEN:',gen
               write(9,*)'*** SHUTDOWN TRIBE',myid+1,
     &                    'DUE TO MUTATIONAL MELTDOWN AT GEN:',gen
               write(6,*) myid+1,'Population size:', current_pop_size
               write(9,*) myid+1,'Population size:', current_pop_size
               run_status = -(myid + 1)
            else
               write(6,'(/"** SHUTDOWN DUE TO MUTATIONAL MELTDOWN **")')
               write(9,'(/"** SHUTDOWN DUE TO MUTATIONAL MELTDOWN **")')
               write(6,*) 'Population size:', current_pop_size
               goto 20
            end if

         end if

c        In case one tribe is set to run less generations than the other
         if(is_parallel .and. .not.homogenous_tribes .and.
     &      gen==gen_0+num_generations) then
            write(6,*) 'TRIBE',myid+1,'IS SHUTTING DOWN. GEN:',gen
            write(9,*) 'TRIBE',myid+1,'IS SHUTTING DOWN. GEN:',gen
            run_status = -(myid + 1)
         end if

c	 START_MPI
c        For the limiting case of two tribes, we must turn off the parallel
c        switch if one of the tribes.  So, every generation communicate the 
c        status of each tribe to the other.

         if(num_tribes == 2 .and. tribal_competition) then

            if(myid == 1) then
               call mpi_send_int(run_status,0,msg_num,ierr)
               msg_num = msg_num + 1
               call mpi_recv_int(other_run_status,0,msg_num,ierr)
            else 
               call mpi_recv_int(other_run_status,1,msg_num,ierr)
               msg_num = msg_num + 1
               call mpi_send_int(run_status,1,msg_num,ierr)
            end if
            msg_num = msg_num + 1

            if(other_run_status < 0)  then
               num_tribes = num_tribes - 1
               is_parallel = .false.
            end if

            if(run_status < 0) goto 30

         else if (num_tribes > 2) then

c           receive status from every process in group 
c           to check if one process has died

            call MPI_ALLREDUCE(run_status,global_run_status,1,
     &           MPI_INTEGER,MPI_SUM,MYCOMM,ierr)
  
c            write(*,*) 'global_run_status:',global_run_status

            if(sum(global_run_status) < 0) then

               ranks(1) = -sum(global_run_status)

               call MPI_COMM_GROUP(MYCOMM,OLDGROUP,ierr)
               call MPI_GROUP_EXCL(OLDGROUP,1,ranks,NEWGROUP,ierr)
               call MPI_COMM_CREATE(MYCOMM,NEWGROUP,MYCOMM,ierr)

               if(run_status < 0) goto 30

               call MPI_COMM_SIZE(MYCOMM,num_tribes,ierr)

            end if

         end if
c	 END_MPI

c...     Write diagnostic information to output files.

         current_pop_size = max(1, current_pop_size)

         call second(tin_diagnostics)

         if(mod(gen, 10) == 0 .or. (.not.bottleneck_yes .and. 
     &      current_pop_size <= pop_size/20) .or. gen < 4) then
            print_flag = .true.
         else
            print_flag = .false.
         end if

         if(num_contrasting_alleles > 0) 
     &      call diagnostics_contrasting_alleles(dmutn, fmutn,
     &           offsprng_lb_mutn_count, work_fitness, 
     &           initial_allele_effects, ica_count, max_size, .false.)

         call diagnostics_history_plot(dmutn, fmutn, lb_mutn_count, 
     &        ica_count, gen, print_flag, current_global_pop_size)

         if(gen <= 3 .or. mod(gen, 20) == 0) then

c...        Output fitness of each individual in population.

            rewind(16)
            write(16,'("# individual",2x,"fitness")')
            do i=1,current_pop_size
               write(16,*) i, fitness(i)
            end do
            call flush(16)

         end if

         if(fitness_distrib_type == 1 .and. mod(gen, 20) == 0) then

            if(tracking_threshold /= 1.0)
     &         call diagnostics_mutn_bins_plot(dmutn, fmutn, accum,
     &                                          gen)

            call diagnostics_near_neutrals_plot(dmutn, fmutn, 
     &               linkage_block_fitness, lb_mutn_count, gen)

            call diagnostics_selection(sorted_score,pheno_fitness,
     &                                 total_offspring,gen)

         end if

         call second(tout_diagnostics)
         sec(7) = sec(7) + tout_diagnostics - tin_diagnostics
         call second(tin_diagnostics)

         if(mod(gen, plot_allele_gens)==0 .and. gen /= num_generations)
     &       call diagnostics_polymorphisms_plot(dmutn, fmutn,
     &                             work_fitness, max_size, gen)

         call second(tout_diagnostics)
         sec(8) = sec(8) + tout_diagnostics - tin_diagnostics

         if(mod(gen, 100) == 0) then

c...        Output user-friendly details of the mutations carried by
c...        a few representative individuals in the population.

c           call write_sample(dmutn,fmutn,lb_mutn_count,
c    &                        linkage_block_fitness,fitness,
c    &                        dmutn_offsprng,dmutn_offsprng(1,1,2),
c    &                        pheno_fitness,
c    &                        offsprng_lb_mutn_count(1,1,1,1),
c    &                        offsprng_lb_mutn_count(1,1,1,2),gen)

         end if

         call second(tout_gen)
         tgen = tout_gen - tin_gen

         write(22,'(i12,f17.7,2f19.7)') gen, tgen, time_offspring,
     &                             time_selection
         call flush(22)
        
         if(is_parallel) then
            call mpi_ravg(tgen,par_tgen,1)
            call mpi_ravg(time_offspring,par_time_offspring,
     &                    3)
            call mpi_ravg(time_selection,par_time_selection,1)
            if (myid==0) then
               write(23,'(i12,f17.7,2f19.7)') gen, par_tgen, 
     &           par_time_offspring, par_time_selection
               if (myid==0.and.(mod(gen,10)==0.or.gen<4)) then
                  write(*,'("iteration time: ",i6,"  milliseconds")') 
     &                 int(1000.*tgen)
               end if
               call flush(23)
            end if
         end if

c...     Monitor state file for shutdown flag.

         if (run_status >= 0) then
            npath = index(data_file_path,' ') - 1
            open(10, file=data_file_path(1:npath)//case_id//'.st8',
     &               status='unknown')
            read(10,*) run_status
            close(10)

c...        Premature shutdown
            shutdown_gen = gen
            if (run_status == 1) then
               write(6,*) 'STATE: WRITING RESTART FILE & EXITING RUN'
               write_dump = .true.
               restart_dump_number = 8
               dump_number = restart_dump_number
               goto 20
            end if
         end if

c...     Write PPM data.

c        do i=1,pop_size
c           if (fitness(i) > 1) then 
c              red = 255
c              green = 0
c              blue = 0
c           else
c              red = int(fitness(i)*255)
c              if (red < 0) red = 0 
c              green = red
c              blue = red
c           end if
c           write(15,'(i4,$)') red,green,blue
c        end do
c        write(15,*)

c...     for dynamic population sizes compute new pop_size

         if(pop_growth_model > 0) then
            if(pop_growth_model == 1) then
               pop_size = ceiling(pop_growth_rate*pop_size)
            else if (pop_growth_model == 2) then
c...           pass carrying capacity through num_generations
               carrying_capacity = num_generations
               pop_size = ceiling(pop_size*(1. + pop_growth_rate*
     &                    (1. - pop_size/carrying_capacity)))
            else 
               write(0,*) 'ERROR: pop_growth_model ', pop_growth_model,
     &                    'not supported'
               stop   
            end if   

            this_size = int((1.1*reproductive_rate*pop_size
     &                  *(1. - fraction_random_death)))
            if(this_size > max_size) then
               write(0,*) "OUT OF MEMORY! SHUTTING DOWN!"
               goto 20
            end if 

         end if

         call flush(6)
         call flush(9)

c...  End generation loop
      end do ! gen

c...  Shutdown procedures

 20   continue

c...  Perform diagnositics on initial contrasting alleles and
c...  polymorphisms and create file for plotting.

      call second(tin_diagnostics)

      if(num_contrasting_alleles > 0) 
     &   call diagnostics_contrasting_alleles(dmutn, fmutn,
     &          offsprng_lb_mutn_count, work_fitness, 
     &          initial_allele_effects, ica_count, max_size, .true.)

      if(num_contrasting_alleles > 0)
     &   call tabulate_initial_alleles(dmutn, fmutn,
     &   linkage_block_fitness, initial_allele_effects, max_size)

      if(tracking_threshold /= 1.0) then
         call diagnostics_polymorphisms_plot(dmutn, fmutn,
     &                       work_fitness, max_size, gen-1)
c         if(.not.clonal_reproduction)
c     &      call diagnostics_heterozygosity(dmutn, fmutn)
      end if

      call second(tout_diagnostics)
      sec(8) = sec(8) + tout_diagnostics - tin_diagnostics

c...  Write an output dump that contains the current set of parameter
c...  values, the stored mutation array mutn, and the linkage block
c...  fitness array linkage_block_fitness.

      dump_number = dump_number + 1

      if(write_dump) call write_output_dump(dmutn,fmutn,lb_mutn_count,
     &                    linkage_block_fitness,initial_allele_effects,
     &                    shutdown_gen,myid_str)

      call second(tout)
      sec(2) = sec(2) + tout - tin

      call profile(6)
      call profile(9)

 30   continue

c...  Close files.

      close(4)
      close(6)
      close(7)
      close(8)
      close(9)
      close(11)
c     close(12)
      close(13)
      close(14)
c     close(15)
      close(16)
      close(25)
      close(26)
      close(30)

      if (is_parallel) then
         close(14)
         close(17)
         close(18)
         close(20)
         close(24)
         close(34)
         close(35)
      end if

c     START_MPI
c...  Wait for all processes to reach this point before shutting down all processes
      if(am_parallel.and.tribal_competition) then
         call mpi_mybarrier()
         if(num_tribes_at_start > 2) then
            call MPI_GROUP_FREE(OLDGROUP,ierr)
            call MPI_GROUP_FREE(NEWGROUP,ierr)
         end if
         call MPI_COMM_FREE(MYCOMM)
         call mpi_myfinalize(ierr)
      elseif (is_parallel) then
         call MPI_COMM_FREE(MYCOMM,ierr)
         call mpi_myfinalize(ierr)
      endif
c     END_MPI

      stop

      end

c     START_MPI
      subroutine compute_tribal_fitness(dmutn, fmutn, pop_size_array,
     &           current_global_pop_size, gen)

      use random_pkg
      include 'common.h'
      include '/usr/local/include/mpif.h'
      integer dmutn(max_del_mutn_per_indiv/2,2,*)
      integer fmutn(max_fav_mutn_per_indiv/2,2,*)
      integer pop_size_array(num_tribes), current_global_pop_size
      integer i, j, k, m, gen
      real*8 fitness, decode_fitness_del, decode_fitness_fav
      real*8 par_pre_sel_fitness, par_post_sel_fitness,
     &       mod_par_post_sel_fitness, 
     &       post_sel_fitness_array(num_tribes)
      real*8 tribal_fitness_variance, par_tribal_fitness
      real*8 global_genetic_fitness

c...  Compute total social bonus.
 
      if(upload_mutations .and. altruistic) then
         social_bonus = 0.d0
         do i=1, current_pop_size
            do j = 1, 2
               do k = 2, dmutn(1,j,i)
                  do m = 1, num_uploaded_mutn
                     if (dmutn(k,j,i) == uploaded_mutn(m)) then
                        fitness = abs(decode_fitness_del(dmutn(k,j,i)))
                        social_bonus = social_bonus + fitness
                     end if
                  end do
               end do
            end do
         end do
         social_bonus = social_bonus / current_pop_size
      else
         social_bonus = 0.d0
      end if

c...  Compute tribal fitness

      if (is_parallel) then

         call mpi_davg(post_sel_fitness,par_post_sel_fitness,1)
         call mpi_davg(pre_sel_fitness,par_pre_sel_fitness,1)
         call mpi_mybcastd(par_post_sel_fitness,1)

         if(tribal_competition) then

c...        Gather the fitnesses from each tribe into a single 
c...        array called post_sel_fitness_array in order to compute
c...        tribal fitness variance below.

            call MPI_GATHER(post_sel_fitness,1,MPI_DOUBLE_PRECISION,
     &                      post_sel_fitness_array,1,
     &                      MPI_DOUBLE_PRECISION,0,MYCOMM,ierr)

            if(myid==0) then

c...           Compute global weighted genetic fitness.

               global_genetic_fitness=0.d0
               do i = 1, num_tribes
                  global_genetic_fitness = 
     &                    pop_size_array(i)*post_sel_fitness_array(i) + 
     &                                     global_genetic_fitness
               end do 
               global_genetic_fitness = global_genetic_fitness/
     &                                  real(current_global_pop_size)

               if(mod(gen,10)==0) then
                  write(*,'("global genetic fitness = ",f7.4)') 
     &                       global_genetic_fitness
               end if

               tribal_fitness_variance=0.d0
               do i = 1, num_tribes
                  tribal_fitness_variance=tribal_fitness_variance+
     &                           (par_post_sel_fitness-
     &                            post_sel_fitness_array(i))**2
               end do

c...           Compute the tribal noise variance required to yield the 
c...           specified group heritability.  Take the square root to 
c...           obtain the standard deviation.

               tribal_noise = sqrt(tribal_fitness_variance*
     &                             (1.d0 - group_heritability)
     &                              /group_heritability)
            end if

c...        Broadcast this value to all tribes.

            call mpi_mybcastd(global_genetic_fitness,1)
            call mpi_mybcastd(tribal_noise,1)

c...        Add noise component to tribal_fitness (post_sel_fitness)
c...        Add a tiny variable positive increment to eliminate identical
c...        fitness values when the noise is zero.

            tribal_noise = tribal_noise*random_normal() + 1.d-15*myid

c...        Compute the total tribal fitness.

            tribal_fitness = post_sel_fitness + tribal_noise 

c...        The tribal_fitness_factor relates the fitness of the
c...        current tribe to the average tribal fitness from all tribes.  

            call mpi_davg(tribal_fitness,par_tribal_fitness,1)
            call mpi_mybcastd(par_tribal_fitness,1)
            
            tribal_fitness_factor=tribal_fitness/
     &                            global_genetic_fitness

c...        Add social_bonus into the total tribal fitness.

            tribal_fitness = tribal_fitness + 
     &                       social_bonus_factor*social_bonus

c...        Recompute tribal_fitness_factor which now includes 
c...        social_bonus.

            call mpi_davg(tribal_fitness,par_tribal_fitness,1)
            call mpi_mybcastd(par_tribal_fitness,1)
            tribal_fitness_factor=tribal_fitness/par_tribal_fitness

         else

c...        Add social_bonus to fitness for the case when parallel is
c...        turned on but tribal competition is turned off.

            tribal_fitness = tribal_fitness + 
     &                       social_bonus_factor*social_bonus

         endif

      else 

c...     Add social bonus to fitness for non-parallel/single-tribe case.
         tribal_fitness = tribal_fitness + 
     &                    social_bonus_factor*social_bonus

      end if

      end
c     END_MPI

      subroutine diagnostics_history_plot(dmutn, fmutn, lb_mutn_count,
     &   ica_count, gen, print_flag, current_global_pop_size)
      use random_pkg
      include 'common.h'
      include '/usr/local/include/mpif.h'
      integer dmutn(max_del_mutn_per_indiv/2,2,*)
      integer fmutn(max_fav_mutn_per_indiv/2,2,*)
      integer lb_mutn_count(num_linkage_subunits,2,2,*)
      integer gen, i, j, k, m, lb, num_recessive, dth
      integer ica_count(2)
      integer current_global_pop_size, global_num_back_mutn
      real*8 total_fav_mutn, tracked_neu_mutn, par_tracked_neu_mutn
      real*8 frac_recessive, par_total_del_mutn, par_total_fav_mutn
      real*8 par_tracked_del_mutn, frac_accum, total_mutn, st
      real*8 par_pre_sel_fitness, par_post_sel_fitness,
     &       par_pre_sel_geno_sd, par_pre_sel_pheno_sd, 
     &       par_pre_sel_corr, par_post_sel_geno_sd, 
     &       par_post_sel_pheno_sd, par_post_sel_corr,
     &       mod_par_post_sel_fitness, 
     &       post_sel_fitness_array(num_tribes)
      logical print_flag

      total_del_mutn   = 0
      total_fav_mutn   = 0
      tracked_del_mutn = 0
      tracked_fav_mutn = 0

      do i=1,current_pop_size
         do lb=1,num_linkage_subunits
            total_del_mutn = total_del_mutn 
     &                     + lb_mutn_count(lb,1,1,i)
     &                     + lb_mutn_count(lb,2,1,i)
            total_fav_mutn = total_fav_mutn 
     &                     + lb_mutn_count(lb,1,2,i)
     &                     + lb_mutn_count(lb,2,2,i)
         end do
         tracked_del_mutn = tracked_del_mutn + dmutn(1,1,i)
     &                                       + dmutn(1,2,i)
         tracked_fav_mutn = tracked_fav_mutn + fmutn(1,1,i)
     &                                       + fmutn(1,2,i)
      end do

      tracked_del_mutn = tracked_del_mutn - ica_count(1)
      tracked_fav_mutn = tracked_fav_mutn - ica_count(2)

c...  Compute averages across processors.

      if (is_parallel) then

         call mpi_davg(post_sel_fitness,par_post_sel_fitness,1)
         call mpi_davg(pre_sel_fitness,par_pre_sel_fitness,1)
         call mpi_mybcastd(par_post_sel_fitness,1)
         call mpi_davg(pre_sel_geno_sd,
     &                 par_pre_sel_geno_sd,1)
         call mpi_davg(pre_sel_pheno_sd,
     &                 par_pre_sel_pheno_sd,1)
         call mpi_davg(pre_sel_corr,
     &                 par_pre_sel_corr,1)
         call mpi_davg(post_sel_geno_sd,
     &                 par_post_sel_geno_sd,1)
         call mpi_davg(post_sel_pheno_sd,
     &                 par_post_sel_pheno_sd,1)
         call mpi_davg(post_sel_corr,
     &                 par_post_sel_corr,1)

         call mpi_dsum(total_del_mutn,par_total_del_mutn,1)
         call mpi_dsum(tracked_del_mutn,par_tracked_del_mutn,1)
         call mpi_dsum(total_fav_mutn,par_total_fav_mutn,1)

      end if

      num_recessive  = 0
      frac_recessive = 0.

      do i=1,current_pop_size
         do j=2,dmutn(1,1,i)+1
            if(dmutn(j,1,i) < 0) num_recessive = num_recessive + 1
         end do
         do j=2,dmutn(1,2,i)+1
            if(dmutn(j,2,i) < 0) num_recessive = num_recessive + 1
         end do
      end do

      if(tracked_del_mutn > 0) frac_recessive =
     &                         real(num_recessive)/tracked_del_mutn

      tracked_neu_mutn     = 0
      par_tracked_neu_mutn = 0

      if(track_neutrals) then

         dth = int((lb_modulo - 2)*(1. - fraction_neutral) + 0.5)

         do i=1,current_pop_size
            do j=2,dmutn(1,1,i)+1
               if(mod(abs(dmutn(j,1,i)), lb_modulo) > dth) 
     &            tracked_neu_mutn = tracked_neu_mutn + 1
            end do
            do j=2,dmutn(1,2,i)+1
               if(mod(abs(dmutn(j,2,i)), lb_modulo) > dth) 
     &            tracked_neu_mutn = tracked_neu_mutn + 1
            end do
         end do

         if(is_parallel)
     &      call mpi_dsum(tracked_neu_mutn,par_tracked_neu_mutn,1)

      end if

c...  Output to a file for plotting the generation number, the mean 
c...  fitness, the average number of mutations per individual, and 
c...  the number of fixed favorable mutations.

      if(tribal_competition) then
         write(7,'(i12,2e16.4,1p3e14.4,e14.4)') gen, post_sel_fitness, 
     &      post_sel_geno_sd,
     &      (total_del_mutn-tracked_neu_mutn)/current_pop_size,
     &      total_fav_mutn/current_pop_size,
     &      tracked_neu_mutn/current_pop_size,
     &      current_pop_size/real(global_pop_size)*100.
      else 
         write(7,'(i12,2e16.4,1p3e14.4,i12)') gen, 
     &      post_sel_fitness, post_sel_geno_sd,
     &      (total_del_mutn-tracked_neu_mutn)/current_pop_size,
     &      total_fav_mutn/current_pop_size,
     &      tracked_neu_mutn/current_pop_size, current_pop_size
      endif
      call flush(7)

      if(is_parallel .and. myid==0) then
         write(17,'(i12,2e16.4,1p3e14.4,i12)') gen, 
     &         par_post_sel_fitness, par_post_sel_geno_sd, 
     &         (par_total_del_mutn-par_tracked_neu_mutn)
     &          /global_pop_size,
     &         par_total_fav_mutn/global_pop_size,
     &         tracked_neu_mutn/global_pop_size,
     &         current_global_pop_size
         call flush(17)
      end if

      if (.not.print_flag) return

      call write_status(9, gen, current_pop_size, 
     &     frac_recessive, total_del_mutn, tracked_del_mutn, 
     &     total_fav_mutn, tracked_neu_mutn, pre_sel_fitness, 
     &     pre_sel_geno_sd, pre_sel_pheno_sd, pre_sel_corr, 
     &     post_sel_fitness, post_sel_geno_sd, post_sel_pheno_sd, 
     &     post_sel_corr)
 
      if(allow_back_mutn) write(9,"('mean number of back mutations',
     &   '/indiv =',f10.2)") real(num_back_mutn)/real(current_pop_size)

      if(is_parallel) then
         if(tribal_competition) then
            call mpi_isum(current_pop_size,current_global_pop_size,1)
         else
            call mpi_isum(current_pop_size,current_global_pop_size,1)
         endif

         call mpi_isum(num_back_mutn,global_num_back_mutn,1)

         if (myid == 0) then 
            call write_status(6, gen, current_global_pop_size,
     &           frac_recessive, par_total_del_mutn*num_tribes, 
     &           par_tracked_del_mutn, par_total_fav_mutn,
     &           par_tracked_neu_mutn,
     &           par_pre_sel_fitness, par_pre_sel_geno_sd, 
     &           par_pre_sel_pheno_sd, par_pre_sel_corr,
     &           par_post_sel_fitness, par_post_sel_geno_sd, 
     &           par_post_sel_pheno_sd, par_post_sel_corr)

            if(allow_back_mutn) write(6,"('mean number of back '
     &         'mutations/indiv =',f10.2)") real(global_num_back_mutn)
     &         /real(current_global_pop_size)

         end if

         if((gen < 4 .or. mod(gen,10)==0) .and. altruistic) then
            write(*,'(a,i3,a,f12.8,$)') 'tribe:', myid+1,
     &                                  ' social_bonus:', social_bonus
            if(tribal_competition) then
               write(*,'(a,f12.8)') ' tribal_noise:', tribal_noise
            else
               write(*,*)
            end if
         end if

      else

         call write_status(6, gen, current_pop_size, 
     &        frac_recessive, total_del_mutn, tracked_del_mutn, 
     &        total_fav_mutn, tracked_neu_mutn, pre_sel_fitness, 
     &        pre_sel_geno_sd, pre_sel_pheno_sd, pre_sel_corr, 
     &        post_sel_fitness, post_sel_geno_sd, post_sel_pheno_sd, 
     &        post_sel_corr)

         if(allow_back_mutn) write(6,"('mean number of back mutations',
     &   '/indiv =',f10.2)") real(num_back_mutn)/real(current_pop_size)

         if((gen < 4 .or. mod(gen,10)==0) .and. altruistic) then
            write(*,'(a,f12.8)') 'social_bonus: ',social_bonus
         end if

      end if

      if(tracking_threshold == 1.0 .and. gen >= 200 .and.
     &   mod(gen,20) == 0) then
         total_mutn = gen*current_pop_size*mutn_rate
         if(frac_fav_mutn /= 1.) then
            frac_accum = total_del_mutn/(total_mutn*(1.-frac_fav_mutn))
            st = 1.3*exp(-alpha_del*(1. - frac_accum)**gamma_del)
            write(9, '("deleterious selection threshold  =",1pe10.3)') 
     &            st
            write(9, '("deleterious fraction accumulated =",f7.4)') 
     &            frac_accum
            if(.not. is_parallel) then
            write(6, '("deleterious selection threshold  =",1pe10.3)') 
     &            st
            write(6, '("deleterious fraction accumulated =",f7.4)') 
     &            frac_accum
            end if
            write(25, '(i10,1p1e15.3,2a15)') 
     &            gen, st, 'NaN', 'NaN' 
            if(is_parallel .and. myid==0) then
               write(35, '(i10,1p1e15.3,2a15)') 
     &            gen, st, 'NaN', 'NaN' 
            end if
         end if
      end if

      if(num_contrasting_alleles > 0)
     &   write(9,'(19x,"Statistics for initial contrasting alleles"/,
     &             " mean fitness contrib =",f7.4,"  fav mean freq =",
     &             f7.4,"  fixed =",i4,"  lost =",i4)')
     &             ica_mean_effect, fav_mean_freq, fav_fixed, fav_lost

      if(num_contrasting_alleles > 0 .and. .not. is_parallel)
     &   write(6,'(19x,"Statistics for initial contrasting alleles"/,
     &             " mean fitness contrib =",f7.4,"  fav mean freq =",
     &             f7.4,"  fixed =",i4,"  lost =",i4)')
     &             ica_mean_effect, fav_mean_freq, fav_fixed, fav_lost

      end

      subroutine diagnostics_mutn_bins_plot(dmutn, fmutn, accum, gen)

      include 'common.h'
      integer dmutn(max_del_mutn_per_indiv/2,2,*)
      integer fmutn(max_fav_mutn_per_indiv/2,2,*)
      integer gen, i, j, k, k0, accum_gen
      integer fid, oneortwo
      real*8 fitness_bins(100,2), par_fitness_bins(100,2), work(100,2)
      real*8 bin_fitness_boxwidth(101), bin_fitness_midpoint(101)
      real*8 refr_bins(100), bin_fitness(101), del_bin_width, b0, b1
      real*8 d, x, x0, x1, y0, y1, s, mutn_sum, fav_bin_width
      real*8 av1, av2, fm1, fm2, sum, accum(50), del, del_no_sel, ratio
      real*8 del_dom_thres, del_rec_thres, fav_dom_thres, fav_rec_thres
      real*8 par_del_dom_thres, par_fav_dom_thres

c...  Compute the total number of mutations and the bin widths.
   
      mutn_sum  = current_pop_size*gen*mutn_rate
      del_bin_width = -log(tracking_threshold)/50
      if(max_fav_fitness_gain > 0.) then
         fav_bin_width = -log(tracking_threshold
     &                        /max_fav_fitness_gain)/50
      else
         fav_bin_width = del_bin_width
      end if

      x0 = 0.
      y0 = 0.
      do k=1,50
         x1 = (del_bin_width*k/alpha_del)**(1./gamma_del)
         refr_bins(k) = (1. - frac_fav_mutn)*mutn_sum*(x1 - x0)
         y1 = (fav_bin_width*k/alpha_fav)**(1./gamma_fav)
         refr_bins(50+k) = frac_fav_mutn*mutn_sum*(y1 - y0)
         x0 = x1
         y0 = y1
      end do

c...  Compute statistics on favorable and recessive mutations.

      fitness_bins = 0.

      do i=1,current_pop_size

         do j=2,dmutn(1,1,i)+1
            x = mod(abs(dmutn(j,1,i)),lb_modulo)*del_scale
            if(x < 1.d0) then
               d = alpha_del*x**gamma_del
               k = 1 + int(d/del_bin_width)
               if(dmutn(j,1,i) < 0) then
                  if(k <= 50) then
                     fitness_bins(k,1) = 
     &               fitness_bins(k,1) + 1.
                  end if
               else
                  if(k <= 50) then
                     fitness_bins(k,2) = 
     &               fitness_bins(k,2) + 1.
                  end if
               end if
            end if
         end do

         do j=2,dmutn(1,2,i)+1
            x = mod(abs(dmutn(j,2,i)),lb_modulo)*del_scale
            if(x < 1.d0) then
               d = alpha_del*x**gamma_del
               k = 1 + int(d/del_bin_width)
               if(dmutn(j,2,i) < 0) then
                  if(k <= 50) then
                     fitness_bins(k,1) = 
     &               fitness_bins(k,1) + 1.
                  end if
               else
                  if(k <= 50) then
                     fitness_bins(k,2) = 
     &               fitness_bins(k,2) + 1.
                  end if
               end if
            end if
         end do

         do j=2,fmutn(1,1,i)+1
            d = alpha_fav
     &          *(mod(abs(fmutn(j,1,i)),lb_modulo)*fav_scale)**gamma_fav
            k = 51 + int(d/fav_bin_width)

            if(fmutn(j,1,i) < 0) then
               if(k <= 100) then
                  fitness_bins(k,1) =
     &            fitness_bins(k,1) + 1.
               end if
            else
               if(k <= 100) then
                  fitness_bins(k,2) =
     &            fitness_bins(k,2) + 1.
               end if
            end if
         end do

         do j=2,fmutn(1,2,i)+1
            d = alpha_fav
     &          *(mod(abs(fmutn(j,2,i)),lb_modulo)*fav_scale)**gamma_fav
            k = 51 + int(d/fav_bin_width)

            if(fmutn(j,2,i) < 0) then
               if(k <= 100) then
                  fitness_bins(k,1) =
     &            fitness_bins(k,1) + 1.
               end if
            else
               if(k <= 100) then
                  fitness_bins(k,2) =
     &            fitness_bins(k,2) + 1.
               end if
            end if
         end do

      end do

c...  Compute fitness values for bin boundaries and bin centers.

      do k=1,51
         bin_fitness(k) = exp(-del_bin_width*(k - 1))
         if (k > 1) then
            bin_fitness_boxwidth(k-1) = 
     &                 abs(bin_fitness(k) - bin_fitness(k-1))
            bin_fitness_midpoint(k-1) = 
     &                    (bin_fitness(k) + bin_fitness(k-1))/2.
         end if
      end do

      do k=51,101
         bin_fitness(k) = max_fav_fitness_gain
     &                    *exp(-fav_bin_width*(k - 51))
         if (k > 51) then
            bin_fitness_boxwidth(k-1) = 
     &                 abs(bin_fitness(k) - bin_fitness(k-1))
            bin_fitness_midpoint(k-1) = 
     &                    (bin_fitness(k) + bin_fitness(k-1))/2.
         end if
      end do

c...  Compute the frequency of output of the mutation accumulation
c...  statistics.

      accum_gen = 1000000
      if(mod(gen, 100) == 0) then
         if(gen <= 500) then
            accum_gen = 100
         elseif(gen <=  1000) then
            accum_gen = 500
         elseif(gen <=  5000) then
            accum_gen = 1000
         elseif(gen <= 10000) then
            accum_gen = 5000
         else
            accum_gen = 10000
         end if
         if(gen == 100) accum = 0.
      end if

c...  Output the number of accumulated deleterious dominant mutations 
c...  in each of 50 bins during the previous accum_gen generations at
c...  appropriate intervals, along with other relevant information.

      if(mod(gen, accum_gen) == 0) then 

         if(gen == 100) then
         write(26,'("#"/"#",11x, "Generation    Accumulation Interval"/
     &      2i19/"#"/"#           Accumulation Over Previous Interval"/
     &      "#"/"# bin  fitness effect    actual      expected       "
     &      "ratio  expected fraction")') gen, accum_gen
         else
         write(26,'("#"/"#",11x, "Generation    Accumulation Interval"/
     &      2i19/"#"/"#           Accumulation Over Previous Interval"/
     &      "#"/"# bin  fitness effect    actual      expected       "
     &      "ratio      total accum")') gen, accum_gen
         end if

         do k=1,50
            del = fitness_bins(k,2) - accum(k)
            del_no_sel = refr_bins(k)*(1. - fraction_recessive)            
     &                   *accum_gen/gen
            ratio = del/del_no_sel
            if(gen == 100) then
            x0    = refr_bins(k)*(1. - fraction_recessive)/mutn_sum
            write(26,'(i4,1pe14.3,i12,0pf14.2,f14.7,1pe14.3)') k,  
     &         bin_fitness_midpoint(k), int(del), del_no_sel, ratio, x0
            else
            write(26,'(i4,1pe14.3,i12,0pf14.2,f14.7,i14)') k,  
     &         bin_fitness_midpoint(k), int(del), del_no_sel, ratio, 
     &         int(fitness_bins(k,2))
            end if
         end do

         accum = fitness_bins(1:50,2)

         call flush(26)

      end if

c...  Normalize the binned mutations by the reciprocal of the expected
c...  number of mutations per bin in the absence of selection.

      x = 1. - fraction_neutral
      if (x.eq.0) x = 1. ! don't scale data if fraction_neutral = 1
      do k=1,100

         if(refr_bins(k) > 0. .and. fraction_recessive > 0.) then
            fitness_bins(k,1) = fitness_bins(k,1)
     &                        /(fraction_recessive*refr_bins(k))/x
         else
            fitness_bins(k,1) = 0.
         end if

         if(refr_bins(k) > 0. .and. fraction_recessive < 1.) then
            fitness_bins(k,2) = fitness_bins(k,2)
     &                       /((1. - fraction_recessive)*refr_bins(k))/x
         else
            fitness_bins(k,2) = 0.
         end if

      end do

c...  Perform an iteration of smoothing on the fitness_bin values 
c...  using a three-point average.  Iterate three times.

      do i=1,3
      fm1 = fitness_bins(1,1)
      fm2 = fitness_bins(1,2)
      do k=2,49
        av1 = fitness_bins(k,1) + 0.5*(fm1 + fitness_bins(k+1,1))
        fm1 = fitness_bins(k,1)
        work(k,1) = 0.5*av1
        av2 = fitness_bins(k,2) + 0.5*(fm2 + fitness_bins(k+1,2))
        fm2 = fitness_bins(k,2)
        work(k,2) = 0.5*av2
      end do
      fitness_bins(50,:) = 0.5*(fitness_bins(49,:) + fitness_bins(50,:))
      fitness_bins(2:49,:) = work(2:49,:)
      end do

c...  For favorable distribution, limit maximum to a value of 100.
c...  To increase the smoothness, iterate the smoothing two times.

      fitness_bins(51:100,:) = min(100., fitness_bins(51:100,:))

      do i=1,2
      fm1 = fitness_bins(51,1)
      fm2 = fitness_bins(51,2)
      do k=52,99
        av1 = fitness_bins(k,1) + 0.5*(fm1 + fitness_bins(k+1,1))
        fm1 = fitness_bins(k,1)
        work(k,1) = 0.5*av1
        av2 = fitness_bins(k,2) + 0.5*(fm2 + fitness_bins(k+1,2))
        fm2 = fitness_bins(k,2)
        work(k,2) = 0.5*av2
      end do
      fitness_bins(52:99,:) = work(52:99,:)
      end do

c...  Write the fitness bin information for deleterious mutations
c...  to standard output.

      if (.not. is_parallel) then
         write(6, '(14x,"Fraction of mutations retained "
     &                  "versus fitness effect")')
         write(6, '(" effect:",10(x,1pe7.0))')
     &             (bin_fitness_midpoint(k),k=3,50,5)
         write(6, '(" domint:",10f7.4)') (fitness_bins(k,2),k=3,50,5) 
         if(fraction_recessive > 0.) write(6, '(" recess:",0p10f7.4)')
     &             (fitness_bins(k,1),k=3,50,5)
      end if

      write(9, '(14x,"Fraction of mutations retained "
     &               "versus fitness effect")')
      write(9, '(" effect:",10(x,1pe7.0))')
     &          (bin_fitness_midpoint(k),k=3,50,5)
      write(9, '(" domint:",10f7.4)') (fitness_bins(k,2),k=3,50,5) 
      if(fraction_recessive > 0.) write(6, '(" recess:",0p10f7.4)')
     &          (fitness_bins(k,1),k=3,50,5)

      rewind (8)

      write(8,'("# generation = ",i8)') gen
      write(8,'("# deleterious mutations")')
      write(8,'("# bin_fitness",3x,"recessive",2x,"dominant",3x,
     &          "box_width")')
      do k=1,50
         write(8, '(1pe13.5,0p2f11.5,1pe13.5)')
     &      bin_fitness_midpoint(k),
     &      fitness_bins(k,1), fitness_bins(k,2),
     &      bin_fitness_boxwidth(k)
      end do

      write(8,'("# favorable mutations")')
      write(8,'("# bin_fitness",3x,"recessive",2x,"dominant",3x,
     &          "box_width")')
      do k=51,100
         write(8, '(1pe13.5,0p2f11.5,1pe13.5,e13.5)')
     &      bin_fitness_midpoint(k),
     &      fitness_bins(k,1), fitness_bins(k,2),
     &      bin_fitness_boxwidth(k), refr_bins(k)
      end do
      call flush(8)

      if(is_parallel) then
         call mpi_davg(fitness_bins,par_fitness_bins,200)
         if(myid==0) then
            rewind (18)
            write(18,'("# generation = ",i8)') gen
            write(18,'("# deleterious mutations")')
            write(18,'("# bin_fitness",3x,"recessive",2x,"dominant",3x,
     &                 "box_width")')
            do k=1,50
               write(18, '(1pe13.5,0p2f11.5,1pe13.5)') bin_fitness(k),
     &            par_fitness_bins(k,1), par_fitness_bins(k,2),
     &            bin_fitness_boxwidth(k)
            end do
            write(18,'("# favorable mutations")')
            write(18,'("# bin_fitness",3x,"recessive",2x,"dominant",3x,
     &                 "box_width")')
            do k=51,100
               write(18, '(1pe13.5,0p2f11.5,1pe13.5)') bin_fitness(k),
     &            par_fitness_bins(k,1), par_fitness_bins(k,2),
     &            bin_fitness_boxwidth(k)
            end do
            call flush(18)
         end if
      end if

c...  Compute the current values of the selection thresholds for both
c...  dominant and recessive deleterious mutations.

c...  Compute estimate for the current deleterious dominant threshold.

      k   = 1
      k0  = 0
      sum = (1. - fraction_recessive)*refr_bins(50)
      del_dom_thres = 0.
 
      do while(k <= 50 .and. sum > 5000) 
         if(fitness_bins(k,2) > 0.25 .and. k0 == 0) k0 = k
         if(fitness_bins(k,2) > 0.75 .and. k > k0 + 1) then
            x0 = 0.
            y0 = 0.
            do i=k0,k-1
               x0 = x0 + i - 0.5
               y0 = y0 + fitness_bins(i,2)
            end do
            x0 = x0/(k - k0)
            y0 = y0/(k - k0)
            s = 0.
            d = 0.
            do i=k0,k-1
               s = s + (i - 0.5 - x0)*(fitness_bins(i,2) - y0)
               d = d + (i - 0.5 - x0)**2
            end do
            b1 = s/d
            b0 =   y0 - b1*x0
            x1 = (0.5 - b0)/b1
            del_dom_thres = exp(-x1*del_bin_width)
            k = 50
         end if
         k = k + 1
      end do

c...  Compute estimate for the current deleterious recessive threshold.

      k   = 1
      k0  = 0
      sum = fraction_recessive*refr_bins(50)
      del_rec_thres = 0.
 
      do while(k <= 50 .and. sum > 5000) 
         if(fitness_bins(k,1) > 0.25 .and. k0 == 0) k0 = k
         if(fitness_bins(k,1) > 0.75 .and. k > k0 + 1) then
            x0 = 0.
            y0 = 0.
            do i=k0,k-1
               x0 = x0 + i - 0.5
               y0 = y0 + fitness_bins(i,1)
            end do
            x0 = x0/(k - k0)
            y0 = y0/(k - k0)
            s = 0.
            d = 0.
            do i=k0,k-1
               s = s + (i - 0.5 - x0)*(fitness_bins(i,1) - y0)
               d = d + (i - 0.5 - x0)**2
            end do
            b1 = s/d
            b0 =   y0 - b1*x0
            x1 = (0.5 - b0)/b1
            del_rec_thres = exp(-x1*del_bin_width)
            k = 50
         end if
         k = k + 1
      end do

c...  Compute estimate for the current favorable dominant threshold.

c...  First find the bin with the maximum ratio of actual to expected
c...  mutations if there were no selection, but restricted to ratios
c...  less than 3.

      y0 = fitness_bins(96,2)
      k0 = 4
      k  = 5
      do while(k <= 50)
         if(fitness_bins(101-k,2) > y0) then
            y0 = fitness_bins(101-k,2)
            k0 = k
         end if
         if(fitness_bins(101-k,2) >= 3.) k = 50
         k = k + 1
      end do

c...  Now find the first bin with k < k0 that is backeted by ratios 
c...  below and above 2.0.

      j = k0 - 1
      do k=k0-1,k0-5,-1
         if(fitness_bins(100-k,2) >  2.0 .and. 
     &      fitness_bins(101-k,2) <= 2.0) then
            j = k
         end if
      end do

      sum = (1. - fraction_recessive)*refr_bins(100)
      fav_dom_thres = 0.

      if(sum > 2000 .and. y0 > 2.5) then

c...    Use simple linear interpolation to find the fitness effect
c...    value corresponding to the ratio of 2.0.

         s  = (fitness_bins(100-j,2) - fitness_bins(101-j,2))/
     &        (bin_fitness_midpoint(100-j)
     &      -  bin_fitness_midpoint(101-j))
         y0 =  fitness_bins(101-j,2) - s*bin_fitness_midpoint(101-j)
         fav_dom_thres = max(0., (2.0 - y0)/s)

      end if

      if(.not. is_parallel) then
         if(del_dom_thres > 0.) then
            x0 = (-log(del_dom_thres)/alpha_del)**(1/gamma_del)
            write(6, '("deleterious selection threshold   =",1pe10.3)') 
     &            del_dom_thres
            write(6, '("deleterious fraction unselectable =",f6.3)') 
     &            1. - x0
         end if
         if(fav_dom_thres > 0.) then
            x0 = (-log(fav_dom_thres/max_fav_fitness_gain)/alpha_fav)
     &           **(1/gamma_fav)
            write(6, '("  favorable selection threshold   =",1pe10.3)') 
     &            fav_dom_thres
            write(6, '("  favorable fraction unselectable =",f6.3)') 
     &            1. - x0
         end if
      else
         call mpi_davg(del_dom_thres,par_del_dom_thres,1)
         if(myid == 0. .and. par_del_dom_thres > 0.) then
            x0 = (-log(par_del_dom_thres)/alpha_del)**(1/gamma_del)
            write(6, '("deleterious selection threshold   =",1pe10.3)') 
     &            par_del_dom_thres
            write(6, '("deleterious fraction unselectable =",f6.3)') 
     &            1. - x0
         end if
         call mpi_davg(fav_dom_thres,par_fav_dom_thres,1)
         if(myid == 0 .and. par_fav_dom_thres > 0.) then
            x0 = (-log(par_fav_dom_thres/max_fav_fitness_gain)
     &           /alpha_fav)**(1/gamma_fav)
            write(6, '("  favorable selection threshold   =",1pe10.3)') 
     &            par_fav_dom_thres
            write(6, '("  favorable fraction unselectable =",f6.3)') 
     &            1. - x0
         end if
      end if

      if(del_dom_thres > 0.) then
         x0 = (-log(del_dom_thres)/alpha_del)**(1/gamma_del)
         write(9, '("deleterious selection threshold   =",1pe10.3)') 
     &         del_dom_thres
         write(9, '("deleterious fraction unselectable =",f6.3)') 
     &         1. - x0
      end if
      if(fav_dom_thres > 0.) then
         x0 = (-log(fav_dom_thres/max_fav_fitness_gain)/alpha_fav)
     &        **(1/gamma_fav)
         write(9, '("  favorable selection threshold   =",1pe10.3)') 
     &         fav_dom_thres
         write(9, '("  favorable fraction unselectable =",f6.3)') 
     &         1. - x0
      end if

      if(is_parallel.and.myid==0) then
         oneortwo=2
      else
         oneortwo=1
      endif

      fid=25

      do i=1,oneortwo
         if(oneortwo==2) then
            fid=35
            del_dom_thres = par_del_dom_thres
            fav_dom_thres = par_fav_dom_thres
         end if
         
c...     Do not write out zero threshold values, instead use NaN's
         if (del_dom_thres == 0 .and. 
     &       del_rec_thres == 0 .and.
     &       fav_dom_thres == 0) then
            write(fid, '(i10,3a15)') 
     &            gen, 'NaN', 'NaN', 'NaN' 
         else if (del_dom_thres == 0 .and. del_rec_thres == 0) then
            write(fid, '(i10,2a15,1p1e15.3)') 
     &            gen, 'NaN', 'NaN', fav_dom_thres
         else if (del_dom_thres == 0 .and. fav_dom_thres == 0) then
            write(fid, '(i10,a15,1p1e15.3,a15)') 
     &            gen, 'NaN', del_rec_thres, 'NaN' 
         else if (del_rec_thres == 0 .and. fav_dom_thres == 0) then
            write(fid, '(i10,1p1e15.3,2a15)') 
     &            gen, del_dom_thres, 'NaN', 'NaN' 
         else if(del_dom_thres == 0) then
            write(fid, '(i10,a15,1p2e15.3)') 
     &            gen, 'NaN', del_rec_thres, fav_dom_thres
         else if(del_rec_thres == 0) then
            write(fid, '(i10,1p1e15.3,a15,1p1e15.3)') 
     &            gen, del_dom_thres, 'NaN', fav_dom_thres
         else if (fav_dom_thres == 0) then
            write(fid, '(i10,1p2e15.3,a15)') 
     &            gen, del_dom_thres, del_rec_thres, 'NaN'
         else
            write(fid, '(i10,1p3e15.3)') 
     &            gen, del_dom_thres, del_rec_thres, fav_dom_thres
         end if

         call flush(fid)

      end do

      end

      subroutine diagnostics_near_neutrals_plot(dmutn, fmutn, 
     &   linkage_block_fitness, lb_mutn_count, gen)

      include 'common.h'
      integer dmutn(max_del_mutn_per_indiv/2,2,*)
      integer fmutn(max_fav_mutn_per_indiv/2,2,*)
      integer lb_mutn_count(num_linkage_subunits,2,2,*)
      real*8 linkage_block_fitness(num_linkage_subunits,2,*)
      integer gen, i, j, k, lb
      real*8 bins_mutns(200,2), expn_bins(200)
      real*8 haplotype_bins(200), haplotype_bin_width, avg_lb_effect
      real*8 lb_fitness_frac_positive, num_del_lb, num_fav_lb
      real*8 par_expn_bins(200)
      real*8 par_haplotype_bins(200), par_avg_lb_effect
      real*8 par_lb_fitness_frac_pos, y0
      real*8 d, x, x0, x0r, x1, z0, z1, del_bin_width, fav_bin_width

c...  Generate the theoretical distribution curves for plotting.
   
      haplotype_bin_width = 1.e-04
      del_bin_width = haplotype_bin_width
      fav_bin_width = 0.01*min(0.01, max_fav_fitness_gain)

      x0 = 1.
      do k=100,1,-1
         x1 = (-log(del_bin_width*(101-k))
     &          /alpha_del)**(1./gamma_del)
         expn_bins(k) = (1. - frac_fav_mutn)*(x0 - x1)
         x0 = x1
      end do

      z0 = 1.
      do k=100,1,-1

         x0 = fav_bin_width*(101-k)/max_fav_fitness_gain
         x0 = min(1., x0)
         z1 = (-log(x0)/alpha_fav)**(1./gamma_fav)
         expn_bins(201-k) = frac_fav_mutn*(z0 - z1)
         if(x0 > fav_scale*lb_modulo) expn_bins(201-k) = 0.
         z0 = z1
      end do

      if(expn_bins(100) > 0.)
     &   expn_bins(  1:100) = expn_bins(  1:100)/expn_bins(100)
      if(expn_bins(101) > 0.)
     &   expn_bins(101:200) = expn_bins(101:200)/expn_bins(101)

c...  Compute statistics on favorable and recessive mutations.

      haplotype_bins = 0
      bins_mutns     = 0

      do i=1,current_pop_size

         do lb=1,num_linkage_subunits

            y0 = (linkage_block_fitness(lb,1,i) - 1.d0)
     &            /haplotype_bin_width

            if(y0 < 1.d-20) then
               k = 100 + int(y0)
               if(k > 0)    haplotype_bins(k) = haplotype_bins(k) + 1.
            else
               k = 101 + int(y0)
               if(k <= 200) haplotype_bins(k) = haplotype_bins(k) + 1.
            end if

            y0 = (linkage_block_fitness(lb,2,i) - 1.d0)
     &            /haplotype_bin_width

            if(y0 < 1.d-20) then
               k = 100 + int(y0)
               if(k > 0)    haplotype_bins(k) = haplotype_bins(k) + 1.
            else
               k = 101 + int(y0)
               if(k <= 200) haplotype_bins(k) = haplotype_bins(k) + 1.
            end if

         end do

         do j=2,dmutn(1,1,i)+1
            x = mod(abs(dmutn(j,1,i)),lb_modulo)*del_scale
            if(x < 1.d0) then
               d = dexp(-alpha_del*x**gamma_del)
               k = 100 - int(d/del_bin_width)
               if(dmutn(j,1,i) < 0) then
                  if(k > 0 .and. k <= 100) then
                     bins_mutns(k,1) = 
     &               bins_mutns(k,1) + 1.
                  end if
               else
                  if(k > 0 .and. k <= 100) then
                     bins_mutns(k,2) = 
     &               bins_mutns(k,2) + 1.
                  end if
               end if
            end if
         end do

         do j=2,dmutn(1,2,i)+1
            x = mod(abs(dmutn(j,2,i)),lb_modulo)*del_scale
            if(x < 1.d0) then
               d = dexp(-alpha_del*x**gamma_del)
               k = 100 - int(d/del_bin_width)
               if(dmutn(j,2,i) < 0) then
                  if(k > 0 .and. k <= 100) then
                     bins_mutns(k,1) = 
     &               bins_mutns(k,1) + 1.
                  end if
               else
                  if(k > 0 .and. k <= 100) then
                     bins_mutns(k,2) = 
     &               bins_mutns(k,2) + 1.
                  end if
               end if
            end if
         end do

         do j=2,fmutn(1,1,i)+1
            d = dexp(-alpha_fav*(mod(abs(fmutn(j,1,i)),lb_modulo)
     &                            *fav_scale)**gamma_fav)
            k = 101 + int(d*max_fav_fitness_gain/fav_bin_width)

            if(fmutn(j,1,i) < 0) then
               if(k > 100 .and. k <= 200) then
                  bins_mutns(k,1) = 
     &            bins_mutns(k,1) + 1.
               end if
            else
               if(k > 100 .and. k <= 200) then
                  bins_mutns(k,2) = 
     &            bins_mutns(k,2) + 1.
               end if
            end if
         end do

         do j=2,fmutn(1,2,i)+1
            d = dexp(-alpha_fav*(mod(abs(fmutn(j,2,i)),lb_modulo)
     &                            *fav_scale)**gamma_fav)
            k = 101 + int(d*max_fav_fitness_gain/fav_bin_width)

            if(fmutn(j,2,i) < 0) then
               if(k > 100 .and. k <= 200) then
                  bins_mutns(k,1) = 
     &            bins_mutns(k,1) + 1.
               end if
            else
               if(k > 100 .and. k <= 200) then
                  bins_mutns(k,2) = 
     &            bins_mutns(k,2) + 1.
               end if
            end if
         end do

      end do

      x0 = 1.e-10
      do k=1,200
         x0 = max(x0, haplotype_bins(k))
      end do

      haplotype_bins = haplotype_bins/x0

      if(tracking_threshold /= 1.0) then
         bins_mutns(  1:100,1) = bins_mutns(  1:100,1)
     &              *expn_bins( 99)/(bins_mutns( 99,1) + 1.e-10)
         bins_mutns(  1:100,2) = bins_mutns(  1:100,2)
     &              *expn_bins( 99)/(bins_mutns( 99,2) + 1.e-10)
         bins_mutns(101:200,1) = bins_mutns(101:200,1)
     &              *expn_bins(102)/(bins_mutns(102,1) + 1.e-10)
         bins_mutns(101:200,2) = bins_mutns(101:200,2)
     &              *expn_bins(102)/(bins_mutns(102,2) + 1.e-10)
      end if

      rewind (4)
      write(4,'("# generation = ",i8)') gen
      write(4,'("# effect-bin",2x,"theory(red)",1x,"lb-fitns(g)",
     &          2x,"dominants",2x,"recessives")')

      write(4, '(5e12.4)') ((k - 100.5)*haplotype_bin_width,
     &        expn_bins(k), haplotype_bins(k), 
     &        bins_mutns(k,2),
     &        bins_mutns(k,1), k=1,200)

      avg_lb_effect = (post_sel_fitness - 1.d0)/(2*num_linkage_subunits)

      num_del_lb = 0
      num_fav_lb = 0

      do k=1,100
         num_del_lb = num_del_lb + haplotype_bins(k)
      end do

      do k = 101,200
         num_fav_lb = num_fav_lb + haplotype_bins(k)
      end do
        
      lb_fitness_frac_positive = 
     &   num_fav_lb/(num_del_lb + num_fav_lb)

      write(4,'("# favorable x-axis scaling = ",1pe12.4)')
     &             fav_bin_width/del_bin_width
      write(4,'("# avg_linkage_block_effect = ",1pe12.4)')
     &             avg_lb_effect
      write(4,'("# lb_fitness_percent_positive = ",f12.4)')
     &             lb_fitness_frac_positive*100.
      call flush(4)

      if (is_parallel) then
         call mpi_davg(avg_lb_effect,par_avg_lb_effect,1)
         call mpi_davg(lb_fitness_frac_positive,
     &                 par_lb_fitness_frac_pos,1)
         call mpi_davg(haplotype_bins,par_haplotype_bins,200)
c...     Note: currently only averaging haplotype_bins--
c...     all the other values are currently coming from processor 0
         if(myid==0) then
            rewind (14)
            write(14,'("# generation = ",i8)') gen
            write(14,'("# effect-bin",2x,"theory(red)",1x,"lb-fitns(g)",
     &                 2x,"dominants",2x,"recessives")')
            write(14,'(5e12.4)') ((k - 100.5)*haplotype_bin_width,
     &            expn_bins(k), par_haplotype_bins(k),
     &            bins_mutns(k,2),
     &            bins_mutns(k,1), k=1,200)
            write(14,'("# avg_linkage_block_effect = ",e12.4)')
     &            avg_lb_effect
            write(14,'("# lb_fitness_percent_positive = ",f12.4)')
     &            par_lb_fitness_frac_pos*100.
            call flush(14)
         end if
      end if
       
      end

      subroutine diagnostics_contrasting_alleles(dmutn, fmutn, count,
     &   cum_effect, initial_allele_effects, ica_count, max_size, list)

c...  This routine analyzes the distribution of the initial contrasting
c...  alleles and their effects on overall fitness.  When logical
c...  variable list is .true., routine outputs a list of allele 
c...  frequencies.

      include 'common.h'

      integer max_size, count(num_linkage_subunits,2)
      integer dmutn(max_del_mutn_per_indiv/2,2,max_size)
      integer fmutn(max_fav_mutn_per_indiv/2,2,max_size)
      real initial_allele_effects(num_linkage_subunits)
      real w, effect, freq
      real*8  cum_effect(pop_size)
      integer i, lb, m, indx, ica_count(2)
      integer zygous(num_linkage_subunits)
      character dom*3
      logical list

      w = multiplicative_weighting

      count = 0
      cum_effect = 1.d0

      do i=1,current_pop_size

         zygous = 0

         do m=2,dmutn(1,1,i)+1
            if(mod(dmutn(m,1,i), lb_modulo) == lb_modulo - 1) then 
               lb = dmutn(m,1,i)/lb_modulo + 1
               zygous(lb) = zygous(lb) + 1
            end if
         end do

         do m=2,dmutn(1,2,i)+1
            if(mod(dmutn(m,2,i), lb_modulo) == lb_modulo - 1) then 
               lb = dmutn(m,2,i)/lb_modulo + 1
               zygous(lb) = zygous(lb) + 1
            end if
         end do

         do lb=1,num_linkage_subunits
            if(zygous(lb) == 1) then
               effect = initial_allele_effects(lb)
     &                  *recessive_hetero_expression
               count(lb,1) = count(lb,1) + 1
               cum_effect(i) = (cum_effect(i) - (1.d0 - w)*effect)
     &                                        * (1.d0 - w *effect)
            elseif(zygous(lb) == 2) then
               effect = initial_allele_effects(lb)
               count(lb,1) = count(lb,1) + 2
               cum_effect(i) = (cum_effect(i) - (1.d0 - w)*effect)
     &                                        * (1.d0 - w *effect)
            end if
         end do

         zygous = 0

         do m=2,fmutn(1,1,i)+1
            if(mod(fmutn(m,1,i), lb_modulo) == lb_modulo - 1) then 
               lb = fmutn(m,1,i)/lb_modulo + 1
               zygous(lb) = zygous(lb) + 1
            end if
         end do

         do m=2,fmutn(1,2,i)+1
            if(mod(fmutn(m,2,i), lb_modulo) == lb_modulo - 1) then 
               lb = fmutn(m,2,i)/lb_modulo + 1
               zygous(lb) = zygous(lb) + 1
            end if
         end do

         do lb=1,num_linkage_subunits
            if(zygous(lb) == 1) then
               effect = initial_allele_effects(lb)
     &                  *dominant_hetero_expression
               count(lb,2) = count(lb,2) + 1
               cum_effect(i) = (cum_effect(i) + (1.d0 - w)*effect)
     &                                        * (1.d0 + w *effect)
            elseif(zygous(lb) == 2) then
               effect = initial_allele_effects(lb)
               count(lb,2) = count(lb,2) + 2
               cum_effect(i) = (cum_effect(i) + (1.d0 - w)*effect)
     &                                        * (1.d0 + w *effect)
            end if
         end do

      end do

      ica_count = 0

      do lb=1,num_linkage_subunits
         ica_count(1) = ica_count(1) + count(lb,1)
         ica_count(2) = ica_count(2) + count(lb,2)
      end do

      if(.not.list) then

c...     Compute average effect of initial contrasting alleles.

         ica_mean_effect = 0.

         do i=1,current_pop_size
            ica_mean_effect = ica_mean_effect + (cum_effect(i) - 1.d0)
         end do

         ica_mean_effect = ica_mean_effect/current_pop_size 

c...     Compute mean frequency of positive initial contrasting alleles
c...     and the number of positive initial contrasting alleles fixed 
c...     and lost.
      
         fav_lost  = 0
         fav_fixed = 0
         fav_mean_freq = 0

         do lb=1,num_linkage_subunits
            fav_mean_freq = fav_mean_freq + count(lb,2)
            if(abs(initial_allele_effects(lb)) > 0.) then
               if(count(lb,2) == 2*current_pop_size) 
     &            fav_fixed = fav_fixed + 1
               if(count(lb,2) == 0) fav_lost = fav_lost + 1
            end if
         end do

         fav_mean_freq = fav_mean_freq
     &                   /(2*current_pop_size*num_contrasting_alleles)

      else

         if(.not. is_parallel)
     &   write(6,'(/3x,"List of initial contrasting allele freqencies"/
     &         "     and fitness effect values at end of run:"//
     &         6x,"allele   linkage  favorable  homozygous"/
     &         15x,"subunit  frequency    effect")')

         write(9,'(/3x,"List of initial contrasting allele freqencies"/
     &         "     and fitness effect values at end of run:"//
     &         6x,"allele   linkage  favorable  homozygous"/
     &         15x,"subunit  frequency    effect")')

         indx = 0
         do lb=1,num_linkage_subunits
            if(abs(initial_allele_effects(lb)) > 0.) then
               indx = indx + 1
               freq = 0.5*real(count(lb,2))/real(current_pop_size)
               if(.not. is_parallel)
     &         write(6,'(i10,i10,f12.4,f11.4,6x,a3)') indx, lb, freq,
     &                  abs(initial_allele_effects(lb))
               write(9,'(i10,i10,f12.4,f11.4,6x,a3)') indx, lb, freq,
     &                  abs(initial_allele_effects(lb))
            end if
         end do

         if(.not. is_parallel) write(6,*)
         write(9,*)

      end if

      end

      subroutine diagnostics_heterozygosity(dmutn, fmutn)
      include 'common.h'
      integer dmutn(max_del_mutn_per_indiv/2,2,*)
      integer fmutn(max_fav_mutn_per_indiv/2,2,*)
      integer i,j,k
      integer count_homozygous, count_heterozygous, total_analyzed
      real mutn_per_individual, fraction_heterozygous
      real individual_heterozygosity 

c...  Analyze percent homozygosity and heterozygosity of deleterious mutations

      count_homozygous = 0
      count_heterozygous = 0
      do i=1, current_pop_size

         j = 2
         do k = 2, dmutn(1,j,i)+1

            do while(abs(dmutn(k,1,i)) >  abs(dmutn(j,2,i)) .and.
     &                                j <= dmutn(1,2,i))
               j = j + 1
            end do

            if(dmutn(k,1,i) == dmutn(j,2,i)) then
               count_homozygous = count_homozygous + 1
            else
               count_heterozygous = count_heterozygous + 1
            end if

         end do 
      end do

      total_analyzed = count_heterozygous+count_homozygous
      if(total_analyzed < 10) goto 10
      fraction_heterozygous = count_heterozygous/real(total_analyzed)
      mutn_per_individual = tracked_del_mutn/real(current_pop_size)
      write(*,'(/"HETEROZYGOSITY ANALYSIS OF DELETERIOUS AND NEUTRAL "
     &           "MUTATIONS:")')
      write(*,'("Out of    ",i10," total deleterious and neutral "
     &  "mutations")') 
     &  total_analyzed
      write(*,'("there are ",i10," homozygous mutations")')
     &  count_homozygous
      write(*,'("and       ",i10," heterozygous mutations")')
     &  count_heterozygous
      write(*,'("resulting in a percent heterozygosity of: ",f5.2,"%")')
     &  fraction_heterozygous*100
      write(*,'("There are: ",f7.1," tracked deleterious and neutral "
     &  "mutations per individual")') mutn_per_individual
      write(*,*)
 10   continue

c...  Analyze percent homozygosity and heterozygosity of favorable mutations
    
      if(frac_fav_mutn > 0.) then

      count_homozygous = 0
      count_heterozygous = 0
      do i=1, current_pop_size

         j = 2
         do k=2, fmutn(1,1,i)+1

            do while(abs(fmutn(k,1,i)) >  abs(fmutn(j,2,i)) .and.
     &                                   j <= fmutn(1,2,i))
               j = j + 1
            end do

            if(fmutn(k,1,i) == fmutn(j,2,i)) then
               count_homozygous = count_homozygous + 1
            else
               count_heterozygous = count_heterozygous + 1
            end if
            
         end do 
      end do

      total_analyzed = count_heterozygous+count_homozygous
      if(total_analyzed < 10) goto 20

      fraction_heterozygous = count_heterozygous/real(total_analyzed)
      mutn_per_individual = tracked_fav_mutn/real(current_pop_size)
      write(*,'(/"HETEROZYGOSITY ANALYSIS OF FAVORABLE MUTATIONS:")')
      write(*,'("Out of    ",i10," total favorable mutations")') 
     &  total_analyzed
      write(*,'("there are ",i10," homozygous mutations")')
     &  count_homozygous
      write(*,'("and       ",i10," heterozygous mutations")')
     &  count_heterozygous
      write(*,'("resulting in a percent heterozygosity of: ",f5.2,"%")')
     &  fraction_heterozygous*100
      write(*,'("There are: ",f7.1,
     &          " tracked favorable mutation per individual")') 
     &  mutn_per_individual
      write(*,*)
   
      end if
 20   continue

      end

      subroutine diagnostics_polymorphisms_plot(dmutn, fmutn, mfirst,
     &                                           max_size, gen)

      include 'common.h'
      include '/usr/local/include/mpif.h'
      integer MNP ! Maximum Number of Polymorphisms
      parameter (MNP=1000000)
      integer dmutn(max_del_mutn_per_indiv/2,2,*)
      integer fmutn(max_fav_mutn_per_indiv/2,2,*)
      integer mutn_count(MNP)
      real*8  mfirst(2,max_size)
      integer i, j, k, m, n, lb, it, it0, ie, max_size, gen, list_count
      integer mutn_list(MNP), dcount, fcount, par_dcount, par_fcount
      integer global_mutn_count(MNP,num_tribes)
      integer global_mutn_list(MNP,num_tribes)
      integer global_list_count(num_tribes)
      integer num_falleles(3), num_dalleles(3), lb_limit, dwarn, fwarn
      integer par_num_falleles(3), par_num_dalleles(3), mutn_limit
      integer ncount, par_ncount, num_nalleles(3), par_nalleles(3)
      integer nwarn, nthres, mutn_thres, mutn
      real*8 dpbin(100), dpbin_count(100), dpbin_max, pbin_width
      real*8 npbin(100), npbin_count(100), npbin_max, x
      real*8 fpbin(100), fpbin_count(100), fpbin_max, scale_factor
      real*8 par_dpbin(100), par_fpbin(100), dsum, fsum, fe_bin_width
      real*8 par_npbin(100), par_npbin_count(100), nsum
      real*8 par_dpbin_count(100), par_fpbin_count(100), febin(10,100)
      real   bin_fitness(11), bin_center(10)
      logical new_mutn

c...  For diploid organisms, mutations can be homozygous, and so the
c...  limiting mutation count if each member of the population is
c...  homozygous in a given mutation is twice the population size.
c...  However, for clonal haploid organisms or pure self-fertilization,
c...  the limiting mutation count when each member carries a given
c...  mutation is the population size.  The polymorphism bin width
c...  pbin_width value reflects this difference.

      if (is_parallel) then 
         pbin_width = 2.*current_pop_size/100.*num_tribes
      else
         pbin_width = 2.*current_pop_size/100.
      end if

      if(clonal_reproduction) pbin_width = pbin_width/2.

      fe_bin_width = -log(tracking_threshold)/10.

      if(int(pbin_width) == 0) then
         write(*,*) 'Polymorphism analysis skipped because population',
     &              ' size is too small.'
         return
      end if

c...  Compute statistics on deleterious polymorphisms.  To keep the
c...  required computer time reasonable, limit the maximum number of
c...  polymorphisms to be considered to be MNP.  This may result in
c...  the analysis being performed only over a portion of the total
c...  total population.

      dsum   = 0.
      dpbin  = 0.
      febin  = 0.
      mfirst = 2
      dwarn  = 0
      nthres = int((lb_modulo - 2)*(1. - fraction_neutral) + 0.5)

c...  Loop over recessives first and dominants second.

      it0 = 1
      if(fraction_recessive == 0.) it0 = 2

      do it=it0,2

         do lb=1,num_linkage_subunits

            if(it == 1) then
               mutn_limit = -lb_modulo*(num_linkage_subunits - lb)
            else
               mutn_limit =  lb_modulo*lb
            end if

c...        mutn_list is the list of mutation indices being analyzed
c...        for their frequency.
c...        mutn_count is the number of occurrences of each mutation
c...        in mutn_list.
c...        list_count is the total number of deleterious alleles
c...        being analyzed.

            mutn_list  = 0
            mutn_count = 0
            list_count = 0

            do i=1,current_pop_size
               do j=1,2
                  m = mfirst(j,i)
                  do while(dmutn(m,j,i) < mutn_limit .and.
     &               m <=  dmutn(1,j,i)+1 .and. list_count < MNP)
                     mutn = mod(abs(dmutn(m,j,i)), lb_modulo)
                     if(mutn < nthres .and. mutn /= lb_modulo-1) then
                        if(upload_mutations) then
                           do k=1,num_uploaded_mutn
                              if(dmutn(m,j,i) == uploaded_mutn(k)) then
                                 list_count = min(MNP, list_count + 1)
                                 mutn_count(k) = mutn_count(k) + 1
                                 mutn_list (list_count) = dmutn(m,j,i)
                              end if
                           end do
                        else
                           new_mutn = .true.
                           do k=1,list_count
                              if(dmutn(m,j,i) == mutn_list(k)) then
                                 mutn_count(k) = mutn_count(k) + 1
                                 new_mutn = .false.
                              end if
                           end do
                           if(new_mutn) then
                              list_count = min(MNP, list_count + 1)
                              mutn_list (list_count) = dmutn(m,j,i)
                              mutn_count(list_count) = 1
                           end if
                        end if
                     end if
                     m = m + 1
                  end do
                  mfirst(j,i) = m
               end do
            end do

c           START_MPI
            if(is_parallel) then

c...           For parallel cases, gather all the data together
c...           and do a single global analysis on processor 0.

               call MPI_GATHER(mutn_list,MNP,MPI_INTEGER,
     &              global_mutn_list,MNP,MPI_INTEGER,0,MYCOMM,ierr)
               call MPI_GATHER(mutn_count,MNP,MPI_INTEGER,
     &              global_mutn_count,MNP,MPI_INTEGER,0,MYCOMM,ierr)
               call MPI_GATHER(list_count,1,MPI_INTEGER,
     &              global_list_count,1,MPI_INTEGER,0,MYCOMM,ierr)

               if(myid.eq.0) then

c...              Rebuild mutn_list and mutn_count arrays from data 
c...              aggregated from all the tribes.

                  mutn_list  = 0
                  mutn_count = 0
                  list_count = 0

                  do m = 1,num_tribes 
                     global_list_count(m) = min(MNP/num_tribes,
     &                                      global_list_count(m))
                     do i = 1, global_list_count(m)
                        new_mutn = .true.
                        do k = 1, list_count
                           if(global_mutn_list(i,m).eq.
     &                        mutn_list(k)) then
                              mutn_count(k) = mutn_count(k) 
     &                                      + global_mutn_count(i,m)
                              new_mutn = .false.
                           end if
                        end do
                        if(new_mutn) then
                           list_count = min(MNP, list_count + 1)
                           mutn_list(list_count)  = 
     &                                global_mutn_list(i,m)
                           mutn_count(list_count) = 
     &                                global_mutn_count(i,m)
                        end if
                     end do
                  end do

               end if

            end if
c           END_MPI

c...     Load the allele hit counts into the proper bins and count
c...     the total number of hits accumulated.  

            do k=1,list_count
               j = min(100, 1 + int(mutn_count(k)/pbin_width))
               dpbin(j) = dpbin(j) + 1
               dsum = dsum + mutn_count(k)
               x = mod(abs(mutn_list(k)),lb_modulo)*del_scale
               if(x < 1.d0) then
                  ie = 1 + int(alpha_del*x**gamma_del/fe_bin_width)
                  febin(ie,j) = febin(ie,j) + 1
               end if
            end do

            if(list_count == MNP) dwarn = 1

         end do

      end do

c...  Compute statistics on neutral polymorphisms.  To keep the
c...  required computer time reasonable, limit the maximum number of
c...  polymorphisms to be considered to be MNP.  This may result in
c...  the analysis being performed only over a portion of the total
c...  total population.

      nsum   = 0.
      npbin  = 0.
      nwarn  = 0

      if(track_neutrals) then

         mfirst = 2
         nwarn  = 0

         do lb=1,num_linkage_subunits

            mutn_limit = lb_modulo*lb

c...        mutn_list is the list of mutation indices being analyzed
c...        for their frequency.
c...        mutn_count is the number of occurrences of each mutation
c...        in mutn_list.
c...        list_count is the total number of deleterious alleles
c...        being analyzed.

            mutn_list  = 0
            mutn_count = 0
            list_count = 0

            do i=1,current_pop_size
               do j=1,2
                  m = mfirst(j,i)
                  do while(dmutn(m,j,i) < mutn_limit .and. 
     &               m <=  dmutn(1,j,i)+1 .and. list_count < MNP)
                     mutn = mod(abs(dmutn(m,j,i)), lb_modulo)
                     if(mutn >= nthres .and. mutn /= lb_modulo-1) then
                        if(upload_mutations) then
                           do k=1,num_uploaded_mutn
                              if(dmutn(m,j,i) == uploaded_mutn(k)) then
                                 list_count = min(MNP, list_count + 1)
                                 mutn_count(k) = mutn_count(k) + 1
                                 mutn_list (list_count) = dmutn(m,j,i)
                              end if
                           end do
                        else
                           new_mutn = .true.
                           do k=1,list_count
                              if(dmutn(m,j,i) == mutn_list(k)) then
                                 mutn_count(k) = mutn_count(k) + 1
                                 new_mutn = .false.
                              end if
                           end do
                           if(new_mutn) then
                              list_count = min(MNP, list_count + 1)
                              mutn_list (list_count) = dmutn(m,j,i)
                              mutn_count(list_count) = 1
                           end if
                        end if
                     end if
                     m = m + 1
                  end do
                  mfirst(j,i) = m
               end do
            end do

c           START_MPI
            if(is_parallel) then

c...           For parallel cases, gather all the data together
c...           and do a single global analysis on processor 0.

               call MPI_GATHER(mutn_list,MNP,MPI_INTEGER,
     &              global_mutn_list,MNP,MPI_INTEGER,0,MYCOMM,ierr)
               call MPI_GATHER(mutn_count,MNP,MPI_INTEGER,
     &              global_mutn_count,MNP,MPI_INTEGER,0,MYCOMM,ierr)
               call MPI_GATHER(list_count,1,MPI_INTEGER,
     &              global_list_count,1,MPI_INTEGER,0,MYCOMM,ierr)

               if(myid.eq.0) then

c...              Rebuild mutn_list and mutn_count arrays from data 
c...              aggregated from all the tribes.

                  mutn_list  = 0
                  mutn_count = 0
                  list_count = 0

                  do m = 1,num_tribes 
                     global_list_count(m) = min(MNP/num_tribes,
     &                                      global_list_count(m))
                     do i = 1, global_list_count(m)
                        new_mutn = .true.
                        do k = 1, list_count
                           if(global_mutn_list(i,m).eq.
     &                        mutn_list(k)) then
                              mutn_count(k) = mutn_count(k) 
     &                                      + global_mutn_count(i,m)
                              new_mutn = .false.
                           end if
                        end do
                        if(new_mutn) then
                           list_count = min(MNP, list_count + 1)
                           mutn_list(list_count)  = 
     &                                global_mutn_list(i,m)
                           mutn_count(list_count) = 
     &                                global_mutn_count(i,m)
                        end if
                     end do
                  end do

               end if

            end if
c           END_MPI

c...        Load the allele hit counts into the proper bins and count
c...        the total number of hits accumulated.

            do k=1,list_count
               j = min(100, 1 + int(mutn_count(k)/pbin_width))
               npbin(j) = npbin(j) + 1
               nsum = nsum + mutn_count(k)
            end do

            if(list_count == MNP) nwarn = 1

         end do

      end if

c...  Compute statistics on favorable polymorphisms.  To keep the
c...  required computer time reasonable, limit the maximum number of
c...  polymorphisms to be considered to be MNP.  This may result in
c...  the analysis being performed only over a portion of the total
c...  total population.

      fsum   = 0.
      fpbin  = 0.
      mfirst = 2
      fwarn  = 0

      if(frac_fav_mutn > 0.) then

c...  Loop over recessives first and dominants second.

      it0 = 1
      if(fraction_recessive == 0.) it0 = 2

      do it=it0,2

         do lb=1,num_linkage_subunits

            if(it == 1) then
               mutn_limit = -lb_modulo*(num_linkage_subunits - lb)
            else
               mutn_limit =  lb_modulo*lb
            end if

            mutn_list  = 0
            mutn_count = 0
            list_count = 0

            do i=1,current_pop_size
               do j=1,2
                  m = mfirst(j,i)
                  do while(fmutn(m,j,i) < mutn_limit .and.
     &               m <=  fmutn(1,j,i)+1 .and. list_count < MNP)
                     if(mod(abs(fmutn(m,j,i)), lb_modulo)
     &                                      /= lb_modulo-1) then
                        if(upload_mutations) then
                           do k=1,num_uploaded_mutn
                              if(fmutn(m,j,i) == uploaded_mutn(k)) then
                                 mutn_count(k) = mutn_count(k) + 1
                              end if
                           end do
                        else
                           new_mutn = .true.
                           do k=1,list_count
                              if(fmutn(m,j,i) == mutn_list(k)) then
                                 mutn_count(k) = mutn_count(k) + 1
                                 new_mutn = .false.
                              end if
                           end do
                           if(new_mutn) then
                              list_count = min(MNP, list_count + 1)
                              mutn_list (list_count) = fmutn(m,j,i)
                              mutn_count(list_count) = 1
                           end if
                        end if
                     end if
                     m = m + 1
                  end do
                  mfirst(j,i) = m
               end do
            end do

c	    START_MPI
            if(is_parallel) then

c...           For parallel cases, gather all the data together
c...           and do a single global analysis on processor 0.

               call MPI_GATHER(mutn_list,MNP,MPI_INTEGER,
     &              global_mutn_list,MNP,MPI_INTEGER,0,MYCOMM,ierr)
               call MPI_GATHER(mutn_count,MNP,MPI_INTEGER,
     &              global_mutn_count,MNP,MPI_INTEGER,0,MYCOMM,ierr)
               call MPI_GATHER(list_count,1,MPI_INTEGER,
     &              global_list_count,1,MPI_INTEGER,0,MYCOMM,ierr)

               if(myid.eq.0) then

c...              Rebuild mutn_list and mutn_count arrays from data 
c...              aggregated from all the tribes.

                  mutn_list  = 0
                  mutn_count = 0
                  list_count = 0

                  do m = 1,num_tribes 
                     global_list_count(m) = min(MNP/num_tribes,
     &                                      global_list_count(m))
                     do i = 1, global_list_count(m)
                        new_mutn = .true.
                        do k = 1, list_count
                           if(global_mutn_list(i,m).eq.
     &                        mutn_list(k)) then
                              mutn_count(k) = mutn_count(k) 
     &                                      + global_mutn_count(i,m)
                              new_mutn = .false.
                           end if
                        end do
                        if(new_mutn) then
                           list_count = min(MNP, list_count + 1)
                           mutn_list(list_count)  = 
     &                                global_mutn_list(i,m)
                           mutn_count(list_count) = 
     &                                global_mutn_count(i,m)
                        end if
                     end do
                  end do

               end if

            end if
c	    END_MPI

c...        Load the allele hit counts into the proper bins and count
c...        the total number of hits accumulated.

            do k=1,list_count
               j = min(100, 1 + int(mutn_count(k)/pbin_width))
               fpbin(j) = fpbin(j) + 1
               fsum = fsum + mutn_count(k)
            end do

            if(list_count == MNP) fwarn = 1

         end do

      end do

      end if

      dpbin_max = 1
      npbin_max = 1
      fpbin_max = 1
      num_dalleles(2) = 0
      num_nalleles(2) = 0
      num_falleles(2) = 0

      do j=1,100
         dpbin_max = max(dpbin_max, dpbin(j))
         npbin_max = max(npbin_max, npbin(j))
         fpbin_max = max(fpbin_max, fpbin(j))
         if(j > 1 .and. j < 100) then
            num_dalleles(2) = num_dalleles(2) + dpbin(j)
            num_nalleles(2) = num_nalleles(2) + npbin(j)
            num_falleles(2) = num_falleles(2) + fpbin(j)
         end if
      end do

      num_dalleles(1) = dpbin(1)
      num_nalleles(1) = npbin(1)
      num_falleles(1) = fpbin(1)
      num_dalleles(3) = dpbin(100)
      num_nalleles(3) = npbin(100)
      num_falleles(3) = fpbin(100)
      dcount = dpbin(1) + num_dalleles(2) + dpbin(100)
      ncount = npbin(1) + num_nalleles(2) + npbin(100)
      fcount = fpbin(1) + num_falleles(2) + fpbin(100)

      dpbin_count = dpbin
      dpbin = dpbin/dpbin_max

      npbin_count = npbin
      npbin = npbin/npbin_max

      fpbin_count = fpbin
      fpbin = fpbin/fpbin_max

c...  Compute values for fitness effect bin centers.

      do k=1,11
         bin_fitness(k) = exp(-fe_bin_width*(k - 1))
         if (k > 1) then
            bin_center(k-1) = 0.5*(bin_fitness(k) + bin_fitness(k-1))
         end if
      end do

      write(19,'("# generation = ",i8)') gen
      write(19,"('#',9x,'Table of polymorphism frequency vs. fitness'
     &   ' effect category'/'#'/
     &   '#freq',17x,'fitness effect category center value')")
      write(19,'(3x,1p4e7.0,6e8.1)') bin_center(1:10)
      write(19,'(i3,4i7,6i8)') (k,int(febin(1:10,k)),k=1,100)
      call flush(19)

c...  Output global statistics to file caseid.000.plm
      if(is_parallel) then

         if(myid.eq.0) then
            rewind(21)
            write(21,'("# Number of tribes = ",i4)') num_tribes
            write(21,'("# generation = ",i8)') gen
            write(21,'("# frequency del_normalized fav_normalized",
     &           "  del_count fav_count neu_normalized  neu_count")')
            write(21,'(i11,2f15.11,2f11.0,f15.11,f11.0)') (k, dpbin(k), 
     &          fpbin(k), dpbin_count(k), fpbin_count(k), npbin(k), 
     &                    npbin_count(k), k=1,100)
            write(21,'("# Allele summary statistics:")')
            write(21,'("#  Very rare",6x,"Polymorphic",9x,"Fixed",
     &                 11x,"Total")')
            write(21,'("#",3x,"(0-1%)",9x,"(1-99%)",11x,"(100%)")')
            write(21,'("#",4i10," deleterious")')
     &                 num_dalleles(1), num_dalleles(2),
     &                 num_dalleles(3), dcount
            write(21,'("#",4i10," favorable")')
     &                 num_falleles(1), num_falleles(2),
     &                 num_falleles(3), fcount
            write(21,'("#",4i10," neutral")')
     &                 num_nalleles(1), num_nalleles(2),
     &                 num_nalleles(3), ncount
            call flush(21)
         end if 

      else 

         write(11,'("# generation = ",i8)') gen
         write(11,'("# frequency del_normalized fav_normalized ",
     &              "  del_count fav_count neu_normalized  neu_count")')
         write(11,'(i11,2f15.11,2f11.0,f15.11,f11.0)')  (k, dpbin(k), 
     &             fpbin(k), dpbin_count(k), fpbin_count(k), npbin(k), 
     &                       npbin_count(k), k=1,100)
      end if

c...  Keep a "snapshot" file of latest polymorphism data.

      rewind(13)
      write(13,'("# generation = ",i8)') gen
      write(13,'("# frequency del_normalized fav_normalized ",
     &           "  del_count fav_count neu_normalized  neu_count")')
      write(13,'(i11,2f15.11,2f11.0,f15.11,f11.0)')  (k, dpbin(k), 
     &          fpbin(k), dpbin_count(k), fpbin_count(k), npbin(k), 
     &                    npbin_count(k), k=1,100)
      call flush(13)

      if(.not.is_parallel) then
         write(11,"('#',11x,'Allele summary statistics (tracked'
     &      ' mutations only):'/
     &      '#   (Statistics are based on ',i12,' tracked deleterious'
     &      ' mutations'/
     &      '#                            ',i12,' tracked   favorable'
     &      ' mutations'/
     &      '#                        and ',i12,' tracked     neutral'
     &      ' mutations.)'/
     &      '#    Very rare   Polymorphic     Fixed      Total'/
     &      '#      (0-1%)      (1-99%)      (100%)')") int(dsum),
     &      int(fsum), int(nsum)
         write(11,"('#',4i12,' deleterious')") num_dalleles(1), 
     &              num_dalleles(2), num_dalleles(3), dcount
         write(11,"('#',4i12,' favorable')")   num_falleles(1), 
     &              num_falleles(2), num_falleles(3), fcount
         write(11,"('#',4i12,' neutral')")   num_nalleles(1), 
     &              num_nalleles(2), num_nalleles(3), ncount
         if(dwarn == 1) write(11,'("# Warning: Number of deleterious "
     &      "polymorhisms exceeded the linkage block limit of ",i8)')MNP
         if(fwarn == 1) write(11,'("# Warning: Number of   favorable "
     &      "polymorhisms exceeded the linkage block limit of ",i8)')MNP
         if(nwarn == 1) write(11,'("# Warning: Number of     neutral "
     &      "polymorhisms exceeded the linkage block limit of ",i8)')MNP
         call flush(11)
      end if

      if(myid == 0) then
      write(6,"(/12x,'Allele summary statistics (tracked mutations'
     &   ' only):'/
     &   '    (Statistics are based on ',i12,' tracked deleterious'
     &   ' mutations'/
     &   '                             ',i12,' tracked   favorable'
     &   ' mutations'/
     &   '                         and ',i12,' tracked     neutral'
     &   ' mutations.)'/
     &   '     Very rare   Polymorphic     Fixed      Total'/
     &   '       (0-1%)      (1-99%)      (100%)')") int(dsum),
     &   int(fsum), int(nsum)
      write(6,"(' ',4i12,' deleterious')") num_dalleles(1), 
     &           num_dalleles(2), num_dalleles(3), dcount
      write(6,"(' ',4i12,' favorable')")   num_falleles(1), 
     &           num_falleles(2), num_falleles(3), fcount
      write(6,"(' ',4i12,' neutral')")   num_nalleles(1), 
     &           num_nalleles(2), num_nalleles(3), ncount
      if(dwarn == 1) write(6,'("  Warning: Number of deleterious "
     &   "polymorhisms exceeded the linkage block limit of ",i8)') MNP
      if(fwarn == 1) write(6,'("  Warning: Number of   favorable "
     &   "polymorhisms exceeded the linkage block limit of ",i8)') MNP
      if(nwarn == 1) write(6,'("  Warning: Number of     neutral "
     &   "polymorhisms exceeded the linkage block limit of ",i8)') MNP
      end if

      write(9,"(/12x,'Allele summary statistics (tracked mutations'
     &   ' only):'/
     &   '    (Statistics are based on ',i12,' tracked deleterious'
     &   ' mutations'/
     &   '                             ',i12,' tracked   favorable'
     &   ' mutations'/
     &   '                         and ',i12,' tracked     neutral'
     &   ' mutations.)'/
     &   '     Very rare   Polymorphic     Fixed      Total'/
     &   '       (0-1%)      (1-99%)      (100%)')") int(dsum),
     &   int(fsum), int(nsum)
      write(9,"(' ',4i12,' deleterious')") num_dalleles(1), 
     &           num_dalleles(2), num_dalleles(3), dcount
      write(9,"(' ',4i12,' favorable')")   num_falleles(1), 
     &           num_falleles(2), num_falleles(3), fcount
      write(9,"(' ',4i12,' neutral')")   num_nalleles(1), 
     &           num_nalleles(2), num_nalleles(3), ncount
      if(dwarn == 1) write(9,'("  Warning: Number of deleterious "
     &   "polymorhisms exceeded the linkage block limit of ",i8)') MNP
      if(fwarn == 1) write(9,'("  Warning: Number of   favorable "
     &   "polymorhisms exceeded the linkage block limit of ",i8)') MNP
      if(nwarn == 1) write(9,'("  Warning: Number of     neutral "
     &   "polymorhisms exceeded the linkage block limit of ",i8)') MNP

      end

      subroutine diagnostics_selection(fitness_pre_sel,fitness_post_sel,
     &                                 total_offspring,gen)

      include 'common.h'
      integer NBINS
      parameter (NBINS=200)
      real*8 fitness_pre_sel(*), fitness_post_sel(*)
      integer total_offspring, gen, i, j, jmax, max_bin
      integer sel_bins(NBINS,2), par_sel_bins(NBINS,2)
      integer fid, oneortwo
      real select_ratio, srm, srp
      real*8 par_pre_sel_fitness, par_post_sel_fitness,
     &       par_pre_sel_geno_sd, par_pre_sel_pheno_sd,
     &       par_pre_sel_corr, par_post_sel_geno_sd,
     &       par_post_sel_pheno_sd, par_post_sel_corr

      sel_bins = 0

      do i=1,total_offspring
         j = min(NBINS, int(100.*fitness_pre_sel(i)))
         sel_bins(j,1) = sel_bins(j,1) + 1
      end do

      do i=1,current_pop_size
         j = min(NBINS, int(100.*fitness_post_sel(i)))
         sel_bins(j,2) = sel_bins(j,2) + 1
      end do
 
      jmax    = 1
      max_bin = 0

      do j=1,NBINS
         if(sel_bins(j,2) > max_bin) then
            max_bin = sel_bins(j,2)
            jmax = j
         end if
      end do

      if(is_parallel) then
         call mpi_isum(sel_bins,par_sel_bins,300)
      end if

c...  Compute averages across processors.

      if (is_parallel) then

         call mpi_davg(pre_sel_fitness,par_pre_sel_fitness,1)
         call mpi_davg(post_sel_fitness,par_post_sel_fitness,1)
         call mpi_mybcastd(par_post_sel_fitness,1)
         call mpi_davg(pre_sel_geno_sd,
     &                 par_pre_sel_geno_sd,1)
         call mpi_davg(pre_sel_pheno_sd,
     &                 par_pre_sel_pheno_sd,1)
         call mpi_davg(pre_sel_corr,
     &                 par_pre_sel_corr,1)
         call mpi_davg(post_sel_geno_sd,
     &                 par_post_sel_geno_sd,1)
         call mpi_davg(post_sel_pheno_sd,
     &                 par_post_sel_pheno_sd,1)
         call mpi_davg(post_sel_corr,
     &                 par_post_sel_corr,1)

      end if

c     If parallel is turned on, write two files
c     caseid.001.sel which contains results for one tribe
c     and caseid.000.sel which contains data averaged from
c     all tribes.
      if (is_parallel .and. myid==0) then
          oneortwo = 2
      else 
          oneortwo = 1
      end if 

      fid = 24

      do i = 1, oneortwo
         if(oneortwo==2) then
            fid = 34
            sel_bins = par_sel_bins
            pre_sel_fitness  = par_pre_sel_fitness
            post_sel_fitness = par_post_sel_fitness
            pre_sel_geno_sd  = par_pre_sel_geno_sd
            post_sel_geno_sd = par_post_sel_geno_sd 
            pre_sel_pheno_sd = par_pre_sel_pheno_sd
         end if

         rewind (fid)

         write(fid,'("# generation = ",i8)') gen
         write(fid,'("# heritability            =",f9.5)')
     &              heritability
         write(fid,'("# non scaling noise       =",f9.5)')
     &              non_scaling_noise
         write(fid,'("# pre  selection fitness  =",f9.5)')
     &              pre_sel_fitness
         write(fid,'("# post selection fitness  =",f9.5)')
     &              post_sel_fitness
         write(fid,'("# pre  selection geno  sd =",f9.5)')
     &              pre_sel_geno_sd
         write(fid,'("# post selection geno  sd =",f9.5)')
     &              post_sel_geno_sd
         write(fid,'("# pre  selection pheno sd =",f9.5)')
     &              pre_sel_pheno_sd
         write(fid,'("# post selection pheno sd =",f9.5)')
     &              post_sel_pheno_sd
         write(fid,'("# Effect of Selection on Phenotypic Fitness ",
     &              "Distribution")')
         write(fid,'("# Note: Individuals with phenotypic fitness > ",
     &              "1.5 are all put into last bin")')
         write(fid,'("# max bin fitness",5x,"before selection",5x,
     &            "after selection",5x,"ratio")')
         do j=1,NBINS-1
            srm = sel_bins(j  ,2)/(real(sel_bins(j  ,1)) + 0.000001)
            if(sel_bins(j  ,1) == 0) srm = -2.
            srp = sel_bins(j+1,2)/(real(sel_bins(j+1,1)) + 0.000001)
            if(sel_bins(j+1,1) == 0) srp = -2.
            select_ratio = 0.5*(srm + srp)
            if(sel_bins(j,2) + sel_bins(j+1,2) <= max(4, max_bin/50)) 
     &         select_ratio = -1.
            if(select_ratio > 0.) then
               write(fid,'(f10.3,2i20,f18.3)') j*0.01,
     &            sel_bins(j,:), select_ratio
            else
               write(fid,'(f10.3,2i20,15x,"?")') j*0.01, sel_bins(j,:) 
            end if
         end do    

         call flush(fid)

      end do

      end

      subroutine favorable_mutn(fmutn,lb_mutn_count,
     &                          linkage_block_fitness)

c...  This routine generates a random mutation in a randomly chosen
c...  linkage block with a randomly chosen haploid identity in a
c...  randomly chosen individual in the population and modifies the
c...  linkage block fitness to reflect the resulting fitness change.

      use random_pkg
      include 'common.h'

      integer fmutn(max_fav_mutn_per_indiv/2,2,*)
      integer lb_mutn_count(num_linkage_subunits,2,2,*)
      real*8 linkage_block_fitness(num_linkage_subunits,2,*)
      real*8 fitness_gain
      real w, x
      integer i, lb, hap_id, mutn, mutn_indx, num_mutn, j
      call second(tin)

c...  Specify the new random favorable mutation. 

c...  Generate the index of the random individual.

      i  = min(current_pop_size,
     &     1 + int(current_pop_size*randomnum(1)))

c...  Generate the linkage block index.

      lb = min(num_linkage_subunits,
     &     1 + int(num_linkage_subunits*randomnum(1)))

c...  Generate the haploid identity.

      hap_id = min(2, 1 + int(2.*randomnum(1)))

c...  Generate a random index mutn to specify the fitness effect
c...  associated with the mutation.

      x = randomnum(1)

      if(tracking_threshold /= 1.0) then
         mutn = min(lb_modulo-2, int(x/fav_scale))
      else
         mutn = 1
      end if

c...  Add an offset to assign it to the appropriate linkage block.

      mutn_indx = mutn + (lb - 1)*lb_modulo 

c...  Specify whether the mutation is dominant or recessive.
c...  (Recessives have a negative mutation index.) 

      if(fraction_recessive > 0.) then
        if(randomnum(1) < fraction_recessive) mutn_indx = -mutn_indx
      end if

c...  Increment the favorable mutation count for the appropriate
c...  individual, linkage block, and haploid index.

      lb_mutn_count(lb,hap_id,2,i) = lb_mutn_count(lb,hap_id,2,i) + 1

c...  Compute the fitness factor associated with this new mutation.
c...  Incorporate this fitness contribution into the fitness of the
c...  the appropriate linkage block. 

c...  When parameter fitness_distrib_type is 1, the fitness
c...  factor f is obtained from the mutation index mutn using a
c...  distribution function of the form
c...
c...    f = (1. + max_fav_fitness_gain*exp(-alpha_fav*x**gamma_fav)
c...
c...  where max_fav_fitness_gain is an input parameter, alpha_fav is 
c...  is log(genome_size*max_fav_fitness_gain) and x is a 
c...  random number uniformly distributed between zero and one.
c...
c...  When parameter fitness_distrib_type is 0, the fitness
c...  factor is constant and given by the expression
c...
c...    f = 1. + uniform_fitness_effect_fav

      if(fitness_distrib_type == 1) then ! Natural distribution
         fitness_gain = max_fav_fitness_gain*dexp(-alpha_fav
     &                                             *x**gamma_fav)
      else if (fitness_distrib_type == 2) then ! All mutn neutral
         fitness_gain = 0
      else ! All mutations have equal effect
         fitness_gain = uniform_fitness_effect_fav
      end if

c...  Track this mutation if its fitness gain exceeds the value of
c...  tracking_threshold. 

      if(fitness_gain > tracking_threshold) then

c...     Test to see if the storage limit of array fmutn has been
c...     exceeded.  (Note that we are using the first slot to hold the
c...     actual mutation count.)

         num_mutn = fmutn(1,hap_id,i) + 1 

         if(num_mutn + 1 > max_fav_mutn_per_indiv/2) then
            write(6,*) 'Favorable mutations exceed the storage limit'
            write(9,*) 'Favorable mutations exceed the storage limit'
            stop
         end if

         fmutn(1,hap_id,i) = num_mutn

c...     Insert new mutation such that mutations are maintained
c...     in ascending order of their absolute value.

         j = num_mutn

         do while(abs(fmutn(j,hap_id,i)) > abs(mutn_indx)
     &               .and. j > 1)
            fmutn(j+1,hap_id,i) = fmutn(j,hap_id,i)
            j = j - 1
         end do

         fmutn(j+1,hap_id,i) = mutn_indx

      end if

c...  Recessive mutations (identified as such with a negative
c...  mutation index) here incur only recessive_hetero_expression
c...  times of their fitness gain, while dominant mutations incur
c...  only dominant_hetero_expression times their fitness gain.
c...  The full fitness gain is realized only when a mutation occurs 
c...  in both instances of its linkage block, that is, is homozygous.

      if(mutn_indx < 0) then
         fitness_gain = recessive_hetero_expression*fitness_gain
      else
         fitness_gain =  dominant_hetero_expression*fitness_gain
      end if

      w = multiplicative_weighting

      linkage_block_fitness(lb,hap_id,i) = 
     &   (linkage_block_fitness(lb,hap_id,i) + (1. - w)*fitness_gain)
     &                                     * (1.d0 + w *fitness_gain)

      call second(tout)
      sec(4) = sec(4) + tout - tin
      end

      subroutine gen_initial_contrasting_alleles(dmutn, fmutn,
     &   linkage_block_fitness, initial_allele_effects, max_size)

c...  This routine generates a small number (no larger than the number
c...  of linkage subunits) of paired alleles, with a random fitness
c...  effect on one haplotype set and an effect with the same magnitude
c...  but the opposite sign on the other haplotype set.  Variation of 
c...  of fitness effect is according to a uniform random distribution
c...  with a user-specified mean value.

      use random_pkg
      include 'common.h'

      integer max_size
      integer dmutn(max_del_mutn_per_indiv/2,2,max_size)
      integer fmutn(max_fav_mutn_per_indiv/2,2,max_size)
      real*8 linkage_block_fitness(num_linkage_subunits,2,max_size)
      real initial_allele_effects(num_linkage_subunits)
      real w, effect, expressed
      integer h1_id, h2_id, lb, mutn, mutn_indx
      integer m, n, nskp

      w = multiplicative_weighting

      if(num_contrasting_alleles > 0) then
         num_contrasting_alleles = min(num_linkage_subunits,
     &                                 num_contrasting_alleles)
         nskp = num_linkage_subunits/num_contrasting_alleles
      else
         return
      end if

      initial_allele_effects = 0.

      do n=1,num_contrasting_alleles

         lb = 1 + (n - 1)*nskp

c...     Use the same mutation effect index for all of these paired 
c...     alleles. This index, lb_modulo-1, is reserved exclusively for
c...     these alleles.  When treated as an ordinary mutation, the 
c...     fitness effect it would imply is the smallest effect possible.
c...     The fitness effects associated with these alleles, however, 
c...     are handled via the linkage_block_fitness array.  We tag these
c...     alleles with a mutation index to be able to track them over
c...     successive generations and obtain statistics on them at the 
c...     end of a run.

         mutn = lb_modulo - 1

c...     Add an offset to assign it to the appropriate linkage block.

         mutn_indx = mutn + (lb - 1)*lb_modulo

c...     Generate random haplotype identities.

         h1_id = min(2, 1 + int(2.*randomnum(1)))
         h2_id = 3 - h1_id

         m = dmutn(1,h1_id,1) + 1
         dmutn(m+1,h1_id,:) = mutn_indx
         dmutn(  1,h1_id,:) = m
         m = fmutn(1,h2_id,1) + 1
         fmutn(m+1,h2_id,:) = mutn_indx
         fmutn(  1,h2_id,:) = m

c...     Generate the uniformly distributed random fitness effect
c...     associated with the allele pair. 

         effect = 2.*initial_alleles_mean_effect*randomnum(1)
         if(num_contrasting_alleles < 11) 
     &      effect = initial_alleles_mean_effect

c...     Store the value of the fitness effect for each allele pair in
c...     array initial_allele_effects.

         initial_allele_effects(lb) = effect

c...     We assume deleterious alleles behave in a recessive manner
c...     and when heterozygous have an effect given by the allele
c...     fitness effect multiplied by recessive_hetero_expression.
c...     Similarly, we assume favorable alleles behave in a dominant
c...     manner and when heterozygous have an effect given by the 
c...     allele fitness effect times dominant_hetero_expression.  The
c...     full allele fitness effect is realized only when the same
c...     version of the allele occurs on both instances of its linkage 
c...     block, that is, is homozygous.

c...     Apply the appropriate fitness effects to the appropriate
c...     linkage blocks.

         expressed = recessive_hetero_expression*effect
         linkage_block_fitness(lb,h1_id,:) = (1.d0 - (1.-w)*expressed)
     &                                         * (1.d0 - w *expressed)

         expressed =  dominant_hetero_expression*effect
         linkage_block_fitness(lb,h2_id,:) = (1.d0 + (1.-w)*expressed)
     &                                         * (1.d0 + w *expressed)

      end do

      end

      subroutine initialize(myid_str)

      use random_pkg
      include 'common.h'

      integer values(8), npath, i, k
      real d1, d2, sum, del_mean, fav_mean, alpha, gamma
      real fraction_del_tracked
      character*3 myid_str, zero_str

c...  Initialize the profile timer
      sec = 0.0
      cyclic_bottlenecking = .false.

c...  Output version information.  RCS will automatically update
c...  the following $Id string on check-in

      write(6,*) 
     & '$Id: mendel.f,v 1.293 2012/02/01 13:31:44 wes Exp $'

      call date_and_time(VALUES=values)

      if(is_parallel) then
         call mpi_myinit(myid,ierr)
         
         write(myid_str,'(i3.3)') myid+1

         if (.not.homogenous_tribes) then
            open (5, file='mendel.in.'//myid_str,status='old')
            call read_parameters(5)
            close(5)
         end if

         if (myid==0) write(*,*) 'subpopulation size is ',pop_size

         if(num_indiv_exchanged > pop_size) then
            write(6,*) 'ERROR: num_indiv_exchanged >= tribal pop_size'
            write(6,*) 'ERROR: decrease num_indiv_exchanged.'
            call mpi_myabort()
         end if
      else
         write(myid_str,'(i3.3)') 0
         myid = 0
      end if 

      npath = index(data_file_path,' ') - 1

      open (4, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.hap',status='unknown')

      if (restart_case) then
         open (7, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.hst',status='unknown',position='append')
      else
         open (7, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.hst',status='unknown')
         write(7,'("# generation",4x,"fitness",9x,"fitness_sd",
     &             6x,"num_dmutns",4x,"num_fmutns",4x,"num_nmutns",
     &             4x,"pop_size")')
      end if

      open (8, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.dst',status='unknown')

      open (9, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.out',status='unknown')

      open(10, file=data_file_path(1:npath)//case_id//'.st8',
     &         status='unknown')
      write(10,*) 0
      close(10)

      if(.not.is_parallel) then
         open(11, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &        //'.plm',status='unknown')
      end if

c     open(12, file=data_file_path(1:npath)//case_id//'.'//myid_str
c    &      //'.sam',status='unknown')

c...  Maintain a separate file for windows which just has a snapshot
c...  of the most recent polymorphism information.
      open(13, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &         //'.pls',status='unknown')

      open(19, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.pmd',status='unknown')

c     open(15, file=data_file_path(1:npath)//case_id//'.'//myid_str
c    &      //'.ppm',status='unknown')

c...  Write header for PPM file
c     write(15,'("P3")')
c     write(15,'(2i)') pop_size, num_generations
c     write(15,'("255")')

      open(16, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.fit',status='unknown')

      open(22, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.tim',status='unknown')

      write(22,'("# generation",2x,"time_per_gen(s)",2x,
     &           "time_offspring(s)",2x,"time_selection(s)")')

      open(24, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.sel',status='unknown')

      open(25, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.thr',status='unknown')
      write(25,'("#  generation",20x,"selection thresholds"/"#",13x,
     &  "del_dom_thres  del_rec_thres  fav_dom_thres  fav_rec_thres")')

      open(26, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.acc',status='unknown')
 
      open(30, file=data_file_path(1:npath)//case_id//'.'//myid_str
     &      //'.ica',status='unknown')

c...  If parallel, write additional average files with name-tag 000.

      if (is_parallel) then

         write(zero_str,'(i3.3)') 0

         open (14, file=data_file_path(1:npath)//case_id//'.'//zero_str
     &         //'.hap',status='unknown')

         open (17, file=data_file_path(1:npath)//case_id//'.'//zero_str
     &         //'.hst',status='unknown')

         open (18, file=data_file_path(1:npath)//case_id//'.'//zero_str
     &         //'.dst',status='unknown')

         open (21, file=data_file_path(1:npath)//case_id//'.'//zero_str
     &         //'.plm',status='unknown')

         open (23, file=data_file_path(1:npath)//case_id//'.'//zero_str
     &         //'.tim',status='unknown')
         write(23,'("# generation",2x,"time_per_gen(s)",2x,
     &              "time_offspring(s)",2x,"time_selection(s)")')

         open (34, file=data_file_path(1:npath)//case_id//'.'//zero_str
     &         //'.sel',status='unknown')

         open (35, file=data_file_path(1:npath)//case_id//'.'//zero_str
     &         //'.thr',status='unknown')
         write(35,'("#  generation",20x,"selection thresholds"/"#",13x,
     &   "del_dom_thres  del_rec_thres  fav_dom_thres  fav_rec_thres")')

      end if
 
      if(myid==0) 
     &   write(6, '(/" Case started ",i2,"/",i2,"/",i4," at ",i2,":",
     &      i2,":",i2/)') values(2:3), values(1), values(5:7)

         write(9, '(/" Case started ",i2,"/",i2,"/",i4," at ",i2,":",
     &      i2,":",i2/)') values(2:3), values(1), values(5:7)

c...  Check to ensure parameter fraction_random_death does not reduce
c...  actual fertility below 1.0.

      if(reproductive_rate*(1. - fraction_random_death) < 1.) then
         write(6,'("ERROR: Input value of fraction_random_death ",
     &             "implies a fertility of less than 1.0.")')
         write(9,'("ERROR: Input value of fraction_random_death ",
     &             "implies a fertility of less than 1.0.")')
         stop
      end if

c...  Limit the minimum value of heritability to be 10**-20.

      heritability = max(1.e-20, heritability)

c...  Do not track neutrals if there are none to track.

      if(fraction_neutral == 0.) track_neutrals = .false.

c...  If neutrals are to be tracked, set the tracking threshold to 
c...  zero.

      if(track_neutrals) tracking_threshold = 0.

c...  If back mutations are allowed, set the tracking threshold to zero
c...  so that all mutations are tracked.

      if(allow_back_mutn) tracking_threshold = 0.

c...  Initialize number of cumulative back mutations to zero.

      num_back_mutn = 0

      if(.not.dynamic_linkage) haploid_chromosome_number = 1

c...  Initialize some quantities from the input values.

c...  For clonal reproduction, set the number of chromosomes to one
c...  and the number of linkage blocks to one.

      if(clonal_reproduction) then
         haploid_chromosome_number  = 1
         num_linkage_subunits       = 1
         fraction_recessive         = 0.
         if(clonal_haploid) dominant_hetero_expression = 1.
      end if

c...  For the case of dynamic linkage, ensure that the number of linkage 
c...  subunits is an integer times the haploid chromosome number.
 
      if(dynamic_linkage) num_linkage_subunits = (num_linkage_subunits
     &           /haploid_chromosome_number)*haploid_chromosome_number

c...  Echo the parameters for this case to the output file.

      if(is_parallel) then
         if(myid == 0) call write_parameters(6)
      else
         call write_parameters(6)
      end if
      call write_parameters(9)

c...  When tracking_threshold is input as zero, this means that all
c...  mutations are to be tracked.  In this case, set tracking_threshold
c...  to be equal to the minimum fitness value to prevent various
c...  numerical overflow problems that would arise otherwise.

      tracking_threshold = max(1./genome_size,
     &                            tracking_threshold)

      lb_modulo  = (2**30-2)/num_linkage_subunits

      alpha_del  = log(genome_size)
      if(max_fav_fitness_gain > 0.) then
         alpha_fav  = log(genome_size*max_fav_fitness_gain)
      else
         alpha_fav = alpha_del
      end if

      gamma_del  = log(-log(high_impact_mutn_threshold)/alpha_del)
     &            /log(high_impact_mutn_fraction)

      gamma_fav  = log(-log(high_impact_mutn_threshold)/alpha_fav)
     &            /log(high_impact_mutn_fraction)

      if(tracking_threshold == 1./genome_size) then
         del_scale = 1./(lb_modulo - 2)
         fav_scale = 1./(lb_modulo - 2)

c...     When neutrals are to be tracked, Mendel stores their mutation
c...     indices in array dmutn at the high end of the absolute range
c...     of mutation index numbers. To accomplish this, del_scale is
c...     divided by (1. - fraction_neutral). With this larger value for
c...     del_scale, mod(abs(dmutn(j,1,i)),lb_modulo)*del_scale can now
c...     exceed 1.0.  For mutations with mutation index dmutn such that
c...     this occurs, their fitness effect in Mendel is set to zero. 
c...     That is, these correspond to the tracked neutral mutations.

         if(track_neutrals) del_scale = del_scale
     &                                  /(1. - fraction_neutral)
      elseif(tracking_threshold == 1.0) then
         del_scale = 0.
         fav_scale = 0.
      else
         del_scale = exp(log(-log(tracking_threshold)/alpha_del)
     &               /gamma_del)/(lb_modulo-2)
         if(max_fav_fitness_gain > 0.) then
            fav_scale = exp(log(-log(tracking_threshold
     &                  /max_fav_fitness_gain)/alpha_fav)
     &                  /gamma_fav)/(lb_modulo-2)
         else
            fav_scale = 0.
         end if
      end if

c...  Compute mean absolute fitness effect for deleterious mutations.

      sum = 0.
      d2  = 1.

      do i=1,1000000
         d1 = d2
         d2 = exp(-alpha_del*(0.000001*i)**gamma_del)
         sum = sum + d1 + d2
      end do

      del_mean = 0.0000005*sum

c...  Compute mean absolute fitness effect for favorable mutations.

      sum = 0.
      d2  = 1.

      do i=1,1000000
         d1 = d2
         d2 = exp(-alpha_fav*(0.000001*i)**gamma_fav)
         sum = sum + d1 + d2
      end do

      fav_mean = 0.0000005*sum*max_fav_fitness_gain

      if(max_fav_fitness_gain > 0.) then
         alpha = alpha_fav
         gamma = gamma_fav
      else
         alpha = 0.
         gamma = 0.
      end if

c...  Print some properties of the fitness effect distribution.

      do i=1,2
         k = 3 + 3*i
         if((myid==0 .and. i==1) .or. i==2) then

         write(k,
     &   '("  Properties of the Weibull fitness effect distribution ",
     &     "function:"//
     &   "              e(x) = exp(-alpha*x**gamma), 0 < x < 1"//
     &   "  genome_size       = ",1pe9.2/
     &   "  e_high_impact     = ",1pe9.2,"   defining value of *high "
     &   "impact* mutation"/ "  frac_high_impact  = ",1pe9.2,
     &   "   fraction *high impact* mutations of total"//
     &   "  mutation type:        deleterious  favorable "/
     &   "  alpha             = ",0p2f12.5,"   log(genome_size) for"/
     &                                         52x,"deleterious case"/
     &   "  gamma             = ",0p2f12.6//
     &   "  mean   effect     = ",1p2e12.2/
     &   "  median effect     = ",1p2e12.2,"   (x = 0.5)"/
     &   "   0th   percentile = ",1p2e12.2,"   (x = 1.0)"/
     &   "  10th   percentile = ",1p2e12.2,"   (x = 0.9)"/
     &   "  20th   percentile = ",1p2e12.2,"   (x = 0.8)"/
     &   "  30th   percentile = ",1p2e12.2,"   (x = 0.7)"/
     &   "  40th   percentile = ",1p2e12.2,"   (x = 0.6)"/
     &   "  50th   percentile = ",1p2e12.2,"   (x = 0.5)"/
     &   "  60th   percentile = ",1p2e12.2,"   (x = 0.4)"/
     &   "  70th   percentile = ",1p2e12.2,"   (x = 0.3)"/
     &   "  80th   percentile = ",1p2e12.2,"   (x = 0.2)"/
     &   "  90th   percentile = ",1p2e12.2,"   (x = 0.1)"/
     &   "  99th   percentile = ",1p2e12.2,"   (x = 0.01)"/
     &   "  99.9   percentile = ",1p2e12.2,"   (x = 0.001)"/
     &   "  99.99  percentile = ",1p2e12.2,"   (x = 0.0001)"/
     &   "  99.999 percentile = ",1p2e12.2,"   (x = 0.00001)"//
     &   "  Notes:"/
     &   "  (1) The e(x) values above are for a homozygous pair of ",
     &      "mutations."/
     &   "  (2) For favorables, e(x) also includes the factor ",
     &      "max_fav_fitness_gain."/)')
     &   genome_size, high_impact_mutn_threshold,
     &   high_impact_mutn_fraction, alpha_del, alpha, 
     &   gamma_del, gamma, -del_mean, fav_mean,
     &   -exp(-alpha_del*0.5**gamma_del),
     &    exp(-alpha_fav*0.5**gamma_fav)*max_fav_fitness_gain,
     &   -exp(-alpha_del*1.0**gamma_del),
     &    exp(-alpha_fav*1.0**gamma_fav)*max_fav_fitness_gain,
     &   -exp(-alpha_del*0.9**gamma_del),
     &    exp(-alpha_fav*0.9**gamma_fav)*max_fav_fitness_gain,
     &   -exp(-alpha_del*0.8**gamma_del), 
     &    exp(-alpha_fav*0.8**gamma_fav)*max_fav_fitness_gain, 
     &   -exp(-alpha_del*0.7**gamma_del),
     &    exp(-alpha_fav*0.7**gamma_fav)*max_fav_fitness_gain,
     &   -exp(-alpha_del*0.6**gamma_del), 
     &    exp(-alpha_fav*0.6**gamma_fav)*max_fav_fitness_gain, 
     &   -exp(-alpha_del*0.5**gamma_del),
     &    exp(-alpha_fav*0.5**gamma_fav)*max_fav_fitness_gain,
     &   -exp(-alpha_del*0.4**gamma_del), 
     &    exp(-alpha_fav*0.4**gamma_fav)*max_fav_fitness_gain, 
     &   -exp(-alpha_del*0.3**gamma_del),
     &    exp(-alpha_fav*0.3**gamma_fav)*max_fav_fitness_gain,
     &   -exp(-alpha_del*0.2**gamma_del), 
     &    exp(-alpha_fav*0.2**gamma_fav)*max_fav_fitness_gain, 
     &   -exp(-alpha_del*0.1**gamma_del),
     &    exp(-alpha_fav*0.1**gamma_fav)*max_fav_fitness_gain,
     &   -exp(-alpha_del*0.01**gamma_del), 
     &    exp(-alpha_fav*0.01**gamma_fav)*max_fav_fitness_gain, 
     &   -exp(-alpha_del*0.001**gamma_del),
     &    exp(-alpha_fav*0.001**gamma_fav)*max_fav_fitness_gain,
     &   -exp(-alpha_del*0.0001**gamma_del), 
     &    exp(-alpha_fav*0.0001**gamma_fav)*max_fav_fitness_gain, 
     &   -exp(-alpha_del*0.00001**gamma_del), 
     &    exp(-alpha_fav*0.00001**gamma_fav)*max_fav_fitness_gain 

         end if
      end do

      fraction_del_tracked = del_scale*(lb_modulo-2)
      if(tracking_threshold == 1./genome_size) fraction_del_tracked = 1.
      if(myid == 0) then
         write(6,*) " Tracking threshold = ", tracking_threshold
         write(6,*) " Fraction deleterious mutations tracked = ", 
     &                fraction_del_tracked
         write(6,*) " Fraction favorable   mutations tracked = ", 
     &                fav_scale*(lb_modulo-2)
      end if
      write(9,*) " Tracking threshold = ", tracking_threshold
      write(9,*) " Fraction deleterious mutations tracked = ", 
     &             fraction_del_tracked
      write(9,*) " Fraction favorable   mutations tracked = ", 
     &             fav_scale*(lb_modulo-2)

c...  Impose a reasonable limit of the number of tracked mutations 
c...  based on the number of new mutations per offspring, the number
c...  of generations, and the fraction of deleterious mutations tracked.
c...  If the run is a restart run, double the number again.  Limit the 
c...  number by the input value for max_tracted_mutn_per_indiv.

      k = 1.8*mutn_rate*num_generations*fraction_del_tracked
      if(restart_case) k = 2*k

c     max_del_mutn_per_indiv = min(k, max_del_mutn_per_indiv)
c     max_fav_mutn_per_indiv = min(k, max_fav_mutn_per_indiv)

      max_del_mutn_per_indiv = max_del_mutn_per_indiv 
     &                       + 2*num_contrasting_alleles
      max_fav_mutn_per_indiv = max_fav_mutn_per_indiv 
     &                       + 2*num_contrasting_alleles

c...  Prevent array overflow for cases with large numbers of initial
c...  favorable mutations.

      max_fav_mutn_per_indiv = max(max_fav_mutn_per_indiv,
     &                             30*num_initial_fav_mutn/pop_size)

c...  When the parameter tracking_threshold is set to one, it signals
c...  that no mutations are to be tracked.  In this case, the size of
c...  the dmutn and fmutn arrays can be reduced to a minimum.

      if(tracking_threshold == 1.0) then
         max_del_mutn_per_indiv = 4
         max_fav_mutn_per_indiv = 4 
         fraction_recessive     = 0.
         dominant_hetero_expression  = 0.5
         recessive_hetero_expression = 0.5
      end if

      if(myid == 0) 
     $   write(6,'(" Maximum  deleterious mutations tracked = ",i8/ 
     &             " Maximum  beneficial  mutations tracked = ",i8)') 
     &             max_del_mutn_per_indiv, max_fav_mutn_per_indiv            
      write(9,'(" Maximum  deleterious mutations tracked = ",i8/ 
     &          " Maximum  beneficial  mutations tracked = ",i8)') 
     &            max_del_mutn_per_indiv, max_fav_mutn_per_indiv            

c...  Initialize random number generator.

      d1 = randomnum(-abs(random_number_seed+myid))
      poisson_mean = mutn_rate

c...  Compute initial_alleles_mean_effect from input parameters
      initial_alleles_mean_effect = max_total_fitness_increase
     &                            / num_contrasting_alleles

      end

      subroutine offspring(dmutn_offsprng,fmutn_offsprng,
     &                     offsprng_lb_mutn_count,
     &                     offsprng_lb_fitness,dmutn,fmutn,
     &                     lb_mutn_count,linkage_block_fitness,dad,mom,
     &                     tsub)

c...  This routine creates an offspring from a pair of individuals,
c...  indexed 'dad' and 'mom', in the current population.  This 
c...  offspring inherits one set of mutations from each linkage block
c...  pair from each parent.  This mutation information is loaded into
c...  array 'offsprng'.  Also, a set of new deleterious mutations, 
c...  equal in number to mutn_rate*(1. - frac_fav_mutn) and
c...  chosen randomly, are generated for this offspring.  The fitness
c...  associated with each of these new mutations is applied to update
c...  the fitness of the linkage block in which it occurs. 

      use random_pkg
      include 'common.h'

      integer dmutn_offsprng(max_del_mutn_per_indiv/2,2),
     &        fmutn_offsprng(max_fav_mutn_per_indiv/2,2)
      integer          dmutn(max_del_mutn_per_indiv/2,2,*),
     &                 fmutn(max_fav_mutn_per_indiv/2,2,*),
     &      offsprng_lb_mutn_count(num_linkage_subunits,2,2), 
     &               lb_mutn_count(num_linkage_subunits,2,2,*)
      real*8   offsprng_lb_fitness(num_linkage_subunits,2)
      real*8 linkage_block_fitness(num_linkage_subunits,2,*)
      real*8 fitness_effect, se_effect
      real w, x, y, tsub, chance_back_mutn
      integer dad, mom, chr_length, ch, ls0, ls1, ls2, iseg, iseg_max
      integer md1, md2, mf1, mf2, mdd_off, mfd_off, mdm_off, mfm_off
      integer lb, hap_id, new_mutn, mut, mutn, mutn_indx, num_mutn, i
      integer lb_syn, hap_id_syn, mutn_sum
      logical fav, is_back_mutn

      w = multiplicative_weighting

      dmutn_offsprng(1,:) = 0
      fmutn_offsprng(1,:) = 0

      if(.not. clonal_reproduction) then

      if(dynamic_linkage) then
         iseg_max = 3
      else
         iseg_max = 1
      end if

      chr_length = num_linkage_subunits/haploid_chromosome_number

      md1     = 2
      md2     = 2
      mf1     = 2
      mf2     = 2
      mdd_off = 2
      mfd_off = 2

      do ch=1,haploid_chromosome_number

         ls0 = (ch - 1)*chr_length + 1
         ls1 = min(chr_length-1, int(chr_length*randomnum(1))) + ls0
         ls2 = min(chr_length-1, int(chr_length*randomnum(1))) + ls0

         if(ls1 > ls2) then
            lb  = ls1
            ls1 = ls2
            ls2 = lb
         end if

         if(.not.dynamic_linkage) ls1 = num_linkage_subunits

         do iseg=1,iseg_max

         if(iseg == 2) then
            ls0 = ls1 + 1
            ls1 = ls2
         elseif(iseg == 3) then
            ls0 = ls2 + 1
            ls1 = ch*chr_length
         end if

         if(dynamic_linkage)
     &      hap_id = min(2, 1 + int(2.*randomnum(1)))

         do lb=ls0,ls1

c...     Copy the mutation list from the randomly selected haplotype
c...     from the father to form gamete one for the offspring.  Also
c...     copy the corresponding linkage block mutation count and
c...     fitness.

         if(.not.dynamic_linkage)
     &      hap_id = min(2, 1 + int(2.*randomnum(1)))

         if(tracking_threshold /= 1.) then

            do while(abs(dmutn(md1,1,dad)) < lb*lb_modulo .and.
     &              md1 <= dmutn(1,1,dad) + 1)
               if(hap_id == 1) then
                  dmutn_offsprng(mdd_off,1) = dmutn(md1,1,dad)
                  mdd_off = mdd_off + 1
               end if
               md1 = md1 + 1
            end do

            do while(abs(dmutn(md2,2,dad)) < lb*lb_modulo .and.
     &              md2 <= dmutn(1,2,dad) + 1)
               if(hap_id == 2) then
                  dmutn_offsprng(mdd_off,1) = dmutn(md2,2,dad)
                  mdd_off = mdd_off + 1
               end if
               md2 = md2 + 1
            end do

            do while(abs(fmutn(mf1,1,dad)) < lb*lb_modulo .and.
     &              mf1 <= fmutn(1,1,dad) + 1)
               if(hap_id == 1) then
                  fmutn_offsprng(mfd_off,1) = fmutn(mf1,1,dad)
                  mfd_off = mfd_off + 1
               end if
               mf1 = mf1 + 1
            end do

            do while(abs(fmutn(mf2,2,dad)) < lb*lb_modulo .and.
     &              mf2 <= fmutn(1,2,dad) + 1)
               if(hap_id == 2) then
                  fmutn_offsprng(mfd_off,1) = fmutn(mf2,2,dad)
                  mfd_off = mfd_off + 1
               end if
               mf2 = mf2 + 1
            end do

         end if

         offsprng_lb_mutn_count(lb,1,1) = lb_mutn_count(lb,hap_id,1,dad)
         offsprng_lb_mutn_count(lb,1,2) = lb_mutn_count(lb,hap_id,2,dad)
         offsprng_lb_fitness(lb,1) =
     &              linkage_block_fitness(lb,hap_id,dad)
         end do

         end do

      end do

      md1     = 2
      md2     = 2
      mf1     = 2
      mf2     = 2
      mdm_off = 2
      mfm_off = 2

      do ch=1,haploid_chromosome_number

         ls0 = (ch - 1)*chr_length + 1
         ls1 = min(chr_length-1, int(chr_length*randomnum(1))) + ls0
         ls2 = min(chr_length-1, int(chr_length*randomnum(1))) + ls0

         if(ls1 > ls2) then
            lb  = ls1
            ls1 = ls2
            ls2 = lb
         end if

         if(.not.dynamic_linkage) ls1 = num_linkage_subunits

         do iseg=1,iseg_max

         if(iseg == 2) then
            ls0 = ls1 + 1
            ls1 = ls2
         elseif(iseg == 3) then
            ls0 = ls2 + 1
            ls1 = ch*chr_length
         end if

         if(dynamic_linkage)
     &      hap_id = min(2, 1 + int(2.*randomnum(1)))

         do lb=ls0,ls1

c...     Copy the mutation list from the randomly selected haplotype
c...     from the mother to form gamete two for the offspring.  Also
c...     copy the corresponding linkage block mutation count and
c...     fitness.

         if(.not.dynamic_linkage)
     &      hap_id = min(2, 1 + int(2.*randomnum(1)))

         if(tracking_threshold /= 1.) then

            do while(abs(dmutn(md1,1,mom)) < lb*lb_modulo .and.
     &              md1 <= dmutn(1,1,mom) + 1)
               if(hap_id == 1) then
                  dmutn_offsprng(mdm_off,2) = dmutn(md1,1,mom)
                  mdm_off = mdm_off + 1
               end if
               md1 = md1 + 1
            end do

            do while(abs(dmutn(md2,2,mom)) < lb*lb_modulo .and.
     &              md2 <= dmutn(1,2,mom) + 1)
               if(hap_id == 2) then
                  dmutn_offsprng(mdm_off,2) = dmutn(md2,2,mom)
                  mdm_off = mdm_off + 1
               end if
               md2 = md2 + 1
            end do

            do while(abs(fmutn(mf1,1,mom)) < lb*lb_modulo .and.
     &              mf1 <= fmutn(1,1,mom) + 1)
               if(hap_id == 1) then
                  fmutn_offsprng(mfm_off,2) = fmutn(mf1,1,mom)
                  mfm_off = mfm_off + 1
               end if
               mf1 = mf1 + 1
            end do

            do while(abs(fmutn(mf2,2,mom)) < lb*lb_modulo .and.
     &              mf2 <= fmutn(1,2,mom) + 1)
               if(hap_id == 2) then
                  fmutn_offsprng(mfm_off,2) = fmutn(mf2,2,mom)
                  mfm_off = mfm_off + 1
               end if
               mf2 = mf2 + 1
            end do

         end if

         offsprng_lb_mutn_count(lb,2,1) = lb_mutn_count(lb,hap_id,1,mom)
         offsprng_lb_mutn_count(lb,2,2) = lb_mutn_count(lb,hap_id,2,mom)
         offsprng_lb_fitness(lb,2) =
     &              linkage_block_fitness(lb,hap_id,mom)
         end do

         end do

      end do

c...  Load the mutation count into the first location in the first 
c...  index of each of the mutation arrays.

      dmutn_offsprng(1,1) = mdd_off - 2
      dmutn_offsprng(1,2) = mdm_off - 2
      fmutn_offsprng(1,1) = mfd_off - 2
      fmutn_offsprng(1,2) = mfm_off - 2

      else   ! Treat case of clonal reproduction.

         mdd_off = dmutn(1,1,dad)
         mdm_off = dmutn(1,2,dad)
         mfd_off = fmutn(1,1,dad)
         mfm_off = fmutn(1,2,dad)

         dmutn_offsprng(1:mdd_off+1,1) = dmutn(1:mdd_off+1,1,dad)
         dmutn_offsprng(1:mdm_off+1,2) = dmutn(1:mdm_off+1,2,dad)
         fmutn_offsprng(1:mfd_off+1,1) = fmutn(1:mfd_off+1,1,dad)
         fmutn_offsprng(1:mfm_off+1,2) = fmutn(1:mfm_off+1,2,dad)

         offsprng_lb_mutn_count(:,:,:) = lb_mutn_count(:,:,:,dad)
         offsprng_lb_fitness(:,:) = linkage_block_fitness(:,:,dad)

      end if  ! end of test on clonal_reproduction

c...  Generate new_mutn new random mutations in randomly chosen
c...  linkage block locations, where new_mutn is a random deviate
c...  drawn from a Poisson distribution with a mean value given by
c...  the parameter poisson_mean, which under most circumstances is
c...  very close to the value of mutn_rate.

      call poisson(poisson_mean, new_mutn)

      new_mutn_count = new_mutn_count + new_mutn

      do mut=1,new_mutn

         is_back_mutn = .false.

         if(allow_back_mutn) then

c...        Possibly substitute a back mutation for a normal one.

c...        The chance of a back mutation = total number of mutations 
c...        in an individual divided by genome size divided by three.

            mutn_sum = fmutn_offsprng(1,1) + fmutn_offsprng(1,2)
     &               + dmutn_offsprng(1,1) + dmutn_offsprng(1,2)
            chance_back_mutn = mutn_sum/(2.*genome_size*3.)

            if(randomnum(1) < chance_back_mutn) then

               is_back_mutn = .true.

               call back_mutn(dmutn_offsprng, fmutn_offsprng,
     &              offsprng_lb_fitness, offsprng_lb_mutn_count)

               num_back_mutn = num_back_mutn + 1

            end if

         end if

         if(.not.is_back_mutn) then

c...     Select a random linkage block for the new mutation.

         lb = min(num_linkage_subunits,
     &        1 + int(num_linkage_subunits*randomnum(1)))

         hap_id = min(2, 1 + int(2.*randomnum(1)))

c...     Determine whether new mutation is deleterious or favorable.

         if(randomnum(1) < frac_fav_mutn*(1. - fraction_neutral)) then
            fav = .true.
         else
            fav = .false.
         end if

c...     Compute the mutation index that is used to specify
c...     its fitness.

 10      continue

         x = randomnum(1)

c...     When neutrals are to be tracked, Mendel stores their mutation
c...     indices in array dmutn at the high end of the absolute range
c...     of mutation index numbers. To accomplish this, del_scale is 
c...     divided by (1. - fraction_neutral) in routine initialize. Here
c...     that is undone so that 1 < mutn <= lb_modulo-2.

         if(tracking_threshold /= 1.0) then
            if(fav) then
               mutn = min(lb_modulo-2, int(x/fav_scale))
            else
               y    = x/del_scale
               if(track_neutrals) y = y/(1. - fraction_neutral)
               mutn = min(lb_modulo-2, int(y))
            end if
         else
            mutn = 1 
         end if

c...     Check to make sure mutation that is being generated does not
c...     correspond with one that has already been uploaded, so
c...     when we track the mutations, they will just include the effects
c...     of the uploaded mutations.
         if(upload_mutations) then
             do i = 1, num_uploaded_mutn
                 if (uploaded_mutn(i) == mutn) then
                    write(*,*)'WARNING: trying to generate a mutation',
     &                        ' with same id as uploaded mutation.   ',
     &                        'Computing new mutation id.'
                    goto 10
                 end if
             end do
         end if

         mutn_indx = (lb - 1)*lb_modulo + mutn

c...     Compute the fitness effect associated with this new mutation.

c...     When parameter fitness_distrib_type is 1, the fitness
c...     effect e is obtained from the mutation index mutn using a
c...     distribution function of the form
c...
c...                   e = exp(-alpha_del*x**gamma) ,
c...
c...     where alpha_del is log(genome_size) and x is a random
c...     number uniformly distributed between zero and one.
c...
c...     When parameter fitness_distrib_type is 0, the fitness
c...     effect is constant and given by the expression
c...
c...                   e = uniform_fitness_effect_del
c...
c...     For favorable mutations, 
c...                   e = uniform_fitness_effect_fav
c...

         if(fitness_distrib_type == 1) then ! Natural mutation distribution
            if(fav) then
               fitness_effect = max_fav_fitness_gain*
     &                          dexp(-alpha_fav*x**gamma_fav)
            else
               y = x/(1. - fraction_neutral)
               if(y < 1.) then
                  fitness_effect = dexp(-alpha_del*y**gamma_del)
               else
                  fitness_effect = 0.
               end if
            end if
         else if (fitness_distrib_type == 2) then ! All mutations neutral
            fitness_effect = 0.
         else ! All mutations have equal effect
            if(fav) then
               fitness_effect = uniform_fitness_effect_fav
            else
               fitness_effect = uniform_fitness_effect_del
            end if
         end if

c...     If neutrals are not being tracked and the fraction of neutrals
c...     is non-zero, assign the appropriate fraction of mutations zero
c...     fitness effect.

         if(.not. track_neutrals .and. fraction_neutral > 0. .and.
     &      .not. fav) then
            if(randomnum(1) < fraction_neutral) fitness_effect = 0.
         end if

c...     Identify the appropriate fraction of new mutations as
c...     recessive.  To distinguish recessive mutations from the
c...     dominant ones, label the recessives by assigning them a
c...     negative mutation index.  Make all neutral mutations 
c...     dominant.

         if(fraction_recessive > 0. .and. fitness_effect > 0.) then
           if(randomnum(1) < fraction_recessive) mutn_indx = -mutn_indx
         end if

c...     Track this mutation if its fitness effect exceeds the value 
c...     of tracking_threshold or if track_neutrals is true. 

         if(fitness_effect>tracking_threshold .or. track_neutrals) then

            if(fav) then

c...           Test to see if the storage limit of array fmutn_offsprng 
c...           has been exceeded.  (Note that we are using the first  
c...           slot to hold the actual mutation count.)

               num_mutn = fmutn_offsprng(1,hap_id) + 1 

               if(num_mutn + 1 > max_fav_mutn_per_indiv/2) then
                  write(6,*) 'Favorable mutation count exceeds limit'
                  write(9,*) 'Favorable mutation count exceeds limit'
                  stop
               end if

               fmutn_offsprng(1,hap_id) = num_mutn

c...           Insert new mutation such that mutations are maintained
c...           in ascending order of their absolute value.

               i = num_mutn

               do while(abs(fmutn_offsprng(i,hap_id)) > abs(mutn_indx)
     &                  .and. i > 1)
                  fmutn_offsprng(i+1,hap_id) = fmutn_offsprng(i,hap_id)
                  i = i - 1
               end do

               fmutn_offsprng(i+1,hap_id) = mutn_indx

            else 

c...           Test to see if the storage limit of array dmutn_offsprng 
c...           has been exceeded.  (Note that we are using the first  
c...           slot to hold the actual mutation count.)

               num_mutn = dmutn_offsprng(1,hap_id) + 1 

               if(num_mutn + 1 > max_del_mutn_per_indiv/2) then
                  write(6,*) 'Deleterious mutation count exceeds limit'
                  write(9,*) 'Deleterious mutation count exceeds limit'
                  stop
               end if

               dmutn_offsprng(1,hap_id) = num_mutn

c...           Insert new mutation such that mutations are maintained
c...           in ascending order of their absolute value.

               i = num_mutn

               do while(abs(dmutn_offsprng(i,hap_id)) > abs(mutn_indx)
     &                  .and. i > 1)
                  dmutn_offsprng(i+1,hap_id) = dmutn_offsprng(i,hap_id)
                  i = i - 1
               end do

               dmutn_offsprng(i+1,hap_id) = mutn_indx

            end if

         end if

c...     Recessive mutations (identified as such with a negative
c...     mutation index) here incur only recessive_hetero_expression
c...     times of their fitness effect, while dominant mutations incur
c...     only dominant_hetero_expression times their fitness effect,
c...     relative to the case of heterozygous expression.  The full 
c...     fitness effect is realized only when a mutation occurs in  
c...     both instances of its linkage block, that is, is homozygous.

         if(mutn_indx < 0) then
            fitness_effect = recessive_hetero_expression*fitness_effect
         else
            fitness_effect =  dominant_hetero_expression*fitness_effect
         end if

c...     Update linkage subunit fitness.

         if(fav) then

            offsprng_lb_fitness(lb,hap_id) = 
     &     (offsprng_lb_fitness(lb,hap_id) + (1. - w)*fitness_effect)
     &                                   * (1.d0 + w *fitness_effect)

c...        Increment the mutation count for the linkage subunit
c...        in which the mutation occurs.

            offsprng_lb_mutn_count(lb,hap_id,2) = 
     &      offsprng_lb_mutn_count(lb,hap_id,2) + 1

         else

            offsprng_lb_fitness(lb,hap_id) = 
     &     (offsprng_lb_fitness(lb,hap_id) - (1. - w)*fitness_effect)
     &                                   * (1.d0 - w *fitness_effect)

c...        Increment the mutation count for the linkage subunit
c...        in which the mutation occurs.

            offsprng_lb_mutn_count(lb,hap_id,1) = 
     &      offsprng_lb_mutn_count(lb,hap_id,1) + 1

         end if

         end if

      end do

      end

      subroutine selection(dmutn, fmutn, lb_mutn_count,
     &                     linkage_block_fitness, fitness,
     &                     pheno_fitness, work_fitness, sorted_score,
     &                     initial_allele_effects, max_size, 
     &                     total_offspring, gen, tsub) 

c...  This routine eliminates the least fit individuals in a new
c...  generation to reduce the population size to a level not to exceed
c...  pop_size.  If the population is recovering from a bottlenecking
c...  event, let half the excess reproduction be used to increase 
c...  population size and the other half be used for selection.

      use random_pkg
      include 'common.h'

      integer dmutn(max_del_mutn_per_indiv/2,2,*), 
     &        fmutn(max_fav_mutn_per_indiv/2,2,*),
     &        lb_mutn_count(num_linkage_subunits,2,2,*)
      integer max_size, total_offspring, gen, remaining
      integer i, j, k, lb, mutn, m, n, zygous(num_linkage_subunits)
      real  initial_allele_effects(num_linkage_subunits)
      real*8 linkage_block_fitness(num_linkage_subunits,2,*)
      real*8 fitness(*), fitness_norm, homozygous_fitness_loss, noise
      real*8 pheno_fitness(*), homozygous_fitness_gain, fitness_loss
      real*8 work_fitness(*), sorted_score(max_size), covariance
      real*8 max_work_fitness, min_work_fitness, score_cutoff
      real*8 geno_fitness_variance, pheno_fitness_variance
      real*8 mean_pheno_fitness, se_linked, se_nonlinked, x, e, sumesq
      real w, p, count, tsub, effect, factor
      call second(tin)

      w = multiplicative_weighting

c...  If the population is recovering from a bottlenecking event,
c...  compute the new population size that accounts for selection
c...  as well as population growth.  As a place holder here, let
c...  half the excess reproduction be used to increase population 
c...  size and the other half be used for selection.

      if(bottleneck_yes) then
         if(gen > bottleneck_generation + num_bottleneck_generations 
     &      .and. current_pop_size < pop_size) current_pop_size = 
     &      min(pop_size, int(1. + current_pop_size*(1. + 0.5*
     &      (reproductive_rate*(1. - fraction_random_death) - 1.0))))
      end if

c...  Compute the fitness of each member of the new generation.

      fitness(1:total_offspring) = 1.d0

      if(fitness_distrib_type == 0) then ! All mutations have equal effect
         homozygous_fitness_loss = uniform_fitness_effect_del
         homozygous_fitness_gain = uniform_fitness_effect_fav
      else if (fitness_distrib_type == 2) then ! All mutations neutral
         homozygous_fitness_loss = 0
         homozygous_fitness_gain = 0
      end if

      do i=1,total_offspring

         do lb=1,num_linkage_subunits
            fitness(i) = (fitness(i) - (1. - w)*(2.d0
     &                     - linkage_block_fitness(lb,1,i)
     &                     - linkage_block_fitness(lb,2,i)))
     &      *(1.d0 - (1.d0 - linkage_block_fitness(lb,1,i))*w)
     &      *(1.d0 - (1.d0 - linkage_block_fitness(lb,2,i))*w)
         end do

c...     Apply the appropriate fitness degradation adjustment for
c...     homozygous deleterious mutations.  Skip this step for the
c...     cases of clonal reproduction and co-dominance. 

         if(.not.clonal_reproduction .and. 
     &      dominant_hetero_expression /= 0.5) then

         j = 2 
         do k=2,dmutn(1,1,i)+1

            do while(abs(dmutn(k,1,i)) >  abs(dmutn(j,2,i)) .and.
     &                                   j <= dmutn(1,2,i))
               j = j + 1
            end do

            if(dmutn(k,1,i) == dmutn(j,2,i)) then

               if(dmutn(k,1,i) == num_linkage_subunits*lb_modulo + 1)
     &            write(6,*) 'ERROR: dmutn range invalid'

               mutn = mod(abs(dmutn(k,1,i)), lb_modulo)
               if(fitness_distrib_type == 1) then ! Natural mutation dist
                  x = real(mutn)*del_scale
                  homozygous_fitness_loss =
     &                           dexp(-alpha_del*x**gamma_del)
                  if(x >= 1.d0) homozygous_fitness_loss = 0.d0
               end if

c...           Apply the proper fitness decrease associated with a
c...           homozygous mutation, giving it 100% of the nominal 
c...           mutation effect.

               fitness(i) = (fitness(i) 
     &                    - (1. - w)*homozygous_fitness_loss)
     &                    *(1.d0 - w*homozygous_fitness_loss)
               if(dmutn(k,1,i) < 0)  homozygous_fitness_loss =
     &                               recessive_hetero_expression
     &                              *homozygous_fitness_loss
               if(dmutn(k,1,i) > 0)  homozygous_fitness_loss =
     &                               dominant_hetero_expression
     &                              *homozygous_fitness_loss
c...           Remove the fitness decreases that were applied elsewhere 
c...           when it was assumed the mutation was heterozygous.  
c...           Remove the heterozygous effect by adding it back twice.
c...           since it was carried out on both haplotypes.
               fitness(i) = fitness(i) / 
     &                      (1.d0 - w*homozygous_fitness_loss)**2
     &                    + (1. - w) *homozygous_fitness_loss*2.
            end if
         end do

c...     Apply the appropriate fitness enhancement adjustment for
c...     homozygous favorable mutations. 

         j = 2 
         do k=2,fmutn(1,1,i)+1

            do while(abs(fmutn(k,1,i)) >  abs(fmutn(j,2,i)) .and.
     &                                   j <= fmutn(1,2,i))
               j = j + 1
            end do

            if(fmutn(k,1,i) == fmutn(j,2,i)) then

               if(fmutn(k,1,i) == num_linkage_subunits*lb_modulo + 1)
     &            write(6,*) 'ERROR: fmutn range invalid'

               mutn = mod(abs(fmutn(k,1,i)), lb_modulo)
               if(fitness_distrib_type == 1) ! Natural mutation dist
     &            homozygous_fitness_gain = max_fav_fitness_gain
     &              *dexp(-alpha_fav*(real(mutn)*fav_scale)**gamma_fav)
               fitness(i) = (fitness(i) 
     &                    + (1. - w)*homozygous_fitness_gain)
     &                    *(1.d0 + w*homozygous_fitness_gain)
               if(fmutn(k,1,i) < 0) homozygous_fitness_gain =
     &                              recessive_hetero_expression
     &                             *homozygous_fitness_gain
               if(fmutn(k,1,i) > 0) homozygous_fitness_gain =
     &                               dominant_hetero_expression
     &                             *homozygous_fitness_gain
               fitness(i) = (fitness(i) 
     &                    - (1. - w) *homozygous_fitness_gain*2.)
     &                    / (1.d0 + w*homozygous_fitness_gain)**2
            end if
         end do

         end if

      end do

      if(synergistic_epistasis .and. .not.clonal_reproduction) then

c...     In our synergistic epistasis (SE) treatment, we break its
c...     effect into two parts, one involving interactions between
c...     mutations occurring on the same linkage block (linked
c...     interactions) and the other part involving interactions of
c...     mutations on different linkage blocks (nonlinked interactions).
c...     SE effects from linked interactions are inherited perfectly,
c...     while those from nonlinked interactions are progressively
c...     scrambled by recombination generation to generation.
c...
c...     Let us first consider the linked interactions. We apply the
c...     following considerations.  First, we require amplitude of
c...     the SE effect to be _proportional_ to the non-epistatic fitness
c...     effects of each of the two interacting mutations. This means
c...     that if a mutation's effect on the non-mutant genome is small,
c...     then the SE contributions from its interactions with other
c...     mutations is assumed likewise to be small. If we use f to
c...     denote linkage block fitness, then (1 - f) represents the sum
c...     of the non-epistatic fitness effects of all the mutations on
c...     the linkage block.  The sum of the products of the fitness
c...     effects of all the mutations is then given by 0.5*(1-f)**2,
c...     corrected for the self-interaction contributions.
c...     We assume co-dominance, however, that is, we assume that only
c...     50% of each mutations base value is used in computing the SE
c...     contribution. Further, we allow the user to scale the SE
c...     contribution through the parameter se_linked_scaling. These
c...     considerations then imply that the SE effect from linked
c...     mutations on a given linkage block is given by
c...
c...       0.125*se_linked_scaling*((1-f)**2 - self_int_contribution)
c...
c...     Lets now consider the nonlinked SE interactions.  If M is the
c...     total number of mutations in the genome and n is the number of
c...     linkage blocks, then the total number of pairwise interactions
c...     between mutations is M(M-1)/2, the mean number of mutations
c...     per linkage block is M/n, and the approximate number of linked
c...     interactions is n(M/n)[(M/n)-1]/2.  Since SE contributions
c...     become significant only when M becomes moderately large, we
c...     approximate M-1 by M and (M/n)-1 by M/n.  With these
c...     approximations, the number of linked interactions becomes
c...     M**2/(2n) and the number of nonlinked interactions becomes
c...     (1 - 1/n)*M**2/2.
c...
c...     Let F denote the overall genotypic fitness.  The total
c...     nonlinked SE fitness contribution is then proportional to the
c...     sum of the non-epistatic fitness effects of all the individual
c...     mutations, (1-F), but scaled to account for the portion of the
c...     mutations which are linked with the factor (1 - 1/n), times
c...     the mean non-epistatic fitness effect of these mutations,
c...     (1-F)/M, times the number of unique pair-wise interactions,
c...     (1 - 1/n)M/2, that each non-linked mutation has with the
c...     others.  We assume co-dominance, which implies each haploid
c...     occurrence of a mutation gives 50% expression of the mutations
c...     non-epistatic value which reduces the overall contribution by
c...     a factor of 0.25.  We also subtract the self-interaction
c...     contribution implicit in the 0.5*(1-F)**2 formula.
c...
c...     We scale this non-linked SE contribution by the user-specified
c...     input parameter se_nonlinked_scaling.  In general one expects
c...     that interaction between mutations within the same linkage
c...     block will on average have much greater SE effects than
c...     mutations which are more distant to one another within the
c...     genome.  Hence, a value for this parameter much less than (say,
c...     by a factor of 0.001 times) the parameter se_linked_scaling
c...     used for the linked mutations is usually appropriate.  The
c...     resulting expression for the non-linked SE contribution to
c...     individual fitness, to be subtracted from F, is
c...
c...                      0.125*se_nonlinked_scaling
c...                *((1-F)**2 - self_int_term)*(1 - 1/n)**2.

         do i=1,total_offspring

c...        Compute self-interaction term, neglecting the non-tracked
c...        mutations because of their small values.  Assume
c...        co-dominance.

            sumesq = 0.d0
            do k=1,2
               do j=2,dmutn(1,k,i)+1
                  x = mod(abs(dmutn(j,k,i)),lb_modulo)*del_scale
                  x = min(x, 1.d0)
                  e = 0.5*dexp(-alpha_del*x**gamma_del)
                  sumesq = sumesq + e**2
               end do
            end do
         
c...        Sum the linked SE contributions from each of the linkage
c...        blocks.

            se_linked = 0.
            if(clonal_reproduction) then
               do lb=1,num_linkage_subunits
                  se_linked = se_linked
     &                      + (2.d0 - linkage_block_fitness(lb,1,i)
     &                              - linkage_block_fitness(lb,2,i))**2
               end do
            else
               do lb=1,num_linkage_subunits
                  se_linked = se_linked
     &                      + (1.d0 - linkage_block_fitness(lb,1,i))**2
     &                      + (1.d0 - linkage_block_fitness(lb,2,i))**2
               end do
            end if

c...        Subtract the self-interaction sum from the se_linked sum
c...        and scale the remainder appropriately.

            se_linked = 0.125*se_linked_scaling
     &                * max(0., se_linked - sumesq)

c...        Compute the non-linked SE contribution, subtract the
c...        self-interaction sum, and scale.

            se_nonlinked = 0.125*se_nonlinked_scaling
     &                   * max(0., ((1.d0 - fitness(i))**2 - sumesq))

c...        If linked SE is being included, add the appropriate factor
c...        to account for the number of linked interactions.  Note that
c...        for diploid organisms the total number of linkage blocks is
c...        2*num_linkage_subunits.

            if(se_linked_scaling > 0.) then
               se_nonlinked = se_nonlinked
     &                        *(1. - 0.5/num_linkage_subunits)**2
            end if
            if(clonal_reproduction) se_nonlinked = 0.

            fitness(i) = fitness(i) - se_linked - se_nonlinked

         end do

      end if

c...  Account for possible homozygosity in initial contrasting alleles.

      if(num_contrasting_alleles > 0) then

         do i=1,total_offspring

            zygous = 0

            do m=2,dmutn(1,1,i)+1
               if(mod(dmutn(m,1,i), lb_modulo) == lb_modulo-1) then 
                  lb = dmutn(m,1,i)/lb_modulo + 1
                  zygous(lb) = zygous(lb) + 1
               end if
            end do

            do m=2,dmutn(1,2,i)+1
               if(mod(dmutn(m,2,i), lb_modulo) == lb_modulo-1) then 
                  lb = dmutn(m,2,i)/lb_modulo + 1
                  zygous(lb) = zygous(lb) + 1
               end if
            end do

            do lb=1,num_linkage_subunits
               if(zygous(lb) == 2) then
                  effect = initial_allele_effects(lb)
                  fitness(i) = (fitness(i) - (1. - w)*effect)
     &                                     *(1.d0 - w*effect)
                  effect = recessive_hetero_expression*effect
                  fitness(i) = fitness(i) / (1.d0 - w*effect)**2
     &                                    + (1. - w) *effect*2.
               end if
            end do

            zygous = 0

            do m=2,fmutn(1,1,i)+1
               if(mod(fmutn(m,1,i), lb_modulo) == lb_modulo-1) then 
                  lb = fmutn(m,1,i)/lb_modulo + 1
                  zygous(lb) = zygous(lb) + 1
               end if
            end do

            do m=2,fmutn(1,2,i)+1
               if(mod(fmutn(m,2,i), lb_modulo) == lb_modulo-1) then 
                  lb = fmutn(m,2,i)/lb_modulo + 1
                  zygous(lb) = zygous(lb) + 1
               end if
            end do

            do lb=1,num_linkage_subunits
               if(zygous(lb) == 2) then
                  effect = initial_allele_effects(lb)
                  fitness(i) = (fitness(i) + (1. - w)*effect)
     &                                     *(1.d0 + w*effect)
                  effect =  dominant_hetero_expression*effect
                  fitness(i) = (fitness(i) - (1. - w) *effect*2.)
     &                                     / (1.d0 + w*effect)**2
               end if
            end do

         end do

      end if

c...  Compute the mean genotypic fitness of the new generation.

      pre_sel_fitness = 0.d0

      do i=1,total_offspring
         pre_sel_fitness = pre_sel_fitness + fitness(i)
      end do

      pre_sel_fitness = pre_sel_fitness/total_offspring
      
c...  Compute the genotypic fitness variance of the new generation.

      geno_fitness_variance = 0.d0

      do i=1,total_offspring
         geno_fitness_variance = geno_fitness_variance
     &                    + (fitness(i) - pre_sel_fitness)**2
      end do

      geno_fitness_variance = geno_fitness_variance/total_offspring

      pre_sel_geno_sd = sqrt(geno_fitness_variance)

c...  If population has collapsed to a single individual, skip the
c...  selection process and return.

      if(total_offspring == 1) then
         current_pop_size = 1
         return
      end if

c...  Compute the noise variance required to yield the specified
c...  heritability.  Add to this fitness-dependent noise a noise 
c...  component that is fitness independent. Take the square root
c...  to obtain the standard deviation. 

      noise = sqrt(geno_fitness_variance*(1. - heritability)
     &             /heritability + non_scaling_noise**2) 

c...  Add noise to the fitness to create a phenotypic fitness score.
c...  Add a tiny variable positive increment to eliminate identical 
c...  fitness values when the noise is zero.

      do i=1,total_offspring
         pheno_fitness(i) = fitness(i) + random_normal()*noise 
     &                    + 1.d-15*i
      end do

c...  Compute the mean phenotypic fitness of offspring.

      mean_pheno_fitness = 0.d0

      do i=1,total_offspring
         mean_pheno_fitness = mean_pheno_fitness + pheno_fitness(i)
      end do

      mean_pheno_fitness = mean_pheno_fitness/total_offspring
      
c...  Compute the phenotypic fitness variance, the covariance of
c...  genotypic and phenotypic fitness, and the genotype-phenotype
c...  correlation.

      pheno_fitness_variance = 0.d0
      covariance = 0.d0

      do i=1,total_offspring
         pheno_fitness_variance = pheno_fitness_variance
     &        + (pheno_fitness(i) - mean_pheno_fitness)**2
         covariance = covariance + fitness(i)*pheno_fitness(i)
      end do

      pheno_fitness_variance = pheno_fitness_variance/total_offspring

      pre_sel_pheno_sd = sqrt(pheno_fitness_variance)

      covariance = covariance/total_offspring 
     &           - pre_sel_fitness*mean_pheno_fitness

      pre_sel_corr = 0.
      effect = sqrt(geno_fitness_variance*pheno_fitness_variance)
      if(effect > 0.) pre_sel_corr = covariance/effect

c...  Move, in effect, those offspring whose phenotypic fitness is 
c...  negative to the end of the list of offspring, and then, in effect,
c...  truncate the list so that these individuals cannot reproduce and
c...  do not even participate in the subsequent selection process.

      remaining = total_offspring
      do i=1,total_offspring
         if(pheno_fitness(i) < 0.d0) then
            do while(pheno_fitness(remaining) < 0.d0
     &               .and. remaining > 1)
               remaining = remaining - 1
            end do
            k = dmutn(1,1,remaining) + 1
            dmutn(1:k,1,i) = dmutn(1:k,1,remaining)
            k = dmutn(1,2,remaining) + 1
            dmutn(1:k,2,i) = dmutn(1:k,2,remaining)
            k = fmutn(1,1,remaining) + 1
            fmutn(1:k,1,i) = fmutn(1:k,1,remaining)
            k = fmutn(1,2,remaining) + 1
            fmutn(1:k,2,i) = fmutn(1:k,2,remaining)
            lb_mutn_count(:,:,:,i) = 
     &      lb_mutn_count(:,:,:,remaining)
            linkage_block_fitness(:,:,i) =
     &      linkage_block_fitness(:,:,remaining)
            fitness(i) = fitness(remaining)
            pheno_fitness(i) = pheno_fitness(remaining)
            if(remaining > 1) remaining = remaining - 1
         end if
      end do

      total_offspring = remaining

c...  Adjust the population size for the next generation such that it
c...  does not exceed the number of offspring after removal of those
c...  with negative phenotypic fitness.

      current_pop_size = min(current_pop_size, remaining)

c...  Allow the population size for the next generation potentially 
c...  to rebound from an earlier reduction in previous generations 
c...  because of individuals with negative phenotypic fitness.

      if(.not.tribal_competition .and. .not.bottleneck_yes .and.
     &   remaining > current_pop_size)
     &   current_pop_size = min(remaining, pop_size)

c...  Copy the phenotypic fitnesses into array work_fitness.

      work_fitness(1:total_offspring) = pheno_fitness(1:total_offspring)

      if (selection_scheme == 2) then

c...     For unrestricted probability selection, divide the phenotypic  
c...     fitness by a uniformly distributed random number prior to 
c...     ranking and truncation.  This procedure allows the probability 
c...     of surviving and reproducing in the next generation to be
c...     directly related to phenotypic fitness and also for the correct
c...     number of individuals to be eliminated to maintain a constant
c...     population size.

         do i=1,total_offspring
            work_fitness(i) = work_fitness(i)/(randomnum(1) + 1.d-15)
         end do
   
      end if

      if (selection_scheme == 3) then

c...     For strict proportionality probability selection, rescale the
c...     phenotypic fitness values such that the maximum value is one.
c...     Then divide the scaled phenotypic fitness by a uniformly
c...     distributed random number prior to ranking and truncation.  
c...     Allow only those individuals to reproduce whose resulting 
c...     ratio of scaled phenotypic fitness to the random number value
c...     exceeds one.  This approach ensures that no individual 
c...     automatically survives to reproduce regardless of the value
c...     of the random number.  But it restricts the fraction of the 
c...     offspring that can survive.  Therefore, when the reproduction
c...     rate is low, the number of surviving offspring may not be
c...     large enough to sustain a constant population size.

         max_work_fitness = 0.d0
         do i=1,total_offspring
            max_work_fitness = max(max_work_fitness, work_fitness(i))
         end do
  
         do i=1,total_offspring
            work_fitness(i) = work_fitness(i)/(max_work_fitness
     &                                           + 1.d-15)
            work_fitness(i) = work_fitness(i)/(randomnum(1) + 1.d-15)
         end do
   
      end if

      if (selection_scheme == 4) then

c...     For partial truncation selection, divide the phenotypic  
c...     fitness by the sum of theta and (1. - theta) times a random 
c...     number distributed uniformly between 0.0 and 1.0 prior to 
c...     ranking and truncation, where theta is the parameter 
c...     partial_truncation_value.  This selection scheme is 
c...     intermediate between truncation selection and unrestricted 
c...     probability selection.  The procedure allows for the correct 
c...     number of individuals to be eliminated to maintain a constant 
c...     population size.

         do i=1,total_offspring
            work_fitness(i) = work_fitness(i)/(partial_truncation_value 
     &                                 + (1. - partial_truncation_value)
     &                                   *randomnum(1))
         end do
   
      end if

c...  Sort the resulting work fitnesses in ascending order.

      sorted_score(1:total_offspring) = work_fitness(1:total_offspring)

      if (total_offspring > 1)
     &    call heapsort(sorted_score, total_offspring)

      if (selection_scheme <= 4) then

c...     Apply truncation selection to reduce the population size to
c...     current_pop_size.

c...     Compute the score cutoff value.

         if(total_offspring > current_pop_size) then
            score_cutoff = sorted_score(total_offspring
     &                                - current_pop_size)
         else
            score_cutoff = -1000.d0
         end if

         if(selection_scheme == 3)
     &      score_cutoff = max(1.d0, score_cutoff)

c...     Copy pheno_fitness into array sorted_score for diagnostics
c...     purposes.

         sorted_score(1:total_offspring) = 
     &                              pheno_fitness(1:total_offspring)

c...     Remove those individuals whose score lies below the cutoff
c...     value to reduce the population size to its appropriate value.

         current_pop_size = min(current_pop_size, total_offspring)
         remaining = total_offspring

         do i=1,current_pop_size

c...        If the work fitness if individual i is below the cutoff 
c...        value, find another individual in the pool of excess 
c...        offspring whose work fitness is equal to or above the
c...        cutoff value and replace the first individual with the 
c...        second in the list of reproducing individuals for that
c...        generation.

            if(work_fitness(i) < score_cutoff .and. i < remaining) then
               do while(work_fitness(remaining) < score_cutoff .and. 
     &                  remaining > 1)
                  remaining = remaining - 1
               end do
               if(i < remaining) then
                  k = dmutn(1,1,remaining) + 1
                  dmutn(1:k,1,i) = dmutn(1:k,1,remaining)
                  k = dmutn(1,2,remaining) + 1
                  dmutn(1:k,2,i) = dmutn(1:k,2,remaining)
                  k = fmutn(1,1,remaining) + 1
                  fmutn(1:k,1,i) = fmutn(1:k,1,remaining)
                  k = fmutn(1,2,remaining) + 1
                  fmutn(1:k,2,i) = fmutn(1:k,2,remaining)
                  lb_mutn_count(:,:,:,i) = 
     &            lb_mutn_count(:,:,:,remaining)
                  linkage_block_fitness(:,:,i) =
     &            linkage_block_fitness(:,:,remaining)
                  fitness(i) = fitness(remaining)
                  pheno_fitness(i) = pheno_fitness(remaining)
                  if(remaining > 1) remaining = remaining - 1
               end if
            end if
         end do

         current_pop_size = min(current_pop_size, remaining)

      else

         write(6,*) 'ERROR: invalid selection scheme', selection_scheme
         write(9,*) 'ERROR: invalid selection scheme', selection_scheme
         stop

      end if

c...  Compute the mean genotypic and phenotypic fitnesses of the new
c...  generation after selection.

      post_sel_fitness   = 0.d0
      mean_pheno_fitness = 0.d0

      do i=1,current_pop_size
         post_sel_fitness   = post_sel_fitness   + fitness(i)
         mean_pheno_fitness = mean_pheno_fitness + pheno_fitness(i)
      end do

      post_sel_fitness   = post_sel_fitness/current_pop_size
      mean_pheno_fitness = mean_pheno_fitness/current_pop_size
      
c...  Compute the genotypic and phenotypic fitness variances, the 
c...  covariance of genotypic and phenotypic fitness, and the 
c...  genotype-phenotype correlation of the new generation.

      geno_fitness_variance  = 0.d0
      pheno_fitness_variance = 0.d0
      covariance = 0.d0

      do i=1,current_pop_size
         geno_fitness_variance  = geno_fitness_variance
     &                    + (fitness(i) - post_sel_fitness)**2
         pheno_fitness_variance = pheno_fitness_variance
     &        + (pheno_fitness(i) - mean_pheno_fitness)**2
         covariance = covariance + fitness(i)*pheno_fitness(i)
      end do

      geno_fitness_variance  = geno_fitness_variance/current_pop_size
      pheno_fitness_variance = pheno_fitness_variance/current_pop_size

      post_sel_geno_sd  = sqrt(geno_fitness_variance)
      post_sel_pheno_sd = sqrt(pheno_fitness_variance)

      covariance = covariance/current_pop_size 
     &           - post_sel_fitness*mean_pheno_fitness

      post_sel_corr = 0.
      effect = sqrt(geno_fitness_variance*pheno_fitness_variance)
      if(effect > 0.) post_sel_corr = covariance/effect

      post_sel_fitness = max(0., post_sel_fitness)

      fitness(current_pop_size+1:max_size) = 0.d0

      call second(tout)
      tsub = tout - tin
      sec(6) = sec(6) + tsub
      end

      subroutine poisson(poisson_mean, deviate)

c...  This routine returns an integer, deviate, that is a random deviate
c...  drawn from a Poisson distribution of mean poisson_mean, using the
c...  function randomnum as a source of uniform random deviates.
c...  Taken from Press, et al., Numerical Recipes, 1986, pp. 207-208.

      use random_pkg
      implicit none
      real poisson_mean, old_mean, pi, em, t, g, sq, lg, y, gammln
      common /pssn/ old_mean, sq, lg, g
      integer deviate
      parameter (pi = 3.14159265)
      data old_mean /-1./             ! Flag for whether poisson_mean
                                      ! has changed since last call.
      if(poisson_mean < 12.) then     ! Use direct method.

         if(poisson_mean /= old_mean) then
            old_mean = poisson_mean
            g = exp(-poisson_mean)    ! If mean is new, compute g.
         end if

         em = -1.
         t  =  1.

         do while(t > g)
            em = em + 1.
            t  = t*randomnum(1)
         end do

      else                            ! Use rejection method.

         if(poisson_mean /= old_mean) then
            old_mean = poisson_mean
            sq = sqrt(2.*poisson_mean)
            lg = log(poisson_mean)
            g  = poisson_mean*lg - gammln(poisson_mean + 1.)
         end if

 1       continue 

         y  = tan(pi*randomnum(1))
         em = sq*y + poisson_mean
         if(em < 0.) go to 1

         em = int(em)
         t  = 0.9*(1. + y**2)*exp(em*lg - gammln(em + 1.) - g)
         if(randomnum(1) > t) go to 1

      end if

      deviate = em

      end

      function gammln(arg)

c...  This function returns the value of log(gamma(arg)) for arg > 0., 
c...  where gamma is the gamma function.  Full accuracy is obtained
c...  for arg > 1.
c...  Taken from Press, et al., Numerical Recipes, 1986, p. 157.

      implicit none
      real gammln, arg
      real*8 cof, stp, x, tmp, ser
      integer j
      common /gmln/ cof(6), stp

      data cof, stp /76.18009173d0, -86.50532033d0, 24.01409822d0,
     &              -1.231739516d0, 0.120858003d-2,  -0.536382d-5,
     &             2.50662827465d0/

      x   = arg - 1.d0
      tmp =  x + 5.5d0
      tmp = (x + 0.5d0)*log(tmp) - tmp
      ser = 1.d0

      do j=1,6
         x   = x   + 1.d0
         ser = ser + cof(j)/x
      end do

      gammln = tmp + log(stp*ser)

      end

      subroutine heapsort(a,n)

c...  This routine applies the heapsort algorithm to sort array a of
c...  length n into ascending numerical order. Array a is replaced on
c...  output by its sorted rearrangement.
c...  Taken from Press, et al., Numerical Recipes, 1986, p. 231.

      implicit none
      real*8 a(*), ra
      integer i, ir, j, l, n

      l  = n/2 + 1
      ir = n

c...  The index l will be decremented from its initial value down to 1
c...  during the hiring (heap creation) phase.  Once it reaches 1, the 
c...  index ir will be decremented from its initial value down to 1
c...  during the retirement-and-promotion (heap selection) phase.

 10   continue

      if(l > 1) then         ! Still in hiring phase.
         l  = l - 1
         ra = a(l)
      else                   ! In retirement-and-promotion phase.
         ra = a(ir)          ! Clear a space at the end of the array.
         a(ir) = a(1)        ! Retire the top of the heap into it.
         ir = ir - 1         ! Decrease the size of the corporation.
         if(ir == 1) then    ! Completed the last promotion.
            a(1) = ra        ! Identify the least competent worker.
            return
         end if
      end if

      i = l                  ! Set up to sift element ra to its proper
      j = l + l              ! level.

      do while(j <= ir)

         if(j < ir) then
            if(a(j) < a(j+1)) j = j + 1  ! Compare to better underling.
         end if

         if(ra < a(j)) then  ! Demote ra.
            a(i) = a(j)
            i = j
            j = j + j
         else                ! This is ra's level. Set j to terminate
            j = ir + 1       ! sift-down.
         end if

      end do
   
      a(i) = ra              ! Put ra into its slot.

      go to 10

      end

      subroutine read_restart_dump(dmutn,fmutn,lb_mutn_count,
     &                             linkage_block_fitness,
     &                             initial_allele_effects,
     &                             generation_number,max_size,myid_str) 

c...  This routine reads a dump file containing the mutation arrays
c...  dmutn and fmutn and the linkage block mutation count array
c...  lb_mutn_count and the linkage block fitness array 
c...  linkage_block_fitness for purposes of restart.  The argument
c...  generation_number is the generation number of the dump file 
c...  being read.

      include 'common.h'
      integer generation_number, max_size, i, lb, n1, n2, npath, nm
      integer dmutn(max_del_mutn_per_indiv/2,2,max_size)
      integer fmutn(max_fav_mutn_per_indiv/2,2,max_size)
      integer lb_mutn_count(num_linkage_subunits,2,2,max_size)
      real*8 linkage_block_fitness(num_linkage_subunits,2,max_size)
      real  initial_allele_effects(num_linkage_subunits)
      real f1
      logical l1
      character char1*1, char12*12, char20*20, char32*32, path*80
      character myid_str*3
      call second(tin)

      npath = index(data_file_path,' ') - 1
      char1 = char(48 + restart_dump_number)

      open (10, file=data_file_path(1:npath)//case_id//
     &      '.'//myid_str//'.dmp.'//char1,status='unknown')

      read(10,'(a20,i12)') char32, generation_number

      dmutn = num_linkage_subunits*lb_modulo + 1
      fmutn = num_linkage_subunits*lb_modulo + 1

      do i=1,pop_size
            read(10,'(12i6)') lb_mutn_count(:,:,:,i) 
            read(10,'(6f12.8)') linkage_block_fitness(:,:,i) 
            read(10,'( i12)') dmutn(1,1,i)
            nm = min(max_del_mutn_per_indiv/2, dmutn(1,1,i)+1)
            read(10,'(6i12)') dmutn(2:nm,1,i)
            read(10,'( i12)') dmutn(1,2,i)
            nm = min(max_del_mutn_per_indiv/2, dmutn(1,2,i)+1)
            read(10,'(6i12)') dmutn(2:nm,2,i)
            read(10,'( i12)') fmutn(1,1,i)
            nm = min(max_fav_mutn_per_indiv/2, fmutn(1,1,i)+1)
            read(10,'(6i12)') fmutn(2:nm,1,i)
            read(10,'( i12)') fmutn(1,2,i)
            nm = min(max_fav_mutn_per_indiv/2, fmutn(1,2,i)+1)
            read(10,'(6i12)') fmutn(2:nm,2,i)
      end do

      if(num_contrasting_alleles > 0) then
         read(10,'(6f12.9)') initial_allele_effects
         if(.not. is_parallel) 
     &   write(6, '("Restart run will use the previous value for"/
     &              "parameter num_contrasting_alleles =", i10)')
     &                         num_contrasting_alleles
         write(9, '("Restart run will use the previous value for"/
     &              "parameter num_contrasting_alleles =", i10)')
     &                         num_contrasting_alleles
      end if

      close (10)

      call second(tout)
      sec(9) = sec(9) + tout - tin
      end

      subroutine back_mutn(dmutn,fmutn,lb_fitness,lb_mutn_count)

      use random_pkg
      include 'common.h'
      integer dmutn(max_del_mutn_per_indiv/2,2)
      integer fmutn(max_fav_mutn_per_indiv/2,2)
      integer lb_mutn_count(num_linkage_subunits,2,2)
      integer lb, hap_id, mutn, i, j, tries, idorf, random_index
      integer num_fmutns, num_dmutns, decode_lb
      real*8  lb_fitness(num_linkage_subunits,2)
      real*8  fitness, decode_fitness_del, decode_fitness_fav
      real    w
      logical fav
      call second(tin)

      tries = 0
 10   continue
      tries = tries + 1
      if(tries > 10) return

c...  Determine whether back mutation is deleterious or favorable.

      if(randomnum(1) < frac_fav_mutn) then
         fav = .true.
      else
         fav = .false.       
      end if

c...  Select either 1 or 2 for haplotype.      

      hap_id = min(2, 1 + int(2.*randomnum(1)))

      if(fav) then
         num_fmutns = fmutn(1,hap_id)
         if(num_fmutns == 0) goto 10
c...     Choose a random mutation from the individual
         random_index = min(num_fmutns,
     &                  int(num_fmutns*randomnum(1))+1)
         mutn = fmutn(1+random_index,hap_id)
         idorf = 2
      else
         num_dmutns = dmutn(1,hap_id)
         if(num_dmutns == 0) goto 10
         random_index = min(num_dmutns,
     &                  int(num_dmutns*randomnum(1))+1)
         mutn = dmutn(1+random_index,hap_id)
         idorf = 1
      endif
         
c...  Compute the linkage block of the mutation

      lb = decode_lb(mutn)

c...  Decrement the linkage block mutation counter

      lb_mutn_count(lb,hap_id,idorf) = lb_mutn_count(lb,hap_id,idorf)-1

      w = multiplicative_weighting

c...  Rebuild the mutation list excluding the random_index, compute the
c...  fitness associated with this mutation, and decrement the total
c...  number of mutations.

      if(fav) then
         do i=1+random_index,num_fmutns
            fmutn(i,hap_id) = fmutn(i+1,hap_id)
         end do
         fmutn(num_fmutns+1,hap_id) = num_linkage_subunits*lb_modulo + 1
         fitness = decode_fitness_fav(mutn)
         fmutn(1,hap_id) = fmutn(1,hap_id) - 1
      else
         do i=1+random_index,num_dmutns
            dmutn(i,hap_id) = dmutn(i+1,hap_id)
         end do
         dmutn(num_dmutns+1,hap_id) = num_linkage_subunits*lb_modulo + 1
         fitness = decode_fitness_del(mutn)
         dmutn(1,hap_id) = dmutn(1,hap_id) - 1
      end if

c...  Make appropriate adjustments to linkage block fitness.

      lb_fitness(lb,hap_id) = (lb_fitness(lb,hap_id) - (1. - w)*fitness)
     &                       *(1.d0 - w*fitness)

      call second(tout)
      sec(14) = sec(14) + tout - tin
      end

      subroutine read_mutn_file(dmutn,fmutn,lb_mutn_count,
     &                          linkage_block_fitness,max_size)
c...  This routine reads the file caseid_mutn.in only when upload_mutations
c...  flag is set to 1.

      include 'common.h'
      integer id, lb, hap_id, mutn, dominance
      real    fitness, w
      integer i, npath, max_size, findex, dindex
      integer nimpi(pop_size), encode_mutn
      integer dmutn(max_del_mutn_per_indiv/2,2,max_size)
      integer fmutn(max_fav_mutn_per_indiv/2,2,max_size)
      integer lb_mutn_count(num_linkage_subunits,2,2,max_size)
      real*8 linkage_block_fitness(num_linkage_subunits,2,max_size)
      call second(tin)

      npath = index(data_file_path,' ') - 1

      open (10, file=data_file_path(1:npath)//case_id//
     &      '_mutn.in',status='unknown')

      read(10,*) num_uploaded_mutn
      write(*,*) 'Reading mutation file with ', num_uploaded_mutn, 
     &           'mutations'
      read(10,*) ! header

      dindex = 2
      findex = 2
      w = multiplicative_weighting

      do i=1,num_uploaded_mutn

         read(10,*) id,lb,hap_id,fitness,dominance
         write(*,*) id,lb,hap_id,fitness,dominance
         mutn = encode_mutn(fitness,lb,dominance)
         uploaded_mutn(i) = mutn

         if(fitness > 0.) then
            fmutn(1,hap_id,id) = fmutn(1,hap_id,id) + 1
            fmutn(fmutn(1,hap_id,id)+1,hap_id,id) = mutn
            lb_mutn_count(lb,hap_id,2,id) = 
     &         lb_mutn_count(lb,hap_id,2,id) + 1
         else
            dmutn(1,hap_id,id) = dmutn(1,hap_id,id) + 1
            dmutn(dmutn(1,hap_id,id)+1,hap_id,id) = mutn
            lb_mutn_count(lb,hap_id,1,id) = 
     &         lb_mutn_count(lb,hap_id,1,id) + 1
         end if

         linkage_block_fitness(lb,hap_id,id) = 
     &      (linkage_block_fitness(lb,hap_id,id) 
     &       + (1. - w)*fitness) * (1.d0 + w *fitness)
  
      end do
   
      close (10)

      call second(tout)
      sec(15) = sec(15) + tout - tin
      end
     
      integer function encode_mutn(fitness,lb,dominance)
      include 'common.h'
      real fitness
      integer lb, dominance 
      encode_mutn = dominance*((lb-1)*lb_modulo+lb_modulo*fitness)
      return
      end

      subroutine decode_mutn_del(mutn,lb,dominance,fitness)
      include 'common.h'
      real*8 fitness, x
      integer mutn, lb, dominance 
      dominance = sign(1,mutn)
      lb  = abs(mutn)/lb_modulo + 1
      x   = mod(abs(mutn), lb_modulo)*del_scale
      fitness = -dexp(-alpha_del*x**gamma_del)
      if(x >= 1.d0) fitness = 0.d0
      return
      end
 
      integer function decode_lb(mutn)
      include 'common.h'
      integer mutn
      decode_lb = abs(mutn)/lb_modulo + 1
      return
      end

      real*8 function decode_fitness_fav(mutn)
      include 'common.h'
      integer mutn, mtn
      mtn = mod(abs(mutn), lb_modulo)
      decode_fitness_fav = max_fav_fitness_gain*dexp(-alpha_fav
     &                     *(real(mtn)*fav_scale)**gamma_fav)
      return
      end

      real*8 function decode_fitness_del(mutn)
      include 'common.h'
      integer mutn
      real*8 x
      x = mod(abs(mutn), lb_modulo)*del_scale
      if(x >= 1.d0) then
         decode_fitness_del = 0.d0
      else
         decode_fitness_del = -dexp(-alpha_del*x**gamma_del)
      end if
      return
      end

      subroutine write_output_dump(dmutn,fmutn,lb_mutn_count,
     &                             linkage_block_fitness,
     &                             initial_allele_effects,
     &                             generation_number,myid_str)

c...  This routine writes an output file containing the current
c...  parameter values, the stored mutation arrays dmutn and fmutn,
c...  the linkage block mutation count array lb_mutn_count and
c...  the linkage block fitness array linkage_block_fitness for
c...  the current generation specified by generation_number.

      include 'common.h'
      integer dmutn(max_del_mutn_per_indiv/2,2,*),
     &        fmutn(max_fav_mutn_per_indiv/2,2,*),
     &               lb_mutn_count(num_linkage_subunits,2,2,*)
      real*8 linkage_block_fitness(num_linkage_subunits,2,*)
      real  initial_allele_effects(num_linkage_subunits)
      integer generation_number, i, lb, npath
      character char1*1
      character myid_str*3
      call second(tin)

      npath = index(data_file_path,' ') - 1
      char1 = char(48 + dump_number)

      open (10, file=data_file_path(1:npath)//case_id//
     &      '.'//myid_str//'.dmp.'//char1,status='unknown')

      write(10,'(a20, i12)') 'generation_number = ', generation_number

      do i=1,pop_size
            write(10,'(12i6)') lb_mutn_count(:,:,:,i) 
            write(10,'(6f12.8)') linkage_block_fitness(:,:,i) 
            write(10,'( i12)') dmutn(1,1,i)
            write(10,'(6i12)') dmutn(2:dmutn(1,1,i)+1,1,i)
            write(10,'( i12)') dmutn(1,2,i)
            write(10,'(6i12)') dmutn(2:dmutn(1,2,i)+1,2,i)
            write(10,'( i12)') fmutn(1,1,i)
            write(10,'(6i12)') fmutn(2:fmutn(1,1,i)+1,1,i)
            write(10,'( i12)') fmutn(1,2,i)
            write(10,'(6i12)') fmutn(2:fmutn(1,2,i)+1,2,i)
      end do

      if(num_contrasting_alleles > 0) 
     &   write(10,'(6f12.9)') initial_allele_effects

      close (10)

      call second(tout)
      sec(10) = sec(10) + tout - tin
      end

      subroutine write_sample(dmutn,fmutn,lb_mutn_count,
     &                        linkage_block_fitness,fitness,
     &                        defect,improve,effect,del_mutn,
     &                        fav_mutn,generation_number)

c...  This routine writes an output file containing details concerning
c...  the mutations carried by five members of the total population in
c...  a format that is (hopefully) readily understandable.

      include 'common.h'
      integer dmutn(max_del_mutn_per_indiv/2,2,*),
     &        fmutn(max_fav_mutn_per_indiv/2,2,*),
     &               lb_mutn_count(num_linkage_subunits,2,2,*),
     &                    del_mutn(num_linkage_subunits,2),
     &                    fav_mutn(num_linkage_subunits,2)
      real*8 linkage_block_fitness(num_linkage_subunits,2,*),
     &       fitness(*), x
      real  defect(num_linkage_subunits,2,*), effect(*),
     &     improve(num_linkage_subunits,2,*), d
      integer generation_number, i, j, lb, m, mutn
      call second(tin)

      rewind (12)

      call write_parameters(12)

      write(12,'(/23x,"generation number = ",i6)') generation_number

      do i=current_pop_size/10,current_pop_size/3,current_pop_size/5

         write(12,'(/"individual number = ",i6,"  fitness = ",f9.6)')
     &         i, fitness(i)

         del_mutn = 0
         fav_mutn = 0
      
         do m=2,dmutn(1,1,i)+1
            lb = abs(dmutn(m,1,i))/lb_modulo + 1
            del_mutn(lb,1) = del_mutn(lb,1) + 1
            x  = mod(abs(dmutn(m,1,i)), lb_modulo)*del_scale
            d  = dexp(-alpha_del*x**gamma_del)
            if(x >= 1.d0) d = 0.
            if(dmutn(m,1,i) < 0) d = -d
            defect(lb,1,del_mutn(lb,1)) = d
         end do

         do m=2,dmutn(1,2,i)+1
            lb = abs(dmutn(m,2,i))/lb_modulo + 1
            del_mutn(lb,2) = del_mutn(lb,2) + 1
            x  = mod(abs(dmutn(m,2,i)), lb_modulo)*del_scale
            d  = dexp(-alpha_del*x**gamma_del)
            if(x >= 1.d0) d = 0.
            if(dmutn(m,2,i) < 0) d = -d
            defect(lb,2,del_mutn(lb,2)) = d
         end do

         do m=2,fmutn(1,1,i)+1
            lb = abs(fmutn(m,1,i))/lb_modulo + 1
            fav_mutn(lb,1) = fav_mutn(lb,1) + 1
            mutn = mod(abs(fmutn(m,1,i)), lb_modulo)
            d    = dexp(-alpha_fav*(real(mutn)*fav_scale)**gamma_fav)
     &             *max_fav_fitness_gain
            if(fmutn(m,1,i) < 0) d = -d
            improve(lb,1,fav_mutn(lb,1)) = d
         end do

         do m=2,fmutn(1,2,i)+1
            lb = abs(fmutn(m,2,i))/lb_modulo + 1
            fav_mutn(lb,2) = fav_mutn(lb,2) + 1
            mutn = mod(abs(fmutn(m,2,i)), lb_modulo)
            d    = dexp(-alpha_fav*(real(mutn)*fav_scale)**gamma_fav)
     &             *max_fav_fitness_gain
            if(fmutn(m,2,i) < 0) d = -d
            improve(lb,2,fav_mutn(lb,2)) = d
         end do

         do lb=1,num_linkage_subunits

            write(12,'(/27x,"lb number = ",i6)') lb

            write(12,'("Haplotype 1: total deleterious mutn count = ",
     &                 i6, "  composite fitness = ",f9.6)') 
     &         lb_mutn_count(lb,1,1,i), linkage_block_fitness(lb,1,i)

            if(tracking_threshold /= 1.0) then
  
            j = 0
            do m=1,del_mutn(lb,1)
               if(defect(lb,1,m) < 0) then
                  j = j + 1
                  effect(j) = -defect(lb,1,m)
               end if
            end do

            if(j > 0) then
               write(12,'("Fitness degradations of tracked deleterious "
     &                    "recessive mutations:")')
               write(12,'(8f9.6)') (effect(m),m=1,j)
            end if 

            j = 0
            do m=1,del_mutn(lb,1)
               if(defect(lb,1,m) > 0) then
                  j = j + 1
                  effect(j) = defect(lb,1,m)
               end if
            end do

            if(j > 0) then
               write(12,'("Fitness degradations of tracked deleterious "
     &                    "dominant mutations:")')
               write(12,'(8f9.6)') (effect(m),m=1,j)
            end if 

            j = 0
            do m=1,fav_mutn(lb,1)
               if(improve(lb,1,m) < 0) then
                  j = j + 1
                  effect(j) = -improve(lb,1,m)
               end if
            end do

            if(j > 0) then
               write(12,'("Fitness improvements of tracked favorable "
     &                    "recessive mutations:")')
               write(12,'(8f9.6)') (effect(m),m=1,j)
            end if 

            j = 0
            do m=1,fav_mutn(lb,1)
               if(improve(lb,1,m) > 0) then
                  j = j + 1
                  effect(j) = improve(lb,1,m)
               end if
            end do

            if(j > 0) then
               write(12,'("Fitness improvements of tracked favorable "
     &                    "dominant mutations:")')
               write(12,'(8f9.6)') (effect(m),m=1,j)
            end if 

            end if 

            write(12,'("Haplotype 2: total deleterious mutn count = ",
     &                 i6, "  composite fitness = ",f9.6)') 
     &         lb_mutn_count(lb,2,1,i), linkage_block_fitness(lb,2,i)

            if(tracking_threshold /= 1.0) then

            j = 0
            do m=1,del_mutn(lb,2)
               if(defect(lb,2,m) < 0) then
                  j = j + 1
                  effect(j) = -defect(lb,2,m)
               end if
            end do

            if(j > 0) then
               write(12,'("Fitness degradations of tracked deleterious "
     &                    "recessive mutations:")')
               write(12,'(8f9.6)') (effect(m),m=1,j)
            end if 

            j = 0
            do m=1,del_mutn(lb,2)
               if(defect(lb,2,m) > 0) then
                  j = j + 1
                  effect(j) = defect(lb,2,m)
               end if
            end do

            if(j > 0) then
               write(12,'("Fitness degradations of tracked deleterious "
     &                    "dominant mutations:")')
               write(12,'(8f9.6)') (effect(m),m=1,j)
            end if 

            j = 0
            do m=1,fav_mutn(lb,2)
               if(improve(lb,2,m) < 0) then
                  j = j + 1
                  effect(j) = -improve(lb,2,m)
               end if
            end do

            if(j > 0) then
               write(12,'("Fitness improvements of tracked favorable "
     &                    "recessive mutations:")')
               write(12,'(8f9.6)') (effect(m),m=1,j)
            end if 

            j = 0
            do m=1,fav_mutn(lb,2)
               if(improve(lb,2,m) > 0) then
                  j = j + 1
                  effect(j) = improve(lb,2,m)
               end if
            end do

            if(j > 0) then
               write(12,'("Fitness improvements of tracked favorable "
     &                    "dominant mutations:")')
               write(12,'(8f9.6)') (effect(m),m=1,j)
            end if 

            end if 

         end do

      end do

      call flush(12)

      call second(tout)
      sec(11) = sec(11) + tout - tin
      end

      subroutine read_parameters(nf)

      include 'common.h'
      integer nf

      namelist /basic/ case_id, mutn_rate, frac_fav_mutn,
     &     reproductive_rate, pop_size, num_generations
      namelist /mutations/ fitness_distrib_type, fraction_neutral,
     &     genome_size, high_impact_mutn_fraction,
     &     high_impact_mutn_threshold, uniform_fitness_effect_del,
     &     uniform_fitness_effect_fav,
     &     max_fav_fitness_gain, num_initial_fav_mutn,
     &     multiplicative_weighting, fraction_recessive,
     &     recessive_hetero_expression, dominant_hetero_expression,
     &     upload_mutations, allow_back_mutn, se_nonlinked_scaling,
     &     se_linked_scaling, synergistic_epistasis
      namelist /selection/ fraction_random_death, heritability,
     &     non_scaling_noise, fitness_dependent_fertility,
     &     selection_scheme, partial_truncation_value
      namelist /population/ clonal_reproduction, clonal_haploid,
     &     num_contrasting_alleles, max_total_fitness_increase,
     &     dynamic_linkage, haploid_chromosome_number,
     &     fraction_self_fertilization, num_linkage_subunits,
     &     pop_growth_model, pop_growth_rate, bottleneck_yes,
     &     bottleneck_generation, bottleneck_pop_size,
     &     num_bottleneck_generations
      namelist /substructure/ is_parallel, homogenous_tribes,
     &     num_indiv_exchanged, migration_model, migration_generations,
     &     tribal_competition, tc_scaling_factor, group_heritability,
     &     altruistic, social_bonus_factor
      namelist /computation/ tracking_threshold, extinction_threshold,
     &     max_del_mutn_per_indiv, max_fav_mutn_per_indiv,
     &     random_number_seed, track_neutrals, write_dump, restart_case,
     &     restart_dump_number, data_file_path, plot_allele_gens

      read (unit=nf, nml=basic)
      read (unit=nf, nml=mutations)
      read (unit=nf, nml=selection)
      read (unit=nf, nml=population)
      read (unit=nf, nml=substructure)
      read (unit=nf, nml=computation)

      end


      subroutine write_parameters(nf)

c...  This routine writes the current parameter values to logical
c...  unit nf.

      include 'common.h'
      integer nf
      call second(tin)

      write(nf,'("basic:")')
      write(nf,'(a32,6xa6)')  ' case_id = ', case_id
      write(nf,'(a32,f12.7)') ' mutn_rate = ', mutn_rate
      write(nf,'(a32,f12.7)') ' frac_fav_mutn = ', frac_fav_mutn
      write(nf,'(a32,f12.7)') ' reproductive_rate = ', reproductive_rate
      write(nf,'(a32,i12)')   ' pop_size = ', pop_size
      write(nf,'(a32,i12)')   ' num_generations = ', num_generations

      write(nf,'(/"mutation:")')
      write(nf,'(a32,i12)')   ' fitness_distrib_type = ',  
     &                          fitness_distrib_type          
      write(nf,'(a32,f12.7)') ' fraction_neutral = ', fraction_neutral
      write(nf,'(a32,e12.3)') ' genome_size = ', genome_size
      write(nf,'(a32,f12.7)') ' high_impact_mutn_fraction = ',
     &                          high_impact_mutn_fraction   
      write(nf,'(a32,f12.7)') ' high_impact_mutn_threshold = ',
     &                          high_impact_mutn_threshold 
      write(nf,'(a32,i12)')   ' num_initial_fav_mutn = ',
     &                          num_initial_fav_mutn         
      write(nf,'(a32,f12.7)') ' max_fav_fitness_gain = ',
     &                          max_fav_fitness_gain 
      write(nf,'(a32,f12.7)') ' uniform_fitness_effect_del = ',
     &                          uniform_fitness_effect_del     
      write(nf,'(a32,f12.7)') ' uniform_fitness_effect_fav = ',
     &                          uniform_fitness_effect_fav     
      write(nf,'(a32,f12.7)') ' fraction_recessive = ',
     &                          fraction_recessive             
      write(nf,'(a32,f12.7)') ' recessive_hetero_expression = ',
     &                          recessive_hetero_expression    
      write(nf,'(a32,f12.7)') ' dominant_hetero_expression = ',
     &                          dominant_hetero_expression     
      write(nf,'(a32,f12.7)') ' multiplicative_weighting = ',
     &                          multiplicative_weighting       
      write(nf,'(a32,l)')     ' synergistic_epistasis = ',
     &                          synergistic_epistasis          
      write(nf,'(a32,e12.5)') ' se_nonlinked_scaling = ',
     &                          se_nonlinked_scaling           
      write(nf,'(a32,e12.5)') ' se_linked_scaling = ', 
     &                          se_linked_scaling              
      write(nf,'(a32,l)')     ' upload_mutations = ',
     &                          upload_mutations               
      write(nf,'(a32,l)')     ' allow_back_mutn = ',
     &                          allow_back_mutn                
 
      write(nf,'(/"selection:")')
      write(nf,'(a32,f12.7)') ' fraction_random_death = ', 
     &                          fraction_random_death          
      write(nf,'(a32,f12.7)') ' heritability = ',
     &                          heritability                   
      write(nf,'(a32,f12.7)') ' non_scaling_noise = ',
     &                          non_scaling_noise              
      write(nf,'(a32,l)')     ' fitness_dependent_fertility = ',
     &                          fitness_dependent_fertility    
      write(nf,'(a32,i12)')   ' selection_scheme = ',
     &                          selection_scheme               
      write(nf,'(a32,f12.7)') ' partial_truncation_value = ',
     &                          partial_truncation_value       

      write(nf,'(/"population:")')
      write(nf,'(a32,l)')     ' clonal_reproduction = ',
     &                          clonal_reproduction            
      write(nf,'(a32,l)')     ' clonal_haploid = ',
     &                          clonal_haploid                 
      write(nf,'(a32,f12.7)') ' fraction_self_fertilization = ',
     &                          fraction_self_fertilization    
      write(nf,'(a32,i12)')   ' num_contrasting_alleles = ',
     &                          num_contrasting_alleles        
      write(nf,'(a32,f12.7)') ' initial_alleles_mean_effect = ',
     &                          initial_alleles_mean_effect    
      write(nf,'(a32,l)')     ' dynamic_linkage = ',
     &                          dynamic_linkage                
      write(nf,'(a32,i12)')   ' haploid_chromosome_number = ',
     &                          haploid_chromosome_number      
      write(nf,'(a32,i12)')   ' num_linkage_subunits = ',
     &                          num_linkage_subunits           
      write(nf,'(a32,i12)')   ' pop_growth_model = ',
     &                          pop_growth_model               
      write(nf,'(a32,f12.7)') ' pop_growth_rate = ',
     &                          pop_growth_rate                
      write(nf,'(a32,l)')     ' bottleneck_yes = ',
     &                          bottleneck_yes                 
      write(nf,'(a32,i12)')   ' bottleneck_generation = ',
     &                          bottleneck_generation
      write(nf,'(a32,i12)')   ' bottleneck_pop_size = ',
     &                          bottleneck_pop_size
      write(nf,'(a32,i12)')   ' num_bottleneck_generations  = ', 
     &                          num_bottleneck_generations

      write(nf,'(/"substructure:")')
      write(nf,'(a32,l)')     ' is_parallel = ', is_parallel
      write(nf,'(a32,l)')     ' homogenous_tribes = ', homogenous_tribes
      write(nf,'(a32,i12)')   ' num_indiv_exchanged = ', 
     &                          num_indiv_exchanged            
      write(nf,'(a32,i12)')   ' migration_generations = ',
     &                          migration_generations          
      write(nf,'(a32,i12)')   ' migration_model = ',   
     &                          migration_model    
      write(nf,'(a32,l)')     ' tribal_competition = ',
     &                          tribal_competition
      write(nf,'(a32,f12.7)') ' tc_scaling_factor = ',   
     &                          tc_scaling_factor 
      write(nf,'(a32,f12.7)') ' group_heritability = ',   
     &                          group_heritability 
      write(nf,'(a32,l)')     ' altruistic = ', altruistic
      write(nf,'(a32,f12.7)') ' social_bonus_factor = ',
     &                          social_bonus_factor

      write(nf,'(/"computation:")')
      write(nf,'(a32,1pe12.3)') ' tracking_threshold = ',
     &                            tracking_threshold
      write(nf,'(a32,f12.7)') ' extinction_threshold = ',
     &                          extinction_threshold
      write(nf,'(a32,i12)')   ' max_del_mutn_per_indiv = ',   
     &                          max_del_mutn_per_indiv
      write(nf,'(a32,i12)')   ' max_fav_mutn_per_indiv = ',   
     &                          max_fav_mutn_per_indiv
      write(nf,'(a32,i12)')   ' random_number_seed = ',
     &                          random_number_seed
      write(nf,'(a32,l)')     ' track_neutrals = ',
     &                          track_neutrals
      write(nf,'(a32,l)')     ' write_dump = ',
     &                          write_dump
      write(nf,'(a32,l)')     ' restart_case = ',
     &                          restart_case
      write(nf,'(a32,i12)')   ' restart_dump_number = ',
     &                          restart_dump_number
      write(nf,'(a20,a80)') '  data_file_path:  ', data_file_path
      write(nf,*)

      call second(tout)
      sec(13) = sec(13) + tout - tin
      end

      subroutine write_status(unit, gen, current_pop_size,
     &           frac_recessive, total_del_mutn, tracked_del_mutn, 
     &           total_fav_mutn, tracked_neu_mutn, pre_sel_fitness, 
     &           pre_sel_geno_sd, pre_sel_pheno_sd, pre_sel_corr, 
     &           post_sel_fitness, post_sel_geno_sd, post_sel_pheno_sd, 
     &           post_sel_corr)
      
      integer unit, gen, current_pop_size
      real*8  pre_sel_fitness, pre_sel_geno_sd, pre_sel_pheno_sd,
     &        pre_sel_corr, post_sel_fitness, post_sel_geno_sd, 
     &        post_sel_pheno_sd, post_sel_corr
      real*8  total_del_mutn, tracked_del_mutn, total_fav_mutn,
     &        frac_recessive, tracked_neu_mutn

      write(unit,'(/"generation     =",i6,"  population size =", i6,
     &      "  frac recessive =",f7.4/"before sel: geno fitness =",f9.5,
     &      "  geno s.d. =",f8.5,"  pheno s.d. =",f8.5/
     &      "after  sel:               ",f9.5,"             ",f8.5,
     &      "              ",f8.5/"before sel geno-pheno corr =",f7.4,
     &      "    after sel geno-pheno corr =",f7.4/
     &      "del mutn/indiv =",i6,
     &      "  tracked del/ind =",i6,"  fav mutn/indiv =",f10.3)')
     &      gen, current_pop_size, frac_recessive,
     &      pre_sel_fitness, pre_sel_geno_sd, pre_sel_pheno_sd,
     &      post_sel_fitness, post_sel_geno_sd, post_sel_pheno_sd,
     &      pre_sel_corr, post_sel_corr,
     &      int((total_del_mutn   - tracked_neu_mutn)/current_pop_size),
     &      int((tracked_del_mutn - tracked_neu_mutn)/current_pop_size),
     &      total_fav_mutn/current_pop_size
            if(tracked_neu_mutn > 0) write(unit,
     &      '("                        tracked neu/ind =",i6)')
     &      int(tracked_neu_mutn/current_pop_size)

      end

      subroutine tabulate_initial_alleles(dmutn, fmutn,
     &   linkage_block_fitness, initial_allele_effects, max_size)

c...  This routine generates a file to report the allele distribution
c...  resulting from a small number (no larger than the number
c...  of linkage subunits) of paired alleles, with a random fitness
c...  effect on one haplotype set and an effect with the same magnitude
c...  but the opposite sign on the other haplotype set.  Variation of
c...  of fitness effect is according to a uniform random distribution
c...  with a user-specified mean value.

      include 'common.h'

      integer max_size
      integer dmutn(max_del_mutn_per_indiv/2,2,max_size)
      integer fmutn(max_fav_mutn_per_indiv/2,2,max_size)
      real*8 linkage_block_fitness(num_linkage_subunits,2,max_size)
      real initial_allele_effects(num_linkage_subunits)
      real effect, expressed
      integer i, lb, m, mutn, mutn_indx, n, ndel, nfav, npath, nskp

      if(num_contrasting_alleles > 0) then
         num_contrasting_alleles = min(num_linkage_subunits,
     &                                 num_contrasting_alleles)
         nskp = num_linkage_subunits/num_contrasting_alleles
      else
         return
      end if

      write(30,*) "#      Distribution of Contrasting Alleles"
      write(30,*) "#   block      del       fav    fitness effect  "

      do n=1,num_contrasting_alleles

         lb = 1 + (n - 1)*nskp

c...     The same mutation effect index is used for all of these paired
c...     alleles. This index, lb_modulo-1, is reserved exclusively for
c...     these alleles.

         mutn = lb_modulo - 1

c...     Add an offset to assign it to the appropriate linkage block.

         mutn_indx = mutn + (lb - 1)*lb_modulo

c...     Loop over entire population, count the number of each of the
c...     alleles, and output these statistics.

         ndel = 0
         nfav = 0

         do i=1,current_pop_size

            do m=2,dmutn(1,1,i) + 1
               if (dmutn(m,1,i) == mutn_indx) ndel = ndel + 1
            end do

            do m=2,dmutn(1,2,i) + 1
               if (dmutn(m,2,i) == mutn_indx) ndel = ndel + 1
            end do

            do m=2,fmutn(1,1,i) + 1
               if (fmutn(m,1,i) == mutn_indx) nfav = nfav + 1
            end do

            do m=2,fmutn(1,2,i) + 1
               if (fmutn(m,2,i) == mutn_indx) nfav = nfav + 1
            end do

         end do

         write(30,'(3i10,f15.10)') lb, ndel, nfav,
     &                             initial_allele_effects(lb)

      end do

      end

      subroutine second(time)

      real time, times(2)

      time = etime(times)
      time = times(1)

      end

      subroutine profile(unit)

c     Routine to dump timing information at end of run
c...  This routine outputs the timing information stored in
c...  common block /clck/.

      include 'common.h'
      integer i, unit

      if (myid == 0) then
         write(unit,10) sec(2) 
         sec(3) = sec(3)/num_generations*migration_generations
         sec(4) = sec(4)/num_generations !*fav_mutn+num_initial_fav_mutn
         sec(5) = sec(5)/num_generations !*actual_offspring
         sec(6) = sec(6)/num_generations
         sec(7) = sec(7)/num_generations ! every 20 generations
         sec(8) = sec(8)/num_generations ! every 100 generations
         write(unit,20) (1000.*sec(i),i=3,6)
         write(unit,30) (1000.*sec(i),i=7,14)
      end if

 10   format(/10x,"CPU SECONDS USED PER PROCESSOR:"//
     &       10x,"TOTAL     ",f10.3)

 20   format(/10x,"PRIMARY SUBROUTINES (MILLISECONDS/GEN/PROC):"//
     &       10x,"MIGRATION        ",f10.3/
     &       10x,"FAVORABLE_MUTN   ",f10.3/
     &       10x,"OFFSPRING        ",f10.3/
     &       10x,"SELECTION        ",f10.3)

 30   format(/10x,"AUXILIARY ROUTINES (MILLISEC/GEN/PROC):"//
     &       10x,"MUTN STATISTICS  ",f10.3/
     &       10x,"ALLELE STATISTICS",f10.3/
     &       10x,"READ_RESTART_DUMP",f10.3/
     &       10x,"WRITE_OUTPUT_DUMP",f10.3/
     &       10x,"WRITE_SAMPLE     ",f10.3/
     &       10x,"READ_PARAMETERS  ",f10.3/
     &       10x,"WRITE_PARAMETERS ",f10.3/
     &       10x,"BACK_MUTN        ",f10.3/10x)

      end
