


class DotDict(dict):
    """
    Makes a  dictionary behave like an object,with attribute-style access.
    """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def __getattr__(self, key: str):
        if key in self.keys():
            value=self[key]
            if isinstance(value,dict):
                value=DotDict(value)
            return value
        else:
            raise AttributeError(f"no attribute '{key}'")
    
    def __setattr__(self, key: str, value) -> None:
        if key in self.keys:
            self[key]=value
        else:
            raise AttributeError('The class does not allow dynamic addition of properties')

    