import datetime as dt

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostFrom
from .models import Comment, Follow, Group, Post, User


@login_required()
def new_post(request):
    form = PostFrom(request.POST or None, files=request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            Post.objects.create(author=request.user, text=form.cleaned_data['text'],
                                group=form.cleaned_data['group'], image=form.cleaned_data['image']).save()
            return redirect("index")
        return render(request, "new.html", {"form": form})
    return render(request, "new.html", {"form": form})


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    # функция get_object_or_404 позволяет получить объект из базы данных
    # по заданным критериям или вернуть сообщение об ошибке если объект не найден
    group = get_object_or_404(Group, slug=slug)

    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group, "page": page, "paginator": paginator})


def profile(request, username):
    user = User.objects.get(username=username)
    post_list = Post.objects.order_by("-pub_date").filter(author=user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = Follow.objects.filter(user=user).count()
    followers = Follow.objects.filter(author=user).count()
    follow_flag = True if Follow.objects.filter(user=request.user, author=user).count() != 0 else False
    context = {
        "tmp_user": user,
        "post_count": post_list.count(),
        "page": page,
        "paginator": paginator,
        "following": following,
        "followers": followers,
        "follow_flag": follow_flag,
    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    user = User.objects.get(username=username)
    post = get_object_or_404(Post, author=user, pk=post_id)
    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    context = {
        "tmp_user": user,
        "post": post,
        "post_count": Post.objects.filter(author=user).count(),
        "comments": comments,
        "forms": form
    }
    return render(request, "post.html", context)


@login_required()
def post_edit(request, username, post_id):
    if username == request.user.get_username():
        post = get_object_or_404(Post, pk=post_id)
        form = PostFrom(request.POST or None, files=request.FILES or None, instance=post)
        if request.method == "POST":
            if form.is_valid():
                form.save()
                return redirect("post", username=username, post_id=post_id)
            else:
                return render(request, "new.html", {"form": form, "post": post})
        else:
            return render(request, "new.html", {"form": form, "post": post})
    else:
        return render(request, "index.html")


@login_required()
def post_delete(request, username, post_id):
    if username == request.user.get_username():
        Post.objects.get(pk=post_id).delete()
    return redirect("index")


@login_required()
def add_comment(request, username, post_id):
    user = User.objects.get(username=request.user.username)
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        post.comment_count = 1 if post.comment_count is None else post.comment_count + 1
        post.save()
        Comment.objects.create(post=post, author=user, text=form.cleaned_data['text']).save()
    return redirect("post", username=username, post_id=post_id)


@login_required()
def follow_index(request):
    followers = Follow.objects.filter(user=request.user).values_list('author', flat=True)
    posts = Post.objects.filter(author__in=followers)
    paginator = Paginator(posts, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, "follow.html", {"page": page, "paginator": paginator})


@login_required()
def profile_follow(request, username):
    user = User.objects.get(username=username)
    pair = Follow.objects.filter(user=request.user, author=user).count()
    if user != request.user and not pair:
        Follow.objects.create(user=request.user, author=user)
    return redirect("profile", username=username)


@login_required()
def profile_unfollow(request, username):
    user = User.objects.get(username=username)
    Follow.objects.get(user=request.user, author=user).delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
