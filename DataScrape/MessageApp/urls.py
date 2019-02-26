from django.urls import path
from . import views

urlpatterns = [
    # path methods take three arguments; 
    # 1. the route which will point towards /'any prepended route in DataScrape urls.py'/ , 
    # 2. the corresponding register method in views.py, and 
    # 3. the alias we are giving the route which can be accessed in our templates with {% url 'alias' %} tags.
    path('message', views.message, name='message'),
    path('inbox', views.inbox, name='inbox'),
    path('alert', views.inboxAlert, name='alert'),
    path('<int:id>', views.inboxMessages, name='inbox-messages')
]

#path('message', views.message, name='message'),
    # path('<int:id>', views.inbox, name='inbox'),
    # path('alert', views.inboxAlert, name='alert'),
    # path('inbox', views.inboxMessages, name='inbox-messages')