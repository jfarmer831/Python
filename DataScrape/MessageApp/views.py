from django.shortcuts import render
from .models import MessageMod 
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse

# Create your views here.


def message(request):
  
    if request.method == 'POST':

        subject = request.POST['subject'] # define where on template text will come from 
        content = request.POST['content']
        reciever = request.POST['reciever']
        sender = request.POST['sender']
    
        reciever_used = User.objects.get(username=reciever) # gets User object from  database based on input 'reciever'
        sender_used = User.objects.get(username=sender) # gets User object from database based on input 'sender'
        
        message = MessageMod() # create  an object that will interact with database item MessageMod in models
        message.msg_content = content #based on object define the above varibles to associate with table rows in models
        message.msg_sub = subject
        message.msg_content = content
        message.reciever = reciever_used
        message.sender = sender_used
        message.save() # don't forget to save changes to database

        return render(request, 'MessageApp/message.html', {'message': message})

    else:
        return render(request,"MessageApp/message.html", {})

def inbox(request):
    if request.user.is_authenticated:
        currentUser = request.user.id
        messages = MessageMod.objects.filter(reciever_id=currentUser)
        return render(request, 'MessageApp/inbox.html', {'messages': messages})
    
    else:
        return render(request, "MessageApp/inbox.html", {})

def inboxMessages(request, id):
    currentUser = request.user.id
    messages = MessageMod.objects.filter(reciever_id=currentUser)
    return render(request, "MessageApp/inbox-messages.html", {'messages': messages} )


def inboxAlert(request):
    x = "is this working"
    print(x)

    return render(request, 'MessageApp/inbox-alert.html', {'x': x})
