
import os
import Yaco

conf = Yaco.Yaco()

dconffile = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.default.yaml')
conffile = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')

def load():
    global conf
    if os.path.exists(dconffile):
        conf.load(dconffile)
    if os.path.exists(conffile):
        conf.load(conffile)

    dtfile = os.path.join(conf.general.config_dir, 'datatypes.yaml')
    if os.path.exists(dtfile):       
        dt = Yaco.Yaco()
        dt.load(dtfile)
        conf.datatypes = dt
    else:
        dtfile_default = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'datatypes.yaml')
        dt = Yaco.Yaco()
        dt.load(dtfile_default)
        conf.datatypes = dt 

def save():
    conf.save(conffile)

load()
