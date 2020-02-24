from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .forms import PostFrom
from .models import Post, Group, User
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import datetime as dt


@login_required()
def new_post(request):
    if request.method == "POST":
        form = PostFrom(request.POST)
        if form.is_valid():
            new = Post.objects.create(author=request.user, text=form.cleaned_data['text'], group=form.cleaned_data['group']).save()
            return redirect("index")
        return render(request, "new.html", {"form": form})
    form = PostFrom()
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
    if username == request.user.get_username():
        u = request.user
    else:
        u = User.objects.get(username=username)
    post_list = Post.objects.order_by("-pub_date").filter(author=u)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "tmp_user": u,
        "post_count": post_list.count(),
        "page": page,
        "paginator": paginator
    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    u = User.objects.get(username=username)
    post = get_object_or_404(Post, author=u, pk=post_id)
    context = {
        "tmp_user": u,
        "post": post,
        "post_count": Post.objects.filter(author=u).count()
    }
    return render(request, "post.html", context)


@login_required()
def post_edit(request, username, post_id):
    if username == request.user.get_username():
        post = get_object_or_404(Post, pk=post_id)
        if request.method == "POST":
            form = PostFrom(request.POST, instance=post)
            if form.is_valid():
                post.text = form.cleaned_data["text"]
                post.group = form.cleaned_data["group"]
                post.save()
                return redirect("post", username=username, post_id=post_id)
            else:
                return render(request, "new.html", {"form": form})
        else:
            form = PostFrom(instance=post)
            return render(request, "new.html", {"form": form})
    else:
        return render(request, "index.html")


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)

