from django.views import View
from django.shortcuts import get_object_or_404, render
from django.db.models import F
from .models import BlogPost


class WeblogView(View):
    def get(self, request):
        blogposts = BlogPost.objects.all().order_by('-publish_date')
        return render(request, 'Weblog/blogpost.html', {'blogpost': blogposts})


class BlogPostView(View):
    def get(self, request, post_slug):
        post = get_object_or_404(BlogPost, slug=post_slug)
        session_key = f'viewed_post_{post.id}'

        if not request.session.get(session_key, False):
            BlogPost.objects.filter(pk=post.pk).update(view_count=F('view_count') + 1)
            request.session[session_key] = True
            request.session.set_expiry(60 * 60 * 24)

        return render(request, 'Weblog/view_blogpost.html', {'blogpost': post})