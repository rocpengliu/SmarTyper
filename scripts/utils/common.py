parent_button_size = {'width': 90, 'height': 18}

child_button_size = {'width': 50, 'height': 12}

title_font = ("Segoe UI", 48, "bold")
module_font = ("Segoe UI", 36, "bold")
subtitle_font = ("Segoe UI", 18)
card_title_font = ("Segoe UI", 30, "bold")
card_desc_font = ("Segoe UI", 12)

header_font = ("Segoe UI", 28, "bold")

bfont = ("Segoe UI", 15, "bold")
bmbfont= ("Segoe UI", 12, "bold")
bmfont= ("Segoe UI", 12)
brfont = ("Segoe UI", 11)
fig_font = ("Segoe UI", 10, "bold")
seq_font = ("Courier", 9)

pnbuttonfont = ("Segoe UI", 13, "bold")
confirm_button_font = ("Segoe UI", 16, "bold")

micro_microhap_df_columns=['Sample','Locus','Allele','BaseChange','NumReads',
                     'AlleleReadsPer','VarRatio','TotalReads',
                     'ReadsPer','Conclusive','Zygosity','Indel','Sequence', 'id']
micro_micohap_df_empty_row=['nan','nan',0,'nan',0,0,'nan',0,0,'N','inconclusive','nan','nan', 'nan']

micro_amplicon_df_columns=['Sample','Locus','NumReads','TotalReads','ReadRatio','BaseChange','Length','Sequence', 'id']
micro_amplicon_df_empty_row=['nan','nan',0,0,0,'nan',0,'nan','nan']

ml_mh_df_columns = ['Locus', 'TotRead', 'Read1', 'Read2', 'Read3', 'NumMut1', 'NumMut2', 'Prop1', 'Prop2', 'Prop3', 'MhProp1', 'MhProp2', 'Indel', 'Zygosity']

color_bars={"dgreen":(0.0, 0.39, 0.0, 1.0),
            "orange":(1.0, 0.65, 0.0, 1.0),
            "lgray":(0.7, 0.7, 0.7, 1.0)}

dna_base_list = ['A', 'T', 'C', 'G']
aa_base_list = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']