# grabs this week's requests and formats them
# outputs date-emails.html
import sys
sys.path.append("../app")
from models import *

def getFormmatedJob(job, number, email):
	print job['name'].encode('utf-8')
	formmated = '<text style="color:#AB1A23;font-weight:bold;">#'+str(number)+' Submitted by </text>'+job['name'].encode('utf-8')+' ( <text style="color:#1144AA">'+email.encode('utf-8')+'</text> )<br/><text style="color:#F3961C;font-weight:bold;">Description</text><br/>'+job['detail'].encode('utf-8')+'<p><text style="color:#F3961C;font-weight:bold;">What needs to get done</text><br/>'+job['needs'].encode('utf-8')+'</p><p><text style="color:#F3961C;font-weight:bold;">Willing to give in return</text><br/>'+job['payment'].encode('utf-8')+'</p><p><text style="color:#F3961C;font-weight:bold;">Timeframe</text><br/>'+job['timeframe'].encode('utf-8')+'</p>'
	
	return formmated
	

def createMail():
	# Note: This query isn't exactly right due to mongo's lack of 
	# selecting by fields on arrays see 
	# https://jira.mongodb.org/browse/SERVER-828 for a work around
	# so I'm doing it the cheap way
	cutoff = datetime.datetime.utcnow() - datetime.timedelta(7)
	print cutoff
	reqs = db.requests.find({'jobs.date':{'$gte':cutoff}})

	f = open(str(datetime.datetime.utcnow())+'-emails.html', 'w')
	f.write('<html>')
	numJobs = 1
	# create emails
	for req in reqs:
		for job in req['jobs']:
			if job['date'] >= cutoff:
				formmated = getFormmatedJob(job, numJobs, req['email'])
				f.write(formmated)
				numJobs += 1
		
	f.write('</html>')
	f.close()

createMail()
