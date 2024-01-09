# 插件管理 第三方插件

# 导入第三方插件
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
# from flask_session import Session
from flask_jwt_extended import JWTManager
import jenkins  # pip install python-jenkins

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


# jenkins

# 和app绑定
def init_exts(app):
    db.init_app(app=app)
    migrate.init_app(app=app, db=db)
    api.init_app(app=app)
    cors.init_app(app=app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    #    session.init_app(app=app)
    jwt.init_app(app=app)

# jenkins 初始化



class jenkins_init(object):
    def __init__(self, jenkins_job):
        """
        jenkins_master ：master地址
        jenkins_job ：jenkins_job名字
        jenkins_user ：登陆账号
        jenkins_passwd ：登陆密码
        :rtype: object
        """
        self.jenkins_master = "http://192.168.0.152:8080"
        self.jenkins_job = jenkins_job
        self.login_user = 'admin'
        self.login_passwd = 'bry@NJ12@x'
        jkServer = jenkins.Jenkins(self.jenkins_master, self.login_user, self.login_passwd)
        self.jenkins_server = jkServer
