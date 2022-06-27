#!/bin/bash

NAME="grpcStartupScript"
DAEMON=/home/lvuser/natinst/bin/ni_grpc_device_server
ARGS="/home/lvuser/natinst/bin/server_config.json"
USER=admin
PIDFILE=/var/run/ni_grpc_device_server.pid

do_start(){
	/sbin/start-stop-daemon --start --pidfile $PIDFILE \
	--make-pidfile --backgroun \
	--chuid $USER --exec $DAEMON $ARGS
}

do_stop(){
	/sbin/start-stop-daemon --stop --pidfile $PIDFILE --verbose
}

case "$1" in
	start)
		echo "Starting $NAME"
		do_start
		;;
	stop)
		echo "Stopping $NAME"
		do_stop
		;;
	restart)
		echo "Restarting $NAME"
		do_stop
		do_start
		;;
	*)
		echo "Usage: $0 (start|stop|restart)
		exit 1
		;;
	esac

	exit 0
	