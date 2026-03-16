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

micro_ml_df_columns = ['sample','locus','readt','read1','read2','read3','rprop1','rprop2','rprop3','mprop1','mprop2	prop','mut','indel','zygosity']

#sample	locus	allele	readt	read	rprop	mprop	sprop	mut	indel	conclusive	zygosity	baseChange	seq
# micro_microhap_df_columns=['Sample','Locus','Allele','BaseChange','NumReads',
#                      'AlleleReadsPer','VarRatio','TotalReads',
#                      'ReadsPer','Conclusive','Zygosity','Indel','Sequence', 'id']
micro_microhap_df_columns=['sample','locus','allele', 'readt', 'read', 'rprop', 'mprop', 'sprop', 'mut', 
                           'indel', 'zygosity', 'baseChange', 'seq', 'id']
micro_microhap_df_empty_row=['nan','nan',0,0,0,0,0,0,'0|0','N','inconclusive','nan', 'nan', 'nan']
# micro_microhap_df_empty_row=['nan','nan',0,'nan',0,0,'nan',0,0,'N','inconclusive','nan','nan', 'nan']

#sample	locus	readt	reads	prop	baseChange	len	seq

micro_amplicon_df_columns=['sample','locus','readt','reads','prop','baseChange','len','seq', 'id']
micro_amplicon_df_empty_row=['nan','nan',0,0,0,'nan',0,'nan','nan']

#sample	locus	readt	read1	read2	read3	rprop1	rprop2	rprop3	mprop1	mprop2	sprop	mut	indel	zygosity	conclusive	basechange	seq1	seq2	seq3
ml_mh_df_columns = ['sample', 'locus', 'readt', 'read1', 'read2', 'read3', 'rprop1', 'rprop2', 'rprop3', 'mprop1', 'mprop2', 'sprop', 'mut', 'indel', 'zygosity']

color_bars={"dgreen":(0.0, 0.39, 0.0, 1.0),
            "orange":(1.0, 0.65, 0.0, 1.0),
            "lgray":(0.7, 0.7, 0.7, 1.0)}

dna_base_list = ['A', 'T', 'C', 'G']
aa_base_list = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']