from django.urls import path
from django.contrib.auth.decorators import login_required

from blog import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('signup/', views.signup, name='signup'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('blog/<int:pk>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('blog/<int:blog_id>/comment/', views.add_comment, name='add_comment'),
    path('blog/create/', views.BlogCreateView.as_view(), name='create_blog'),
    path('blog/update/<int:pk>/', views.BlogEditView.as_view(), name='update_blog'),
    path('blog/delete/<int:pk>/', views.BlogDeleteView.as_view(), name='delete_blog'),
    path('my_blogs/', login_required(views.MyBlogListView.as_view()), name='my_blogs'),
    path('profile/<int:pk>/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change_password/', views.change_user_password, name='change_password'),
    # path('blogs/', views.BlogListView.as_view(), name='blogs'),
    # path('blogger/<int:pk>', views.BlogListbyAuthorView.as_view(), name='blogs-by-author'),
    # path('blog/<int:pk>', views.BlogDetailView.as_view(), name='blog-detail'),
    # path('bloggers/', views.BloggerListView.as_view(), name='bloggers'),
    # path('blog/<int:pk>/comment/', views.BlogCommentCreate.as_view(), name='blog_comment'),
]
