#!/bin/sh

_DB_NAME="openPDC"
_DB_USER="polito"
_DB_PASS="pass"
_DB_URL="localhost"
_DB_PORT="3306"

if test ! -z $DB_NAME
then
    _DB_NAME=$DB_NAME
fi

if test ! -z $DB_USER
then
    _DB_USER=$DB_USER
fi

if test ! -z $DB_PASS
then
    _DB_PASS=$DB_PASS
fi

if test ! -z $DB_URL
then
    _DB_URL=$DB_URL
fi

if test ! -z $DB_PORT
then
    _DB_PORT=$DB_PORT
fi

if test ! -z $NODE_ID
then
    _NODE_ID=$NODE_ID
else
    echo "No Node Id was provided, generating a random one"
    _NODE_ID=$(cat /proc/sys/kernel/random/uuid)
fi

echo "Database url: ${_DB_URL}"
echo "Database port: ${_DB_PORT}"
echo "Database name: ${_DB_NAME}"
echo "Database user: ${_DB_USER}"
echo "Database password: ${_DB_PASS}"
echo "Node ID: ${_NODE_ID}"

# save default configuration, just in case
mv /opt/openPDC/openPDC.exe.config /opt/openPDC/openPDC.exe.config.old

# generate new configuration
sed 's/DB_URL/'"${_DB_URL}"'/;s/DB_PORT/'"${_DB_PORT}"'/;s/DB_NAME/'"${_DB_NAME}"'/;s/DB_USER/'"${_DB_USER}"'/;s/DB_PASS/'"${_DB_PASS}"'/;s/NODE_ID/'"${_NODE_ID}"'/' \
openPDC.exe.config.template > /opt/openPDC/openPDC.exe.config

echo "openPDC configuration generated in /opt/openPDC/openPDC.exe.config"

touch /opt/openPDC/ErrorLog.txt
touch /opt/openPDC/StatusLog.txt

# run openpdc in a detached terminal
screen -dmS openpdc mono /opt/openPDC/openPDC.exe -RunAsConsole

tail -f /opt/openPDC/StatusLog.txt | sed 's/^/status: /' &
tail -f /opt/openPDC/ErrorLog.txt | sed 's/^/error: /'
