from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from .models import Post, PostLike, Comment
from .forms import PostForm, CommentForm
from notifications.models import Notification


def post_detail_view(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('student', 'student__student_profile', 'student__profile', 'category')
        .prefetch_related('comments', 'comments__user', 'comments__user__profile'),
        id=post_id,
        is_active=True
    )
    is_liked = post.is_liked_by(request.user) if request.user.is_authenticated else False
    comment_form = CommentForm()

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'is_liked': is_liked,
        'comment_form': comment_form,
    })


@login_required
def create_post_view(request):
    if not request.user.is_student:
        messages.warning(request, "Only registered student providers can publish portfolio posts.")
        return redirect('home')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.student = request.user
            post.save()
            messages.success(request, "Your skill showcase post has been published!")
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm()

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, student=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.student != request.user and not request.user.is_platform_admin:
        return HttpResponseForbidden("You cannot delete this post.")

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect('manage_posts' if request.user.is_student else 'home')

    return render(request, 'posts/confirm_delete.html', {'post': post})


@login_required
@require_POST
def like_toggle_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_active=True)
    existing_like = PostLike.objects.filter(post=post, user=request.user).first()

    if existing_like:
        existing_like.delete()
        liked = False
    else:
        PostLike.objects.create(post=post, user=request.user)
        liked = True
        if post.student != request.user:
            Notification.send(
                recipient=post.student,
                sender=request.user,
                notification_type='LIKE',
                title='Post Liked',
                message=f"{request.user.get_display_name()} liked your post: '{post.caption[:40]}...'",
                link=f"/posts/{post.id}/"
            )

    return JsonResponse({
        'liked': liked,
        'count': post.likes.count(),
        'post_id': post.id
    })


@login_required
@require_POST
def add_comment_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, is_active=True)
    content = request.POST.get('content', '').strip()

    if not content:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Comment cannot be empty.'}, status=400)
        messages.error(request, "Comment cannot be empty.")
        return redirect('post_detail', post_id=post.id)

    comment = Comment.objects.create(
        post=post,
        user=request.user,
        content=content
    )

    if post.student != request.user:
        Notification.send(
            recipient=post.student,
            sender=request.user,
            notification_type='COMMENT',
            title='New Comment',
            message=f"{request.user.get_display_name()} commented: '{content[:50]}...'",
            link=f"/posts/{post.id}/"
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'user': comment.user.get_display_name(),
                'username': comment.user.username,
                'avatar': comment.user.profile.get_avatar_url() if hasattr(comment.user, 'profile') else '',
                'content': comment.content,
                'created_at': comment.created_at.strftime('%b %d, %Y %H:%M'),
            },
            'comments_count': post.comments.count()
        })

    messages.success(request, "Comment posted!")
    return redirect('post_detail', post_id=post.id)


@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user and not request.user.is_platform_admin and comment.post.student != request.user:
        return HttpResponseForbidden("Not authorized to delete this comment.")

    post_id = comment.post.id
    comment.delete()
    messages.success(request, "Comment deleted.")
    return redirect('post_detail', post_id=post_id)


@login_required
def manage_posts_view(request):
    if not request.user.is_student:
        return redirect('home')

    posts = Post.objects.filter(student=request.user).order_by('-created_at')
    return render(request, 'posts/manage_posts.html', {'posts': posts})
