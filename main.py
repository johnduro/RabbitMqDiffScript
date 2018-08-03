
# encoding=utf8

import argparse
import requests
import json
import itertools
import sys
import pprint

HOST = 'http://localhost:15672'
USERNAME = 'guest'
PASSWORD = 'guest'

class _Config:
    def __init__(self, args):
        if args.files is None:
            raise Exception('You must provide a new configuration file to read, argument "-f" or "--file"')
        self.files = args.files
        self.host = args.host[0] if args.host is not None else HOST
        self.username = args.username[0] if args.username is not None else USERNAME
        self.password = args.password[0] if args.password is not None else PASSWORD
        self.dryRun = args.dry_run
        self.silent = args.silent
        self.force = args.force



class _RabbitMqConfiguration():
    def __init__(self, rmqConfiguration):
        if (rmqConfiguration['queues'] is None
             or rmqConfiguration['exchanges'] is None
             or rmqConfiguration['bindings'] is None):
            raise Exception('For rabbitMq configuration keys "queues", "exchanges" and "bindings" must be set')
        self.queues = rmqConfiguration['queues']
        self.exchanges = rmqConfiguration['exchanges']
        self.bindings = rmqConfiguration['bindings']



class _RabbitMqModification():
    def __init__(self):
        self.queuesAdd = []
        self.queuesDelete = []
        self.exchangesAdd = []
        self.exchangesDelete = []
        self.bindingsAdd = []
        self.bindingsDelete = []


    def extractArguments(self, arguments):
        argumentList = []
        for key, value in arguments.items():
            argumentList.append(
                key + ':' + value
            )

        return ' ; '.join(argumentList)


    def extractQueuesNames(self, queues):
        names = []
        for queue in queues:
            names.append(
                ' | '.join([queue['vhost'], queue['name'], self.extractArguments(queue['arguments'])])
            )

        return names


    def extractExchangesNames(self, exchanges):
        names = []
        for exchange in exchanges:
            names.append(
                ' | '.join([exchange['vhost'], exchange['name'], exchange['type'], self.extractArguments(exchange['arguments'])])
            )

        return names


    def extractBindingsNames(self, bindings):
        names = []
        for binding in bindings:
            names.append(
                ' | '.join([binding['vhost'], binding['source'] + ' --> ' + binding['destination'], binding['destination_type'], binding['routing_key'], self.extractArguments(binding['arguments'])])
            )

        return names


    def __str__(self):
        queuesToAddNames = self.extractQueuesNames(self.queuesAdd)
        queuesToDeleteNames = self.extractQueuesNames(self.queuesDelete)
        exchangesToAddNames = self.extractExchangesNames(self.exchangesAdd)
        exchangesToDeleteNames = self.extractExchangesNames(self.exchangesDelete)
        bindingsToAddNames = self.extractBindingsNames(self.bindingsAdd)
        bindingsToDeleteNames = self.extractBindingsNames(self.bindingsDelete)

        out = 'The following modifications will be applied:\n\n'
        out += '   Exchanges ADDED:\n     '
        out += '\n     '.join(exchangesToAddNames)
        out += '\n   Exchanges DELETED:\n     '
        out += '\n     '.join(exchangesToDeleteNames)
        out += '\n   Queues ADDED:\n     '
        out += '\n     '.join(queuesToAddNames)
        out += '\n   Queues DELETED:\n     '
        out += '\n     '.join(queuesToDeleteNames)
        out += '\n   Bindings ADDED:\n     '
        out += '\n     '.join(bindingsToAddNames)
        out += '\n   Bindings DELETED:\n     '
        out += '\n     '.join(bindingsToDeleteNames)

        return out


    def queuesToAdd(self, queues):
        self.queuesAdd = queues

    def queuesToDelete(self, queues):
        self.queuesDelete = queues

    def exchangesToAdd(self, exchanges):
        self.exchangesAdd = exchanges

    def exchangesToDelete(self, exchanges):
        self.exchangesDelete = exchanges

    def bindingsToAdd(self, bindings):
        self.bindingsAdd = bindings

    def bindingsToDelete(self, bindings):
        self.bindingsDelete = bindings



