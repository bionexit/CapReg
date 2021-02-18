from app import db, login_manager
from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash


class Permission:
    GENERAL = 0
    ADMINISTER = 1


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    index = db.Column(db.String(64))
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    _user = db.relationship('User', uselist=False, back_populates='_role')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.GENERAL, 'main', True),
            'Administrator': (
                Permission.ADMINISTER,
                'admin',
                False  # grants all permissions
            )
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.index = roles[r][1]
            role.default = roles[r][2]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role \'%s\'>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(32))  # 登陆用户名
    role_id = db.Column(db.Integer, db.ForeignKey('role.id')) # 普通用户：0x01 管理员：0xff
    _role = db.relationship("Role", back_populates='_user')

    password_hash = db.Column(db.String(128))  #只有管理员有密码
    contact_name = db.Column(db.String(64))
    phone = db.Column(db.String(12))
    value_usble = db.Column(db.Float(20)) # 当前可用数量，从外部数据库中获取，每次登陆刷新
    trade_num = db.Column(db.String(12))  # 交易系统股权代码
    reg_date = db.Column(db.String(50),default='CURRENT_TIMESTAMP') # 初始化后需要在数据库中对该字段进行手工设置
    _posts = db.relationship('Posts', back_populates='_user')
    _log = db.relationship('Log',back_populates='_user')
    status = db.Column(db.Boolean,default=True)





    def __init__(self, **kwargs):  # 默认权限为普通用户
        super(User, self).__init__(**kwargs)
        self._role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_admin(self):
        return self.can(Permission.ADMINISTER)

    @property
    def password(self):
        raise AttributeError('`password` is not a readable attribute')

    @password.setter
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=604800):
        """Generate a confirmation token to email a new user."""

        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    @staticmethod
    def generate_fake(count=100, **kwargs):
        """Generate a number of fake users for testing."""
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice
        from faker import Faker

        fake = Faker()
        roles = Role.query.all()

        seed()
        for i in range(count):
            u = User(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password='password',
                confirmed=True,
                role=choice(roles),
                **kwargs)
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<User %r>' % (self.username)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)

    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    _user = db.relationship("User",back_populates='_log')

    type = db.Column(db.String(64), unique=True) # 登陆、发布、阅读、禁用、
    result = db.Column(db.Boolean) #执行成功 1，失败0
    comments = db.Column(db.String(200))

    def __repr__(self):
        return '<Logs %r>' % (self.type)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key = True,index=True,unique=True,autoincrement=True)

    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    _user = db.relationship("User", back_populates='_posts')

    start_date = db.Column(db.String(50))  # 初始化后需要在数据库中对该字段进行手工设置
    end_date = db.Column(db.String(50))  # 初始化后需要在数据库中对该字段进行手工设置
    status = db.Column(db.Boolean) # 0.禁用 1.正常
    deal_date = db.Column(db.String(50))  # 成交时间
    post_value = db.Column(db.Float(20))  # 交易数量
    post_direction = db.Column(db.Boolean)  # 交易方向 0卖出，1买入

    post_type_id = db.Column(db.Integer, db.ForeignKey('posttype.id'))
    posttypename = db.relationship("PostType",back_populates="Posttypes")
    remark = db.Column(db.String(500))

    def __repr__(self):
        return '<Post %r>' % (self.id)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def dobule_to_dict(self):
        result = {}
        for key in self.__mapper__.c.keys():
            if getattr(self, key) is not None:
                result[key] = str(getattr(self, key))
            else:
                result[key] = getattr(self, key)
        return result


class PostType(db.Model):  # 1.发布 2.撮合中 3.部分成交 4.全部成交
    __tablename__ = 'posttype'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    description = db.Column(db.String(20))
    Posttypes = db.relationship('Posts',back_populates='posttypename')

    def __repr__(self):
        return '<PostType %r>' % (self.description)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Bounds(db.Model):  # 持仓数据
    __tablename__ = 'bounds'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    boundnum = db.Column(db.Float(20))
    trade_num = db.Column(db.String(12))
    username = db.Column(db.String(12))
    def __repr__(self):
        return '<Bounds %r>' % (self.boundnum)