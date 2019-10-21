import datetime

from sqlalchemy_utils.types.scalar_list import ScalarListType

from affo_user_service.extensions import db, ma

__all__ = ["User"]


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(256))

    is_active = db.Column(db.Boolean(), default=True)

    last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    roles = db.Column(ScalarListType(), default=[])

    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def rolenames(self):
        return self.roles

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(email=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    def is_valid(self):
        return self.is_active

    def has_role(self, *roles):
        return any(role in self.roles for role in roles)

    def get_full_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name


class UserSchema(ma.ModelSchema):
    roles = ma.List(ma.String())

    class Meta:
        model = User
        exclude = ("password",)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
