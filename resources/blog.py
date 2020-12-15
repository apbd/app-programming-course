import os

from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
from http import HTTPStatus

from models.blog import Blog
from schemas.blog import BlogSchema

from extensions import image_set

from utils import save_image

blog_schema = BlogSchema()
blog_cover_schema = BlogSchema(only=('cover_url', ))
blog_list_schema = BlogSchema(many=True)


class BlogListResource(Resource):

    def get(self):

        blogs = Blog.get_all_published()

        return blog_list_schema.dump(blogs).data, HTTPStatus.OK

    @jwt_required
    def post(self):

        json_data = request.get_json()

        current_user = get_jwt_identity()

        data, errors = blog_schema.load(data=json_data)

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        blog = Blog(**data)
        blog.user_id = current_user
        blog.save()

        return blog_schema.dump(blog).data, HTTPStatus.CREATED


class BlogResource(Resource):

    @jwt_optional
    def get(self, blog_id):

        blog = Blog.get_by_id(blog_id=blog_id)

        if blog is None:
            return {'message': 'Blog not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if blog.is_publish == False and blog.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return blog_schema.dump(blog).data, HTTPStatus.OK

    @jwt_required
    def patch(self, blog_id):

        json_data = request.get_json()

        data, errors = blog_schema.load(data=json_data, partial=('name',))

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        blog = Blog.get_by_id(blog_id=blog_id)

        if blog is None:
            return {'message': 'Blog not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != blog.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        blog.blog_title = data.get('blog_title') or blog.blog_title
        blog.blog_status = data.get('blog_status') or blog.blog_status
        blog.rating = data.get('rating') or blog.rating
        blog.author = data.get('author') or blog.author

        blog.save()

        return blog_schema.dump(blog).data, HTTPStatus.OK

    @jwt_required
    def delete(self, blog_id):

        blog = Blog.get_by_id(blog_id=blog_id)

        if blog is None:
            return {'message': 'Blog not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != blog.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        blog.delete()

        return {}, HTTPStatus.NO_CONTENT


class BlogPublishResource(Resource):

    @jwt_required
    def put(self, blog_id):

        blog = Blog.get_by_id(blog_id=blog_id)

        if blog is None:
            return {'message': 'Blog not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != blog.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        blog.is_publish = True
        blog.save()

        return {}, HTTPStatus.NO_CONTENT

    @jwt_required
    def delete(self, blog_id):

        blog = Blog.get_by_id(blog_id=blog_id)

        if blog is None:
            return {'message': 'Blog not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != blog.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        blog.is_publish = False
        blog.save()

        return {}, HTTPStatus.NO_CONTENT


class BlogCoverUploadResource(Resource):

    @jwt_required
    def put(self, blog_id):

        file = request.files.get('cover')

        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST

        if not image_set.file_allowed(file, file.filename):
            return {'message': 'File type not allowed'}, HTTPStatus.BAD_REQUEST

        blog = Blog.get_by_id(blog_id=blog_id)

        if blog is None:
            return {'message': 'Blog not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != blog.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        if blog.cover_image:
            cover_path = image_set.path(folder='blogs', filename=blog.cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)

        filename = save_image(image=file, folder='blogs')

        blog.cover_image = filename
        blog.save()

        return blog_cover_schema.dump(blog).data, HTTPStatus.OK