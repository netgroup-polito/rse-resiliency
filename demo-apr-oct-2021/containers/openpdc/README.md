# openPDC

## Introduction
Alpine based docker image containing openPDC version 2.4 along with dependecies needed to use MySQL as DBMS for storing configuration and data.

## Configuration
The openPDC instance is configurable using environment variables descripted in the table below. Before running this container a MySQL instance should be running, and already initialised using the image [openpdc-init](../openpdc-init) or the script provided by the openPDC installation to create the database schema, database user and insert initial data.

Environment variables:
| env var | description |
|-|-|
| `DB_USER` | Database user that have granted access to `DB_NAME` [default is `polito`] |
| `DB_PASS` | Database user's password [default is an empty string] |
| `DB_NAME` | Database name tied to the openPDC instance [default is `openPDC`] |
| `DB_PORT` | Port associated to the MySQL instance [default is `3306`]|
| `DB_URL` | URL of the MySQL instance [default is `localhost`] |
| `NODE_ID` | Node id [default to a randomly generated uuid] |

## Troubleshooting

The [init.sh](./init.sh) script is used to configure the application and run it in a detached terminal using `screen` due to some logging issue arising in a kubernetes environment.

The console output is obtained tailing the logfiles (they correspond to the conosole log).

It is still possibile to access the detached screen instance where it's running the interactive console application running this command (inside a running container):
```
screen -r openpdc
```
To detach the screen instance without terminating the application use `Ctrl`+ `a` followed by `d`.