from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, SelectField, FileField, SelectMultipleField, RadioField, TextAreaField
#from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, Email, Length
import email_validator
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_uploads import configure_uploads, IMAGES, UploadSet
import datetime
from datetime import timedelta
from functools import wraps
import pytz
import datetime
from functools import wraps
import jwt
import requests
import json
from time import time
import asyncio
from GoogleNews import GoogleNews
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
import smtplib, ssl

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:superuncrackable@localhost:5432/patients'
app.config['UPLOADED_IMAGES_DEST'] = '/Users/armaanjohal/Desktop/Healthcare_Scheduler_Project-master/Healthcare_Scheduler_Project/static'
app.config['UPLOADED_IMAGES_ALLOW'] = set(['png', 'jpg', 'jpeg'])
app.config['MAX_CONTENT_PATH'] = 2000
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

#Enter your API key and your API secret (for ZOOM)
#API_KEY = 'SnvfkrTiRUKZK4zCK1hYMQ'  #'5Ev7vHyMTqmnzmoDz3buXQ'
#API_SEC = 'RO1yDVWoWxUBZX2yIIcdXYrP2gNvqhnlBjGu'  #'OjbEsetTDDkCoWwUvK8pCPalCxN6zgn3AcuP'

GTN_CODE = 'H$&jtG3eu!'


######### TO DO (future) ############
	### Add share button (to social media) to patient_dashboard, doctor_dashboard, and index. 
	### Integrate OpenEMR
	### 
	###
	###
	###
	###



##################################################################################################
#Creating PostgreSQL tables
##################################################################################################

# class Patient(UserMixin, db.Model):
# 	__tablename__ = 'patient'
# 	id = db.Column(db.Integer, primary_key=True)
# 	username = db.Column(db.String(15), unique=True)
# 	email = db.Column(db.String(50), unique=True)
# 	password = db.Column(db.String(100))

# class Doctor(UserMixin, db.Model):
# 	__tablename__ = 'doctor'
# 	id = db.Column(db.Integer, primary_key=True)
# 	username = db.Column(db.String(15), unique=True)
# 	email = db.Column(db.String(50), unique=True)
# 	password = db.Column(db.String(100))
# 	npi = db.Column(db.String(10), unique=True)
# 	practiceName = db.Column(db.String(80))
# 	specialty = db.Column(db.String(80))

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(20))  # this is the discriminator column

	__mapper_args__ = {
		'polymorphic_on':type,
	}

class Patient(User):
	__tablename__ = 'patient'
	id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	#username = db.Column(db.String(15), unique=True)
	fname = db.Column(db.String(30))
	lname = db.Column(db.String(30))
	dob = db.Column(db.String(30))
	email = db.Column(db.String(50), unique=True)
	phoneNumber = db.Column(db.String(20), unique=True)
	password = db.Column(db.String(100))
	timezone = db.Column(db.String(80))
	gtnclinic = db.Column(db.String(100))
	userType = db.Column(db.String(80))

	__mapper_args__ = {
		'polymorphic_identity':'patient'
	}

class Doctor(User):
	__tablename__ = 'doctor'
	id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	#username = db.Column(db.String(15), unique=True)
	fname = db.Column(db.String(30))
	lname = db.Column(db.String(30))
	email = db.Column(db.String(50), unique=True)
	phoneNumber = db.Column(db.String(20), unique=True)
	dob = db.Column(db.String(30))
	password = db.Column(db.String(100))
	imgName = db.Column(db.String(150))
	npi = db.Column(db.String(10), unique=True)
	practiceName = db.Column(db.String(80))
	zoomlink = db.Column(db.String(50))
	specialty = db.Column(db.String(80))
	timezone = db.Column(db.String(80))
	malpractice = db.Column(db.Boolean)
	liability = db.Column(db.Boolean)
	userType = db.Column(db.String(80))

	__mapper_args__ = {
		'polymorphic_identity':'doctor'
	}

# class Communities(UserMixin, db.Model):
# 	__tablename__ = 'communities'
# 	id = db.Column(db.Integer, primary_key=True)
# 	community = db.Column(db.String(150))

# class Doctor_Communities(UserMixin, db.Model):
# 	__tablename__ = 'doctor_communities'
# 	id = db.Column(db.Integer, primary_key=True)
# 	doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
# 	community_id = db.Column(db.Integer, db.ForeignKey('communities.id'))
# 	#doctor = db.relationship("Doctor", backref=db.backref("doctor", uselist=False))
# 	#communities = db.relationship("Communities", backref=db.backref("communities", uselist=False))

# 	# To reference a community:
# 	# community_object = Communities.query.filter_by(id=community_id).first()
# 	# print(community_object.community)

class Schedule(UserMixin, db.Model):
	#schedule_id = db.Column(db.Integer, db.ForeignKey(Doctor.id), primary_key=True)
	__tablename__ = 'schedule'
	id = db.Column(db.Integer, primary_key=True)
	doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
	#doctor = db.relationship("Doctor", backref=db.backref("doctor_schedule", uselist=False))
	timeAvailable = db.Column(db.DateTime)
	booked = db.Column(db.Boolean, unique=False, default=False)
	patient_id = db.Column(db.Integer, unique=False) ##CHANGE UNIQUE TO FALSE IF WANT TO ALLOW MULTIPLE PATIENT BOOKINGS
	description = db.Column(db.String(250))
	zoom = db.Column(db.String(250))
	accepted = db.Column(db.Boolean, default=False)
	# mon_end = db.Column(db.DateTime)
	# tue_start = db.Column(db.DateTime)
	# tue_end = db.Column(db.DateTime)
	# wed_start = db.Column(db.DateTime)
	# wed_end = db.Column(db.DateTime)
	# thr_start = db.Column(db.DateTime)
	# thr_end = db.Column(db.DateTime)
	# fri_start = db.Column(db.DateTime)
	# fri_end = db.Column(db.DateTime)
	# sat_start = db.Column(db.DateTime)
	# sat_end = db.Column(db.DateTime)
	# sun_start = db.Column(db.DateTime)
	# sun_end = db.Column(db.DateTime)
	#schedule = db.relationship('Doctor', foreign_keys='Schedule.schedule_id')

##################################################################################################
#User Loader & Login Functions
##################################################################################################

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

def require_role(role):
	def decorator(func):
		@wraps(func)
		def wrapped_function(*args, **kwargs):
			if not current_user.type==role:
				return redirect("/")
			else:
				return func(*args, **kwargs)
		return wrapped_function
	return decorator

##################################################################################################
#Creating Forms for Log In and Sign Up
##################################################################################################

class LoginForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Length(min=4, max=50)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=100)])
	remember = BooleanField('remember me')

