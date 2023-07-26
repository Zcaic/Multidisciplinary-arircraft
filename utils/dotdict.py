# from typing import List
# from aerosandbox.common import AeroSandboxObject

class DotDict(dict):
    """
    Makes a  dictionary behave like an object,with attribute-style access.
    """
    def __init__(self,*args,**kwargs):
        # super().__init__(*args,**kwargs)
        for i in args:
            super().__setattr__(i.name,i)


    def __getattr__(self, key: str):
        if key in self.keys():
            return self[key]
        else:
            raise AttributeError(f"no attribute '{key}'")
    
    def __setattr__(self, key: str, value) -> None:
        if hasattr(self,key):
            super().__setattr__(key,value)
        else:
            raise AttributeError('The class does not allow dynamic addition of properties')

    