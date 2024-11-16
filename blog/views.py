from django.shortcuts import render, get_object_or_404

from .models import BlogPost


def blog_list(request):
    """Returns a list where the content is also displayed"""
    posts = BlogPost.objects.all().order_by("-created_at")
    return render(request, "blog/blog_list.html", {"posts": posts})
