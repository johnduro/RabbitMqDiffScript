
import requests
import json

class _RabbitMqApi:
    def __init__(self, config):
        self.host = config.host + '/api/'
        self.username = config.username
        self.password = config.password


    def returnResponse(self, response):
        if response.status_code is not 200:
            raise Exception('An error occured while calling the api, response code ' + str(response.status_code) + ' and response : ' + str(response._content))

        return response.json()


    def getCurrentConfiguration(self):
        response = requests.get(self.host + 'definitions', auth=(self.username, self.password))

        return self.returnResponse(response)


    def getBindings(self):
        response = requests.get(self.host + 'bindings', auth=(self.username, self.password))

        return self.returnResponse(response)


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
        requests.put(
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
