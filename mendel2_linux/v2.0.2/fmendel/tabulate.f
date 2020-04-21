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

      npath = index(data_file_path,' ') - 1
      open (30, file=data_file_path(1:npath)//case_id//'.ica',
     &          status='unknown')
      write(30,*) "#  Final Distribution of Contrasting Alleles"
      write(30,*) "#   del       fav    fitness effect

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

         write(30,'(2i10,f15.12)') ndel, nfav, 
     &                             initial_allele_effects(lb)

      end do

      close(30)

      end
