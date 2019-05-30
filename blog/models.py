from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=30)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created_date"]

    def get_blog_count(self):
        return self.blog_set.count()


class Blog(models.Model):
    title = models.CharField(max_length=50)
    body = models.TextField()
    image = models.ImageField(upload_to='uploads/')
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    published_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']
        verbose_name = 'blog'
        verbose_name_plural = 'blogs'

    def get_likes_count(self):
        return self.likedislikes.filter(action='L').count()

    def get_dislikes_count(self):
        return self.likedislikes.filter(action='D').count()


class Comment(models.Model):
    text = models.TextField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Profile(models.Model):
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Un-categorized'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    image = models.ImageField(upload_to='profile_uploads/')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.birth_date)


class LikeDislike(models.Model):
    ACTION_CHOICES = (
        ('L', 'Liked'),
        ('D', 'Disliked'),
    )
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="likedislikes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} has {self.action} the blog '{self.blog.title}'"
