from .version import VERSION as __version__

def real_path(path):
    import os
    return os.path.join(os.path.dirname(__file__), path)
