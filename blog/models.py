from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from unidecode import unidecode
from django.conf import settings


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    # Qisqa matn — ro'yxatda va ijtimoiy tarmoqda ko'rinadi
    excerpt = models.CharField(
        max_length=300, blank=True, default="",
        verbose_name="Qisqa tavsif",
        help_text="Maqola ro'yxatida ko'rinadigan qisqa matn (1-2 gap)"
    )

    content = models.TextField(verbose_name="Maqola matni")
    cover_image = models.ImageField(upload_to="blog/", verbose_name="Muqova rasmi")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Muallif"
    )

    is_published = models.BooleanField(default=True, verbose_name="Nashr qilingan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── SEO ──
    meta_title = models.CharField(max_length=70, blank=True, default="")
    meta_description = models.CharField(max_length=160, blank=True, default="")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Blog maqolasi"
        verbose_name_plural = "Blog maqolalari"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.title))[:200]
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog:post_detail', kwargs={'slug': self.slug})


class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    name = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.post.title}"