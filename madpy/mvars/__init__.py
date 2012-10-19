"""
Variable types for MAD
"""
import os
import shelve
import sys

import sqlite3

from madpy.conf import conf
from madpy.logger import *
from madpy.util import *

def mad_string(md, k, v):
    #core value - just return val as a string
    md[k] = str(v)

def mad_set_string(md, k, v):
    #core value - just return val as a string
    if not md.has_key(k):
        md[k] = []
    md[k].append(str(v))
    md[k] = list(set(md[k]))

def mad_integer(md, k, v):
    try:
        md.update({k: int(v)})
    except:
        exerr("%s is not an integer" % val)

def mad_integer(md, k, v):
    try:
        md.update({k: int(v)})
    except:
        exerr("%s is not an integer" % val)

def _ontology_item_finder(taxname, val, endpoints=[0]):
    """
    Generic ontology lookup term
    """
    
    G.debug("starting ontology lookup in %s with value %s" % (taxname, val))
    parchild = {}
    idnames = {}
    partials = []

    dbconnection = sqlite3.connect(os.path.join(get_conf_dir(), taxname + '.sqlite3'))
    c = dbconnection.cursor()

    sql = "SELECT * FROM item WHERE name = ?"
    c.execute(sql, [val])
    
    G.debug("SQL %s with %s" % (sql, str(val)))
    result =  c.fetchall()
    if len(result) > 1:
        G.critical("Duplicate name in the ontology - no clue what to do")
        G.critical("name: %s" % val)
        G.critical("ontology: %s" % taxname)


    if len(result) == 0:
        #print a few suggestions
        G.warning("Cannot find %s in %s" % (val, taxname))
        tryagain = val
        res2 = []
        firstTry = True
        while (firstTry) or (len(tryagain) > 3 and len(res2) == 0):
            firstTry = False
            c.execute('SELECT * FROM item WHERE name LIKE "%s%%" LIMIT 9' % tryagain)
            res2 = c.fetchall()

            c.execute('SELECT * FROM item WHERE name LIKE "%%%s%%" LIMIT 18' % tryagain)
            res2.extend(c.fetchall())
            tryagain = tryagain[:-3]

        if not res2:
            G.warning("No clue what you might have meant")
            sys.exit(-1)

        if len(res2) == 18:
            print ('Maybe you meant (probably not a complete list!):')
        else:
            print ('Maybe you meant:')
        for r in res2:
            print " - %s (%s)" % (r[1], r[0])
        sys.exit(-1)

    ontology_id = result[0][0].encode('ascii')
    parents = []
    
    def _find_parent(cid, endpoints):
        endpoints = map(unicode, endpoints)
        rv = []
        c.execute('SELECT parent FROM link WHERE child=?', [cid])
        parents = [x[0] for x in c.fetchall() if x[0] not in endpoints]
        rv.extend(parents)
        for p in parents:
            rv.extend(_find_parent(p, endpoints))
        return rv
    
    parent_ids =  _find_parent(ontology_id, endpoints)
    c.execute('select name from item where id IN ("%s")' % '","'.join(map(str,parent_ids)))

    parent_names = [x[0].encode('ascii') for x in c.fetchall()]
    parent_ids = [x.encode('ascii') for x in parent_ids]
    return ontology_id, parent_ids, parent_names

def mad_taxonomy_name(md, k, v):
    #find name in taxonomy file
    G.debug("starting taxonomy lookup for %s=%s" % (k,v))
    _result =  _ontology_item_finder('taxonomy', v, endpoints=['0', '1'])

    try:
        hitid, parent_ids, parent_names = _result
    except ValueError:
        exerr("unexpected return from the taxonomy %s" % _result)
    
    rv = {'Organism' : [v] + parent_names,
          'NcbiTaxonomyId' : [hitid] + parent_ids}
    md.update(rv)

def mad_plant_ontology_name(md, k, v):
    #find name in plant_ontology file

    _result = _ontology_item_finder('plant_ontology', v)
    try:
        hitid, parent_ids, parent_names = _result
    except ValueError:
        exerr("unexpected return from the taxonomy %s" % _result)
    rv = {'PlantTissue' : [v] + parent_names,
          'plantOntologyId' : [hitid] + parent_ids}
    md.update(rv)

def mad_edam_format_name(md, k, v):
    #find name in plant_ontology file

    _result = _ontology_item_finder('edam_format', v, endpoints=['EDAM_format:1915'])
    try:
        hitid, parent_ids, parent_names = _result
    except ValueError:
        exerr("unexpected return from the taxonomy %s" % _result)
    rv = {'DataFormat' : [v] + parent_names,
          'EdamDataFormatId' : [hitid] + parent_ids}
    md.update(rv)

def mad_edam_coredata(md, k, v):
    #find name in plant_ontology file

    G.debug("checking edam coredata %s %s" % (k,v)) 
    _result = _ontology_item_finder('edam_coredata', v, endpoints=['EDAM_data:3031'])
    G.debug("check result %s" % str(_result)[:50])
    try:
        hitid, parent_ids, parent_names = _result
    except ValueError:
        exerr("unexpected return from the taxonomy %s" % _result)
    rv = {'DataType' : [v] + parent_names,
          'EdamDataTypeId' : [hitid] + parent_ids}
    md.update(rv)

def update(md, k, v):
    G.debug("updating %s / %s" % (k, v))

    if k in conf.datatypes:
        dt = conf.datatypes[k].get('mad_data_type', 'string')
    else:
        dt = "string"
        
    G.debug("%s=%s is of datatype %s" % (k, v, dt))
    return eval("mad_%s(md, k, v)" % dt)
    
