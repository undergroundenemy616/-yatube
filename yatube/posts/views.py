from django.shortcuts import render

from .models import Post
import datetime as dt

def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    year = dt.datetime.now().year
    return render(request, "index.html", {"posts": latest, "year": year})