from flask import abort
from flask.globals import current_app
from flask_restful import Resource, reqparse, fields, marshal
from models import UserModel, RevokedTokenModel, BlogModel
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

list_route = '/blogapi/blogs'
item_route = '/blogapi/blogs/<int:id>'
blog_fields = {
    'title': fields.String,
    'content': fields.String,
    'author_id': fields.Integer,
    'uri': fields.Url('blog'),
    'dateupdated': fields.DateTime(dt_format='rfc822')
}


class UserRegistration(Resource):
    def post(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', help='This field cannot be blank', required=True)
        self.parser.add_argument('password', help='This field cannot be blank', required=True)
        data = self.parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {'message': 'User {} already exists'.format(data['username'])}

        new_user = UserModel(
            username=data['username'],
            password=UserModel.generate_hash(data['password'])
        )

        try:
            new_user.save_to_db()
            access_token = create_access_token(identity=new_user.id)
            refresh_token = create_refresh_token(identity=new_user.id)
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', help='This field cannot be blank', required=True)
        self.parser.add_argument('password', help='This field cannot be blank', required=True)
        data = self.parser.parse_args()
        current_user = UserModel.find_by_username(data['username'])

        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=current_user.id)
            refresh_token = create_refresh_token(identity=current_user.id)
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()

    def delete(self):
        return UserModel.delete_all()


class BlogListAPI(Resource):
    @jwt_required
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', type=str, required=True,
                                 help='No Blog title provided',
                                 location='json')
        self.parser.add_argument('content', type=str, default="",
                                 location='json')
        self.parser.add_argument('author_id', type=int, default="",
                                 location='json')
        self.parser.add_argument('dateupdated', type=str, default="",
                                 location='json')
        super(BlogListAPI, self).__init__()

    def get(self):
        blogs = BlogModel.query.all()
        return {'blogs': marshal(blogs, blog_fields)}

    def post(self):
        args = self.parser.parse_args()
        same_title = BlogModel.find_by_title(args['title'])
        if same_title:
            return {'message': 'Blog with title ({}) already exists'.format(same_title.title)}
        new_blog = BlogModel(
            title=args['title'],
            content=args['content'],
            author_id=get_jwt_identity()
        )
        try:
            new_blog.save_to_db()
            return {'created blog': marshal(new_blog, blog_fields)}, 201
        except:
            return {'message': 'Something went wrong'}, 500


class BlogItemAPI(Resource):
    # @jwt_required
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', type=str, required=True,
                                 help='No Blog title provided',
                                 location='json')
        self.parser.add_argument('content', type=str, default="",
                                 location='json')
        self.parser.add_argument('author_id', type=int, default="",
                                 location='json')
        self.parser.add_argument('dateupdated', type=str, default="",
                                 location='json')
        super(BlogItemAPI, self).__init__()

    def get(self, id):
        blog = BlogModel.query.get(id)
        if blog:
            return {'blog': marshal(blog, blog_fields)}
        abort(404)

    def put(self, id):
        args = self.parser.parse_args()
        same_title = BlogModel.find_by_title(args['title'])
        if same_title:
            return {'message': 'Blog with title ({}) already exists'.format(same_title.title)}
        blog = BlogModel.query.get(id)
        if blog:
            try:
                args['author_id'] = get_jwt_identity()
                blog.update_db(args)
                updated_blog = BlogModel.query.get(id)
                return {'Updated args': marshal(updated_blog, blog_fields)}
            except:
                return {'message': 'Something went wrong, internal error'}, 500
        return {'No blog with this id': id}

    def delete(self, id):
        blog = BlogModel.query.get(id)
        if blog:
            BlogModel.delete_db(blog)
            return {'Deleted': marshal(blog, blog_fields)}
