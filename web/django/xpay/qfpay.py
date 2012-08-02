#coding = utf-8
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'qf_core',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'TEST_CHARSET': 'utf8',
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    },
    'mis':{
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'qf_mis',                      # Or path to database file if using sqlite3.
        'TEST_CHARSET': 'utf8',
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',
        #'OPTIONS': {'init_command': 'SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED'},
    },
    'core':{
        'ENGINE':'django.db.backends.mysql',
        'TEST_CHARSET': 'utf8',
        'NAME':'qf_core',
        'USER':'root',
	    'PASSWORD':'',
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    },
    'trade':{
        'ENGINE':'django.db.backends.mysql',
        'TEST_CHARSET': 'utf8',
        'NAME':'qf_trade',
        'USER':'root',
	    'PASSWORD':'',
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    },

    'risk':{
        'ENGINE':'django.db.backends.mysql',
        'TEST_CHARSET': 'utf8',
        'NAME':'qf_risk',
        'USER':'root',
	    'PASSWORD':'',
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    },
    'settle':{
        'ENGINE':'django.db.backends.mysql',
        'TEST_CHARSET': 'utf8',
        'NAME':'qf_settle',
        'USER':'root',
	    'PASSWORD':'',
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
    }

}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/home/qfpay/storage/userprofile/' 


#The ip list of the channel clients
IP_LIST = ['211.101.142.242','123.233.240.102','211.101.142.243','123.233.246.158','172.100.100.23']

#Our domain, this is for alipay call back.
QF_DOMAIN = 'http://mis.dev.qfpay.net'
MY_QFPAY_COM_URL = 'http://dev.qfpay.net:9701'

#Location of storing user's bills
BILLS_LOCATION = '/home/wkz/bills/'

#Location of the settling file
SETTLE_DIR= '/home/wkz/settle/'

MIS_NOTIFY = {
    'MOBILE':[15810062484,],
    'MAIL' :['zhanghui@qfpay.net',],
}
