from django.urls import path

from blog import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('signup/', views.signup, name='signup'),
    path('blogs/', views.BlogListView.as_view(), name='blogs'),
    path('blog/<int:pk>', views.BlogDetailView.as_view(), name='blog_detail'),
    # path('blogs/', views.BlogListView.as_view(), name='blogs'),
    # path('blogger/<int:pk>', views.BlogListbyAuthorView.as_view(), name='blogs-by-author'),
    # path('blog/<int:pk>', views.BlogDetailView.as_view(), name='blog-detail'),
    # path('bloggers/', views.BloggerListView.as_view(), name='bloggers'),
    # path('blog/<int:pk>/comment/', views.BlogCommentCreate.as_view(), name='blog_comment'),
]
