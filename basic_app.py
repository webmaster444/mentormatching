# This file contains an example Flask-User application.
# To keep the example simple, we are applying some unusual techniques:
# - Placing everything in one file
# - Using class-based configuration (instead of file-based configuration)
# - Using string-based templates (instead of file-based templates)

from datetime import datetime

from flask import Flask, current_app, request, redirect, render_template_string, render_template
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
import json
import requests
from bs4 import BeautifulSoup
import math
import sys
import random
import time

expertises = [
    "Accounting","Advertising & PR", "Agriculture","Anthropology","Architecture and planning","Artificial intelligence and Machine learning","Audio/video technology and Communication","Automotive Design","Auto Mechanic","Banking and Investing","Bilogy","Biotech","Business management and administration","Chemistry","Computer Science","Construction","Divinity","Earth Sciences","Economics","Education and Training","Engineering","Environmental studies and Forestry","Family and Consumer science","Fashion Design and Manufacture","Finance","Fine arts","Forestry","Geography","Government and Public Administration","Health Science","History","Hospitality and Tourism","Human Resource Management","Human Services(nursing, psychology)","Information Technology","Insurance","Interior Design","Information Affairs","Journalism and Media studies","Law, Public Safety, Corrections and Security","Library and Museum studies","Marketing, Sales, and Service", "Mathematics","Medicine","Military Sciences","Natural Resource management","Non-profit Management","Performing arts","Philosophy","Physics","Politics","Publishing","Real Estate","Religion","Science, Technology, Engineering and Mathematics","Sociology","Social Work", "Sports and Fitness coaching","Telecommunication","Theology","Transport,Distribution and Logistics","Veterinary Science"
]

education_level = [
    "Pre-vocational secondary education (VMBO)","Senior general secondary education (HAVO)","Pre-university education (VWO)","Senior secondary vocational education and training (MBO)","Bachelor's degree","Master's degree","Doctorate (PhD)", "Post-doctorate","n.a."
]

corporate_business = [
    "Entry level","Administration",'Middle management', "Senior management","N.a."
]

entrepreneurs = [
    "Start-up", "Mature business", "Expanding enterprise", "N.a."
]

personality_types = [
    "Unknown, I like to do the official test", "Unknown, I don't want to do the offical test","ISTJ","ISFJ","ESTP","ESFP","INTJ","INFJ","ENTP","ENFP","ISTP","INTP","ESTJ","ENTJ","ISFP","INFP","ESFJ","ENFJ"
]

careers = [
    "Am I Ready For A Job Change?", "How Can I Do My Current job more effictively?","What strategy do i follow to achieve my goal?","how do i setup my own business?","how do i make my business flourish"
]

empowerments = [
    "How do i enhance my visibliity and power in my organization","how do i survive in an old boys' network?"
]

educations = [
    "which major am i going to choose?","what new knowledge do i need?"
]

family_options = [
    'how to manage work-life balance?'
]
personal_skills = [
    'how to communicate effectively?','how do i negotiate?','how to improve my self-esteem/confidence?','how do i improve my functional/technical skills?','how do i improve my efficiency?','what are my weaknesses and what are my strengths?'
]

fundings = [
    'how do i find a bursary?','how do i find a research budget?','how do i find startup funds?'
]
# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'jlmobile710@gmail.com'
    MAIL_PASSWORD = 'eoqldir111'
    MAIL_DEFAULT_SENDER = '"FX Risk App" <noreply@gmail.com>'

    # Flask-User settings
    # Shown in and email templates and page footers
    USER_APP_NAME = "FX Risk App"
    USER_ENABLE_EMAIL = True        # Enable email authentication
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_ALLOW_LOGIN_WITHOUT_CONFIRMED_EMAIL = True
    USER_EMAIL_SENDER_NAME = USER_APP_NAME
    USER_EMAIL_SENDER_EMAIL = "noreply@example.com"
    USER_LOGIN_URL = "/login"
    USER_LOGIN_TEMPLATE = "login.html"
    USER_AFTER_LOGIN_ENDPOINT = 'account_page'
    USER_REGISTER_URL = "/register"
    USER_REGISTER_TEMPLATE = "register.html"
    USER_AFTER_REGISTER_ENDPOINT = 'account_page'
    USER_LOGOUT_URL = "/logout"
    USER_AFTER_LOGOUT_ENDPOINT = "user.login"

# Create Flask app load app.config
app = Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')

# Initialize Flask-BabelEx
babel = Babel(app)

