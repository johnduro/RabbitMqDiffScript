
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
