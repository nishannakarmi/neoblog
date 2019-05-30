from django.shortcuts import render, redirect, Http404
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from blog.models import Blog, Category
from blog.forms import UserForm, UserProfileForm


# Create your views here.

def index(request):
    resp = render(request, 'blog/index.html')
    resp.set_cookie('blog_type', 'apple')
    return resp


class IndexView(TemplateView):
    template_name = 'blog/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['blogs'] = Blog.objects.filter(is_published=True).order_by('-published_date')[:5]
        context['categories'] = Category.objects.all()
        return self.render_to_response(context)

    def render_to_response(self, context, **response_kwargs):
        response = super(IndexView, self).render_to_response(context, **response_kwargs)
        if self.request.user.is_authenticated:
            response.set_cookie('blog_type', 'ball')

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

        return Blog.objects.select_related('created_by', 'category').filter(**filter_args)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = self.request.GET.get('category_name', '')
        return context


class BlogDetailView(DetailView):
    model = Blog

    # def dispatch(self, request, *args, **kwargs):
    #     pk = self.kwargs.get('pk', None)
    #     if not pk:
    #         raise Http404


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
