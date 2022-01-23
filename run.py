from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from data import blogs
import os
from dotenv import load_dotenv
from flask_cors import CORS


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=f"{THIS_FOLDER}/config.env")

app = Flask(__name__)
api = Api(app)
CORS(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

db = SQLAlchemy(app)


@app.before_first_request
def create_tables():
    db.create_all()


import views, resources, models


@app.before_first_request
def init_db():
    db.session.query(models.UserModel).delete()
    db.session.query(models.BlogModel).delete()
    for blog in blogs:
        new_blog = resources.BlogModel(
            author_id=blog['author_id'],
            title=blog['title'],
            content=blog['content']
        )
        try:
            new_blog.save_to_db()
        except:
            print('message: Something went wrong')


jwt = JWTManager(app)


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.AllUsers, '/users')
api.add_resource(resources.BlogListAPI, resources.list_route, endpoint='blogs')
api.add_resource(resources.BlogItemAPI, resources.item_route, endpoint='blog')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)