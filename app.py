from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class

from config import Config
from extensions import db, jwt, image_set


from resources.user import UserListResource, UserResource, MeResource, UserBlogListResource, UserActivateResource, UserAvatarUploadResource
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list
from resources.blog import BlogListResource, BlogResource, BlogPublishResource, BlogCoverUploadResource
from resources.comment import CommentListResource, CommentResource


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.app_context().push()

    register_extensions(app)
    register_resources(app)

    return app


def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)
    configure_uploads(app, image_set)
    patch_request_class(app, 10 * 1024 * 1024)

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return jti in black_list


def register_resources(app):
    api = Api(app)

    api.add_resource(UserListResource, '/users')
    api.add_resource(UserActivateResource, '/users/activate/<string:token>')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(UserAvatarUploadResource, '/users/avatar')
    api.add_resource(UserBlogListResource, '/users/<string:username>/blogs')

    api.add_resource(MeResource, '/me')

    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')

    api.add_resource(BlogListResource, '/blogs')
    api.add_resource(BlogResource, '/blogs/<int:blog_id>')
    api.add_resource(BlogPublishResource, '/blogs/<int:blog_id>/publish')
    api.add_resource(BlogCoverUploadResource, '/blogs/<int:blog_id>/cover')

    api.add_resource(CommentListResource, '/blogs/<int:blog_id>/comments')
    api.add_resource(CommentResource, '/blogs/<int:blog_id>/comments/<int:comment_id>')


if __name__ == '__main__':
    app = create_app()
    app.run()
