from django.db import models

class Profile(models.Model):
    text = models.CharField(max_length=4096)

class Member(models.Model):
    username = models.CharField(max_length=16,primary_key=True)
    password = models.CharField(max_length=16)
    profile = models.OneToOneField(Profile, null=True)

    def __str__(self):
        return self.username

class Message(models.Model):
    user = models.ForeignKey(Member, related_name='%(class)s_user')
    recip = models.ForeignKey(Member, related_name='%(class)s_recip')
    pm = models.BooleanField(default=True)
    time = models.DateTimeField()
    text = models.CharField(max_length=4096)

class FriendRequests(models.Model):
    sender = models.ForeignKey(Member, related_name='%(class)s_sender')
    recipient = models.ForeignKey(Member, related_name='%(class)s_recipient')
    status = models.BooleanField(default=True)

class Friends(models.Model):
    friend1 = models.ForeignKey(Member, related_name='%(class)s_friend1')
    friend2 = models.ForeignKey(Member, related_name='%(class)s_friend2')
