import datetime
import pymongo
from modelsGlobalConfig import *

@connection.register
class Requests(Document):
	__collection__ = 'requests'
	__database__ = DATABASE_HIRE
	structure = {
		'email' : unicode,
		'jobs' : [{	
					#'jid' : pymongo.objectid.ObjectId,
					'name': unicode,
					'needs': unicode, 
					'payment': unicode,
					'detail': unicode,
					'date':datetime.datetime,
					'timeframe': unicode,
					'sent': int}],
	}
	# ensuring unique emails
	indexes = [ 
		{ 
			'fields':['email'], 
			'unique':True, 
		} 
	]
	use_dot_notation = True 
	required_fields = ['email']
	default_values = {
        'jobs': [{
            'sent': 0,
        }],
    }
	
@connection.register
class Oliners(Document):
	__collection__ = 'oliners'
	__database__ = DATABASE_HIRE
	structure = {
		'email' : unicode,
		'date' : datetime.datetime
	}
	# ensuring unique emails
	indexes = [ 
		{ 
			'fields':['email'], 
			'unique':True, 
		} 
	]
	use_dot_notation = True 
	required_fields = ['email']
