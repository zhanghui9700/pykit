PRJDIR=`pwd`
PIDFILE="$PRJDIR/web.pid"
SOCKET="$PRJDIR/web.sock"

echo 'dir     :'$PRJDIR
echo 'pid file:'$PIDFILE
echo 'socket  :'$SOCKET

if [ -f $PIDFILE ]; then
kill `cat -- $PIDFILE`
rm -rf -- $PIDFILE
fi

/home/qfpay/python/bin/python ./manage.py runfcgi --settings=settings maxchildren=20  maxspare=10 minspare=4 method=prefork socket=$SOCKET pidfile=$PIDFILE
chmod 777 $SOCKET
