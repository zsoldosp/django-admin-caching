class Patched(object):
    def __init__(self, orig, new):
        self.orig = orig
        self.new = new

    def __call__(self, *a, **kw):
        return self.new(self.orig, *a, **kw)
