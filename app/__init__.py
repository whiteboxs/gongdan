# 初始化文件 创建flash应用
# url_for, request, redirect, render_template
from flask import Flask
# from ..apis.system_api import blue
from .exts import init_exts
# 导入urls这里测试是暗的也有作用，不添加则访问接口报错
from . import urls

# 时间
import datetime


def create_app():
    app = Flask(__name__)
    # app_context = app.app_context()
    # app_context.push()
    # app.secret_key = "1u4141414141244o14ufgqr&*"
    # 注册蓝图，
    # app.register_blueprint(blueprint=blue)

    # 解决flask接口中文数据编码问题(使用RESTFUL)
    app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
    # tocker 秘钥
    app.config['JWT_SECRET_KEY'] = 'ruobhuyoqurogq^!$^&*@#'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)  # 设置访问令牌过期时间为1小时
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=1)  # 设置刷新令牌过期时间为30天
    #app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=1)
    #app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(minutes=10)
    # 配置数据库
    # DB_URI = 'sqlite:///sqlite3.db'
    DB_URI = 'mysql+pymysql://test:123456@192.168.86.123:3306/restful'
    app.config['SELECT_KEY'] = '411ffdafqGR1'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # # 配置redis
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # app.config["SESSION_TYPE"] = "redis"  # 设置那个数据库
    # app.config["SECRET_KEY"] = "sdfsdfsdf"
    # app.config["SESSION_USE_SIGNER"] = True  # 对cookie中session_id进行隐藏处理 加密混淆
    # app.config["PERMANENT_SESSION_LIFETIME"] = 360  # session数据的有效期，单位秒
    # app.config["SESSION_REDIS"] = redis.Redis(host="192.168.0.123", port=6379, password=123456, db=2)  # 连接数据库
    # app.config["SESSION_KEY_PREFIX"] = "session:"  # 设置你在session中的session头添加的东西
    # 初始化插件
    # jenkins登录
    app.config['JENKINS_MASTER'] = "http://192.168.0.152:8080"
    app.config['JENKINS_LOGIN_USER'] = 'admin'
    app.config['JENKINS_LOGIN_PASSWD'] = 'bry@NJ12@x'
    #jumpserver
    app.config['key_id'] = 'af14e012-186e-4528-8298-e1505552682b'
    app.config['secret'] = '7cafb5cb-fa4f-4e16-b482-cde9f608a526'
    init_exts(app=app)

    return app



