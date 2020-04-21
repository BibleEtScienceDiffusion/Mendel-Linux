      implicit none

      integer pop_size, num_generations, num_linkage_subunits, 
     &        bottleneck_generation, bottleneck_pop_size,
     &        num_bottleneck_generations, fitness_distrib_type,
     &        new_mutn_count,
     &        max_del_mutn_per_indiv, max_fav_mutn_per_indiv,
     &        num_initial_fav_mutn, num_indiv_exchanged,
     &        random_number_seed, restart_dump_number, 
     &        dump_number, lb_modulo, current_pop_size,
     &        mutn_per_indiv, haploid_chromosome_number,
     &        selection_scheme, migration_generations,
     &        migration_model, num_contrasting_alleles,
     &        myid, num_tribes, ierr, msg_num, MYCOMM,
     &        par_mutn_per_indiv, pop_growth_model,
     &        fav_fixed, fav_lost, tracked_fav_mutn,
     &        global_pop_size, new_pop_size, uploaded_mutn(1000),
     &        num_uploaded_mutn, num_back_mutn, 
     &        plot_allele_gens

      real    reproductive_rate, mutn_rate, 
     &        genome_size, high_impact_mutn_fraction,
     &        high_impact_mutn_threshold, fraction_recessive,
     &        dominant_hetero_expression, max_fav_fitness_gain,
     &        recessive_hetero_expression, frac_fav_mutn, 
     &        heritability, uniform_fitness_effect_del, 
     &        uniform_fitness_effect_fav, multiplicative_weighting, 
     &        fraction_random_death, fraction_self_fertilization,
     &        initial_alleles_mean_effect, non_scaling_noise,
     &        partial_truncation_value, del_scale, fav_scale,
     &        gamma_del, gamma_fav, se_nonlinked_scaling, 
     &        se_linked_scaling, poisson_mean, tin, tout, sec,
     &        pop_growth_rate, ica_mean_effect, fav_mean_freq,
     &        tc_scaling_factor, group_heritability, 
     &        social_bonus_factor, fraction_neutral,
     &        max_total_fitness_increase

      real*8  alpha_del, alpha_fav, synergistic_factor,
     &        pre_sel_fitness, post_sel_fitness, 
     &        pre_sel_geno_sd, pre_sel_pheno_sd, pre_sel_corr,
     &        post_sel_geno_sd, post_sel_pheno_sd, post_sel_corr,
     &        total_del_mutn, tracked_del_mutn, tribal_fitness_factor,
     &        tribal_fitness_factor_scaled, tribal_fitness,
     &        tribal_noise, social_bonus, tracking_threshold,
     &        extinction_threshold

      logical fitness_dependent_fertility, dynamic_linkage,
     &        synergistic_epistasis, is_parallel, bottleneck_yes, 
     &        restart_case, write_dump, homogenous_tribes,
     &        clonal_reproduction, clonal_haploid,
     &        upload_mutations, altruistic, allow_back_mutn,
     &        cyclic_bottlenecking, track_neutrals, tribal_competition

      character case_id*6, data_file_path*80

      common /mndl1/ pop_size, num_generations, num_linkage_subunits, 
     &               bottleneck_generation, bottleneck_pop_size,
     &               num_bottleneck_generations, fitness_distrib_type,
     &               new_mutn_count,
     &               max_del_mutn_per_indiv, max_fav_mutn_per_indiv,
     &               num_initial_fav_mutn, num_indiv_exchanged,
     &               random_number_seed, restart_dump_number, 
     &               dump_number, lb_modulo, current_pop_size,
     &               mutn_per_indiv, haploid_chromosome_number,
     &               selection_scheme, migration_generations,
     &               migration_model, num_contrasting_alleles, 
     &               myid, num_tribes, MYCOMM, 
     &               par_mutn_per_indiv, pop_growth_model,
     &               fav_fixed, fav_lost, tracked_fav_mutn,
     &               num_uploaded_mutn, uploaded_mutn, num_back_mutn,
     &               global_pop_size, new_pop_size, plot_allele_gens

      common /mndl2/ reproductive_rate, mutn_rate, 
     &               genome_size, high_impact_mutn_fraction,
     &               high_impact_mutn_threshold, fraction_recessive,
     &               dominant_hetero_expression, max_fav_fitness_gain,
     &               recessive_hetero_expression, frac_fav_mutn, 
     &               heritability, uniform_fitness_effect_del, 
     &               uniform_fitness_effect_fav,
     &               multiplicative_weighting, 
     &               fraction_random_death, fraction_self_fertilization,
     &               initial_alleles_mean_effect, non_scaling_noise,
     &               partial_truncation_value, del_scale, fav_scale,
     &               gamma_del, gamma_fav, se_nonlinked_scaling, 
     &               se_linked_scaling, poisson_mean, sec(15),
     &               pop_growth_rate, ica_mean_effect, fav_mean_freq,
     &               tc_scaling_factor, group_heritability, 
     &               social_bonus_factor, fraction_neutral,
     &               max_total_fitness_increase

      common /mndl3/ alpha_del, alpha_fav, synergistic_factor,
     &               pre_sel_fitness, post_sel_fitness, 
     &               pre_sel_geno_sd, pre_sel_pheno_sd, pre_sel_corr,
     &               post_sel_geno_sd, post_sel_pheno_sd, post_sel_corr,
     &               total_del_mutn, tracked_del_mutn, tribal_fitness, 
     &               tribal_noise, tribal_fitness_factor, 
     &               tribal_fitness_factor_scaled, social_bonus,
     &               tracking_threshold, extinction_threshold

      common /mndl4/ fitness_dependent_fertility, dynamic_linkage,
     &               synergistic_epistasis, is_parallel, bottleneck_yes, 
     &               restart_case, write_dump, homogenous_tribes,
     &               clonal_reproduction, clonal_haploid, 
     &               cyclic_bottlenecking, upload_mutations, 
     &               allow_back_mutn, altruistic, 
     &               track_neutrals, tribal_competition

      common /mndl5/ case_id, data_file_path
