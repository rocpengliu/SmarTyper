
class ResultParameter:
    def __init__(self):
        self._res_type = "sample"
        self._sample = ""
        self._marker=""
            
    def get_res_type(self):
        return self._res_type
    
    def set_res_type(self, res_type):
        self._res_type = res_type
        if not isinstance(res_type, str):
            raise ValueError("Result type must be a string")
    
    def get_sample(self):
        return self._sample
    def set_sample(self, sample):
        self._sample = sample
        if not isinstance(sample, str):
            raise ValueError("Sample name must be a string")
    
    def get_marker(self):
        return self._marker
    def set_marker(self, marker):
        self._marker = marker
        if not isinstance(marker, str):
            raise ValueError("Marker name must be a string")
    
    def set_sample_or_marker(self, item) -> None:
        if self.get_res_type() == "sample":
            self.set_sample(item)
        elif self.get_res_type() == "marker":
            self.set_marker(item)
        else:
            raise ValueError("you must select sample or marker")
 