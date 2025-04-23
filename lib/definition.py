# Configuration/Definition class object for simpler dot notation references
# i.e. converts an object of keys into a class object of attributes
class Definition:

    def __init__(self, obj={}):
        self._keys_ = []        # list of assigned attributes
        self.add(obj)

    def has(self, key=None):
        if key == None:
            return self._keys_.copy()
        return hasattr(self, key)

    def add(self, obj={}):
        if isinstance(obj, list):
            for a in obj:
                self.add(a)
        else:
            for k in obj.keys():
                setattr(self,k,obj[k])
                if not self._keys_.count(k):
                    self._keys_.append(k)
    
    def remove(self, key=None):
        if key==None:
            for k in self._keys_:
                self.remove(k)
        else:
            if hasattr(self, key):
                delattr(self, key)
                self._keys_.remove(k)
    
    def resolve(self, key=None, default=None):
        if key==None:
            dx = {}
            for k in self._keys_:
                dx[k] = getattr(self,k)
            return dx
        if not self.has(key):
            self.add(dict([(key, default)]))
        return getattr(self,key)
