# Mr. Mailboto
import sys
sys.path.append("../app")
from models import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mailboto:
	def __init__(self, pw, user="mail-bot@hireanoliner.com"):
		self.fromUser = {}
		self.fromUser['user'] = user
		self.fromUser['pw'] = pw
		
	def requestConfirmation(self, job, to, name):
		smtpserver = smtplib.SMTP("smtp.gmail.com",587)
		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.login(self.fromUser['user'], self.fromUser['pw'])
		
		msg = MIMEMultipart('alternative')
		msg['Subject'] = '[HireAnOliner] Request Submitted'
		msg['From'] = self.fromUser['user']
		msg['To'] = to
		formmated = self.getFormmatedJob(job, 1, to)
		formmated['plain'] = 'Hello '+name+',\n\n You have submitted the following request to HireAnOliner.com:\n\n'+formmated['plain']+'\n It is currently under review. If it all looks good it\'ll be sent out with the next mailing of HireAnOliner. We will notify you if we require any additional information about this posting. \n\n Thanks for using HireAnOliner,\n mail-bot'
		formmated['html'] = "<html><body><div style='width:600px; margin-left:auto; margin-right:auto;'><p>Hello "+name+",</p><p>You have submitted the following request to HireAnOliner.com:</p>"+formmated['html']+"<p>If it all looks good it'll be sent out with the next mailing of HireAnOliner. We will notify you if we require any additional information about this posting.</p><p>Thanks for using HireAnOliner,<br/>mail-bot</p></body></html>"
		msg.attach(MIMEText(formmated['plain'], 'plain'))
		msg.attach(MIMEText(formmated['html'], 'html'))
		
		smtpserver.sendmail(self.fromUser['user'], msg['To'] , msg.as_string())
		smtpserver.close()
	
	def olinerConfirmation(self, oliner):
		smtpserver = smtplib.SMTP("smtp.gmail.com",587)
		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.login(self.fromUser['user'], self.fromUser['pw'])
		
		msg = MIMEMultipart('alternative')
		msg['Subject'] = '[HireAnOliner] Added To Mailing list'
		msg['From'] = self.fromUser['user']
		msg['To'] = oliner.email
		formmated = {}
		formmated['plain'] = 'Hello,\n\n You have been added to the HireAnOliner mailing list. Look for some cool project listings coming your way! \n\n Thanks for using HireAnOliner,\n mail-bot \n\n If you would like to unsubscribe, please go here http://www.hireanoliner.com/unsubscribe/'+str(oliner._id)
		formmated['html'] = "<html><body><div style='width:600px; margin-left:auto; margin-right:auto;'><p>Hello,</p><p>You have been added to the HireAnOliner mailing list. Look for some cool project listings coming your way!</p><p>Thanks for using HireAnOliner,<br/>mail-bot</p><br/><p style='font-size:8px;'>If you would like to unsubscribe, please <a href='http://www.hireanoliner.com/unsubscribe/"+str(oliner._id)+"'>click here</p></body></html>"
		msg.attach(MIMEText(formmated['plain'], 'plain'))
		msg.attach(MIMEText(formmated['html'], 'html'))
		
		smtpserver.sendmail(self.fromUser['user'], msg['To'] , msg.as_string())
		smtpserver.close()
	
	def getFormmatedJob(self, job, number, email):
		formmated = {}
		formmated['html'] = '<div style="margin-top:30px;"><span style="color:#AB1A23;font-weight:bold;">#'+str(number)+' Submitted by </span>'+job['name'].encode('utf-8')+' ( <span style="color:#1144AA">'+email.encode('utf-8')+'</span> )<br/><div style="margin-left:20px;"><span style="color:#F3961C;font-weight:bold;">Description</span><br/>'+job['detail'].encode('utf-8')+'<p><span style="color:#F3961C;font-weight:bold;">What needs to get done</span><br/>'+job['needs'].encode('utf-8')+'</p><p><span style="color:#F3961C;font-weight:bold;">Willing to give in return</span><br/>'+job['payment'].encode('utf-8')+'</p><p><span style="color:#F3961C;font-weight:bold;">Timeframe</span><br/>'+job['timeframe'].encode('utf-8') +'</p></div></div>'
		formmated['plain'] = str(number)+' Submitted by' + job['name'].encode('utf-8') + '\n\nDescription\n'+job['detail'].encode('utf-8')+'\n\nWhat needs to get done\n' + job['needs'].encode('utf-8') + '\n\nWilling to give in return\n' + job['payment'].encode('utf-8') + '\n\nTimeframe\n'+ job['timeframe'].encode('utf-8')+ '\n\n' 
		return formmated
		
	def createMail(self):
		# Note: This query isn't exactly right due to mongo's lack of 
		# selecting by fields on arrays see 
		# https://jira.mongodb.org/browse/SERVER-828 for a work around
		# so I'm doing it the cheap way
		reqs = db.requests.find({'jobs.sent':0})

		fHtml = open(str(datetime.datetime.utcnow().date())+'-emails.html', 'w')
		fHtml.write('<html><body><div style="width:600px; margin-left:auto; margin-right:auto;">')
		fPlain = open(str(datetime.datetime.utcnow().date())+'-emails.plain', 'w')
		numJobs = 1
		# create emails
		for req in reqs:
			for job in req['jobs']:
				if job['sent'] == 0:
					formmated = self.getFormmatedJob(job, numJobs, req['email'])
					fHtml.write(formmated['html'])
					fPlain.write(formmated['plain'])
					# change to sent
					db.requests.update({'jobs.date':job['date']}, {'$set':{'jobs.$.sent':1}})
					numJobs += 1
					
		fHtml.close()
		fPlain.close()
		
	def sendToUsers(self, htmlEmail, plainEmail):
		smtpserver = smtplib.SMTP("smtp.gmail.com",587)
		smtpserver.ehlo()
		smtpserver.starttls()
		
		smtpserver.login(self.fromUser['user'], self.fromUser['pw'])
		
		users = db.oliners.find()
		plainFile = open(plainEmail, 'r')
		plainEmail = plainFile.read()
		htmlFile = open(htmlEmail, 'r')
		htmlEmail = htmlFile.read()
		for user in users:
			msg = MIMEMultipart('alternative')
			msg['Subject'] = '[HireAnOliner] project listings for '+str(datetime.datetime.now().date())
			msg['From'] = self.fromUser['user']
			msg['To'] = user['email']
			closingMsgHtml = '<br/><p style="font-size:8px;">In order to unsubscribe to this email list, please <a href="http://www.hireanoliner.com/unsubscribe/'+str(user['_id'])+'">click here</a></p></div></body></html>'
			closingMsgPlain = '\n\n In order to unsubscribe to this email list, please go to http://www.hireanoliner.com/unsubscribe/'+str(user['_id'])+'\n'
			msg.attach(MIMEText(plainEmail+closingMsgPlain, 'plain'))
			msg.attach(MIMEText(htmlEmail+closingMsgHtml, 'html'))
			smtpserver.sendmail(self.fromUser['user'], msg['To'] , msg.as_string())
			print "sent mail to "+user['email']
		
		smtpserver.close()
		plainFile.close()
		htmlFile.close()
 
def main(name, task, pw='', htmlEmail='',plainEmail='', user="mail-bot@hireanoliner.com"):
	m = Mailboto(pw, user)
	if task == 'create':
		m.createMail()
	if task == 'send':
		m.sendToUsers(htmlEmail, plainEmail)
	
if __name__ == '__main__':
    main(*sys.argv)
