
# encoding=utf8

import argparse
import sys
import pprint

from src.Config import _Config
from src.RabbitMqConfiguration import _RabbitMqConfiguration
from src.RabbitMqModification import _RabbitMqModification
from src.RabbitMqApi import _RabbitMqApi
from src.RabbitMqModificator import _RabbitMqModificator

#Constant
import src.Config as default

def getParsedArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--files', help='path(s) to the new(s) configuration file(s)', nargs='+')
    parser.add_argument('-c', '--conf', help='path to the script configuration file', nargs=1)
    parser.add_argument('-a', '--host', help='the rabbitMq host, default: "%s"' % default.HOST, nargs=1)
    parser.add_argument('-u', '--username', help='username for rabbitMq, default: "%s"' % default.USERNAME, nargs=1)
    parser.add_argument('-p', '--password', help='password for rabbitMq, default: "%s"' % default.PASSWORD, nargs=1)
    parser.add_argument('--dry-run', help='print the modifications and exit', action='store_true')
    parser.add_argument('--silent', help='do not print anything', action='store_true')
    parser.add_argument('--force', help='do not ask for confirmation', action='store_true')

    return parser.parse_args()


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
        nextConfiguration = _RabbitMqConfiguration(configurationPaths=config.files)

        modifications = _RabbitMqModification(config, currentConfiguration, nextConfiguration)

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
