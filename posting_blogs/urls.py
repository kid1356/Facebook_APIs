from django.urls import path
from .views import *

urlpatterns = [
    path('create-blog/',Blog_Create_view.as_view(),name= 'create-blog-view'),
    path('get-blog/<int:id>/',Blog_Get_view.as_view(),name= 'get-blog-view'),
    path('edit-blog/<int:id>/',Blog_Put_view.as_view(),name= 'put-blog-view'),
    path('delete-blog/<int:id>/',DeleteBlogView.as_view(),name =' Delete-view'),
    path('comment-blog/',Comment_Create_View.as_view(),name= 'create-comment-view'),
    path('get-comment-of-blog/<int:id>/',Comment_Get_view.as_view(),name= 'get-comment-view'),
    path('edit-comment/<int:id>/',Comment_Put_view.as_view(),name= 'put-comment-view'),
    path('delete-comment/<int:id>/',Comment_Delete_view.as_view(),name =' Delete-comment-view'),
    path('like-blog/',Like_Blog_view.as_view(),name =' Like-view'),

]   