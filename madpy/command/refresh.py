"""
Load & refresh ontologies
"""

import os
import re
import sqlite3
import urllib2
import tarfile

from madpy.conf import conf
from madpy.logger import G
from madpy.util import get_conf_dir, exer

DBS =['taxonomy', 'plant_ontology', 'edam_format', 'edam_coredata']

def hook_define_args(parser):
    """
    Set the arguments for 'set'
    """
    parser.add_argument('what', help='what db do you want refreshed? ' + 
                        'You can choose from "%s"' % '", "'.join(DBS))

def run(args):
    """ Run refresh """
    if args.what == 'all':
        for d in DBS:
            fnc = globals()['refresh_%s' % d]
            G.warning("Start refresh of %s" % d)
            fnc(args)
        return
    if not args.what in DBS:
        exer("Unknown database: %s" % args.what)

    fnc = globals()['refresh_%s' % args.what]
    fnc(args)
    


def _check_ontology_db(conn):
    G.info("Dropping old database")
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS  item")
    c.execute("DROP TABLE IF EXISTS link")
    c.execute("DROP INDEX IF EXISTS item_id")
    c.execute("DROP INDEX IF EXISTS item_name")
    c.execute("DROP INDEX IF EXISTS link_parent")
    c.execute("DROP INDEX IF EXISTS link_child")

    try:
        c.execute("SELECT * FROM item LIMIT 1")
        return
    except sqlite3.OperationalError, e:
        if not 'no such table' in str(e):
            raise

    G.info("Initalizing database")
    #create the table
    c.execute("""CREATE TABLE item (
                    id TEXT PRIMARY KEY,
                    name TEXT )
                    """)
    c.execute("""CREATE TABLE link (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent TEXT,
                    child TEXT)
                    """)
    c.execute("""CREATE INDEX item_id ON item ( id collate nocase)""")
    c.execute("""CREATE INDEX item_name ON item ( name collate nocase)""")
    c.execute("""CREATE INDEX link_parent ON link ( parent collate nocase)""")
    c.execute("""CREATE INDEX link_child ON link ( child collate nocase)""")

def _download_edam(uri):

    edam_raw_file = '/tmp/edam'

    if os.path.exists(edam_raw_file):
        G.warning("Found a copy at %s - using that" % edam_raw_file)
        return edam_raw_file

    G.info("Start download of EDAM")
    handle = urllib2.urlopen(uri)
    with open(edam_raw_file, 'wb') as F:
            F.write(handle.read())
    G.info("Downloaded EDAM")
    return edam_raw_file
        
def _obo_parser(ontology_id, handle):
    """
    Parse an OBO formatted ontology and yield triples of::

        Item_id,
        Item_name
        Parent_ids
    """

    G.info("Ontology id %s" % ontology_id)
    find_po_id = re.compile('^id: (' + ontology_id + ':.+)$')
    find_name = re.compile('^name: (.*)$')
    find_parent = re.compile('^is_a: (' + ontology_id + ':[0-9]+)')

    parents = []
    po_name = ""
    in_term_id = ""

    for i, line in enumerate(handle):

        found_po = find_po_id.match(line)
            
        if found_po:
            in_term_id = found_po.groups()[0]
            continue
        
        found_name = find_name.match(line)
        if (in_term_id != None) and found_name:            
            po_name = found_name.groups()[0]            
            
        found_parent = find_parent.match(line)        
        if (in_term_id != None) and found_parent:
            po_parent = found_parent.groups()[0]
            parents.append(po_parent)
            
        if '[Term]' in line: 
            if in_term_id != None:
                #yield an item!
                yield in_term_id, po_name, parents
            parents = []
            in_term_id = None
            po_name = ""
    if in_term_id != None:
        yield in_term_id, po_name, parents


def refresh_edam_format(args):
    """ Refresh the data format ontology - a part of Edam"""

    edam_file = _download_edam(conf.ontologies.url.edam_ontology)

    dbconn = sqlite3.connect(os.path.join(get_conf_dir(), 'edam_format.sqlite3'))
    c = dbconn.cursor()

    format_parent = conf.ontologies.edam_format.parent_id
    G.info("scanning edam ontology for anything that is a child of %s" % format_parent)
    _check_ontology_db(dbconn)
    itemdata = []
    linkdata = []
    with open(edam_file) as F:
        for poid, poname, popar in _obo_parser('EDAM_format', F):
            G.info('Found %s %s %s' % (poid, poname, str(popar)))
            itemdata.append([poid, poname])
            if popar:
                linkdata.extend(zip(popar, [poid] * len(popar)))         
    G.info("start saving %d items to the database" % len(itemdata))
    c.executemany("INSERT INTO item (id, name) VALUES (?, ?)", itemdata)
    dbconn.commit()
    G.info("start saving %d links to the database" % len(linkdata)) 
    c.executemany("INSERT INTO link (parent, child) VALUES (?, ?)", linkdata)
    dbconn.commit()

                  
