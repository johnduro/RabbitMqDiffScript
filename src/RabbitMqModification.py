
import itertools
import re

class _RabbitMqModification():
    def __init__(self, config, currentConfiguration, nextConfiguration):
        self.config = config
        self.exchangesAdd = []
        self.exchangesDelete = []
        self.queuesAdd = []
        self.queuesDelete = []
        self.bindingsAdd = []
        self.bindingsDelete = []

        self.findDifferences(currentConfiguration, nextConfiguration)


    def checkExchangeOrQueue(self, excluded, toCheck):
        for p in excluded.vhost:
            if re.search(p, toCheck['vhost']) is not None:
                return False
        for p in excluded.names:
            if re.search(p, toCheck['name']) is not None:
                return False

        return True


    def filterExchangesOrQueues(self, excluded, toCheckList):
        return list(
            filter(
                lambda x: self.checkExchangeOrQueue(excluded, x),
                toCheckList
            )
        )


    def checkBinding(self, binding):
        excluded = self.config.excludedBindings

        for p in excluded.vhost:
            if re.search(p, binding['vhost']) is not None:
                return False
        for p in excluded.source:
            if re.search(p, binding['source']) is not None:
                return False
        for p in excluded.destination:
            if re.search(p, binding['destination']) is not None:
                return False
        for p in excluded.routingKeys:
            if re.search(p, binding['routing_key']) is not None:
                return False
        for p in excluded.destinationType:
            if re.search(p, binding['destination_type']) is not None:
                return False
        for combo in excluded.sourceDestination:
            [source, destination] = combo.split(':')
            if (re.search(source, binding['source']) is not None
               and re.search(destination, binding['destination']) is not None) :
                return False

        return True


    def filterBindings(self, bindings):
        return list(
            filter(
                lambda x: self.checkBinding(x),
                bindings
            )
        )


    def findDifferences(self, currentConfiguration, nextConfiguration):
        self.exchangesAdd = self.filterExchangesOrQueues(
            self.config.excludedExchanges,
            self.getDeltaFromFirst(currentConfiguration.exchanges, nextConfiguration.exchanges)
        )
        self.exchangesDelete = self.filterExchangesOrQueues(
            self.config.excludedExchanges,
            self.getDeltaFromFirst(nextConfiguration.exchanges, currentConfiguration.exchanges)
        )

        self.queuesAdd = self.filterExchangesOrQueues(
            self.config.excludedQueues,
            self.getDeltaFromFirst(currentConfiguration.queues, nextConfiguration.queues)
        )
        self.queuesDelete = self.filterExchangesOrQueues(
            self.config.excludedQueues,
            self.getDeltaFromFirst(nextConfiguration.queues, currentConfiguration.queues)
        )

        self.bindingsAdd = self.filterBindings(
            self.getDeltaFromFirst(currentConfiguration.bindings, nextConfiguration.bindings)
        )
        self.bindingsDelete = self.filterBindings(
            self.getDeltaFromFirst(nextConfiguration.bindings, currentConfiguration.bindings)
        )


    def getDeltaFromFirst(self, oldConfiguration, newConfiguration):
        return list(itertools.filterfalse(lambda x: x in oldConfiguration, newConfiguration))


    def extractArguments(self, arguments):
        argumentList = []
        for key, value in arguments.items():
            argumentList.append(
                str(key) + ':' + str(value)
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
