from run import db
from passlib.hash import pbkdf2_sha256 as sha256
import datetime


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'username': x.username,
                'password': x.password
            }

        return {'users': list(map(lambda x: to_json(x), UserModel.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class BlogModel(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.String(1000), nullable=True)
    dateupdated = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow,
                            onupdate=datetime.datetime.utcnow)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self, args):
        for arg in args.items():
            k, v = arg
            if v is not None and k != 'dateupdated':
                setattr(self, k, v)
        db.session.commit()

    def delete_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(title=title).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'id': x.id,
                'Author': x.author_id,
                'Title': x.title,
                'Content': x.content
            }

        return {'blogs': list(map(lambda x: to_json(x), BlogModel.query.all()))}
