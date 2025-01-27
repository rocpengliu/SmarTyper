import os

class FastqFile:
    def __init__(self, dirpath, fname, suffix1="_R1_001.fastq.gz", suffix2="_R2_001.fastq.gz", pe = True):
        self.dirpath = dirpath
        self.name = fname
        self.read1=fname+suffix1
        self.read2=fname+suffix2
        self.suffix1=suffix1
        self.suffix2=suffix2
        self.read1_size = self.__get_file_size(False, pe)
        self.read2_size = self.__get_file_size(True, pe)
    
    def __get_file_size(self, sec = False, pe = True):
        if sec and pe:
            read2file = os.path.join(self.dirpath, self.read2)
            if os.path.isfile(read2file):
                return os.path.getsize(read2file)

        else:
            read1file = os.path.join(self.dirpath, self.read1)
            if os.path.isfile(read1file):
                return os.path.getsize(read1file)
        return 0
    
    def readable_size(self, sec = False):
        # Converts the file size to a readable format
        if sec:
            size = self.read2_size
        else:
            size = self.read1_size
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def print(self):
        print(f"File: {self.name}, Read1: {self.read1}, Read2: {self.read2}, Read1 size: {self.readable_size(False)}, Read2 size: {self.readable_size(True)}")

class FastqFileSimple:
    def __init__(self, id, fname, read1, read2, dirpath, pe = True):
        self.id = id
        self.dirpath = dirpath
        self.name = fname
        self.read1=read1
        self.read2=read2
        self.read1_size = self.__get_file_size(False, pe)
        self.read2_size = self.__get_file_size(True, pe)
        self.status=False
        self.pe = pe
    
    def __get_file_size(self, sec = False, pe = True):
        if sec and pe:
            read2file = os.path.join(self.dirpath, self.read2)
            if os.path.isfile(read2file):
                return os.path.getsize(read2file)
        else:
            read1file = os.path.join(self.dirpath, self.read1)
            if os.path.isfile(read1file):
                return os.path.getsize(read1file)
        return 0
    
    def readable_size(self, sec = False):
        # Converts the file size to a readable format
        if sec:
            size = self.read2_size
            if self.pe:
                if size > 0:
                    self.status= (self.status and True)
                else:
                    self.status=False
        else:
            size = self.read1_size
            if size > 0:
                self.status=True
                
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def print(self):
        print(f"File: {self.name}, Read1: {self.read1}, Read2: {self.read2}, Read1 size: {self.readable_size(False)}, Read2 size: {self.readable_size(True)}")
   