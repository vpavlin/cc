#!/usr/lib/python

import os, sys
import json
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import logging
import docker
from contextlib import contextmanager
import signal
import re
import subprocess

logging.basicConfig()
logger = logging.getLogger('ImageTests')
format = logging.Formatter("%(levelname)s: %(message)s")
logger.setLevel(logging.INFO)


def fail(msg):
    logger.error(msg)
    sys.exit(1)

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):  # From http://stackoverflow.com/a/601168/1576438
    def signal_handler(signum, frame):
        raise TimeoutException('Timed out!')
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


class ImageTests():
    config = {}
    dockerfile_builds = {}
    driver_ext = ( '.py', '.pyo', '.pyc' )
    
    def __init__(self, config, debug=False):
        '''
        Constructor
        '''

        if debug:
            logger.setLevel(logging.DEBUG)

        if config and os.path.exists(config):
            with open(config) as json_fp:
                self.config=json.load(json_fp)
        elif config:
            self.config=json.loads(config)
        else:
            fail("Missing config!")                   

        self.client = docker.Client(timeout=3600)
        self.load_test_drivers(os.path.join(os.path.dirname(__file__), "tests"))
 
    def __del__(self):
        '''
        Clean after yourself
        '''

    def load_test_drivers(self, drivers_dir):
        logger.debug(drivers_dir)
        for driver in os.listdir(drivers_dir):
            if driver.endswith(self.driver_ext) and not driver.startswith('__init__.py'):
                logger.debug("Loading %s" % driver)


    def create_binds(self, volumes):
        binds={}
        for vol in volumes:
            bind=vol.split(":")
            binds[bind[0]]={}
            binds[bind[0]]['bind']=bind[1]
            if len(bind) == 3:
                binds[bind[0]]['ro'] = True
            else:
                binds[bind[0]]['ro'] = False

        return binds

    def run_check_grep(self, what, where):
        grep_result=[]
        if type(what) is list:
            for w in what:
                m = map(lambda x: x.strip("\r"), re.findall(".*%s.*" % w, where))
                logger.info("Looking for '%s', found %s" % (w, m))
                grep_result += m
        else:
            grep_result = map(lambda x: x.strip("\r"), re.findall(".*%s.*" % what, where))
            logger.info("Looking for '%s', found %s" % (what, grep_result))

        return grep_result

    def run_check(self, output, check_config):
        logger.debug(check_config)
        regex=""
        
        if "grep" in check_config:
            result = self.run_check_grep(check_config['grep'], output)
            logger.debug("Result: %s" % result)
        if "empty_output" in check_config and check_config['empty_output']:
            logger.debug(output)
            if len(output) == 0:
                logger.info("Ok")

    def run_test_path(self, image, test_config):
        logger.info("Running %s" % test_config['path'])

        args=[]
        if 'args' in test_config:
            args=test_config['args']
        
        pargs = [test_config['path'], image]
        logger.debug(pargs + args)
        out, err = subprocess.Popen(pargs + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()


        if 'output' in test_config:
            with open(test_config['output'], "w") as fp:
                fp.write("STDOUT: %s" % out)
                fp.write("STDERR: %s" % err)
                logger.debug("STDOUT: %s" % out)
                logger.debug("STDERR: %s" % err)
        else:
            logger.info("STDOUT: %s" % out)
            logger.info("STDERR: %s" % err)


    def run_test(self, image, test_config):
        volumes=None
        binds=None
        env=None
        run=None
        timeout=2

        logger.debug(test_config)


        if 'output' in test_config:
            print("Test: %s > %s" % (test_config['name'], test_config['output']))
        else:
            print("Test: %s > STDOUT" % test_config['name'])
        
        if 'image' in test_config:
            image=test_config['image']
        
        if 'path' in test_config:
            self.run_test_path(image, test_config)
            return

        if 'volumes' in test_config:
            volumes=map(lambda vol: vol.split(":")[0], test_config['volumes'])
            binds=self.create_binds(test_config['volumes'])
            logger.debug("Volumes: %s -> %s" % (test_config['volumes'], list(volumes)))
            logger.debug("Binds: %s" % (binds))
        
        if 'env' in test_config:
            env=test_config['env']

        if 'timeout' in test_config:
            timeout=test_config['timeout']
        
        if 'run' in test_config:
            run=test_config['run']

        container = self.client.create_container(image=image, command=run, tty=True, volumes=volumes, environment=env)
        cont_id = container.get("Id")
        logger.debug(container)

        
        response=self.client.start(cont_id, binds=binds)


        try:
            with time_limit(timeout):
                logger.debug("Waiting (for %ss)" % timeout)
                self.client.wait(cont_id)
        except TimeoutException:
            pass
        
        self.client.kill(cont_id)
        

        logger.debug(response)
        if 'output' in test_config:
            with open(test_config['output'], "w") as fp:
                fp.write(self.client.logs(cont_id))
                logger.debug("Logs: %s" % self.client.logs(cont_id))
        else:
            logger.info("Logs: %s" % self.client.logs(cont_id))

        if 'check' in test_config:
            self.run_check(self.client.logs(cont_id), test_config['check'])

        self.client.remove_container(cont_id)

    def run_dockerfile_rm(self, test_config):
        if not os.path.exists(os.path.join(test_config['dockerfile'], "Dockerfile")) or not test_config['name'] in self.dockerfile_builds:
            return

        self.client.remove_image(image=test_config['name'])
        logger.info("Image %s removed" % test_config['name'])

    def test(self):
        for test in self.config['test']['tests']:
            if 'dockerfile' in test:
                self.run_dockerfile_test(test)
            else:
                self.run_test(self.config['test']['image'], test)

        logger.debug(self.dockerfile_builds)

        for test in self.config['test']['tests']:
            if 'dockerfile' in test:
                self.run_dockerfile_rm(test)

if __name__ == "__main__":
    parser = ArgumentParser(description='Test suite for Docker Base images', formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("-c", "--config", dest="config", help="JSON configuration file")
    parser.add_argument("-d", "--debug", dest="debug", default=False, action='store_true', help="Enable debug mode")

    
    args = parser.parse_args()
    DEBUG = args.debug

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    it = ImageTests(args.config)
    it.test()
    
    logger.debug("Done.")
    sys.exit(0)
