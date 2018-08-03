# RabbitMq Diff Script


This python script allow you to maintain a rabbitMq configuration file and upload the modification to your rabbitMq server.

## Usage

``` shell
$ python main.py --files path/to/conf/file.json [OPTIONS(s)]
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