# Initialize Flask-SQLAlchemy
db = SQLAlchemy(app)

# Setup Flask DB
class TimestampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

# Define the User data-model.
# NB: Make sure to add flask_user UserMixin !!!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(),
                       nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column(db.String(255, collation='NOCASE'),
                      nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')

    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')
    def has_role(self, role):
        return current_user.has_roles(role)

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey(
        'users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey(
        'roles.id', ondelete='CASCADE'))

class UserDetail(db.Model):
    __tablename__ = 'user_detail'
    id = db.Column(db.Integer(), primary_key=True)
    # User information
    name = db.Column(db.String(100, collation='NOCASE'), nullable=True, server_default='')
    date_of_birth = db.Column(db.String(100, collation='NOCASE'), nullable=True, server_default='')
    country_of_residence = db.Column(
        db.String(100, collation='NOCASE'), nullable=True, server_default='')
    city_of_residence = db.Column(
        db.String(100, collation='NOCASE'), nullable=True, server_default='')
    phoneno = db.Column(
        db.String(100, collation='NOCASE'), nullable=True, server_default='')
    preferred_language = db.Column(db.String(100,collation="NOCASE"), nullable=True, server_default='English')
    years_of_experience = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    field_of_expertise = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    before_mentor = db.Column('before_mentor', db.Boolean(),nullable=True, server_default='0')
    career = db.Column(db.String(500, collation='NOCASE'), nullable=True, server_default='')
    empowerment = db.Column(db.String(500, collation='NOCASE'), nullable=True, server_default='')
    education = db.Column(db.String(500, collation='NOCASE'), nullable=True, server_default='')
    family = db.Column(db.String(500, collation='NOCASE'), nullable=True, server_default='')    
    personal_skills = db.Column(db.String(500, collation='NOCASE'), nullable=True, server_default='')    
    funding = db.Column(db.String(500, collation='NOCASE'), nullable=True, server_default='')    
    highest_education_level = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')    
    corporate_business_position = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')    
    work_as_entrepreneur = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')    
    personality_type = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')    
    mentor_or_mentee = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='mentee')    
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False, unique=True)
    is_active = db.Column('is_active', db.Boolean(),nullable=False, server_default='1')
    assigned_users = db.Column(db.String(200, collation='NOCASE'), nullable=True, server_default='[]')
    user = db.relationship('User')

#Normalized Google Distance table
class NGD(db.Model):
    __tablename__ = 'ngds'
    id = db.Column(db.Integer, primary_key=True)
        
    word1 = db.Column(db.String(255, collation='NOCASE'),nullable=False, unique=False)
    word2 = db.Column(db.String(255, collation='NOCASE'),nullable=False, unique=False)
    ngd = db.Column(db.REAL(255), nullable=False, server_default='')

def add_detail(user_id, detail):
    detail = UserDetail(
        user_id=user_id,
        name=detail['name'],        
        date_of_birth=detail['date_of_birth'],        
        country_of_residence=detail['country_of_residence'],        
        city_of_residence=detail['city_of_residence'],        
        phoneno=detail['phoneno'],        
        preferred_language=detail['preferred_language'],        
        years_of_experience=detail['years_of_experience'],        
        field_of_expertise =detail['field_of_expertise'],        
        before_mentor=detail['before_mentor'],        
        career=detail['career'],        
        empowerment=detail['empowerment'],        
        education=detail['education'],        
        family=detail['family'],        
        personal_skills=detail['personal_skills'],        
        funding=detail['funding'],        
        highest_education_level=detail['highest_education_level'],        
        corporate_business_position =detail['corporate_business_position'],        
        work_as_entrepreneur=detail['work_as_entrepreneur'],        
        personality_type=detail['personality_type'],    
        mentor_or_mentee=detail['mentor_or_mentee'],
        is_active=detail['is_active'],
    )
    db.session.add(detail)
    db.session.commit()

