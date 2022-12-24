from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Room(models.Model):
    name = models.CharField(max_length=120, null=True, blank=False)

    def __str__(self):
        return self.name

class Message(models.Model):
    sender = models.ForeignKey(User, blank=False, null=True, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, blank=False, null=True, on_delete=models.CASCADE)
    message = models.TextField()

    def __str__(self):
        return self.sender.username