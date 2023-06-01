from __future__ import division
from flask import Flask, render_template, url_for, request, redirect, session, flash, g
import firebase_admin
from firebase_admin import credentials, firestore
from firebase_admin import auth
import os
from datetime import datetime
import pandas as pd
import pyrebase
# from qrcode_small import main_value_small
# from qrcode_large import main_value_large

# from read_barcode import open_camera
# from read_barcode_long_wait import open_camera_for_long

app = Flask(__name__)

app.secret_key = '2' # for flask session
# Use a service account
cred = credentials.Certificate('aventus_for_hosting.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# pyrebase init
# Your web app's Firebase configuration
firebaseConfig = {
  'apiKey': "AIzaSyDIerahYw7xS6madhWGYuvF2n8A3-VMUkg",
  'authDomain': "aventus-b0068.firebaseapp.com",
  'databaseURL': "https://aventus-b0068-default-rtdb.asia-southeast1.firebasedatabase.app",
  'projectId': "aventus-b0068",
  'storageBucket': "aventus-b0068.appspot.com",
  'messagingSenderId': "1004778993565",
  'appId': "1:1004778993565:web:5ccb91f7a09dede0342174",
  'measurementId': "G-LEE5266T98"
};

firebase = pyrebase.initialize_app(firebaseConfig)
auth_pyrebase = firebase.auth()
# auth=firebase_admin.auth

# lock = threading.Lock()

@app.before_request
def before_request():
    g.df=pd.read_csv('teams.csv')



@app.route('/', methods = ['GET'])
def home_page():
        if 'user' in session:
            return render_template('home_page.html')
        else:
            return render_template('sign_in_page.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method=='GET':
        return render_template('sign_in_page.html')
    elif request.method=='POST':
        password=request.form['password']
        email="avirakshit2002@gmail.com"
        try:
            # user=auth.get_user_by_email(email)
            user = auth_pyrebase.sign_in_with_email_and_password(email, password)
            # auth.verify_password(user.uid, password)
            # user=auth.sign_in_with_email_and_password(email, password)
            if user:
            # user=auth.sign_in_with_email_and_password(email, password)
                session['user']=email
                message='Signed In'
        except auth.EmailAlreadyExistsError:
            message= 'Email already exists.'
        return redirect('/scan_barcode/'+session['uid'])
        # return render_template('home_page.html', message=message)



# FOR ENTERING MASTER CHECKIN SECOND PAGE
@app.route('/add_entry', methods=['POST'])
def add_entry():
    # if request.method=='GET':
    #      return render_template('add_entry_page.html')
    
    if request.method=='POST':


        # results=open_camera()
        # team_member_id=str(results.text)
        # team_member_id=session[team_member_id]
        team_member_id=session['uid']
        team_name= request.form['team_name']
        team_member= request.form['team_member']
        track=request.form['track']
        gender=request.form['gender']
        team_id=request.form['team_id']
        college=request.form['college']
        college_id=request.form.get('college_id')
        consent_form=request.form.get('consent_form')
        
        if college_id:
            final_college_id='True'
        else:
            final_college_id='False'
        
        if consent_form:
            final_consent_form='True'
        else:
            final_consent_form='False'

        now = datetime.now()
        entry_time=now.strftime("%d/%m/%Y %H:%M:%S")

        db.collection(track).document(team_id).set({
             'team_name':team_name
        })

        db.collection(track).document(team_id).collection(team_member_id).document(team_member).set({
             'sign_in_time':entry_time,
             'gender':gender,
             'college_id': final_college_id,
             'consert_form': final_consent_form,
             'college':college,
             'count':0
        })
        # flash('Participants successfuly registered.')
        # return render_template('add_entry.html', text=['team_id_csv', 'track_csv', 'team_name_csv', 'team_member_csv'])
        message='Participant successfuly registered.'
        return render_template('barcode_reader_page.html',message=message)


#FOR CHECKING IN CHECK OUT MAIN LINK
@app.route('/scan_barcode/<uid>', methods=['GET'])
def scan_barcode(uid):
    if request.method=='GET':
        if 'user' in session:
            # lock.acquire()
            # process_output(team_member_id)
            # lock.release()
            # team_member_id=open_camera()
            # while team_member_id==None:
            #     pass


            #FOR TEAM MEMBERS
            member_text_add=''
            #FOR TEAMS
            text_for_team=''
            flag=0
            team_member_id=uid
            session['uid']=uid
            # for team_member_id in team_member_ids:
                # print(type(team_member_id))
            participant_row=g.df.loc[g.df['UID']==team_member_id]
            count_csv=participant_row.at[participant_row.index[0], 'count']
            # team_id=str(participant_row.at[participant_row.index[0], 'Team Code'])
            team_name=participant_row.at[participant_row.index[0], 'Team Name']
            gender=participant_row.at[participant_row.index[0], 'Gender']
            college=participant_row.at[participant_row.index[0], 'college']
            team_id=team_member_id[0:len(team_member_id)-3]
            track=participant_row.at[participant_row.index[0], 'Project Tracks']
            team_member=str(participant_row.at[participant_row.index[0], 'First Name']+' '+participant_row.at[participant_row.index[0], 'Last Name'])


            if count_csv==0:
                g.df.loc[g.df['UID'] == team_member_id, 'count'] = 1
                g.df.to_csv('teams.csv', index=False)
                check=db.collection(track).document(team_id)
                team_members_id=[]
                team_members_temp=check.collections()
                for m in team_members_temp:
                    team_members_id.append(m.id)
                if team_member_id in team_members_id:
                    message='Member already registered'
                    return render_template('barcode_reader_page.html', message=message)
                # print(team_member_id)
                return render_template('add_entry_page.html', text=[team_id, track, team_name, team_member, gender, team_member_id, college])

            else:
                available_teams=[]
                available_teams_temp = db.collection(track).stream()
                for team in available_teams_temp:
                    available_teams.append(team.id)
                    
                if team_id not in available_teams:
                    flag=1
                    t2='\n'+str(team_id)+' ,not checked in.'
                    text_for_team+=t2
                else:
                    check=db.collection(track).document(team_id)
                    team_member_temp=check.collections()
                    team_members=[]

                    for i in team_member_temp:
                        team_members.append(i.id)
                    if team_member_id in team_members:

                        now = datetime.now()
                        lastseen_time=now.strftime("%d/%m/%Y %H:%M:%S")
                        doc=db.collection(track).document(team_id).collection(team_member_id).document(team_member).get()
                        count=doc.get('count')
                        if count==0:
                            s='IN'
                            db.collection(track).document(team_id).collection(team_member_id).document(team_member).update({
                            'status1':['IN', lastseen_time],
                            'count':1
                            })
                        elif count%2==1:
                            final_count=count+1
                            final_status='status'+str(final_count)
                            s='OUT'
                            db.collection(track).document(team_id).collection(team_member_id).document(team_member).update({
                            final_status:['OUT', lastseen_time],
                            'count':final_count
                            })
                        elif count%2==0 and count!=0:
                            final_count=count+1
                            final_status='status'+str(final_count)
                            s='IN'
                            db.collection(track).document(team_id).collection(team_member_id).document(team_member).update({
                            final_status:['IN', lastseen_time],
                            'count':final_count
                            })
                    else:
                        flag=1
                        t1=str(team_member_id)+' '
                        member_text_add+=t1
                        # text_add+=t1
                if flag==0:
                    message="Successfully updated "+str(s)+' '+str(team_member_id)
                else:
                    message="Not Updated for"+" "+ member_text_add+text_for_team
                return render_template('scan_page_first_page.html', message=message)
            
        elif 'user' not in session:
            session['uid']=uid
            return render_template('sign_in_page.html')
                    # else:
                #     message='Participant not checked in'
            #     return render_template('scan_page_first_page.html', message=message)


#NOT NEEDED USED FOR CHECKIN CHECKOUT SECOND PAGE
@app.route('/scan_update', methods=['POST'])
def scan_update():
    # if request.method=='':
    #     return render_template('scan_page.html')
    team_member_id=session['uid']
    status=request.form['status']
    participant_row=g.df.loc[g.df['UID']==team_member_id]
    team_id=team_member_id[0:len(team_member_id)-3]
    track=participant_row.at[participant_row.index[0], 'Project Tracks']
    team_name=participant_row.at[participant_row.index[0], 'Team Name']
    team_member=str(participant_row.at[participant_row.index[0], 'First Name']+' '+participant_row.at[participant_row.index[0], 'Last Name'])

    now = datetime.now()
    lastseen_time=now.strftime("%d/%m/%Y %H:%M:%S")
    
    doc=db.collection(track).document(team_id).collection(team_member_id).document(team_member).get()
    count=doc.get('count')
    final_count=count+1
    last_seen='status'+str(count+1)
    db.collection(track).document(team_id).collection(team_member_id).document(team_member).update({
            last_seen:[status, lastseen_time],
            'count':final_count
        })
    message='The Status has been updated.'
    return render_template('scan_page_first_page.html', message=message)


#STATUS OF ALL TEAMS
@app.route('/status_first', methods=['GET', 'POST'])
def status_first():
    if request.method=='GET':
        return render_template('status_first_page.html')
    elif request.method=='POST':
        team_id=request.form['team_id']
        track=request.form['track']
        session['team_id']=team_id
        session['track']=track
        return redirect('/status_all_team_member')



@app.route('/status_all_team_member', methods=['GET', 'POST'])
def status_all_team_member():
    if request.method=='GET':
        team_id=session['team_id']
        track=session['track']
        doc=db.collection(track).document(team_id)
        team_member_temp=doc.collections()
        team_members=[]
        for i in team_member_temp:
            team_members.append(i.id)
        all_timings={}
        member_ids=[]
        member_names=[]
        for member in team_members:
            member_ids.append(member)
            participant_row=g.df.loc[g.df['UID']==member]
            team_member=str(participant_row.at[participant_row.index[0], 'First Name']+' '+participant_row.at[participant_row.index[0], 'Last Name'])
            team_name=participant_row.at[participant_row.index[0], 'Team Name']
            member_names.append(team_member)

            details=db.collection(track).document(team_id).collection(member).document(team_member).get()
            details=details.to_dict()
            count=details['count']
            master_checkin=details['sign_in_time']
            all_timings[member]=[]
            for i in range(0, count):
                status='status'+str(i+1)
                all_timings[member].append(details[status])
            count=0
        session.clear()
        return render_template('status_all_team_member_page.html', all_timings=all_timings, team_name=team_name, member_ids=member_ids, member_names=member_names, master_checkin=master_checkin)

    

     



if __name__ == '__main__':
    app.run(debug=True)