def number_of_results(text):
    time.sleep(1)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    text = text.replace("&","")
    r = requests.get("https://www.google.com/search?q="+text.replace(" ","+"),params={"gl":"us"},headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    res = soup.find("div", {"id": "result-stats"})
    try:
        for t in res.text.split():
            try:
                number = float(t.replace(",",""))
                return number
            except:
                pass
    except:
        return 25270000000

def normalized_google_distance(w1, w2):
    f_w1 = math.log(number_of_results(w1),2)
    f_w2 = math.log(number_of_results(w2),2)
    N = 25270000000.0
    N = math.log(N,2)
    f_w1_w2 = math.log(number_of_results(w1+" "+w2),2)

    return (max(f_w1,f_w2) - f_w1_w2) / (N - min(f_w1,f_w2))

class CustomUserManager(UserManager):
    def login_view(self):
        """Prepare and process the login form."""

        # Authenticate username/email and login authenticated users.

        safe_next_url =  self._get_safe_next_url('next', self.USER_AFTER_LOGIN_ENDPOINT)

        # Immediately redirect already logged in users
        if self.call_or_get(current_user.is_authenticated) and self.USER_AUTO_LOGIN_AT_LOGIN:
            return redirect(safe_next_url)

        # Initialize form
        login_form = self.LoginFormClass(request.form)

        if request.method != 'POST':
            return render_template('login.html')
        
        # Retrieve User
        user = None
        if self.USER_ENABLE_EMAIL:
            # Find user by email (with form.email)
            user, _ = self.db_manager.get_user_and_user_email_by_email(
                login_form.email.data)
        if user:
            safe_next_url = self.make_safe_url(login_form.next.data)
            return self._do_login_user(user, safe_next_url, True)
        

    def register_view(self):
        safe_reg_next = self._get_safe_next_url('reg_next', self.USER_AFTER_REGISTER_ENDPOINT)

        # Immediately redirect already logged in users
        if self.call_or_get(current_user.is_authenticated) and self.USER_AUTO_LOGIN_AT_LOGIN:
            return redirect(safe_reg_next)

        # Initialize form
        register_form = self.RegisterFormClass(request.form)
        page_number = request.args.get('p') or 1

        if request.method == 'POST':
            tmp_email = request.form.getlist('email').pop()
            tmp_user = User.query.filter_by(email=tmp_email).first() 
            if tmp_user != None:
                return render_template('register.html', msg="Sorry, that email is already exist")

            user = self.db_manager.add_user()
            register_form.populate_obj(user)
            user_email = self.db_manager.add_user_email(
                user=user, is_primary=True)            
            register_form.populate_obj(user_email)
            user.password = self.hash_password(user.password)

            self.db_manager.save_user_and_user_email(user, user_email)
            self.db_manager.commit()
            
            add_detail(user.id, {
                'name': request.form.getlist('name').pop(),              
                'date_of_birth': request.form.getlist('date_of_birth').pop(),
                'country_of_residence': request.form.getlist('country_of_residence').pop(),
                'city_of_residence': request.form.getlist('city_of_residence').pop(),
                'phoneno': request.form.getlist('phoneno').pop(),
                'preferred_language': request.form.getlist('preferred_language').pop(),
                'years_of_experience': request.form.getlist('years_of_experience').pop(),
                'field_of_expertise': request.form.getlist('field_of_expertise').pop(),
                'before_mentor': 1 if request.form.get('before_mentor') else 0,
                'career': json.dumps(request.form.getlist('career')) if request.form.get('career') else "[]",
                'empowerment': json.dumps(request.form.getlist('empowerment')) if request.form.get('empowerment') else "[]",
                'education':json.dumps( request.form.getlist('education')) if request.form.get('education') else "[]",
                'family': json.dumps(request.form.getlist('family')) if request.form.get('family') else "[]",
                'funding': json.dumps(request.form.getlist('funding')) if request.form.get('funding') else "[]",
                'personal_skills': json.dumps(request.form.getlist('personal_skills')) if request.form.get('personal_skills') else "[]",
                'highest_education_level': request.form.getlist('highest_education_level').pop(),
                'corporate_business_position': request.form.getlist('corporate_business_position').pop(),
                'work_as_entrepreneur': request.form.getlist('work_as_entrepreneur').pop(),
                'personality_type': request.form.getlist('personality_type').pop(),
                'mentor_or_mentee': request.form.getlist('mentor_or_mentee').pop(),
                'is_active':1,
            })            

            return self._do_login_user(user, safe_reg_next, False)

        return render_template('register.html', expertises=expertises, personality_types=personality_types, education_levels=education_level,corporate_business=corporate_business,entrepreneurs=entrepreneurs, careers=careers,empowerments=empowerments, educations=educations, family=family_options, personal_skills=personal_skills,fundings=fundings)

# Setup Flask-User and specify the User data-model
user_manager = CustomUserManager(app, db, User)

# Create all database tables
db.create_all()

# Create 'member@example.com' user with no roles
if not User.query.filter(User.email == 'admin@example.com').first():
    user = User(
        email='admin@example.com',
        email_confirmed_at=datetime.utcnow(),
        password=user_manager.hash_password('Password1'),
    )
    user.roles.append(Role(name='Admin'))
    user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()
    db.session.flush()
    add_detail(user.id, {
        'name': 'Admin',                
        'phoneno': '9090909090',
        'date_of_birth': '1990/04/12',
        'country_of_residence':"UK",
        'city_of_residence':'London',
        'preferred_language':'English',
        'years_of_experience':5,
        'field_of_expertise': 'Software Engineering',
        'before_mentor': 0,
        'career': '[]',
        'empowerment': '[]',
        'education': '[]',
        'family': '[]',
        'personal_skills': '[]',
        'funding': '[]',
        'highest_education_level': 'MBA',
        'corporate_business_position': 'YES',
        'work_as_entrepreneur': 'YES',
        'personality_type': 'YES',   
        'mentor_or_mentee': 'mentor',
        'is_active':1,
    })

def get_matching_users(user_id):
    users = User.query.all()
    detail = UserDetail.query.filter_by(user_id=user_id).first()
    cu_role = detail.mentor_or_mentee
    cu_language = detail.preferred_language
    if cu_role=="mentor":
        user_details = UserDetail.query.filter_by(mentor_or_mentee="mentee",preferred_language=cu_language).all()
        matching_rate = {}
        for user in user_details:
            matching_rate[user.user_id] = get_matching_rate(detail, user)
    else:
        user_details = UserDetail.query.filter_by(mentor_or_mentee="mentor",preferred_language=cu_language).all()
        matching_rate = {}
        for user in user_details:
            matching_rate[user.user_id] = get_matching_rate(detail, user)

    if matching_rate=={}:
        return None

    temp = min(matching_rate.values()) 
    if temp < 5:
        res = [key for key in matching_rate if matching_rate[key] == temp]     
        return res
    return None
def get_or_calc_match_rate(w1,w2):
    rate_exist = NGD.query.filter_by(word1=w1,word2=w2).first() == None and NGD.query.filter_by(word1=w2,word2=w1).first()== None
    if rate_exist:
        rate = normalized_google_distance(w1, w2)
        ngd_pair = NGD(
            word1=w1,
            word2=w2,        
            ngd = rate,
        )
        db.session.add(ngd_pair)
        db.session.commit()
    else:
        if NGD.query.filter_by(word1=w1,word2=w2).first() == None:
            ngd_pair = NGD.query.filter_by(word1=w2,word2=w1).first()
            rate = ngd_pair.ngd
        else:
            ngd_pair = NGD.query.filter_by(word1=w1,word2=w2).first()
            rate = ngd_pair.ngd
    return rate

def get_matching_rate(cu_detail, user_detail):
    match_rate = 0
    #Field of expertise
    if cu_detail.field_of_expertise == user_detail.field_of_expertise:
        match_rate += 0
    else:
        w1 = cu_detail.field_of_expertise
        w2 = user_detail.field_of_expertise
        match_rate += get_or_calc_match_rate(w1,w2)
    
    # Highest education level
    if cu_detail.highest_education_level == user_detail.highest_education_level:
        match_rate += 0
    else:
        w1 = cu_detail.highest_education_level
        w2 = user_detail.highest_education_level
        match_rate += get_or_calc_match_rate(w1,w2)

    # Corporate Business Position
    if cu_detail.corporate_business_position == user_detail.corporate_business_position:
        match_rate += 0
    else:
        w1 = cu_detail.corporate_business_position
        w2 = user_detail.corporate_business_position
        match_rate += get_or_calc_match_rate(w1,w2)

    # Personality Type
    if cu_detail.personality_type == user_detail.personality_type:
        match_rate += 0
    else:
        w1 = cu_detail.personality_type
        w2 = user_detail.personality_type
        match_rate += get_or_calc_match_rate(w1,w2)

    return match_rate

def add_routes():
    """ Add Routes to Flask App """

    # The Members page is only accessible to authenticated users
    @app.route('/admin/members')
    def member_page():
        if current_user.has_roles('Admin'):
            users = User.query.all()
            users_array = []
            for user in users:
                detail = UserDetail.query.filter_by(user_id=user.id).first()
                if detail!=None:
                    users_array.append([user.id, user.email, detail.name, detail.mentor_or_mentee, detail.date_of_birth,detail.country_of_residence, detail.city_of_residence])
                            
            return render_template('./admin/members.html', users=users_array)
        return redirect('/account')

    @app.route('/register')
    def register_page():
        return render_template('./register.html')
    
    @app.route('/find-matches',methods=['POST'])
    def find_matches():
        matched_user = get_matching_users(current_user.id)
        print(matched_user)
        detail = UserDetail.query.filter_by(user_id=current_user.id).first()
        if matched_user==None:
            return "Sorry but not matching mentor/mentee"
        current_assigned_users = json.loads(detail.assigned_users)
        if matched_user[0] in set(current_assigned_users) : 
            return "No more new matches"
        else:
            current_assigned_users.append(matched_user[0])
        detail.assigned_users= json.dumps(current_assigned_users)
        db.session.commit()
        
        return "Test"
    @app.route('/account', methods=['GET','POST'])
    # @login_required
    def account_page():   
        if not current_user.is_authenticated:
            return redirect('/login')                 
        user = User.query.filter_by(email=current_user.email).first()
        if request.method == 'POST':
            detail = UserDetail.query.filter_by(user_id=user.id).first()            
            detail.name = request.form.getlist('name')[0]      
            detail.date_of_birth = request.form.getlist('date_of_birth').pop()
            detail.country_of_residence= request.form.getlist('country_of_residence').pop()
            detail.city_of_residence= request.form.getlist('city_of_residence').pop()
            detail.phoneno= request.form.getlist('phoneno').pop()
            detail.preferred_language= request.form.getlist('preferred_language').pop()
            detail.years_of_experience= request.form.getlist('years_of_experience').pop()
            detail.field_of_expertise= request.form.getlist('field_of_expertise').pop()
            detail.before_mentor= 1 if request.form.get('before_mentor') else 0
            detail.career= json.dumps(request.form.getlist('career')) if request.form.get('career') else "[]"
            detail.empowerment= json.dumps(request.form.getlist('empowerment')) if request.form.get('empowerment') else "[]"
            detail.education=json.dumps( request.form.getlist('education')) if request.form.get('education') else "[]"
            detail.family= json.dumps(request.form.getlist('family')) if request.form.get('family') else "[]"
            detail.funding= json.dumps(request.form.getlist('funding')) if request.form.get('funding') else "[]"
            detail.personal_skills= json.dumps(request.form.getlist('personal_skills')) if request.form.get('personal_skills') else "[]"
            detail.highest_education_level= request.form.getlist('highest_education_level').pop()
            detail.corporate_business_position= request.form.getlist('corporate_business_position').pop()
            detail.work_as_entrepreneur= request.form.getlist('work_as_entrepreneur').pop()
            detail.personality_type = request.form.getlist('personality_type').pop()
            detail.mentor_or_mentee = request.form.getlist('mentor_or_mentee').pop()
            db.session.add(detail)
            db.session.commit()
        
        detail = UserDetail.query.filter_by(user_id=user.id).first()        
        cu_career = json.loads(detail.career)
        cu_funding = json.loads(detail.funding)
        cu_personal_skill = json.loads(detail.personal_skills)
        cu_family = json.loads(detail.family)
        cu_empowerment = json.loads(detail.empowerment)
        cu_education = json.loads(detail.education)        
        assigned_users = []
        for id in json.loads(detail.assigned_users):
            detail = UserDetail.query.filter_by(user_id=id).first()            
            assigned_users.append([detail.user_id, detail.name, detail.date_of_birth, detail.phoneno, detail.city_of_residence])

        return render_template(
            './account.html',
            detail=detail,
            email=current_user.email,
            name=detail.name,            
            cu_career=cu_career,
            cu_funding=cu_funding,
            cu_family = cu_family,
            cu_personal_skill = cu_personal_skill,
            cu_empowerment = cu_empowerment,
            cu_education = cu_education,
            role=detail.mentor_or_mentee,
            expertises=expertises, personality_types=personality_types, education_levels=education_level,corporate_business=corporate_business,entrepreneurs=entrepreneurs, careers=careers,empowerments=empowerments, educations=educations, family=family_options, personal_skills=personal_skills,fundings=fundings,assigned=assigned_users            
        )

    @app.route('/contact')
    def contact_page():        
        return render_template(
            './contact.html'            
        )

    @app.route('/')
    def index():
        return redirect('/login')


# Start development web server
if __name__ == '__main__':
    # Setup Flask Server Routes    
    add_routes()
    app.run(host='0.0.0.0', port=5000, debug=True)
