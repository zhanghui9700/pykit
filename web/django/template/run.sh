cd /opt/eayun/eayuncenter

.venv/bin/python eayuncenter/manage.py runfcgi maxchildren=2 maxspare=4 minspare=2 method=prefork socket=/var/log/eayuncenter.sock pidfile=/var/log/eayuncenter.pid

chmod 777 /var/log/eayuncenter.sock
