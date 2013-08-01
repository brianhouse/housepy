def num_args(f):
    """Returns the number of arguments received by the given function"""
    import inspect
    return len(inspect.getargspec(f).args)  
        
def soup(string, **kwargs):
    """Create a BeautifulSoup parse object from a string"""
    from bs4 import BeautifulSoup
    return BeautifulSoup(string, **kwargs)
    
def chunk(l, size):    
    def ck(l, size):
        for i in xrange(0, len(l), size):
            yield l[i:i + size] 
    return list(ck(l, size))
