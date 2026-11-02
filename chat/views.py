from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from notifications.models import Notification

User = get_user_model()


@login_required
def chat_view(request, conversation_id=None):
    conversations = Conversation.objects.filter(
        Q(participant1=request.user) | Q(participant2=request.user)
    ).select_related('participant1', 'participant1__profile', 'participant2', 'participant2__profile').prefetch_related('messages')

    active_conversation = None
    messages_list = []

    if conversation_id:
        active_conversation = get_object_or_404(Conversation, id=conversation_id)
        if active_conversation.participant1 != request.user and active_conversation.participant2 != request.user:
            return HttpResponseForbidden("Not authorized to view this conversation.")
    elif conversations.exists():
        active_conversation = conversations.first()

    if active_conversation:
        # Mark unread messages sent by other as read
        active_conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        messages_list = active_conversation.messages.select_related('sender', 'sender__profile').order_by('created_at')

    other_user = active_conversation.get_other_user(request.user) if active_conversation else None

    return render(request, 'chat/chat.html', {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'messages_list': messages_list,
        'other_user': other_user,
    })


@login_required
def start_chat_view(request, username):
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return redirect('chat')

    conversation, _ = Conversation.get_or_create_conversation(request.user, target_user)
    return redirect('chat_conversation', conversation_id=conversation.id)


@login_required
@require_POST
def send_message_ajax(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if conversation.participant1 != request.user and conversation.participant2 != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Message content cannot be empty'}, status=400)

    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=content
    )
    conversation.save()  # update updated_at timestamp

    other_user = conversation.get_other_user(request.user)
    Notification.send(
        recipient=other_user,
        sender=request.user,
        notification_type='MESSAGE',
        title=f'New Message from {request.user.get_display_name()}',
        message=content[:60],
        link=f"/chat/{conversation.id}/"
    )

    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_display_name(),
            'is_me': True,
            'content': message.content,
            'created_at': message.created_at.strftime('%H:%M'),
        }
    })


@login_required
def poll_messages_ajax(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if conversation.participant1 != request.user and conversation.participant2 != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    last_id = int(request.GET.get('last_id', 0))
    new_messages = conversation.messages.filter(id__gt=last_id).order_by('created_at')

    # Mark messages from other user as read
    new_messages.exclude(sender=request.user).update(is_read=True)

    data = []
    for m in new_messages:
        data.append({
            'id': m.id,
            'sender_id': m.sender.id,
            'sender_name': m.sender.get_display_name(),
            'is_me': (m.sender == request.user),
            'content': m.content,
            'created_at': m.created_at.strftime('%H:%M'),
        })

    return JsonResponse({'messages': data})
