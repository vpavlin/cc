#!/usr/lib/python

import tarfile
import tempfile
import json
import os,sys
import logging
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import ConfigParser
import shutil
import json

ID_LENGTH = 64

DEBUG = 0


logging.basicConfig()
logger = logging.getLogger('BaseImageBuilder')
format = logging.Formatter("%(levelname)s: %(message)s")


def read_conf(conf_file):
    conf = ConfigParser.ConfigParser()
    conf.readfp(open(conf_file))
    return conf

def scrub_list(alist):
    """
    Take a comma-separate list, split on the commas, and scrub out any leading
    or trailing whitespace for each element.
    """
    return [p.strip() for p in alist.split(',')]


def touchopen(filename, *args, **kwargs):
    # Open the file in R/W and create if it doesn't exist. *Don't* pass O_TRUNC
    fd = os.open(filename, os.O_RDWR | os.O_CREAT, 0644)

    # Encapsulate the low-level file descriptor in a python file object
    return os.fdopen(fd, *args, **kwargs)

def fail(msg):
    logger.error(msg)
    sys.exit(1)


class BaseImageBuilder():
    config={}
    
    def __init__(self, config):
        '''
        Constructor
        '''

        if config and os.path.exists(config):
            self.config=json.load(config)
        elif config:
            self.config=json.loads(config)
        else:
            fail("Missing config!")                   
 
    def __del__(self):
        '''
        Clean after yourself
        '''

    def build(self):
        print(self.config)

if __name__ == "__main__":
    parser = ArgumentParser(description='Add "repositories" file to exported docker image', formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--config", dest="config", help="JSON configuration file")
    parser.add_argument("-d", "--debug", dest="debug", default=False, action='store_true', help="Enable debug mode")

    
    args = parser.parse_args()
    DEBUG = args.debug

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    bib = BaseImageBuilder(args.config)
    bib.build()
    
    logger.debug("Done.")
    sys.exit(0)

