import csv,datetime,pdb
from mis.models import Terminal

import logging
_LOG = logging.getLogger('mis_error')

def csv2terminal(file):
    #pdb.set_trace()
    count = 0
    reader = csv.reader(file)
    for r in reader:
        try:
            Terminal.objects.create(terminalid=r[0],
                                    psamid=r[1],
                                    group_id=r[2],
                                    tck=u'0EA08C852B9653F76DB4A90612850CBD',
                                    used=1,
                                    state=0,
                                    producer='0001',
                                    produce_date=datetime.datetime.now(),
                                    model='0001')
            count += 1
        except Exception,ex:
            _LOG.exception(ex)

    return count

def csv_readlines(file):
    try:
        reader = csv.reader(file)
    except:
        reader = None

    return reader

