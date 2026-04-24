from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from .models import Follow, Post, Profile, Like, Comment, Message, Story, Reel, Notification
from .forms import PostForm, ProfileForm, StoryForm, ReelForm


def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    stories = Story.objects.all().order_by('-created_at')[:12]
    highlighted_stories = Story.objects.filter(is_highlighted=True).order_by('-created_at')[:12]
    reels = Reel.objects.all().order_by('-created_at')[:12]

    query = request.GET.get('q', '').strip()
    hashtag = request.GET.get('hashtag', '').strip().lstrip('#')

    user_results = User.objects.none()

    if query:
        user_results = User.objects.filter(username__icontains=query)
        # Only show profile results when searching; hide regular feed posts
        posts = Post.objects.none()
    elif hashtag:
        # hashtag search remains for feed posts when no user text search active
        posts = Post.objects.filter(caption__icontains=f"#{hashtag}").order_by('-created_at')

    following_ids = []
    notif_data = {'likes': 0, 'comments': 0, 'follows': 0, 'unread': 0}

    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)

        notif_data = {
            'likes': Notification.objects.filter(user=request.user, verb='like', is_read=False).count(),
            'comments': Notification.objects.filter(user=request.user, verb='comment', is_read=False).count(),
            'follows': Notification.objects.filter(user=request.user, verb='follow', is_read=False).count(),
            'unread': Notification.objects.filter(user=request.user, is_read=False).count(),
        }

    return render(request, 'blog/index.html', {
        'posts': posts,
        'stories': stories,
        'highlighted_stories': highlighted_stories,
        'reels': reels,
        'following_ids': list(following_ids),
        'search_query': query,
        'selected_hashtag': hashtag,
        'user_results': user_results,
        'notifications': notif_data
    })


@login_required
def create_story(request):
    if request.method == 'POST':
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()

            # Notify followers
            follower_ids = Follow.objects.filter(following=request.user).values_list('follower', flat=True)
            for uid in follower_ids:
                Notification.objects.create(
                    user_id=uid,
                    actor=request.user,
                    verb='story',
                    story=story,
                    message=f"{request.user.username} added a new story: {story.title}"
                )

            return redirect('feed')
    else:
        form = StoryForm()

    return render(request, 'blog/create_story.html', {'form': form})


@login_required
def create_reel(request):
    if request.method == 'POST':
        form = ReelForm(request.POST, request.FILES)
        if form.is_valid():
            reel = form.save(commit=False)
            reel.author = request.user
            reel.save()

            follower_ids = Follow.objects.filter(following=request.user).values_list('follower', flat=True)
            for uid in follower_ids:
                Notification.objects.create(
                    user_id=uid,
                    actor=request.user,
                    verb='reel',
                    reel=reel,
                    message=f"{request.user.username} shared a new reel"
                )

            return redirect('reels')
    else:
        form = ReelForm()

    return render(request, 'blog/create_reel.html', {'form': form})


def reels(request):
    reels_list = Reel.objects.all().order_by('-created_at')
    return render(request, 'blog/reels.html', {'reels': reels_list})


@login_required
def notifications(request):
    user_notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'blog/notifications.html', {'notifications': user_notifs})


@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('notifications')


@login_required
def toggle_story_highlight(request, story_id):
    story = get_object_or_404(Story, id=story_id, author=request.user)
    story.is_highlighted = not story.is_highlighted
    story.save()
    return redirect('feed')


def view_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    return render(request, 'blog/story_detail.html', {
        'story': story,
        'author_profile': Profile.objects.get(user=story.author)
    })


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()

    return render(request, 'blog/create_post.html', {'form': form})


def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('password_confirm')

        if password != confirm:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username exists')
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created')
        return redirect('login')

    return render(request, 'blog/register.html')


@login_required
def account(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    stories = Story.objects.filter(author=request.user).order_by('-created_at')
    highlighted_stories = stories.filter(is_highlighted=True)

    followers_count = Follow.objects.filter(following=request.user).count()
    following_count = Follow.objects.filter(follower=request.user).count()

    return render(request, 'blog/account.html', {
        'profile': profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'stories': stories,
        'highlighted_stories': highlighted_stories
    })


@login_required
def edit_post(request, post_id):
    post = Post.objects.get(id=post_id, author=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create_post.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = Post.objects.get(id=post_id, author=request.user)
    post.delete()
    return redirect('account')


@login_required
def follow_toggle(request, user_id):
    user = User.objects.get(id=user_id)

    if user == request.user:
        return redirect('feed')

    follow = Follow.objects.filter(follower=request.user, following=user)

    if follow.exists():
        follow.delete()
    else:
        Follow.objects.create(follower=request.user, following=user)
        Notification.objects.create(
            user=user,
            actor=request.user,
            verb='follow',
            message=f"{request.user.username} is now following you."
        )

    return redirect('feed')


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'blog/edit_profile.html', {'form': form})
from .models import Like, Comment

@login_required
def like_toggle(request, post_id):
    post = Post.objects.get(id=post_id)

    like = Like.objects.filter(user=request.user, post=post)

    if like.exists():
        like.delete()
    else:
        Like.objects.create(user=request.user, post=post)
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,
                actor=request.user,
                verb='like',
                post=post,
                message=f"{request.user.username} liked your post."
            )

    return redirect('feed')
@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(id=post_id)
        text = request.POST.get('comment')

        if text:
            Comment.objects.create(
                user=request.user,
                post=post,
                text=text
            )
            if post.author != request.user:
                Notification.objects.create(
                    user=post.author,
                    actor=request.user,
                    verb='comment',
                    post=post,
                    message=f"{request.user.username} commented: {text[:80]}"
                )

    return redirect('feed')
def user_profile(request, user_id):
    user = User.objects.get(id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)

    posts = Post.objects.filter(author=user).order_by('-created_at')
    stories = Story.objects.filter(author=user).order_by('-created_at')
    highlighted_stories = stories.filter(is_highlighted=True)

    followers = Follow.objects.filter(following=user).count()
    following = Follow.objects.filter(follower=user).count()

    return render(request, 'blog/user_profile.html', {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'followers': followers,
        'following': following,
        'stories': stories,
        'highlighted_stories': highlighted_stories
    })
from .models import Message

@login_required
def inbox(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'blog/inbox.html', {'users': users})
@login_required
def chat(request, user_id):
    other_user = User.objects.get(id=user_id)

    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('created_at')

    # ✅ MARK AS SEEN
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        seen=False
    ).update(seen=True)

    if request.method == "POST":
        text = request.POST.get('message')
        image = request.FILES.get('image')

        Message.objects.create(
            sender=request.user,
            receiver=other_user,
            text=text,
            image=image
        )

        return redirect('chat', user_id=user_id)

    return render(request, 'blog/chat.html', {
        'messages': messages,
        'other_user': other_user
    })
@login_required
def share_post(request, post_id):
    post = Post.objects.get(id=post_id)

    following = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    users = User.objects.filter(id__in=following)

    if request.method == "POST":
        receiver_id = request.POST.get('receiver')
        receiver = User.objects.get(id=receiver_id)

        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            post=post
        )

        return redirect('chat', user_id=receiver.id)

    return render(request, 'blog/share.html', {
        'users': users,
        'post': post
    })
from django.shortcuts import get_object_or_404

def view_post(request, post_id):
    post = Post.objects.get(id=post_id)
    return redirect(f'/user/{post.author.id}/#post-{post.id}')