from django.db import models

class EmailAccount(models.Model):
  email = models.EmailField(unique=True)
  password = models.CharField(max_length=255)
  provider = models.CharField(max_length=20, choices=[('yandex', 'Yandex'), ('gmail', 'Gmail'), ('mailru', 'Mail.ru')])

class Message(models.Model):
  email_account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE)
  subject = models.CharField(max_length=255)
  sent_date = models.DateTimeField()
  received_date = models.DateTimeField()
  body = models.TextField()
  attachments = models.JSONField(default=list) # Массив имен прикрепленных файлов