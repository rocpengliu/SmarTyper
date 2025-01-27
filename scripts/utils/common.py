parent_button_size = {'width': 160, 'height': 30}

child_button_size = {'width': 100, 'height': 20}

micro_microhap_df_columns=['Sample','Locus','Allele','BaseChange','NumReads',
                     'AlleleReadsPer','VarRatio','TotalReads',
                     'ReadsPer','Conclusive','Zygosity','Indel','Sequence', 'id']
micro_micohap_df_empty_row=['nan','nan',0,'nan',0,0,'nan',0,0,'N','inconclusive','nan','nan', 'nan']

micro_amplicon_df_columns=['Sample','Locus','NumReads','TotalReads','ReadRatio','BaseChange','Length','Sequence', 'id']
micro_amplicon_df_empty_row=['nan','nan',0,0,0,'nan',0,'nan','nan']
color_bars={"dgreen":(0.0, 0.39, 0.0, 1.0),
            "orange":(1.0, 0.65, 0.0, 1.0),
            "lgray":(0.83, 0.83, 0.83, 1.0)}

dna_base_list = ['A', 'T', 'C', 'G']
aa_base_list = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']