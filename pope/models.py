from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.middleware import get_user
# Create your models here.
import uuid

def get_default_user_id():
    user = get_user()
    return user.pk if user and user.is_authenticated else None



class Questions(models.Model):
    ANSWER_TYPE_CHOICES = (
        ('Text Answer', 'Text Answer'),
        ('Multiple Choice', 'Multiple Choice'),
    )

    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)

    question = models.CharField(max_length=300)
    ansType = models.CharField(max_length=20, choices=ANSWER_TYPE_CHOICES)
    options = models.JSONField(blank=True, null=True)
    

    def is_multiple_choice(self):
        return self.ansType == 'Multiple Choice'

class myUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class UserResponse(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    form_uid=models.CharField(max_length=300, default="sanyamjain")
    responses = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    def add_response(self, question_id, response):
        self.responses[question_id] = response
        self.save()

class Form(models.Model):
    form_uid = models.CharField(max_length=300, default=uuid.uuid4, unique=True)
    questions = models.JSONField()

    

