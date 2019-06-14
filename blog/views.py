from django.shortcuts import render, redirect, Http404, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.utils.timezone import now

from blog.models import Blog, Category, Comment, Profile, LikeDislike
from blog.forms import UserForm, UserProfileForm, UserUpdateForm, ChangePasswordForm, BlogUpdateForm
from blog.utils import superuser_only


# Create your views here.

def index(request):
    resp = render(request, 'blog/index.html')
    resp.set_cookie('blog_type', 'apple')
    return resp


class IndexView(TemplateView):
    template_name = 'blog/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['blogs'] = Blog.objects.filter(is_published=True).order_by('published_date')[:5]
        context['categories'] = Category.objects.all()
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        response = super(IndexView, self).render_to_response(context, **response_kwargs)
        if self.request.user.is_authenticated:
            response.set_cookie('blog_type', 'ball')
        else:
            response.set_cookie('blog_type', 'man')
        return response


class BlogListView(ListView):
    # model = Blog
    paginate_by = 1
    template_name = 'blog/blog_list.html'

    def get_queryset(self):
        filter_args = {
            'is_published': True
        }
        category_qs = self.request.GET.get('category_name', None)
        if category_qs:
            filter_args['category__name__exact'] = category_qs

        search = self.request.GET.get('search', None)
        if search:
            filter_args['title__icontains'] = search
            filter_args['body__icontains'] = search

        return Blog.objects.select_related('created_by', 'category').filter(**filter_args).distinct()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = self.request.GET.get('category_name', '')
        return context


class MyBlogListView(ListView):
    paginate_by = 1
    template_name = 'blog/my_blog_list.html'

    def get_queryset(self):
        return Blog.objects.select_related('created_by', 'category').filter(created_by=self.request.user)


class UnpublishBlogListView(ListView):
    paginate_by = 1
    template_name = 'blog/unpublish_blog_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise Http404('Permission Denied')
        return super(UnpublishBlogListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Blog.objects.filter(is_published=False)


class BlogDetailView(DetailView):
    model = Blog

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk', None)
        if not pk:
            raise Http404
        try:
            blog = Blog.objects.get(pk=pk)
        except Blog.DoesNotExist:
            raise Http404('Invalid Blog Id')
        else:
            if not blog.is_published:
                if request.user != blog.created_by:
                    raise Http404('Invalid Blog Id or trying to access unpublished post')
            else:
                if request.user != blog.created_by:
                    blog.views = blog.views + 1
                    blog.save()
        return super().dispatch(request, **kwargs)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    context_object_name = 'profile'
    template_name = 'blog/profile_detail.html'


@method_decorator(login_required, name='dispatch')
class BlogCreateView(CreateView):
    model = Blog
    template_name = 'blog/blog_create_form.html'
    fields = ['title', 'body', 'image', 'category']

    def get_success_url(self, new_obj=None):
        return reverse_lazy('blog_detail', args=(new_obj.id,))

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.created_by = self.request.user
        obj.save()
        return HttpResponseRedirect(self.get_success_url(new_obj=obj))


@method_decorator(superuser_only, name='dispatch')
class BlogPublishView(UpdateView):
    model = Blog
    form_class = BlogUpdateForm
    template_name = "blog/blog_publish.html"

    def get_success_url(self):
        return reverse_lazy('index')


class BlogEditView(LoginRequiredMixin, UpdateView):
    model = Blog
    template_name = 'blog/blog_update_form.html'
    fields = ['title', 'body', 'image', 'category']

    def get_success_url(self):
        return reverse_lazy('blog_detail', args=(self.object.id,))

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        try:
            blog = Blog.objects.get(pk=pk)
        except Blog.DoesNotExist:
            raise Http404('Invalid Blog Id to edit')
        else:
            if blog.created_by != self.request.user:
                raise Http404('You are not authorized to update this blog post')
            return super().dispatch(request, **kwargs)


class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog
    template_name = 'blog/blog_delete_confirm.html'
    success_url = reverse_lazy('my_blogs')

    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        try:
            blog = Blog.objects.get(pk=pk)
        except Blog.DoesNotExist:
            raise Http404('Invalid Blog Id to delete')
        else:
            if blog.created_by != self.request.user:
                raise Http404('You are not authorized to delete this blog post')
            return super().dispatch(request, **kwargs)


def signup(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        user_profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and user_profile_form.is_valid():
            user = user_form.save()
            user.refresh_from_db()
            user_profile_form.save(user=user)
            return redirect('index')
    else:
        user_form = UserForm()
        user_profile_form = UserProfileForm

    return render(request, 'blog/signup.html', context={
        'user_form': user_form,
        'user_profile_form': user_profile_form
    })


@login_required(login_url='/login/')
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(data=request.POST, instance=request.user)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and user_profile_form.is_valid():
            user = user_form.save()
            user.refresh_from_db()
            user_profile_form.save(user=user)
            return redirect('index')
    else:
        try:
            profile = Profile.objects.get(pk=request.user.profile.id)
        except Profile.DoesNotExist:
            raise Http404('Invalid Profile')
        else:
            user_form = UserUpdateForm(instance=profile.user)
            user_profile_form = UserProfileForm(instance=profile)

    return render(request, 'blog/edit_profile.html', context={
        'user_form': user_form,
        'user_profile_form': user_profile_form
    })


@login_required(login_url='/login/')
def change_user_password(request):
    if request.method == 'POST':
        change_password_form = ChangePasswordForm(data=request.POST, instance=request.user)

        if change_password_form.is_valid():
            change_password_form.save()
            logout(request)
            return redirect('index')

    else:
        try:
            Profile.objects.get(pk=request.user.profile.id)
        except Profile.DoesNotExist:
            raise Http404('Invalid Profile')
        else:
            change_password_form = ChangePasswordForm()
    return render(request, 'blog/change_password_form.html', context={
        'change_password_form': change_password_form
    })


@login_required(login_url='/login/')
def add_comment(request, blog_id):
    if request.method == 'POST':
        if not blog_id:
            raise Http404('Blog Id should be provided to comment for')

        comment = request.POST.get('comment', None)

        if not comment:
            raise Http404('Comment text should be provided')

        try:
            blog = Blog.objects.get(pk=blog_id)
        except Blog.DoesNotExist:
            raise Http404('Invalid Blog Id')
        else:
            if not blog.is_published:
                raise Http404('You are not allowed to comment on this blog post')

            Comment.objects.create(text=comment, blog=blog, created_by=request.user)
            return redirect('blog_detail', pk=blog.id)
    else:
        return redirect('blog_detail', pk=blog_id)


@login_required(login_url='/login/')
def add_blog_action(request, blog_id, action_type):
    if action_type.upper() not in ['L', 'D']:
        raise Http404('Invalid Action Type')

    try:
        blog = Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        raise Http404('Invalid Blog')
    else:
        if not blog.is_published:
            raise Http404('You cannot make action on unpublished blog')
        try:
            like_dislike_action = LikeDislike.objects.get(blog=blog, user=request.user)
        except LikeDislike.DoesNotExist:
            LikeDislike.objects.create(blog=blog, user=request.user, action=action_type)
        else:
            if like_dislike_action.action != action_type:
                like_dislike_action.action = action_type
                like_dislike_action.updated_date = now()
                like_dislike_action.save()
        finally:
            return redirect('blog_detail', pk=blog.id)