class LoginFormDoctor(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Length(min=4, max=50)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=100)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
	fname = StringField('First Name', validators=[InputRequired(), Length(max=30)])
	lname = StringField('Last Name', validators=[InputRequired(), Length(max=30)])
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	phoneNumber = StringField('Phone Number', validators=[InputRequired(), Length(10)])
	dob = StringField('Date of Birth (mm/dd/yyyy)', validators=[InputRequired(), Length(max=30)])
	#username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=100)])
	timezoneList = list(pytz.all_timezones_set)
	timezoneList.sort()
	timezone = SelectField('Timezone', choices = timezoneList, validators=[InputRequired(), Length(min=8, max=100)])
	gtnClinicList = ['Kenya Clinic #1', "Uganda Clinic #1"] ##### SHOULD BE CHANGED AND UPDATED AS NECESSARY ##################
	gtnclinic = SelectField('GTN Clinic', choices = gtnClinicList, validators=[InputRequired(), Length(min=1, max=100)])
	gtncode = StringField('GTN 10-digit Code (provided by GTN)', validators=[InputRequired(), Length(min=9, max=10)])

class RegisterFormDoctor(FlaskForm):
	fname = StringField('First Name', validators=[InputRequired(), Length(min=2, max=30)])
	lname = StringField('Last Name', validators=[InputRequired(), Length(min=2, max=30)])
	email = StringField('Email (**please make sure this is the same email registered with Zoom**)', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	phoneNumber = StringField('Phone Number', validators=[InputRequired(), Length(max=10)])
	dob = StringField('Date of Birth (mm/dd/yyyy)', validators=[InputRequired(), Length(max=30)])
	img = FileField('Add Headshot')
	#username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	npi = StringField('NPI number', validators=[InputRequired(), Length(10)])
	#specialty = StringField('Specialty', validators=[InputRequired(), Length(min=4, max=80)])
	practiceName = StringField('Practice Name', validators=[InputRequired(), Length(min=4, max=80)])
	zoomlink = StringField('HIPPA Compliant Personal Meeting Room (PMI) Zoom Link (example: https://zoom.us/j/1234567899)', validators=[InputRequired(), Length(min=10, max=50)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=100)])
	#specialtyList = ["El Sobrante Sikh Gurudwara", "San Diego Gurudwara", "Moraga Catholic Church", "Newport Beach Jewish Synagogue", "Alameda Mosque"]
	specialtyList = ['', 'Pathology', 'Anesthesiology', 'Cardiology', 'Cardiovascular/Thoracic Surgery', 'Clinical Immunology/Allergy', 'Critical Care', 
		'Dermatology', 'Radiology', 'Emergency Medicine', 'Endocrinology', 'Family Medicine', 'Gastroenterology', 'General Internal Medicine', 'General Surgery', 
		'Geriatric Medicine', 'Hematology', 'Hematology & Oncology', 'Medical Genetics', 'Infectious Diseases', 'Oncology', 'Nephrology', 'Neurology', 
		'Neurosurgery', 'Nuclear Medicine', 'Obstetrics/Gynecology', 'Occupational Medicine', 'Ophthalmology', 'Orthopedic Surgery', 'Otolaryngology', 'Pediatrics', 
		'Physical Medicine and Rehabilitation (PM & R)', 'Plastic Surgery', 'Psychiatry', 'Psychology', 'Public Health and Preventive Medicine (PhPm)', 
		'Radiation Oncology', 'Respirology', 'Rheumatology', 'Urology']
	timezoneList = list(pytz.all_timezones_set)
	timezoneList.sort()
	specialty = SelectField('Specialty', choices = specialtyList, validators=[InputRequired(), Length(min=8, max=100)])
	timezone = SelectField('Timezone', choices = timezoneList, validators=[InputRequired(), Length(min=8, max=100)])
	malpractice = RadioField('malpractice', choices=[(0,'I have comprehensive malpractice coverage'),(1,'I do not have comprehensive malpractice coverage')], validators=[InputRequired()])
	gtncode = StringField('GTN 10-digit Code (provided by GTN)', validators=[InputRequired(), Length(min=9, max=10)])

class RegisterFormDoctorLiability(FlaskForm):
	liability = StringField ('Type your full name below (acknowledgement of liability)', validators=[InputRequired()])


# class RegisterFormDoctorCommunities(FlaskForm):
# 	#communitiesList = [r[0] for r in db.session.query(Communities).filter(id>0).values('community')]
# 	#communitiesList = [comm.community for comm in db.session.query(Communities).all()]
# 	comm1 = SelectField(u'Community #1', validators=[Length(min=1, max=130)], default='-')
# 	comm2 = SelectField(u'Community #2', validators=[Length(min=1, max=130)], default='-')
# 	comm3 = SelectField(u'Community #3', validators=[Length(min=1, max=130)], default='-')
# 	added_community = StringField('Add a Community')

class ScheduleForm(FlaskForm):
	def createTimeList():
		start = '6:00AM'
		dt = datetime.datetime.strptime(start, '%I:%M%p')
		dtstr = datetime.datetime.strftime(dt, '%I:%M%p')
		listOfDates = ['-']
		for i in range(0, 24*4):
			newDate = dt + datetime.timedelta(hours=i*0.25)
			dtstr = datetime.datetime.strftime(newDate, '%I:%M%p')
			listOfDates.append(dtstr)
		return listOfDates

	timeList = createTimeList()
	repeat = RadioField('repeat', choices=[(0,'week'),(1,'other week')])
	mon_start = SelectField(u'Start Time', choices = timeList, default='-')
	mon_end = SelectField(u'End Time', choices = timeList, default='-')
	tue_start = SelectField(u'Start Time', choices = timeList, default='-')
	tue_end = SelectField(u'End Time', choices = timeList, default='-')
	wed_start = SelectField(u'Start Time', choices = timeList, default='-')
	wed_end = SelectField(u'End Time', choices = timeList, default='-')
	thu_start = SelectField(u'Start Time', choices = timeList, default='-')
	thu_end = SelectField(u'End Time', choices = timeList, default='-')
	fri_start = SelectField(u'Start Time', choices = timeList, default='-')
	fri_end = SelectField(u'End Time', choices = timeList, default='-')
	sat_start = SelectField(u'Start Time', choices = timeList, default='-')
	sat_end = SelectField(u'End Time', choices = timeList, default='-')
	sun_start = SelectField(u'Start Time', choices = timeList, default='-')
	sun_end = SelectField(u'End Time', choices = timeList, default='-')

class SearchForm(FlaskForm):
	specialtyList = ['', 'Pathology', 'Anesthesiology', 'Cardiology', 'Cardiovascular/Thoracic Surgery', 'Clinical Immunology/Allergy', 'Critical Care', 
		'Dermatology', 'Radiology', 'Emergency Medicine', 'Endocrinology', 'Family Medicine', 'Gastroenterology', 'General Internal Medicine', 'General Surgery', 
		'Geriatric Medicine', 'Hematology', 'Hematology & Oncology', 'Medical Genetics', 'Infectious Diseases', 'Oncology', 'Nephrology', 'Neurology', 
		'Neurosurgery', 'Nuclear Medicine', 'Obstetrics/Gynecology', 'Occupational Medicine', 'Ophthalmology', 'Orthopedic Surgery', 'Otolaryngology', 'Pediatrics', 
		'Physical Medicine and Rehabilitation (PM & R)', 'Plastic Surgery', 'Psychiatry', 'Psychology', 'Public Health and Preventive Medicine (PhPm)', 
		'Radiation Oncology', 'Respirology', 'Rheumatology', 'Urology']
	urgencyList = ['', 'Within 6 hours', 'Within 12 hours', 'Within 24 hours', 'Within 48 hours', 'Within 72 hours', 'Within 1 week']
	#specialty = SelectField('Specialty', choices = specialtyList)
	specialty = SelectField(u'Specialty', validators=[Length(min=0, max=130)], default='')
	#comm = SelectField(u'Community', validators=[Length(min=1, max=130)], default='-') #CHANGE TO TIMING (6hr, 12hr, 24hr, 48hr, 72hr, 1 week) ####
	urgency = SelectField('Time Urgency', choices=urgencyList, validators=[Length(min=0, max=130)], default='')

