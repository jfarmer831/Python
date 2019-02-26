from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class MessageMod(models.Model):
    sender = models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    reciever = models.ForeignKey(User, related_name="reciever", on_delete=models.CASCADE)
    msg_sub = models.CharField(max_length=100, default='')
    msg_content = models.TextField()
    datesent = models.DateTimeField(auto_now_add=True)


