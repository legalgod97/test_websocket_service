from channels.generic.websocket import AsyncWebsocketConsumer
from .models import EmailAccount, Message
import imaplib
import email
import json

class MessageConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    self.email_account = EmailAccount.objects.get(id=1) # Получите аккаунт из запроса
    await self.accept()

  async def disconnect(self, code):
    pass

  async def start_fetch(self, event):
    await self.fetch_messages()

  async def fetch_messages(self):
    # Установите соединение с почтовым сервером
    imap = imaplib.IMAP4_SSL(self.email_account.provider + '.com')
    imap.login(self.email_account.email, self.email_account.password)
    imap.select('INBOX')

    # Найдите последнее добавленное сообщение
    typ, data = imap.search(None, '(SINCE "2023-10-01")')
    message_ids = data[0].split()

    # Если нет новых сообщений, завершите
    if not message_ids:
      return

    # Получите сообщения с почты
    for i, message_id in enumerate(message_ids):
      typ, data = imap.fetch(message_id, '(RFC822)')
      msg = email.message_from_bytes(data[0][1])

      # Извлеките данные из сообщения
      subject = msg['Subject']
      sent_date = msg['Date']
      received_date = msg['Received']
      body = msg.get_payload()
      attachments = [attachment.get_filename() for attachment in msg.get_payload() if isinstance(attachment, email.mime.multipart.MIMEMultipart) and attachment.get_filename()]

      # Сохраните сообщение в базу данных
      message = Message.objects.create(
        email_account=self.email_account,
        subject=subject,
        sent_date=sent_date,
        received_date=received_date,
        body=body,
        attachments=attachments
      )

      # Отправьте сообщение через WebSocket
      await self.channel_layer.group_send(
        'messages',
        {
          'type': 'message.received',
          'message': {
            'id': message.id,
            'subject': message.subject,
            'sent_date': message.sent_date,
            'received_date': message.received_date,
            'body': message.body,
            'attachments': message.attachments,
            'progress': len(message_ids) - i
          }
        }
      )

    # Завершите соединение
    imap.close()
    imap.logout()

  async def message_received(self, event):
    await self.send(text_data=json.dumps(event['message']))

  async def receive(self, text_data=None, bytes_data=None):
    if text_data == 'start-fetch':
      await self.start_fetch()