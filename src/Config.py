
import configparser

from src.Excludes import _RmqExcludeExchangeOrQueue
from src.Excludes import _RmqExcludeBindings;

HOST = 'http://localhost:15672'
USERNAME = 'guest'
PASSWORD = 'guest'

class _Config:
    def __init__(self, args):
        if args.files is None and args.conf is None:
            raise Exception('You must provide a new rabbitmq configuration file to read, argument "-f" or "--file" or a configuration file for the script "-c" or "--conf"')

        self.setDefaultValues()

        if args.conf is not None:
            self.setConfigFromConfigFile(args.conf[0])

        self.setValuesFromCommandLine(args)


    def setValuesFromCommandLine(self, args):
        self.files = args.files if args.files is not None else self.files
        self.host = args.host[0] if args.host is not None else self.host
        self.username = args.username[0] if args.username is not None else self.username
        self.password = args.password[0] if args.password is not None else self.password
        self.dryRun = args.dry_run
        self.silent = args.silent
        self.force = args.force


    def setDefaultValues(self):
        self.host = HOST
        self.username = USERNAME
        self.password = PASSWORD
        self.excludedExchanges = _RmqExcludeExchangeOrQueue([])
        self.excludedQueues = _RmqExcludeExchangeOrQueue([])
        self.excludedBindings = _RmqExcludeBindings([])


    def getConfList(self, rawList):
        return list(filter(None, rawList.split('\n')))


    def setConfigFromConfigFile(self, configPath):
        configuration = self.getConfiguration(configPath)

        if 'configuration' in configuration:
            self.setConfigurationKey(configuration['configuration'])

        if 'exclude-exchanges' in configuration:
            self.excludedExchanges = _RmqExcludeExchangeOrQueue(configuration['exclude-exchanges'])
        if 'exclude-queues' in configuration:
            self.excludedQueues = _RmqExcludeExchangeOrQueue(configuration['exclude-queues'])
        if 'exclude-bindings' in configuration:
            self.excludedBindings = _RmqExcludeBindings(configuration['exclude-bindings'])


    def setConfigurationKey(self, configuration):
        if 'files' in configuration:
            self.files = self.getConfList(configuration['files'])
        if 'host' in configuration:
            self.host = configuration['host']
        if 'username'in configuration:
            self.username = configuration['username']
        if 'password' in configuration:
            self.password = configuration['password']


    def getConfiguration(self, configPath):
        with open(configPath) as configurationFile:
            parser = configparser.ConfigParser()
            parser.read_file(configurationFile)
            return parser

        raise Exception('Could not open configuration file at ' + configPath)
