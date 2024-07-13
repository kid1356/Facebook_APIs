from django.shortcuts import render
from user.views import *
from .serializers import *
from .models import *
from django.http import HttpRequest

#custom permissions
class IsOwnerOfBlog(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:  # Can read the object only
            return True

        return obj.user == request.user
        

# Create your views here.  
class Blog_Create_view(APIView):
    def post(self, request):
        serializer = BlogSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user = request.user)

        return Response({'The Blogs is Posted':serializer.data},status=status.HTTP_201_CREATED)


class Blog_Get_view(APIView):
        
    def get(self,request,id):
        try:
            blog = Blogs.objects.get(id=id)
            serializer = BlogSerializer(blog)
            return Response({'Blog':serializer.data},status=status.HTTP_200_OK)
        except Blogs.DoesNotExist:
            return Response({"Blog not Found"},status=status.HTTP_404_NOT_FOUND)

class Blog_Put_view(APIView):   
    permission_classes = [IsOwnerOfBlog]
    def put(self, request,id):
        try:
            blog = Blogs.objects.get(id=id)

            self.check_object_permissions(request,blog)

            serializer = BlogSerializer(blog, data=request.data)
        
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'updated successfully':serializer.data},status=status.HTTP_200_OK)
        except Blogs.DoesNotExist:
            return Response('Blog Does not FOund',status=status.HTTP_404_NOT_FOUND)
    
class DeleteBlogView(APIView):
    permission_classes = [IsOwnerOfBlog]
    def delete(self, request,id):
        try:
            blog = Blogs.objects.get(id=id)
            serializer = BlogSerializer(blog)
            blog_serialized = serializer.data
            self.check_object_permissions(request, blog)
            blog.delete()
            return Response({"the blog is deleted":blog_serialized}, status=status.HTTP_200_OK)

        except Blogs.DoesNotExist:
            return Response({"blog DOes not found or already deleted"}, status=status.HTTP_400_BAD_REQUEST)


class Like_Blog_view(APIView):
    def post(self,request,*args,**kwargs):
        serializer =BlogLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        blog_id = serializer.validated_data['blog_id']
        # like = serializer.validated_data['like']
        user = request.user

        try:
            blog = Blogs.objects.get(id=blog_id)
        except Blogs.DoesNotExist:
            return Response({'Blog Not found'},status=status.HTTP_404_NOT_FOUND)

        if user in blog.likes.all():
            blog.likes.remove(user)
            message = 'Unliked successfully'
        else:
            blog.likes.add(user)
            message = 'Liked successfully'

        return Response({"message":message},status=status.HTTP_200_OK)     



class Comment_Create_View(APIView):
   
    def post(self, request):
        serializer = CommentSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user= request.user)

        return Response({"Commented successfully":serializer.data},status=status.HTTP_201_CREATED)
    


class Comment_Get_view(APIView):    
    def get(self,request,id):
        try:
            comment = Comment.objects.get(id=id)
            serializer = CommentSerializer(comment)
            return Response({'Comment':serializer.data},status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response("comment does not found", status=status.HTTP_404_NOT_FOUND)
        

class Comment_Put_view(APIView):
    permission_classes = [IsOwnerOfBlog]
    def put(self, request,id):
        try:
            comment = Comment.objects.get(id=id)
            self.check_object_permissions(request,comment)
            serializer = CommentSerializer(comment, data=request.data)
        
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'updated successfully':serializer.data},status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response("comment does not found", status=status.HTTP_404_NOT_FOUND)

class Comment_Delete_view(APIView):  
    def delete(self,request,id):
      try:  
        comment= Comment.objects.get(id=id)
        serializer = CommentSerializer(comment)
        serializer_data = serializer
        comment.delete()

        return Response({'the comment is deleted':serializer_data},status=status.HTTP_200_OK)
      except Comment.DoesNotExist:
            return Response("comment does not found", status=status.HTTP_404_NOT_FOUND)