class BookingForm(FlaskForm):
	time = RadioField('time', validators=[InputRequired()])
	description = TextAreaField('Brief Reason for Consultation', validators=[InputRequired(), Length(min=1, max=250)])

class SpecialtyHelp(FlaskForm):
	description = TextAreaField('Description of Problem and Reason for Consult', validators=[InputRequired(), Length(min=1, max=400)])

class PlaceHolderForm(FlaskForm):
	placeholder = StringField('Placeholder')



##################################################################################################
#Website Routes
##################################################################################################

@app.route('/', methods=['GET', 'POST'])
def index():
	form = SearchForm()
	book_form = SearchForm()
	#form.comm.choices = [comm.community for comm in db.session.query(Communities).all()]
	form.specialty.choices = [''] + list(set([doc.specialty for doc in db.session.query(Doctor).all()])) + ['Not sure']
	filteredDoctors = db.session.query(Doctor).all()
	soonestAvailability = []
	currTimeUTC = getCurrentServerUTCTime();

	if form.validate_on_submit():
		if current_user.is_authenticated==False:
			return redirect(url_for('login'))
		sp = form.specialty.data
		urgencyString = form.urgency.data

		if sp=='Not sure':
			print('\n' + "Not sure" + '\n')
			return redirect(url_for('specialty_help'))

		if sp != '' and urgencyString != '':
			filteredDoctorIdSpecialty = [doc.id for doc in db.session.query(Doctor).filter_by(specialty=sp).all()]
			filteredDoctorIdUrgency = filteredDoctorIdsUrgency(urgencyString)
			filteredDoctorIds = [doc for doc in filteredDoctorIdSpecialty if doc in filteredDoctorIdUrgency]
			filteredDoctors = []
			for doc_id in filteredDoctorIds:
				filteredDoctors.append(db.session.query(Doctor).filter_by(id=doc_id).first())
				localTimeAvailability = getDoctorAvailability(doc_id, 1)[0][0]
				utcTimeAvailability = changeToUTC(localTimeAvailability)
				timeDelta = utcTimeAvailability - currTimeUTC
				soonestAvailability.append(timeDelta.days*24 + (timeDelta.seconds // 3600))

		elif sp == '' and urgencyString != '':
			filteredDoctorIdUrgency = filteredDoctorIdsUrgency(urgencyString)
			filteredDoctors = []
			for doc_id in filteredDoctorIdUrgency:
				filteredDoctors.append(db.session.query(Doctor).filter_by(id=doc_id).first())
				localTimeAvailability = getDoctorAvailability(doc_id, 1)[0][0]
				utcTimeAvailability = changeToUTC(localTimeAvailability)
				timeDelta = utcTimeAvailability - currTimeUTC
				soonestAvailability.append(timeDelta.days*24 + (timeDelta.seconds // 3600))

		elif sp != '' and urgencyString == '':
			filteredDoctorIdSpecialty = [doc.id for doc in db.session.query(Doctor).filter_by(specialty=sp).all()]
			filteredDoctors = []
			for doc_id in filteredDoctorIdSpecialty:
				filteredDoctors.append(db.session.query(Doctor).filter_by(id=doc_id).first())
				localTimeAvailability = getDoctorAvailability(doc_id, 1)[0][0]
				utcTimeAvailability = changeToUTC(localTimeAvailability)
				timeDelta = utcTimeAvailability - currTimeUTC
				soonestAvailability.append(timeDelta.days*24 + (timeDelta.seconds // 3600))
		else:
			filteredDoctors = db.session.query(Doctor).all()
			for doc in filteredDoctors:
				localTimeAvailability = getDoctorAvailability(doc.id, 1)[0][0]
				utcTimeAvailability = changeToUTC(localTimeAvailability)
				timeDelta = utcTimeAvailability - currTimeUTC
				soonestAvailability.append(timeDelta.days*24 + (timeDelta.seconds // 3600))

		return render_template('index.html', filteredDoctors=filteredDoctors, soonestAvailability=soonestAvailability, form=form)

	if book_form.is_submitted():
		if current_user.is_authenticated:
			doctor_id = request.form.get('action')
			session['doctor_id'] = doctor_id;
		else:
			return redirect(url_for('login'))
		return redirect(url_for('booking', doctor_id=doctor_id))

	return render_template('index.html', filteredDoctors=filteredDoctors, soonestAvailability=soonestAvailability, form=form)


@app.route('/specialty_help', methods=['GET', 'POST'])
@login_required
@require_role('patient')
def specialty_help():
	form = SpecialtyHelp()
	specialtyList = ['', 'Pathology', 'Anesthesiology', 'Cardiology', 'Cardiovascular/Thoracic Surgery', 'Clinical Immunology/Allergy', 'Critical Care', 
		'Dermatology', 'Radiology', 'Emergency Medicine', 'Endocrinology', 'Family Medicine', 'Gastroenterology', 'General Internal Medicine', 'General Surgery', 
		'Geriatric Medicine', 'Hematology', 'Hematology & Oncology', 'Medical Genetics', 'Infectious Diseases', 'Oncology', 'Nephrology', 'Neurology', 
		'Neurosurgery', 'Nuclear Medicine', 'Obstetrics/Gynecology', 'Occupational Medicine', 'Ophthalmology', 'Orthopedic Surgery', 'Otolaryngology', 'Pediatrics', 
		'Physical Medicine and Rehabilitation (PM & R)', 'Plastic Surgery', 'Psychiatry', 'Psychology', 'Public Health and Preventive Medicine (PhPm)', 
		'Radiation Oncology', 'Respirology', 'Rheumatology', 'Urology']
	if form.validate_on_submit():
		## send email to gtn with description
		description_txt = form.description.data
		specialty_txt = ', '.join(specialtyList)
		lp_email = current_user.email

		[intro_text,ending_text] = get_emailText(lp_email, specialty_txt)
		html_email_msg = '<html>  <body>  <font size="4" face="Arial" >      <style>      table {        border-collapse: collapse;      }      th, td {        border: 1px solid black;        padding: 10px;        text-align: right;      }    </style>    <p>    <br>'+intro_text+' <br><br> '+description_txt+' <br><br>'+ending_text+'</p>  </body></html>'

		tolist = ['gtn.careify@gmail.com']
		cclist = ['armaanj2016@gmail.com', lp_email]
		bcclist = []

		port = 465  # For SSL
		smtp_server = "smtp.gmail.com"
		sender_email = "gtn.careify@gmail.com"  # Enter your address

		toaddrs = tolist + cclist + bcclist

		password='gtn-admin2022!'

		message = MIMEMultipart("mixed")
		message["Subject"] = 'Careify: Request for Physician Matching'
		message["From"] = sender_email
		message["To"] = ', '.join(tolist)

		# Turn these into html MIMEText objects)
		part = MIMEText(html_email_msg, "html")
		message.attach(part)

		 # Create secure connection with server and send email
		context = ssl.create_default_context()
		with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
			server.login(sender_email, password)
			server.sendmail(sender_email, toaddrs, message.as_string())

		return redirect(url_for('index'))

	return render_template('specialty_help.html', form=form)

# @app.route('/', methods=['GET', 'POST'])
# def index():
# 	form = SearchForm()
# 	book_form = SearchForm()
# 	form.comm.choices = [comm.community for comm in db.session.query(Communities).all()]
# 	form.specialty.choices = [''] + list(set([doc.specialty for doc in db.session.query(Doctor).all()]))
# 	filteredDoctors = db.session.query(Doctor).all()

# 	if form.validate_on_submit():
# 		sp = form.specialty.data
# 		commString = form.comm.data

# 		if sp != '' and commString != '-':
# 			comm_id = db.session.query(Communities.id).filter_by(community=commString).first()[0]
# 			filteredDoctorIdSpecialty = [doc.id for doc in db.session.query(Doctor).filter_by(specialty=sp).all()]
# 			filteredDoctorIdCommunity = [doc.doctor_id for doc in db.session.query(Doctor_Communities).filter_by(community_id=comm_id).all()]
# 			filteredDoctorIds = [doc for doc in filteredDoctorIdSpecialty if doc in filteredDoctorIdCommunity]
# 			filteredDoctors = []
# 			for doc_id in filteredDoctorIds:
# 				filteredDoctors.append(db.session.query(Doctor).filter_by(id=doc_id).first())

# 		elif sp == '' and commString != '-':
# 			comm_id = db.session.query(Communities.id).filter_by(community=commString).first()[0]
# 			filteredDoctorIdCommunity = [doc.doctor_id for doc in db.session.query(Doctor_Communities).filter_by(community_id=comm_id).all()]
# 			filteredDoctors = []
# 			for doc_id in filteredDoctorIdCommunity:
# 				filteredDoctors.append(db.session.query(Doctor).filter_by(id=doc_id).first())

# 		elif sp != '' and commString == '-':
# 			filteredDoctorIdSpecialty = [doc.id for doc in db.session.query(Doctor).filter_by(specialty=sp).all()]
# 			filteredDoctors = []
# 			for doc_id in filteredDoctorIdSpecialty:
# 				filteredDoctors.append(db.session.query(Doctor).filter_by(id=doc_id).first())
# 		else:
# 			filteredDoctors = db.session.query(Doctor).all()

# 		return render_template('index.html', filteredDoctors=filteredDoctors, form=form)

# 	if book_form.is_submitted():
# 		if current_user.is_authenticated:
# 			doctor_id = request.form.get('action')
# 			session['doctor_id'] = doctor_id;
# 		else:
# 			return redirect(url_for('login'))
# 		return redirect(url_for('booking', doctor_id=doctor_id))

# 	return render_template('index.html', filteredDoctors=filteredDoctors, form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

if __name__ == '__main__':
	#app.run(host='0.0.0.0', port=5000, debug=True)
	app.run(debug=True)


##################################################################################################
#Patient-Specific Website Routes
##################################################################################################

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = Patient.query.filter_by(email=form.email.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('patient_dashboard'))

		return '<h1>Invalid username or password</h1>'
		#return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

	return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()

	if form.validate_on_submit():
		if (form.gtncode.data != GTN_CODE):
			return render_template('signup.html', form=form)
		user = Patient.query.filter_by(email=form.email.data).first()
		if not user:
			hashed_password = generate_password_hash(form.password.data, method='sha256')
			new_user = User(type='patient')
			new_patient = Patient(id=new_user.id, fname=form.fname.data, lname=form.lname.data, email=form.email.data, phoneNumber=form.phoneNumber.data, dob=form.dob.data, password=hashed_password, timezone=form.timezone.data, gtnclinic=form.gtnclinic.data, userType='patient')
			db.session.add(new_user)
			db.session.add(new_patient)
			db.session.commit()
			login_user(new_patient)

			############ SEND EMAIL TO GTN HERE##############
			lp_name = current_user.fname + ' ' + current_user.lname
			lp_email = current_user.email
			intro_text = 'Dear GTN, <br><br>A user with the name ' + lp_name + ' has registered as a local provider. Their email is ' + lp_email + '. This is just an automated message. No action is required.'
			ending_text = 'Sincerely,' + '<br>' + 'The Careify Team'

			html_email_msg = '<html>  <body>  <font size="4" face="Arial" >      <style>      table {        border-collapse: collapse;      }      th, td {        border: 1px solid black;        padding: 10px;        text-align: right;      }    </style>    <p>    <br>'+intro_text+' <br><br> '+ending_text+'</p>  </body></html>'

			tolist = ['gtn.careify@gmail.com']
			cclist = ['armaanj2016@gmail.com']
			bcclist = []

			port = 465  # For SSL
			smtp_server = "smtp.gmail.com"
			sender_email = "gtn.careify@gmail.com"  # Enter your address

			toaddrs = tolist + cclist + bcclist

			password='gtn-admin2022!'

			message = MIMEMultipart("mixed")
			message["Subject"] = 'Careify: New Local Provider Registered'
			message["From"] = sender_email
			message["To"] = ', '.join(tolist)

			# Turn these into html MIMEText objects)
			part = MIMEText(html_email_msg, "html")
			message.attach(part)

			 # Create secure connection with server and send email
			context = ssl.create_default_context()
			with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
				server.login(sender_email, password)
				server.sendmail(sender_email, toaddrs, message.as_string())

		else:
			redirect(url_for('login'))

		return redirect(url_for('patient_dashboard'))
		#return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

	return render_template('signup.html', form=form)


@app.route('/booking', methods=['GET', 'POST'])
def booking():
	form = BookingForm()
	description=None
	form.time.choices = getDoctorAvailability(session['doctor_id'], 10) #function that returns list of top 10 upcoming times (in local time)

	# try:
	# 	zoomJSON = createZoomJSON('Patient1', 'armaanj2016@gmail.com', 'This is a test', 'Dr. Sumer Johal', 'sumer.johal@gmail.com', '2022-02-05 02:00:00')
	# 	responseJSON = createMeeting(zoomJSON)
	# 	zoomLink = responseJSON['join_url']
	# 	print(zoomLink)
	# except:
	# 	print("failed")

	if form.validate_on_submit():
		dt = changeToUTC(datetime.datetime.strptime(form.time.data, '%Y-%m-%d %H:%M:%S'))
		description = form.description.data
		zoomLink = db.session.query(Doctor.zoomlink).filter(Doctor.id==session['doctor_id']).first()[0]

		#Zoom stuff
		# ProviderName = 'Dr. ' + db.session.query(Doctor.fname).filter_by(id=session['doctor_id']).first()[0] + ' ' + db.session.query(Doctor.lname).filter_by(id=session['doctor_id']).first()[0]
		# ProviderEmail = db.session.query(Doctor.email).filter_by(id=session['doctor_id']).first()[0]
		# startTimeUTC = datetime.datetime.strftime(dt, '%Y-%m-%dT%H:%M:%S')
		# try:
		# 	zoomJSON = createZoomJSON(current_user.fname, current_user.email, description, ProviderName, ProviderEmail, startTimeUTC)
		# 	responseJSON = createMeeting(zoomJSON)
		# 	zoomLink = responseJSON['join_url']
		# except:
		# 	zoomLink = "Error: Email not registered with zoom."

		print('\n' + zoomLink + '\n')
		db.session.query(Schedule).filter_by(timeAvailable=dt, doctor_id=session['doctor_id']).update({'booked': True, 'patient_id': current_user.id, 'description': description, 'zoom': zoomLink})
		db.session.commit()

		############ SEND EMAIL TO GTN ##############
		doc = db.session.query(Doctor).filter(Doctor.id==session['doctor_id']).first()
		cp_name = doc.fname + ' ' + doc.lname
		lp_name = current_user.fname + ' ' + current_user.lname
		cp_email = doc.email

		intro_text = 'Dear GTN, <br><br>A local provider with the name ' + lp_name + '(email: ' + current_user.email + ') has booked an appointment with a consulting physician with the name ' + cp_name + '(email: ' + cp_email + '). The booking is for ' + FancyDateTime(dt) + ' and needs to be approved by the consulting physician. This is just an automated message. No action is required.'
		ending_text = 'Sincerely,' + '<br>' + 'The Careify Team'
		html_email_msg = '<html>  <body>  <font size="4" face="Arial" >      <style>      table {        border-collapse: collapse;      }      th, td {        border: 1px solid black;        padding: 10px;        text-align: right;      }    </style>    <p>    <br>'+intro_text+' <br><br> '+ending_text+'</p>  </body></html>'
		tolist = ['gtn.careify@gmail.com']
		cclist = ['armaanj2016@gmail.com']
		bcclist = []
		port = 465  # For SSL
		smtp_server = "smtp.gmail.com"
		sender_email = "gtn.careify@gmail.com"  # Enter your address
		toaddrs = tolist + cclist + bcclist
		password='gtn-admin2022!'
		message = MIMEMultipart("mixed")
		message["Subject"] = 'Careify: New Booking Requested!'
		message["From"] = sender_email
		message["To"] = ', '.join(tolist)
		# Turn these into html MIMEText objects)
		part = MIMEText(html_email_msg, "html")
		message.attach(part)
		 # Create secure connection with server and send email
		context = ssl.create_default_context()
		with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
			server.login(sender_email, password)
			server.sendmail(sender_email, toaddrs, message.as_string())

		############ SEND EMAIL TO CP ###############
		intro_text = 'Dear Dr. ' + cp_name + ', <br><br>A GTN local provider with the name ' + lp_name + '(email: ' + current_user.email + ') has booked an consultation appointment with you on ' + FancyDateTime(dt) + '. Please accept this consult request by logging into Careify at URLHERE, navigating to your dashboard, and clicking the red accept button next to the corresponding request.' + '<br><br>' + 'Here is google calendar link to add this consult to your calendar. It includes the zoom link for the consult.' + '<br><br>' + 'If you have any questions or concerns, please email gt.careify@gmail.com'
		ending_text = 'Sincerely,' + '<br>' + 'The Careify Team'
		html_email_msg = '<html>  <body>  <font size="4" face="Arial" >      <style>      table {        border-collapse: collapse;      }      th, td {        border: 1px solid black;        padding: 10px;        text-align: right;      }    </style>    <p>    <br>'+intro_text+' <br><br> '+ending_text+'</p>  </body></html>'
		tolist = [cp_email]
		cclist = ['armaanj2016@gmail.com']
		bcclist = []
		port = 465  # For SSL
		smtp_server = "smtp.gmail.com"
		sender_email = "gtn.careify@gmail.com"  # Enter your address
		toaddrs = tolist + cclist + bcclist
		password='gtn-admin2022!'
		cpmessage = MIMEMultipart("mixed")
		cpmessage["Subject"] = 'Careify: URGENT! Accept New Consult Request from GTN Local Provider'
		cpmessage["From"] = sender_email
		cpmessage["To"] = ', '.join(tolist)
		# Turn these into html MIMEText objects)
		part = MIMEText(html_email_msg, "html")
		cpmessage.attach(part)
		 # Create secure connection with server and send email
		context = ssl.create_default_context()
		with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
			server.login(sender_email, password)
			server.sendmail(sender_email, toaddrs, cpmessage.as_string())

		#flash("Your booking is confirmed")
		return redirect(url_for('patient_dashboard'))

	return render_template('booking.html', form=form, description=description)


@app.route('/patient_dashboard')
@login_required
@require_role('patient')
def patient_dashboard():
	doctorList = []
	dtList = []
	zoomList = []
	tupleList = []
	acceptedList = []

	doctorListPrev = []
	dtListPrev = []
	zoomListPrev = []
	tupleListPrev = []
	acceptedListPrev = []

	upcomingSessions = db.session.query(Schedule).filter(Schedule.patient_id==current_user.id, Schedule.timeAvailable>=getCurrentServerUTCTime()).all()
	for sessions in upcomingSessions:
		doctorList.append(db.session.query(Doctor).filter_by(id=sessions.doctor_id).first())
		dtList.append(FancyDateTime(sessions.timeAvailable))
		zoomList.append(sessions.zoom)
		acceptedList.append(sessions.accepted)
	for x in range(len(doctorList)):
		tupleList.append((doctorList[x], dtList[x], zoomList[x], acceptedList[x]))

	previousSessions = db.session.query(Schedule).filter(Schedule.patient_id==current_user.id, Schedule.timeAvailable<=getCurrentServerUTCTime()).all()
	for sessions in previousSessions:
		doctorListPrev.append(db.session.query(Doctor).filter_by(id=sessions.doctor_id).first())
		dtListPrev.append(FancyDateTime(sessions.timeAvailable))
		zoomListPrev.append(sessions.zoom)
		acceptedListPrev.append(sessions.accepted)
	for x in range(len(doctorListPrev)):
		tupleListPrev.append((doctorListPrev[x], dtListPrev[x], zoomListPrev[x], acceptedListPrev[x]))

	return render_template('patient_dashboard.html', name=current_user.fname, tupleList=tupleList, tupleListPrev=tupleListPrev)


@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html', name=current_user.fname)

##################################################################################################
#Doctor-Specific Website Routes
##################################################################################################

@app.route('/doc_login', methods=['GET', 'POST'])
def doc_login():
	form = LoginFormDoctor()

	if form.validate_on_submit():
		user = Doctor.query.filter_by(email=form.email.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('doctor_dashboard'))

		return '<h1>Invalid username or password</h1>'
		#return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

	return render_template('doc_login.html', form=form)

@app.route('/doc_signup1', methods=['GET', 'POST'])
def doc_signup1():
	form = RegisterFormDoctor()
	#community = request.form.get('community')

	if form.validate_on_submit():
		if (form.gtncode.data != GTN_CODE):
			return render_template('doc_signup1.html', form=form)
		user = Doctor.query.filter_by(email=form.email.data).first()
		if not user:
			hashed_password = generate_password_hash(form.password.data, method='sha256')
			imgName = images.save(form.img.data)
			hasMalpractice = False
			if form.malpractice.data == 0:
				hasMalpractice = True
			new_user = User(type='doctor')
			new_doctor = Doctor(id=new_user.id, fname=form.fname.data, lname=form.lname.data, email=form.email.data, 
					phoneNumber=form.phoneNumber.data, imgName=imgName, npi=form.npi.data, practiceName=form.practiceName.data, 
					timezone=form.timezone.data, password=hashed_password, specialty=form.specialty.data, userType='doctor', dob=form.dob.data,
					zoomlink=form.zoomlink.data, malpractice=hasMalpractice)
			db.session.add(new_user)
			db.session.add(new_doctor)
			db.session.commit()
			login_user(new_doctor)

			############ SEND EMAIL TO GTN HERE##############
			cp_name = current_user.fname + ' ' + current_user.lname
			cp_email = current_user.email
			intro_text = 'Dear GTN, <br><br>A user with the name ' + cp_name + ' has registered as a consulting physician. Their email is ' + cp_email + '. This is just an automated message. No action is required.'
			ending_text = 'Sincerely,' + '<br>' + 'The Careify Team'

			html_email_msg = '<html>  <body>  <font size="4" face="Arial" >      <style>      table {        border-collapse: collapse;      }      th, td {        border: 1px solid black;        padding: 10px;        text-align: right;      }    </style>    <p>    <br>'+intro_text+' <br><br> '+ending_text+'</p>  </body></html>'

			tolist = ['gtn.careify@gmail.com']
			cclist = ['armaanj2016@gmail.com']
			bcclist = []

			port = 465  # For SSL
			smtp_server = "smtp.gmail.com"
			sender_email = "gtn.careify@gmail.com"  # Enter your address

			toaddrs = tolist + cclist + bcclist

			password='gtn-admin2022!'

			message = MIMEMultipart("mixed")
			message["Subject"] = 'Careify: New Consulting Physician Registered'
			message["From"] = sender_email
			message["To"] = ', '.join(tolist)

			# Turn these into html MIMEText objects)
			part = MIMEText(html_email_msg, "html")
			message.attach(part)

			 # Create secure connection with server and send email
			context = ssl.create_default_context()
			with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
				server.login(sender_email, password)
				server.sendmail(sender_email, toaddrs, message.as_string())

		else:
			redirect(url_for('doc_login'))

		return redirect(url_for('doc_signup_liability'))
		#return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

	return render_template('doc_signup1.html', form=form)


@app.route('/doc_signup_liability', methods=['GET', 'POST'])
@login_required
@require_role('doctor')
def doc_signup_liability():
	form = RegisterFormDoctorLiability()
	if form.validate_on_submit():
		doctor_id = current_user.id
		setattr(current_user, 'liability', True)
		db.session.commit()
		return redirect(url_for('doc_signup3'))
		#return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

	return render_template('doc_signup_liability.html', form=form)


# @app.route('/doc_signup2', methods=['GET', 'POST'])
# @login_required
# @require_role('doctor')
# def doc_signup2():
# 	form = RegisterFormDoctorCommunities()
# 	form.comm1.choices = [comm.community for comm in db.session.query(Communities).all()]
# 	form.comm2.choices = [comm.community for comm in db.session.query(Communities).all()]
# 	form.comm3.choices = [comm.community for comm in db.session.query(Communities).all()]
	
# 	#community = request.form.get('community')

# 	if form.validate_on_submit():
# 		if request.form['action'] == 'next':
# 			#doctor_id = db.session.query(Doctor).filter_by(current_user.id)
# 			doctor_id = current_user.id
# 			comm1_id = db.session.query(Communities.id).filter_by(community=form.comm1.data).first()[0]
# 			comm2_id = db.session.query(Communities.id).filter_by(community=form.comm2.data).first()[0]
# 			comm3_id = db.session.query(Communities.id).filter_by(community=form.comm3.data).first()[0]
# 			if (comm1_id != 1): db.session.add(Doctor_Communities(doctor_id=doctor_id, community_id=comm1_id))
# 			if (comm2_id != 1): db.session.add(Doctor_Communities(doctor_id=doctor_id, community_id=comm2_id))
# 			if (comm3_id != 1): db.session.add(Doctor_Communities(doctor_id=doctor_id, community_id=comm3_id))
# 			db.session.commit()
# 			return redirect(url_for('doc_signup3'))

# 		elif request.form['action'] == 'add':			
# 			exists = db.session.query(Communities).filter_by(community=form.added_community.data).first() is not None
# 			if not exists and form.added_community.data!='':
# 				db.session.add(Communities(community=form.added_community.data))
# 				db.session.commit()
# 			return redirect(url_for('doc_signup2'))

# 		else:
# 			return redirect(url_for('doc_signup2'))
# 		form.added_community.data = ''
# 		#return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

# 	return render_template('doc_signup2.html', form=form)


@app.route('/doc_signup3', methods=['GET', 'POST'])
@login_required
@require_role('doctor')
def doc_signup3():
	form = ScheduleForm()
	#community = request.form.get('community')

	if form.validate_on_submit():
		if request.form['action'] == 'save':
			startTimeList = [form.mon_start.data, form.tue_start.data, form.wed_start.data, form.thu_start.data, form.fri_start.data, form.sat_start.data, form.sun_start.data]
			endTimeList = [form.mon_end.data, form.tue_end.data, form.wed_end.data, form.thu_end.data, form.fri_end.data, form.sat_end.data, form.sun_end.data]
			repeat = form.repeat.data #0 is every week, 1 is every other week
			createOneYearListAll(startTimeList, endTimeList, repeat)
			return redirect(url_for('doctor_dashboard'))

	return render_template('doc_signup3.html', form=form)


@app.route('/doctor_dashboard', methods=['GET', 'POST'])
@login_required
@require_role('doctor')
def doctor_dashboard():
	form = PlaceHolderForm()

	patientList = []
	dtList = []
	desList = []
	zoomList = []
	tupleList = []
	sessionsList = []
	isAccepted = []

	patientListPrev = []
	dtListPrev = []
	desListPrev = []
	zoomListPrev = []
	tupleListPrev = []

	news = getGoogleNews(current_user.specialty)

	upcomingSessions = db.session.query(Schedule).filter(Schedule.doctor_id==current_user.id, Schedule.booked==True, Schedule.timeAvailable>=getCurrentServerUTCTime()).all()
	for sessions in upcomingSessions:
		patientList.append(db.session.query(Patient).filter_by(id=sessions.patient_id).first())
		dtList.append(FancyDateTime(sessions.timeAvailable))
		desList.append(sessions.description)
		zoomList.append(sessions.zoom)
		sessionsList.append(sessions)
		isAccepted.append(sessions.accepted)
	for x in range(len(patientList)):
		tupleList.append((patientList[x], dtList[x], desList[x], zoomList[x], sessionsList[x], isAccepted[x]))

	previousSessions = db.session.query(Schedule).filter(Schedule.doctor_id==current_user.id, Schedule.booked==True, Schedule.timeAvailable<=getCurrentServerUTCTime()).all()
	for sessions in previousSessions:
		patientListPrev.append(db.session.query(Patient).filter_by(id=sessions.patient_id).first())
		dtListPrev.append(FancyDateTime(sessions.timeAvailable))
		desListPrev.append(sessions.description)
		zoomListPrev.append(sessions.zoom)
	for x in range(len(patientListPrev)):
		tupleListPrev.append((patientListPrev[x], dtListPrev[x], desListPrev[x], zoomListPrev[x]))

	# if form.is_submitted():
	# 	print('\n' + 'GOT IT' + '\n')
	# 	acceptedBool = request.form.get('action').accepted
	# 	emr = request.form.get('emr')
	# 	print('\n' + acceptedBool + '\n')
	# 	print('\n' + emr + '\n')

	if request.method == 'POST':
		#print('\n' + str(request.form['action']) + '\n')
		if request.form['action'] == 'EMR':
			###### ADD LINK TO EMR EVENTUALLY ######
			emr = 'EMR'
		elif request.form['action'].isdigit():
			db.session.query(Schedule).filter_by(id=int(request.form['action'])).update({'accepted': True})
			db.session.commit()

			############ SEND EMAIL TO GTN HERE##############
			scheduleSlot = db.session.query(Schedule).filter_by(id=int(request.form['action'])).first()
			lp = db.session.query(Patient).filter(Patient.id==scheduleSlot.patient_id).first()
			lp_name = lp.fname + ' ' + lp.lname
			cp_name = current_user.fname + ' ' + current_user.lname
			cp_email = current_user.email

			intro_text = 'Dear GTN, <br><br>A consulting physician with the name ' + cp_name + '(email: ' + cp_email + ') has accepted their consult with local provider ' + lp_name + '(email: ' + lp.email + '). The consult is confirmed on ' + FancyDateTime(scheduleSlot.timeAvailable) + '. This is just an automated message. No action is required.'
			ending_text = 'Sincerely,' + '<br>' + 'The Careify Team'
			html_email_msg = '<html>  <body>  <font size="4" face="Arial" >      <style>      table {        border-collapse: collapse;      }      th, td {        border: 1px solid black;        padding: 10px;        text-align: right;      }    </style>    <p>    <br>'+intro_text+' <br><br> '+ending_text+'</p>  </body></html>'
			tolist = ['gtn.careify@gmail.com']
			cclist = ['armaanj2016@gmail.com']
			bcclist = []
			port = 465  # For SSL
			smtp_server = "smtp.gmail.com"
			sender_email = "gtn.careify@gmail.com"  # Enter your address
			toaddrs = tolist + cclist + bcclist
			password='gtn-admin2022!'
			message = MIMEMultipart("mixed")
			message["Subject"] = 'Careify: Consult Request Accepted'
			message["From"] = sender_email
			message["To"] = ', '.join(tolist)
			# Turn these into html MIMEText objects)
			part = MIMEText(html_email_msg, "html")
			message.attach(part)
			 # Create secure connection with server and send email
			context = ssl.create_default_context()
			with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
				server.login(sender_email, password)
				server.sendmail(sender_email, toaddrs, message.as_string())

		else:
			pass

	return render_template('doctor_dashboard.html', name=current_user.lname, tupleList=tupleList, tupleListPrev=tupleListPrev, news=news, form=form, isAccepted=isAccepted)


##################################################################################################
#ZOOM functions
##################################################################################################

# def generateToken():
#     token = jwt.encode(

#         # Create a payload of the token containing
#         # API Key & expiration time
#         {'iss': API_KEY, 'exp': time() + 5000},

#         # Secret used to generate token signature
#         API_SEC,

#         # Specify the hashing alg
#         algorithm='HS256'
#     )
#     return token #.decode('utf-8')


# def createZoomJSON(PatientName, PatientEmail, PatientChiefComplaint, ProviderName, ProviderEmail, startTimeUTC):
# 	# create json data for post requests
# 	meetingdetails = {
# 	    "topic": "Careify QuickConsult: Patient:-: "+PatientName+" and Provider:-:"+ProviderName,
# 	    "type": 2,
# 	    "start_time": startTimeUTC,
# 	    "duration": "15",
# 	    "timezone": "GMT",
# 	    "agenda": "QuickConsult Reason: "+PatientChiefComplaint,
# 	    "recurrence": {
# 	        "type": 1,
# 	        "repeat_interval": 1
# 	    },
# 	    "settings": {
# 	        "host_video": "true",
# 	        "participant_video": "true",
# 	        "join_before_host": "False",
# 	        "mute_upon_entry": "False",
# 	        "waiting_room": "true",
# 	        "watermark": "true",
# 	        "audio": "voip",
# 	        "auto_recording": "none",
# 	        "alternative_hosts": ProviderEmail
# 	    },
# 	    "registrants_email_notification": "true",
# 	    "registrants_confirmation_email": "true",
# 	    "private_meeting": "true",
# 	    "meeting_invitees": [PatientEmail, ProviderEmail],
# 	    "calender_type": 1,
# 	}
# 	return meetingdetails

# # returns json with everything you need for zoom meeting
# def createMeeting(zoomJSON):
#     headers = {'authorization': 'Bearer ' + generateToken(),
#                'content-type': 'application/json'}
#     r = requests.post(
#         f'https://api.zoom.us/v2/users/me/meetings',
#         headers=headers, data=json.dumps(zoomJSON))
 
#     #rint("\n Creating Zoom Meeting ... \n")
#     # print(r.text)
#     # converting the output into json and extracting the details
#     responseJSON = json.loads(r.text)
#     #join_URL = y["join_url"]
#     #meetingPassword = y["password"]
 
#     #print(f'\n here is your zoom meeting link {join_URL} and your password: "{meetingPassword}"\n')
#     return responseJSON




##################################################################################################
#Other functions
##################################################################################################

# def communityQuery():
# 	return db.session.query(Communities).all()

def getGoogleNews(specialty):
	#Instatiate
	googlenews = GoogleNews()

	#get the date strings for the last 30 days - NOTE THIS IS UTC TIME
	end_date = datetime.datetime.strftime(datetime.datetime.utcnow(), '%m/%d/%Y')
	start_date =  datetime.datetime.strftime(datetime.datetime.utcnow() - datetime.timedelta(days=31), '%m/%d/%Y')
	#print([start_date, end_date])

	#Set Prefs
	googlenews.set_lang('en')
	googlenews.set_period('31d')
	googlenews.set_time_range(start_date,end_date)
	googlenews.set_encode('utf-8')

	#set topic
	googlenews.search(specialty)

	news_result = googlenews.page_at(1) #Only get the first page of results
	#Result is a list of jsons for each new item
	return news_result

def FancyDateTime(dt):
	#takes utc datetime in format '%Y-%m-%d %H:%M:%S' and converts it to
	#local time with readable format "%A, %b %d, %I:%M%p"
	localTime = changeUTCToUserTime(dt)
	fancyDatetime = datetime.datetime.strftime(localTime, "%A, %b %d, %I:%M%p")
	return fancyDatetime

def getDoctorAvailability(doctor_id, num):
	# This function takes a doctor_id and returns a list of tuples (length num) of the upcoming
	# available timeslots for that doctor. 
	availableTimes = db.session.query(Schedule.timeAvailable).filter(Schedule.timeAvailable>=getCurrentServerUTCTime(), Schedule.doctor_id==doctor_id, Schedule.booked==False).all()
	availableTimes.sort()
	filteredTimes = []
	for x in range(min(num, len(availableTimes))):
		localTime = changeUTCToUserTime(availableTimes[x][0])
		fancyDatetime = datetime.datetime.strftime(localTime, "%A, %b %d, %I:%M%p")
		#fancyDatetime = availableTimes[x][0]
		dateTuple = (localTime, fancyDatetime)
		filteredTimes.append(dateTuple)
	return filteredTimes

def getCurrentServerUTCTime ():
	timezone = 'US/Pacific' ####Change if server is not in Pacific/US timezone
	local_time = datetime.datetime.now() # Enter your user/client's time [var datetime_now = new Date();]
	offsetTime = pytz.timezone(timezone).utcoffset(local_time)
	utc_time = local_time - offsetTime #NOTICE the "-" here
	return utc_time

def changeToUTC (dtime):
	timezone = current_user.timezone
	#timezone = 'US/Pacific'
	local_time = dtime # Enter your user/client's time [var datetime_now = new Date();]
	offsetTime = pytz.timezone(timezone).utcoffset(local_time)
	utc_time = local_time - offsetTime #NOTICE the "-" here
	return utc_time

def changeUTCToUserTime (dtime):
	timezone = current_user.timezone
	#timezone = 'US/Pacific'
	utc_time = dtime
	offsetTime = pytz.timezone(timezone).utcoffset(utc_time)
	local_time = utc_time + offsetTime #NOTICE the "-" here
	return local_time

def findNextWeekday(weekday):
	date = datetime.datetime.now()
	curr_weekday = date.weekday()
	diff = weekday - curr_weekday
	if (diff<0): diff=7+diff
	date += datetime.timedelta(days=diff)
	return date

def createOneYearList(startTime, endTime, weekday, repeat):
	# Take datetime start and end (and day of week as integer) (and repeat as integer, 0=ever week, 1=every other week) and
	# returns a list of recurring 15-min increment times 
	# on that day for one year from current time. 
	# Also account for timezone (list should be in UTC, startTime/endTime are in user's local time).
	OneYearList = []
	if startTime=='-' or endTime=='i':
		return OneYearList

	firstDate = findNextWeekday(weekday)
	dtst = datetime.datetime.strptime(startTime, '%I:%M%p')
	dtStartTime = dtst.replace(day=firstDate.day, month=firstDate.month, year=firstDate.year)
	dtet = datetime.datetime.strptime(endTime, '%I:%M%p')
	dtEndTime = dtet.replace(day=firstDate.day, month=firstDate.month, year=firstDate.year)

	start = changeToUTC(dtStartTime)
	end = changeToUTC(dtEndTime)

	if repeat=='0':
		# repeat every week
		for i in range(0, 50):
			next_start = start
			while next_start < end:
				OneYearList.append(next_start)
				next_start += datetime.timedelta(hours=0.25)
			start += datetime.timedelta(days=7)
			end += datetime.timedelta(days=7)
	elif repeat=='1':
		# repeat every other week
		for i in range(0, 50):
			next_start = start
			while next_start < end:
				OneYearList.append(next_start)
				next_start += datetime.timedelta(hours=0.25)
			start += datetime.timedelta(days=14)
			end += datetime.timedelta(days=14)
	else:
		next_start = start
		while next_start < end:
			OneYearList.append(next_start)
			next_start += datetime.timedelta(hours=0.25)
	return OneYearList


def commitAvailabilityTimes(doctor_id, MegaList):
	# First deletes all existing times with no bookings from schedule table, if exist
	# Takes a list of datetimes and commits them to the Schedule table
	timeSlots = db.session.query(Schedule).filter_by(doctor_id=doctor_id, booked=False).delete()
	db.session.commit()
	
	for dt in MegaList:
		exists = db.session.query(Schedule).filter_by(timeAvailable=dt).first() is not None
		if not exists:
			db.session.add(Schedule(doctor_id=current_user.id, timeAvailable=dt))
	db.session.commit()


def createOneYearListAll(startTimeList, endTimeList, repeat):
	# Takes a list of 7 startTimes and 7 endTimes (starting on monday(0))
	# and calls createOneYearList() for each one.
	# Merges all One-Year lists into one large list.
	# Calls commitAvailabilityTimes() to commit the large datetime list to the schedule table
	MegaList = []
	for i in range(0, len(startTimeList)):
		listOfDates = createOneYearList(startTimeList[i], endTimeList[i], i, repeat)
		MegaList += listOfDates
	MegaList.sort()
	commitAvailabilityTimes(current_user.id, MegaList)


def filteredDoctorIdsUrgency(urgencyString):
	listOfDoctorIds = []
	doc_id_list = [doc.id for doc in db.session.query(Doctor).all()]
	soonest_appt_dict = {}
	currTimeUTC = getCurrentServerUTCTime();
	for doc_id in doc_id_list:
		if getDoctorAvailability(doc_id, 1)==[]:
			continue
		localTimeAvailability = getDoctorAvailability(doc_id, 1)[0][0]
		utcTimeAvailability = changeToUTC(localTimeAvailability)
		timeDelta = utcTimeAvailability - currTimeUTC
		soonest_appt_dict[doc_id] = timeDelta
		if urgencyString == 'Within 6 hours':
			if timeDelta <= datetime.timedelta(hours=6):
				listOfDoctorIds.append(doc_id)
		elif urgencyString == 'Within 12 hours':
			if timeDelta <= datetime.timedelta(hours=12):
				listOfDoctorIds.append(doc_id)
		elif urgencyString == 'Within 24 hours':
			if timeDelta <= datetime.timedelta(hours=24):
				listOfDoctorIds.append(doc_id)
		elif urgencyString == 'Within 48 hours':
			if timeDelta <= datetime.timedelta(hours=48):
				listOfDoctorIds.append(doc_id)
		elif urgencyString == 'Within 72 hours':
			if timeDelta <= datetime.timedelta(hours=72):
				listOfDoctorIds.append(doc_id)
		elif urgencyString == 'Within 1 week':
			if timeDelta <= datetime.timedelta(hours=168):
				listOfDoctorIds.append(doc_id)
		else:
			continue
	return listOfDoctorIds


def validate(email):
	match=re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]*\.*[com|org|edu]{3}$)",email)
	if match:
		return True
	else:
		return False


def get_emailText(lp_email, specialty_txt):
	it = 'Dear GTN, <br><br>A Local Provider has requested physician matching. Here is a description of their problem:'
	et = 'Please determine the physician specialty that is most appropriate for this problem and email the Local Provider at ' + lp_email + '.<br><br>' + 'Here is a list of specialties: ' + specialty_txt + '<br><br>' + 'Sincerely,' + '<br>' + 'The Careify Team'
	return [it,et]











