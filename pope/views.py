from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login, logout
from django.contrib.auth.decorators import login_required
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import uuid
from django.shortcuts import get_object_or_404
# Create your views here.

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load the credentials obtained from the Service Account Key file
creds = service_account.Credentials.from_service_account_file(
    'D:\AtlanProject\MAIN\credddddd.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets'],
)

# Create the Sheets API client
service = build('sheets', 'v4', credentials=creds)



def showSheet(request, form_uid):
    spreadsheet_id = '15ah0DcQnitgF0T232_qsQU-q2byA-XPi4ft90hopLBA'
    request = service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range='Sheet1!A1:Z1000')
    request.execute()

# The data to be put into the sheet
    # user_responses = UserResponse.objects.all().filter(form_uid=form_uid)
    user_responses = UserResponse.objects.filter(form_uid=form_uid)
    data = {
        'values': [list(response.responses.values()) for response in user_responses]
    }

    # Update the values in the sheet
    range_name = 'Sheet1!A1'
    request = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=data,
        insertDataOption='INSERT_ROWS',
    )
    response = request.execute()
    return HttpResponse("Data updated in the sheet.")

@login_required(login_url="/orgLogin/")
def pope(request):
    return render(request,'orgLogin.html')


@login_required(login_url="/orgLogin/")
def orgHome(request):
    form_uid=uuid.uuid4()
    if request.method == "POST":
        question = request.POST.get("question")
        ansType = request.POST.get("ansType")

        # Retrieve the dynamically added options
        options = request.POST.getlist("option")

        # Print the question, answer type, and options
        print("Question:", question)
        print("Answer Type:", ansType)
        print("Options:", options)

        # Create a new Questions instance
        new_question = Questions.objects.create(user=request.user, question=question, ansType=ansType)

        # Save options as a list in the JSONField
        new_question.options = options
        new_question.save()
        return redirect('/orgHome')

    queryset = Questions.objects.filter(user=request.user)
    userSet=myUser.objects.filter(user=request.user)
    lst=[]
    for question in queryset:
        lst.append(question.question)
    Form(questions=lst, form_uid=form_uid).save()

    context = {'ques': queryset,'thisUser':userSet, 'form_uid': form_uid }
    return render(request, 'orgHome.html', context)

@login_required(login_url="/orgLogin/")
def orgForm(request, form_uid):
    
    userSet=myUser.objects.filter(user=request.user)
    uuid_list = [user.uuid for user in userSet]
    user_uid=uuid_list[0]
    queryset=Questions.objects.filter(user=request.user)

    

    context = {'ques': queryset,'thisUid':user_uid, 'form_uid':form_uid}
    
    return render(request, 'orgForm.html',context)


def publicForm(request, thisUid, form_uid):
        USER_ID=thisUid
        FORM_ID=form_uid



        formm=get_object_or_404(Form,form_uid= FORM_ID)
        lst=[]
        for ques in formm.questions:
            lst.append(get_object_or_404(Questions,question=ques))
        if request.method == 'POST':
            form_data = request.POST
            user_response = UserResponse.objects.create(form_uid=FORM_ID)
            for question_id, response in form_data.items():
                if question_id != 'csrfmiddlewaretoken' and question_id != 'action':
                    user_response.add_response(question_id, response)

        context={'ques':lst}
        return render(request, 'public_form.html', context)


@login_required(login_url="/orgLogin/")
def delete_question(request, id):
    Questions.objects.get(id=id).delete()
    return redirect('/orgHome')

def orgRegister(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)

        if user.exists():
            messages.error(request, "Username Already Taken!")
            return redirect('/orgRegister/') 

        user=User.objects.create(username=username,
                                    first_name=first_name, last_name=last_name
                                )
        
        user.set_password(password)
        user.save()
        myUser(user=user, uuid=uuid.uuid4()).save()
        messages.info(request, "Account created successfully!")
        return redirect('/orgRegister')
    return render(request, 'orgRegister.html')



def orgLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not User.objects.filter(username=username).exists():
            messages.error(request,'Invalid Username!')
            return redirect('/orgLogin/')
        user=authenticate(request,username=username, password=password)
        if user is None:
            messages.error(request,'Invalid Password!')
            return redirect('/orgLogin/')
            
        
        else:
            login(request,user)
            
            return redirect('/orgHome/')
    return render(request, 'orgLogin.html')


def orgLogout(request):
    logout(request)
    return redirect('/orgLogin/')


# @login_required(login_url="/orgLogin/")
# def orgHome(request):
#     return render(request, 'orgHome.html')