      subroutine mpi_myinit(ownid,ierr)
      end
 
      subroutine mpi_mybarrier()
      end

      subroutine mpi_myabort()
      end

      subroutine mpi_mybcastd(x,n)
      end

      subroutine mpi_mybcasti(x,n)
      end

      subroutine mpi_send_int(istatus,dest,msg_num,ierr)
      end

      subroutine mpi_recv_int(istatus,src,msg_num,ierr)
      end

      subroutine mpi_myfinalize(ierr)
      end

      subroutine mpi_davg(x, xavg, n)
      end

      subroutine mpi_dsum(x, xsum, n)
      end

      subroutine mpi_ravg(x, xavg, n)
      end

      subroutine mpi_isum(i, isum, n)
      end

      subroutine mpi_migration(dmutn,fmutn,linkage_block_fitness,
     &           lb_mutn_count,gen,ierr,msg_num,available)
      end
