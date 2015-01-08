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
from src.test import ImageTests

ID_LENGTH = 64

DEBUG = 0


logging.basicConfig()
logger = logging.getLogger('DockerBaseImages')
format = logging.Formatter("%(levelname)s: %(message)s")





def touchopen(filename, *args, **kwargs):
    # Open the file in R/W and create if it doesn't exist. *Don't* pass O_TRUNC
    fd = os.open(filename, os.O_RDWR | os.O_CREAT, 0644)

    # Encapsulate the low-level file descriptor in a python file object
    return os.fdopen(fd, *args, **kwargs)

def fail(msg):
    logger.error(msg)
    sys.exit(1)


class ContainerChecker():
    config={}
    
    def __init__(self, config):
        '''
        Constructor
        '''

        if config and os.path.exists(config):
            with open(config) as json_fp:
                self.config=json.load(json_fp)
        elif config:
            self.config=json.loads(config)
        else:
            fail("Missing config!")                   
 
    def __del__(self):
        '''
        Clean after yourself
        '''

    def build(self):
        logger.debug(self.config)

    def test(self):
        t = ImageTests(args.config, debug=DEBUG)
        t.test()
        



if __name__ == "__main__":
    parser = ArgumentParser(description='Simple tool to build and test Docker base images', formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--config", dest="config", help="JSON configuration file")
    parser.add_argument("-d", "--debug", dest="debug", default=False, action='store_true', help="Enable debug mode")

    
    args = parser.parse_args()
    DEBUG = args.debug

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    cc = ContainerChecker(args.config)
    cc.build()
    cc.test()
    
    logger.debug("Done.")
    sys.exit(0)