class _RabbitMqApi:
    def __init__(self, config):
        self.host = config.host + '/api/'
        self.username = config.username
        self.password = config.password


    def getCurrentConfiguration(self):
        response = requests.get(self.host + 'definitions', auth=(self.username, self.password))

        return response.json()

    def getBindings(self):
        response = requests.get(self.host + 'bindings', auth=(self.username, self.password))

        return response.json()

    def getVhost(self, vhost):
        return vhost.replace('/', '%2f')

    def removeExchange(self, exchange):
        requests.delete(
            self.host + 'exchanges/' + self.getVhost(exchange['vhost']) + '/' + exchange['name'],
            auth=(self.username, self.password)
        )

    def removeQueue(self, queue):
        requests.delete(
            self.host + 'queues/' + self.getVhost(queue['vhost']) + '/' + queue['name'],
            auth=(self.username, self.password)
        )

    def removeExchangeToQueueBinding(self, binding, props):
        requests.delete(
            self.host + 'bindings/' + self.getVhost(binding['vhost']) + '/e/' + binding['source'] + '/q/' + binding['destination'] + '/' + props,
            auth=(self.username, self.password)
        )

    def removeExchangeToExchangeBinding(self, binding, props):
        requests.delete(
            self.host + 'bindings/' + self.getVhost(binding['vhost']) + '/e/' + binding['source'] + '/e/' + binding['destination'] + '/' + props,
            auth=(self.username, self.password)
        )

    def removeBinding(self, binding, props):
        if binding['destination_type'] == 'queue':
            self.removeExchangeToQueueBinding(binding, props)
        elif binding['destination_type'] == 'exchange':
            self.removeExchangeToExchangeBinding(binding, props)

    def addExchange(self, exchange):
        requests.put(
            self.host + 'exchanges/' + self.getVhost(exchange['vhost']) + '/' + exchange['name'],
            json=exchange,
            auth=(self.username, self.password)
        )

    def addQueue(self, queue):
        r = requests.put(
            self.host + 'queues/' + self.getVhost(queue['vhost']) + '/' + queue['name'],
            json=queue,
            auth=(self.username, self.password)
        )

    def addToQueueBinding(self, binding):
        requests.post(
            self.host + 'bindings/' + self.getVhost(binding['vhost']) + '/e/' + binding['source'] + '/q/' + binding['destination'],
            json=binding,
            auth=(self.username, self.password)
        )

    def addToExchangeBinding(self, binding):
        requests.post(
            self.host + 'bindings/' + self.getVhost(binding['vhost']) + '/e/' + binding['source'] + '/e/' + binding['destination'],
            json=binding,
            auth=(self.username, self.password)
        )

    def addBinding(self, binding):
        if binding['destination_type'] == 'queue':
            self.addToQueueBinding(binding)
        elif binding['destination_type'] == 'exchange':
            self.addToExchangeBinding(binding)



class _RabbitMqModificator:
    def __init__(self, api, modifications):
        self.api = api
        self.modifications = modifications
        self.bindingsList = api.getBindings()


    def getProps(self, binding):
        for sb in self.bindingsList:
            if (binding['arguments'] == sb['arguments']
                 and binding['destination'] == sb['destination']
                 and binding['destination_type'] == sb['destination_type']
                 and binding['routing_key'] == sb['routing_key']
                 and binding['source'] == sb['source']
                 and binding['vhost'] == sb['vhost']):
                return sb['properties_key']

        raise Exception('Could not find "properties_key" for binding:\n' + pprint.pformat(binding, indent=4))

    def apply(self):
        for exchange in self.modifications.exchangesDelete:
            self.api.removeExchange(exchange)
        for queue in self.modifications.queuesDelete:
            self.api.removeQueue(queue)
        for binding in self.modifications.bindingsDelete:
            self.api.removeBinding(binding, self.getProps(binding))

        for exchange in self.modifications.exchangesAdd:
            self.api.addExchange(exchange)
        for queue in self.modifications.queuesAdd:
            self.api.addQueue(queue)
        for binding in self.modifications.bindingsAdd:
            self.api.addBinding(binding)



def getParsedArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', help='path(s) to the new(s) configuration file(s)', nargs='+')
    parser.add_argument('-a', '--host', help='the rabbitMq host, default: "%s"' % HOST, nargs=1)
    parser.add_argument('-u', '--username', help='username for rabbitMq, default: "%s"' % USERNAME, nargs=1)
    parser.add_argument('-p', '--password', help='password for rabbitMq, default: "%s"' % PASSWORD, nargs=1)
    parser.add_argument('--dry-run', help='print the modifications and exit', action='store_true')
    parser.add_argument('--silent', help='do not print anything', action='store_true')
    parser.add_argument('--force', help='do not ask for confirmation', action='store_true')

    return parser.parse_args()



def mergeConfigurations(configurationOne, configurationTwo):
    keys = set(configurationOne).union(configurationTwo)
    emptyList = []

    return dict((k, configurationOne.get(k, emptyList) + configurationTwo.get(k, emptyList)) for k in keys)


def getNextConfiguration(config):
    allConfigurations = {}
    for confFile in config.files:
        with open(confFile) as nextConfigurationFile:
            newConfiguration = json.load(nextConfigurationFile)
        if newConfiguration is None:
            raise Exception('Could not load next configuration file')
        allConfigurations = mergeConfigurations(allConfigurations, newConfiguration)

    return _RabbitMqConfiguration(allConfigurations)



def getNewFromConfiguration(oldConfiguration, newConfiguration):
    return list(itertools.filterfalse(lambda x: x in oldConfiguration, newConfiguration))



def findDifferences(currentConfiguration, nextConfiguration):
    modifications = _RabbitMqModification()


    modifications.exchangesToAdd(
        getNewFromConfiguration(currentConfiguration.exchanges, nextConfiguration.exchanges)
    )
    modifications.exchangesToDelete(
        getNewFromConfiguration(nextConfiguration.exchanges, currentConfiguration.exchanges)
    )

    modifications.queuesToAdd(
        getNewFromConfiguration(currentConfiguration.queues, nextConfiguration.queues)
    )
    modifications.queuesToDelete(
        getNewFromConfiguration(nextConfiguration.queues, currentConfiguration.queues)
    )

    modifications.bindingsToAdd(
        getNewFromConfiguration(currentConfiguration.bindings, nextConfiguration.bindings)
    )
    modifications.bindingsToDelete(
        getNewFromConfiguration(nextConfiguration.bindings, currentConfiguration.bindings)
    )

    return modifications


def queryYesNo(question):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}

    while True:
        sys.stdout.write(question + " [y/N] ")
        choice = input().lower()
        if choice == '':
            return False
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

def main():

    try:
        config = _Config(getParsedArguments())

        api = _RabbitMqApi(config)

        currentConfiguration = _RabbitMqConfiguration(api.getCurrentConfiguration())
        nextConfiguration = getNextConfiguration(config)

        modifications = findDifferences(currentConfiguration, nextConfiguration)

        if not config.silent:
            print(modifications)

        if config.dryRun:
            print('dry-run : exiting')
            exit()

        if not config.force:
            if not queryYesNo('Do you want to apply theses modifications ?'):
                print('exiting...')
                exit()

        modificator = _RabbitMqModificator(api, modifications)
        modificator.apply()

    except Exception as exp:
        print("An error occured:")
        print("     %s" % ' | '.join(str(x) for x in exp.args))

main()
