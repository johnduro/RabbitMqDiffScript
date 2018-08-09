
class _RmqExcludeExchangeOrQueue:
    def __init__(self, excludes):
        self.names = []
        self.vhost = []

        if 'name' in excludes:
            self.names = list(filter(None, excludes['name'].split('\n')))
        if 'vhost' in excludes:
            self.vhost = list(filter(None, excludes['vhost'].split('\n')))



class _RmqExcludeBindings:
    def __init__(self, excludes):
        self.vhost = []
        self.source = []
        self.destination = []
        self.sourceDestination = []
        self.routingKeys = []
        self.destinationType = []

        if 'vhost' in excludes:
            self.vhost = list(filter(None, excludes['vhost'].split('\n')))
        if 'source' in excludes:
            self.source = list(filter(None, excludes['source'].split('\n')))
        if 'destination' in excludes:
            self.destination = list(filter(None, excludes['destination'].split('\n')))
        if 'source-destination' in excludes:
            self.sourceDestination = list(filter(None, excludes['source-destination'].split('\n')))
        if 'routingkey' in excludes:
            self.routingKeys = list(filter(None, excludes['routingkey'].split('\n')))
        if 'destination_type' in excludes:
            self.destinationType = list(filter(None, excludes['destination_type'].split('\n')))
