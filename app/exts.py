# 插件管理 第三方插件

# 导入第三方插件
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_cors import CORS
# from flask_session import Session
from flask_jwt_extended import JWTManager



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
    cors.init_app(app=app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
 #    session.init_app(app=app)
    jwt.init_app(app=app)
