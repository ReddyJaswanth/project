from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.pk} for {self.user.username}"

class UserChat(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    user_input = models.TextField()
    result = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session.user.username} - {self.session.session_id} - {self.id}"
    
class Document(models.Model):
    chat = models.ForeignKey('UserChat', related_name='documents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='chat_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document {self.file.name} for chat {self.chat.id}"
