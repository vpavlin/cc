import docker
import logging
import os, sys




class dockerfile_test():
    client=None
    test_config=None
    def __init__(self, docker_client, test_config):
        self.client=docker_client
        self.test_config=test_config

    def run(self):
        self.run_dockerfile_test(self, self.test_config)

    def run_dockerfile_test(self, test_config):
        logger.debug(test_config['dockerfile'])
        if not os.path.exists(os.path.join(test_config['dockerfile'], "Dockerfile")):
            logger.error("Dockerfile not found in dockerfile_path")
            return

        response = [line for line in self.client.build(path=test_config['dockerfile'], rm=True, timeout=3600, nocache=True, tag=test_config['name'])]
        
        if 'error' in response[-1]:
            logger.error(json.loads(response[-1])['error'])
        else:
            logger.info("Build of %s finnished" % test_config['name'])
            self.dockerfile_builds[test_config['name']]=json.loads(response[-1])['stream']

        logger.debug(response)
