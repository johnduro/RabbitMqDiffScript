
import json

class _RabbitMqConfiguration():
    def __init__(self, rmqConfiguration=None, configurationPaths=None):
        if configurationPaths is not None:
            rmqConfiguration = self.initFromConfigurationPaths(configurationPaths)

        if ('queues' not in rmqConfiguration
             or 'exchanges' not in rmqConfiguration
             or 'bindings' not in rmqConfiguration):
            raise Exception('For rabbitMq configuration keys "queues", "exchanges" and "bindings" must be set')

        self.queues = rmqConfiguration['queues']
        self.exchanges = rmqConfiguration['exchanges']
        self.bindings = rmqConfiguration['bindings']


    def initFromConfigurationPaths(self, configurationPaths):
        allConfigurations = {}
        for file in configurationPaths:
            with open(file) as nextConfigurationFile:
                newConfiguration = json.load(nextConfigurationFile)
            if newConfiguration is None:
                raise Exception('Could not load next configuration file')
            allConfigurations = self.mergeConfigurations(allConfigurations, newConfiguration)


        return allConfigurations


    def mergeConfigurations(self, configurationOne, configurationTwo):
        keys = set(configurationOne).union(configurationTwo)
        emptyList = []

        return dict((k, configurationOne.get(k, emptyList) + configurationTwo.get(k, emptyList)) for k in keys)
