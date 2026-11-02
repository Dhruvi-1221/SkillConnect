from django.db import models
from django.conf import settings
from django.db.models import Q


class Conversation(models.Model):
    participant1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_p1'
    )
    participant2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations_as_p2'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat between {self.participant1.username} and {self.participant2.username}"

    def get_other_user(self, user):
        if self.participant1 == user:
            return self.participant2
        return self.participant1

    def get_last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_count_for(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    @classmethod
    def get_or_create_conversation(cls, user1, user2):
        if user1 == user2:
            return None, False
        conv = cls.objects.filter(
            (Q(participant1=user1) & Q(participant2=user2)) |
            (Q(participant1=user2) & Q(participant2=user1))
        ).first()
        if conv:
            return conv, False
        # Always order consistently
        p1, p2 = (user1, user2) if user1.id < user2.id else (user2, user1)
        conv = cls.objects.create(participant1=p1, participant2=p2)
        return conv, True


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at.strftime('%H:%M')}"
