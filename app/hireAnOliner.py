#
# HireAnOliner 
# 2012
# Jialiya Huang
#

########################################################################
# Imports
########################################################################

import flask
import shutil
from flask import Flask, request, session, g, redirect, url_for, \
	 abort, render_template, flash, Response
from contextlib import closing
import os
import datetime, sys, json, time, uuid, subprocess
from models import *
import sys
sys.path.append("../scripts")
from mailboto import Mailboto

########################################################################
# Configuration
########################################################################

DEBUG = True
# create app
app = Flask(__name__)
app.config.from_object(__name__)

########################################################################
# Helper functions
########################################################################
	
def json_res(obj):
	# convert datetimes to miliseconds since epoch
	dthandler = lambda obj: time.mktime(obj.timetuple())*1000 if isinstance(obj, datetime.datetime) else None
	return Response(json.dumps(obj, default=dthandler), mimetype='application/json')

########################################################################
# Routes
########################################################################

@app.route('/error')
def error(error_msg):
	return render_template("error.html", error = error_msg)

@app.route('/unsubscribe/<uid>')
def unsubscribe(uid, methods=['GET', 'POST']):
	try:
		userId = pymongo.objectid.ObjectId(uid)
		user = db.oliners.find_one({'_id':userId})
		if user:
			db.oliners.remove({'_id':userId})
			return render_template('unsubscribed.html')
	except:
		pass
		
	return error("""We could not find this user. 
	If you wish to unsubscribe please send an email 
	with the subject 'Unsubscribe' to mail-bot@hireanoliner.com""")

@app.route('/requests', methods=['GET','POST'])
def requests():
	if request.method == 'POST':
		email = request.form.get('email')
		name = request.form.get('name')
		needs = request.form.get('needs')
		detail = request.form.get('detail')
		payment = request.form.get('payment')
		timeframe = request.form.get('timeframe')
		
		if not email or not name or not needs or not detail or not payment or not timeframe:
			return json_res({'error':'Please fill out all fields.'})
		if len(detail) > 650:
			return json_res({'error':'Please restrict project information to under 650 characters.'})
			
		date = datetime.datetime.utcnow()
		req = db.Requests.find_one({'email': email})
		job = {'name':name, 'needs': needs, 'detail': detail, 'payment':payment, 'date':date, 'timeframe':timeframe, 'sent':0}
		
		if req:
			db.requests.update({'email':req.email}, {'$push':{'jobs':job}})
		else:
			# create new entry for email
			req = db.Requests()
			req.update({'email':email, 'jobs':[job]})
			req.save()
		
		m = Mailboto(PW)
		try:
			m.requestConfirmation(job, email, name)
		except:
			return json_res({'error': "We weren't able to find the recipient email. Please double check that the spelling is correct."})
			
		return json_res({'success':'Success! Your project information will be emailed to Olin students soon.'})
		
	return render_template('requests.html')

@app.route('/oliners', methods=['POST'])
def oliners():
	email = request.form.get('email')
	if not email:
		return json_res({'error':"You must enter an email address"})
	
	emailType = request.form.get('type')
	if emailType == 'student':
		email = email +'@students.olin.edu'
	elif emailType == 'alum':
		email = email + '@alumni.olin.edu'
	else:
		return json_res({'error': "You didn't select a valid student type"})
	
	email = email.lower()
	oliner = db.oliners.find_one({'email':email})
	
	if oliner:
		return json_res({'error': "You're already on the mailing list"})
	else:
		oliner = db.Oliners()
		oliner.email = email
		oliner.date = datetime.datetime.utcnow()
		oliner.save()
		
		m = Mailboto(PW)
		try:
			m.olinerConfirmation(oliner)
		except:
			db.oliners.remove({'email':email})
			return json_res({'error': "We weren't able to find the recipient email. Please double check that the spelling is correct."})
		
		return json_res({'success':"You've been added to the mailing list. Look out for some cool projects!"})
		
@app.route('/', methods=['GET'])
def main():
	return render_template('main.html')

########################################################################
# Entry
########################################################################

if __name__ == '__main__':
	app.run()