def refresh_edam_coredata(args):
    """ Refresh the core data ontology - a part of Edam"""

    edam_file = _download_edam(conf.ontologies.url.edam_ontology)

    dbconn = sqlite3.connect(os.path.join(get_conf_dir(), 'edam_coredata.sqlite3'))
    c = dbconn.cursor()

    format_parent = conf.ontologies.edam_coredata.parent_id
    G.info("scanning edam ontology for anything that is a child of %s" % format_parent)
    _check_ontology_db(dbconn)
    itemdata = []
    linkdata = []
    with open(edam_file) as F:
        for poid, poname, popar in _obo_parser('EDAM_data', F):
            G.info('Found %s %s %s' % (poid, poname, str(popar)))
            itemdata.append([poid, poname])
            if popar:
                linkdata.extend(zip(popar, [poid] * len(popar)))         
    G.info("start saving %d items to the database" % len(itemdata))
    c.executemany("INSERT INTO item (id, name) VALUES (?, ?)", itemdata)
    dbconn.commit()
    G.info("start saving %d links to the database" % len(linkdata)) 
    c.executemany("INSERT INTO link (parent, child) VALUES (?, ?)", linkdata)
    dbconn.commit()

def refresh_plant_ontology(args):

    """ Run refresh plant ontology """
    POURL = conf.ontologies.url.plant_ontology
    response = urllib2.urlopen(POURL)
    in_term_id = None

    G.info("Start download of the plant ontology")    
    dbconnection = sqlite3.connect(os.path.join(get_conf_dir(), 'plant_ontology.sqlite3'))
    
    _check_ontology_db(dbconnection)
    c = dbconnection.cursor()

    itemdata = []
    linkdata = []
    for poid, poname, popar in _obo_parser('PO', response):
        itemdata.append([poid, poname])
        if popar:
            linkdata.extend(zip(popar, [poid] * len(popar)))
            
    G.info("start saving %d items to the database" % len(itemdata))
    c.executemany("INSERT INTO item (id, name) VALUES (?, ?)", itemdata)
    dbconnection.commit()
    G.info("start saving %d links to the database" % len(linkdata)) 
    c.executemany("INSERT INTO link (parent, child) VALUES (?, ?)", linkdata)
    dbconnection.commit()
           
def refresh_taxonomy(args):
    """
    Download & refresh the NCBI taxonomy database
    """
    
    locfile = '/tmp/mad_taxonomy.tar.gz'
    dbconnection = sqlite3.connect(os.path.join(get_conf_dir(), 'taxonomy.sqlite3'))
    
    _check_ontology_db(dbconnection)
    c = dbconnection.cursor()
    
    if not os.path.exists(locfile):
        server = 'ftp.ncbi.nih.gov'
        uri = "ftp://%s/%s" % (server, '/pub/taxonomy/taxdump.tar.gz')
        G.warning("start downloading ncbi taxonomy from %s" % server)
        ftp = urllib2.urlopen(uri)
        with open(locfile, 'wb') as F:
            F.write(ftp.read())
    else:
        G.warning("Found a copy of %s, using that" % locfile)

    G.warning("Processing taxonomy")
    
    T = tarfile.open(locfile)
    E = T.extractfile('nodes.dmp')
    outbase = get_conf_dir()

    parents = {}
    linkdata = []
    for i, line in enumerate(E):
        ls = line.split()
        tax, partax = int(ls[0]), int(ls[2])
        if parents.has_key(tax):
            raise Exception("Invalid tree structure in ncbi taxonomy")
        linkdata.append((partax, tax))
        parents[tax] = partax
    
    G.info("Found %d parent/child relations" % len(parents))
    F = T.extractfile('names.dmp')

    itemdata = []
    localfile = os.path.join(outbase, 'taxonomy')
    with open(localfile, 'w') as O:
        for i, line in enumerate(F):
            ls = [x.strip() for x in line.split('|')]
            #if ls[3] in ['in-part', 'misspelling']: continue
            if ls[3] != 'scientific name': continue
            itemdata.append((ls[0], ls[1]))
            O.write("%s\t%s\t%s\n" % (ls[0], parents.get(int(ls[0]), 0), ls[1]))
            
    G.warning("Done - saved %d entries" % i)
    G.info("start saving %d items to the database" % len(itemdata))
    c.executemany("INSERT INTO item (id, name) VALUES (?, ?)", itemdata)
    dbconnection.commit()
    G.info("start saving %d links to the database" % len(linkdata)) 
    c.executemany("INSERT INTO link (parent, child) VALUES (?, ?)", linkdata)
    dbconnection.commit()
