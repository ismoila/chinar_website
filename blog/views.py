from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import BlogPost, BlogComment


def blog_list_view(request):
    posts = BlogPost.objects.filter(is_published=True)
    context = {'posts': posts}
    return render(request, 'blog/blog_list.html', context)


def blog_detail_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        text = request.POST.get('text', '').strip()

        errors = []
        if not name or len(name) > 100:
            errors.append("Ism noto'g'ri kiritilgan.")
        if not text or len(text) < 3:
            errors.append("Sharh matni juda qisqa.")
        elif len(text) > 1000:
            errors.append("Sharh matni 1000 belgidan oshmasligi kerak.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            BlogComment.objects.create(
                post=post,
                user=request.user if request.user.is_authenticated else None,
                name=name,
                text=text,
            )
            messages.success(request, "Sharhingiz uchun rahmat!")
            return redirect(post.get_absolute_url() + "#comments")

    prev_post = BlogPost.objects.filter(
        is_published=True, created_at__lt=post.created_at
    ).order_by('-created_at').first()

    next_post = BlogPost.objects.filter(
        is_published=True, created_at__gt=post.created_at
    ).order_by('created_at').first()

    context = {
        'post': post,
        'prev_post': prev_post,
        'next_post': next_post,
    }
    return render(request, 'blog/blog_detail.html', context)