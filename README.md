# RabbitMq Diff Script


This python script allow you to maintain a rabbitMq configuration file and upload the modification to your rabbitMq server.

## Install

To install the needed dependecies do :

``` shell
$ pip install --requirement requirements.txt
```


## Usage

``` shell
$ python main.py --files path/to/rabbitmq/config/file.json [OPTIONS(s)]
```

or

``` shell
$ python main.py --conf path/to/script/config/file.json [OPTIONS(s)]
```

Running the script will prompt you with informations like this :

``` shell
The following modifications will be applied:

   Exchanges ADDED:
     / | exchange-to-add | topic |
   Exchanges DELETED:
	 / | exchange-to-delete | fanout | key:value
   Queues ADDED:
	 / | queue-to-add | x-dead-letter-routing-key:routing.key ; x-dead-letter-exchange:dl-exchange
   Queues DELETED:
	 / | queue-to-delete | key:value
   Bindings ADDED:
	 / | exchange-to-add --> queue-to-add | queue |  |
   Bindings DELETED:
	/ | exchange-to-delete --> queue-to-delete | queue | # |
Do you want to apply theses modifications ? [y/N]
```

Typing `yes` / `y` will apply the modifications


## Arguments

 - `files` : the path(s) to the new configuration file(s)
 - `host` : the host of the server, by default `http://localhost:15672`
 - `username` : the username for the connection to rmq, by default `guest`
 - `password` : the password for the connection to rmq, by default `guest`
 - `dry-run` : print the detected modifications and exit
 - `silent` : do not print the modification
 - `force` : do not ask for confirmation before applying modifications
 - `conf` : the path of the script configuration file


## Script configuration file

If you want to save your settings for the script or exclude certain elements
you can use a configuration file like this :


```
[configuration]
host = https://host-to-rmq.com
username = guest
password = guest
files = path/to/rabbitmq/config/file.json
	  path/to/another/rabbitmq/config/file.json

[exclude-exchanges]
name = exchange.name
	 exchange.another.name
vhost = vhostName
	  anotherVhost

[exclude-queues]
name = queue.name
vhost = vhostName

[exclude-bindings]
vhost = vhostName
source = exchangeName
destination = queueOrExchangeName
source-destination = source:destination
routingkey = routing.\#
destination_type = queue
```

All keys but `host`, `username` and `password` can take a list of values separated by `\n`.

The sections `exclude-exchanges`, `exclude-queues` and `exclude-bindings` are rule to remove
certain element from all modifications.
Notes that all rules inside a section are applied together.
In the exclude sections you can use regex instead of full values.


### Remark
Command line arguments can overload the values set in the configuration file.

Remember that you must set `files` in configuration file or in command line arguments.
