# 插件管理 第三方插件

# 导入第三方插件
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
# from flask_session import Session
from flask_jwt_extended import JWTManager
import jenkins
import httpsig.requests_auth
import requests
import datetime

# 利用flask-session，将session数据保存到redis中

# 初始化db
db = SQLAlchemy()
migrate = Migrate()

# 初始化flask_restful 创建Api对象的时候，使用蓝图对象
api = Api()
# 跨域
cors = CORS()
# redis-session
# session = Session()
# jwt token
jwt = JWTManager()


# 和app绑定
def init_exts(app):
    db.init_app(app=app)
    migrate.init_app(app=app, db=db)
    api.init_app(app=app)
    cors.init_app(app=app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    #    session.init_app(app=app)
    jwt.init_app(app=app)
    # Jenkins 登录初始化
    Jenkins_login(app=app)
    # jumpserver 登录
    JumpserverAuth(app=app)
    # # 在 Flask 实例化后执行的函数
    # def initialize():
    #     print("Flask app initialized!")
    #
    # # 在处理第一个请求之前执行初始化
    # app.before_first_request(initialize)


# jenkins 登录

class Jenkins_login:
    def __init__(self, app=None):
        self.jenkins_server = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('JENKINS_MASTER', 'http://localhost:8080')
        app.config.setdefault('JENKINS_LOGIN_USER', 'admin')
        app.config.setdefault('JENKINS_LOGIN_PASSWD', 'password')

        jenkins_master = app.config['JENKINS_MASTER']
        login_user = app.config['JENKINS_LOGIN_USER']
        login_passwd = app.config['JENKINS_LOGIN_PASSWD']

        self.jenkins_server = jenkins.Jenkins(jenkins_master, login_user, login_passwd)
        app.extensions['jenkins'] = self


class JumpserverAuth:
    def __init__(self, app=None):
        self.headers = {
            'Accept': 'application/json',
            'X-JMS-ORG': '00000000-0000-0000-0000-000000000002',
            'Date': datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        }
        self.auth = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config.setdefault('JUMPSERVER_KEY_ID', 'af14e012-186e-4528-8298-e1505552682b')
        app.config.setdefault('JUMPSERVER_SECRET', '7cafb5cb-fa4f-4e16-b482-cde9f608a526')

        key_id = app.config['JUMPSERVER_KEY_ID']
        secret = app.config['JUMPSERVER_SECRET']

        self.auth = httpsig.requests_auth.HTTPSignatureAuth(
            key_id=key_id,
            secret=secret,
            algorithm='hmac-sha256',
            headers=['(request-target)', 'accept', 'date']
        )
        app.extensions['jumpserver_auth'] = self
