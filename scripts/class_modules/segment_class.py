from ..utils.utils_common import print_time
class SegmentClass:
    def __int__(self)->None:
        self._seg_type = '' #intron or exon
        self._seg_id_in_gene = 0 # idx in the whole gene, eg 0:exon0, 1:intron0, 2:exon1, 3:intron1
        self._seg_id_in_zon = 0 # idx in the exon or introns, eg, 0:exon0, 1:exon2, or 0:intron0, 1:intron1
        self._start_pos_in_gene = 0
        self._end_pos_in_gene = 0
        self._start_pos_in_zon = 0 # this is the real position in the CDS or ORF, exon0 pos0-9, exon1 pos10-16....  or for intron0 pos0-pos10
        self._end_pos_in_zon = 0
        self._offset_len = 0 #not for intron, only for exon, for converting between pos in whole gene and splicer, is an accamulated introns,
                            #please be noted that for the splicers, some unused exons could be treated as intron
                            #tot length of all the previous lens of introns
    
    def get_seg_type(self):
        return self._seg_type
    
    def set_seg_type(self, seg_type):
        self._seg_type = seg_type
    
    def get_seg_id_in_gene(self):
        return self._seg_id_in_gene
    
    def set_seg_id_in_gene(self, seg_id_in_gene):
        self._seg_id_in_gene = seg_id_in_gene
    
    def get_seg_id_in_zon(self):
        return self._seg_id_in_zon
    
    def set_seg_id_in_zon(self, seg_id_in_zon):
        self._seg_id_in_zon = seg_id_in_zon
    
    def get_start_pos_in_gene(self):
        return self._start_pos_in_gene
    
    def set_start_pos_in_gene(self, start_pos_in_gene):
        self._start_pos_in_gene = start_pos_in_gene
    
    def get_end_pos_in_gene(self):
        return self._end_pos_in_gene
    
    def set_end_pos_in_gene(self, end_pos_in_gene):
        self._end_pos_in_gene = end_pos_in_gene
    
    def get_start_pos_in_zon(self):
        return self._start_pos_in_zon
    
    def set_start_pos_in_zon(self, start_pos_in_zon):
        self._start_pos_in_zon = start_pos_in_zon
    
    def get_end_pos_in_zon(self):
        return self._end_pos_in_zon
    
    def set_end_pos_in_zon(self, end_pos_in_zon):
        self._end_pos_in_zon = end_pos_in_zon
    
    def get_offset_len(self):
        return self._offset_len
    
    def set_offset_len(self, offset_len):
        self._offset_len = offset_len
    
    def print(self):
        if self._seg_type == "exon":
            print_time(f'exon\n'
                       f'self._seg_id_in_gene is {self.get_seg_id_in_gene()}\n'
                        f'self._seg_id_in_zon is {self.get_seg_id_in_zon()}\n'
                        f'self._start_pos_in_gene is {self.get_start_pos_in_gene()}\n'
                        f'self._end_pos_in_gene is {self.get_end_pos_in_gene()}\n'
                        f'self._start_pos_in_zon is {self.get_start_pos_in_zon()}\n'
                        f'self._end_pos_in_zon is {self.get_end_pos_in_zon()}\n')
        elif self._seg_type == "intron":
            print_time(f'intron\n'
                       f'self._seg_id_in_gene is {self.get_seg_id_in_gene()}\n'
                        f'self._seg_id_in_zon is {self.get_seg_id_in_zon()}\n'
                        f'self._start_pos_in_gene is {self.get_start_pos_in_gene()}\n'
                        f'self._end_pos_in_gene is {self.get_end_pos_in_gene()}\n'
                        f'self._start_pos_in_zon is {self.get_start_pos_in_zon()}\n'
                        f'self._end_pos_in_zon is {self.get_end_pos_in_zon()}\n')
        else:
            print_time(f"Invalid segment type")