from flask import jsonify, request, session, g
from flask_restful import Resource, fields, marshal_with, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os
from .models import *
# from flask import Blueprint
from .utils.tools import user_login_required, admin_login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# from flask_wtf import FlaskForm
# from wtforms import StringField, FileField

# token头 Bearer
"""
管理员

    登录 /admin/login
    检查登陆状态 /admin/session
    登出 /admin/logout
    添加管理员 /admin/ manager
    删除管理员 /admin/ manager
    增删改查环境标签 /environment
    查看所有用户 /all/user/int:page
    获取所有工单 /all/ticket/int:page
    搜索 /main/work_order/search/int:page
    搜索工单id /user/work_order/article/detail/int:blog_id


用户
    注册 /user/register
    登录 /user/login
    登录状态 /user/session
    登出 /user/session
    增删改查工单 /ticket
    工单历史 /ticket/history
    


"""


# 初始化蓝图
# blue = Blueprint('user', __name__)

# 类视图 cbv class based view 这里写的都是class类视图 这里和前端后集成里的view差不多
# 类视图不用加装饰器，单独写个路由文件配合使用名称为urls.py


class hello(Resource):
    def get(self):
        session['username'] = 'John'
        return 'Session data is stored in Redis.'

    def post(self):
        return 'post request souer'


# flask-restful 字段格式化
# 字段格式化：返回给前端的数据格式
# 下面的字段里对应的是要返回的字段和类型如果注释掉data行，那类里面有 最终也不显示，
# 类里没有但是字典里有则显示 data2是给data修改名称 然后可以注释掉data data2里显示的是data的数据
ret_fields = {
    'data': fields.String,
    'msg': fields.String,
    'code': fields.Integer,
    'like': fields.String(default='foot'),
    'data2': fields.String(attribute='data')
}


class UserResource(Resource):
    @marshal_with(ret_fields)
    def get(self):
        return {'code': '200',
                'msg': 'ok',
                'data': 'test'}


usertest2_fields = {
    'id': fields.Integer,
    'department': fields.String,
    'username': fields.String,
    'password': fields.Integer
}
ret_fields_mysql = {
    'status': fields.Integer,
    'msg': fields.String,
    # user对象的字段进行匹配 对一个显示
    # 'data': fields.Nested(user_fields)
    # 下面查询是all 显示全部则加个fields.List
    'data': fields.List(fields.Nested(usertest2_fields))

}


class MysqlResource(Resource):
    @marshal_with(ret_fields_mysql)
    def get(self):
        user = User.query.all()
        return {'status': '1',
                'msg': 'ok',
                'data': user
                }


# --------------前端传入的参数解析
parser = reqparse.RequestParser()
parser.add_argument('username', type=str)
parser.add_argument('password', type=int)
parser.add_argument('department', type=str)


# def get(self):
#     args = parser.parse_args()
#     username = args.get('username')
#     password = args.get('password')
#     department = args.get('department')
#     return jsonify({'username': username, 'password': password, 'department': department})


class admin_login(Resource):
    pass


class admin_session_check(Resource):
    pass


class admin_logout(Resource):
    pass


# 用户注册
class user_register(Resource):
    def post(self):
        req_data = request.get_json()
        username = req_data.get("username")
        password = req_data.get("password")
        department = req_data.get("department")
        user = User(username=username, password=password)
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify(code=200, msg="用户注册成功")
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="用户注册失败")


class admin_login(Resource):
    def get(self):
        req_data = request.get_json()
        username = req_data.get("username")
        password = req_data.get("password")
        if not all([username, password]):
            return jsonify(code=400, msg="登录参数不全")
        # 查找管理源账号    验证密码
        admin = Admin.query.filter(Admin.username == username).first()
        if admin is None or password != admin.password:
            return jsonify(code=400, msg="管理员或者密码错误,或者没有这个账号")
        # 保存session
        session["admin_name"] = username
        session["admin_id"] = admin.id
        return jsonify(code=200, msg="登录成功")


class user_session_check(Resource):
    pass


# 用户登录
class user_login(Resource):
    def get(self):
        req_data = request.get_json()
        username = req_data.get("username")
        password = req_data.get("password")
        if not all([username, password]):
            return jsonify(code=200, msg="用户登录参数不全")
        # 查找用户账号    验证密码
        user = User.query.filter(User.username == username).first()
        if user is None or password != user.password:
            return jsonify(code=400, msg="管理员或者错误")
        # 保存session
        # 认证成功，创建JWT令牌
        token = create_access_token(identity={"user": user.username, "id": user.id})
        #session["user_name"] = username
        #session["user_id"] = user.id
        return jsonify(code="200", username=username, token=token, msg="登录成功")


# 用户退出登录
class user_logout(Resource):
    @jwt_required()
    def get(self):
        #if 'user_id' in session:
            #session.pop('user_id')
            #session.modified = True
        return jsonify(code=200, msg="退出登录")


class environment(Resource):
    #@user_login_required
    @jwt_required()
    def post(self):
        user_identity = get_jwt_identity()
        user_id = user_identity['id']
        username = user_identity['user']
        print(user_id, username)
        # 传入标签 获取sesion看有没有登录
        req_data = request.get_json()
        environment = req_data.get("environment")  # 获取标签 这里用的是data可能是数据id可以查查区别
        # user_id = g.user_id  # 装饰器里获取session里的用户id
        if not all([environment, user_id]):
            return jsonify(code=400, msg="参数不完整，账号未登录")
        environment_name = Environment(name=environment)
        try:
            db.session.add(environment_name)
            db.session.commit()
            return jsonify(code=200, msg="添加标签成功")
        except Exception as e:
            print(e)
            db.session.rollback()  # 数据库回滚
            return jsonify(code=400, msg="添加标签失败")


class add_ticket(Resource):
    #@user_login_required
    @jwt_required()
    def post(self):
        # restful创建传入标准
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, location='form')
        parser.add_argument('description', type=str, location='form')
        parser.add_argument('environment', type=str, required=True, location='form')
        parser.add_argument('assignee', type=str, required=True, location='form')
        parser.add_argument('attachment', type=FileStorage, location='files', required=False)
        args = parser.parse_args()
        #user_id = g.user_id
        user_identity = get_jwt_identity()
        user_id = user_identity['id']
        # 查询输入的环境
        environment = Environment.query.filter_by(name=args['environment']).first()
        # 获取经办人
        assignee = Assignee.query.filter_by(name=args['assignee']).first()
        # 获取上传的附件文件
        attachment_file = args['attachment']
        # 处理附件文件，例如保存到服务器
        if attachment_file:
            filename = secure_filename(attachment_file.filename)
            attachment_file.save('C:\\Users\\Administrator\\PycharmProjects\\pythonProject3\\restful-gogndan\\app\\attachment\\' + filename)
            attachment_url = f'C:\\Users\\Administrator\\PycharmProjects\\pythonProject3\\restful-gogndan\\app\\attachment\\{filename}'
        else:
            attachment_url = None

        try:
            ticket = Ticket(title=args['title'], description=args['description'], user_id=user_id, environment_id=environment.id, assignee_id=assignee.id, attachment_url=attachment_url)
            if args['environment'] == "开发环境" or "测试环境":
                ticket.status = "未完成"
            db.session.add(ticket)
            db.session.commit()
            # 更新工单的附件名和链接字段
            return {
                       'id': ticket.id,
                       'title': ticket.title,
                       'description': ticket.description,
                       'environment_id': ticket.environment_id,
                       'user_id': ticket.user_id,
                       'assignee_id': ticket.assignee_id,
                       'status': ticket.status,
                       'attachment_url': ticket.attachment_url

                   }, 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="发布工单失败")


# class add_ticket(Resource):
#     @user_login_required
#     def post(self):
# req_data =request.form.to_dict()
#         req_data = request.get_json()
#         user_id = g.user_id
#         title = req_data.get("title")
#         description = req_data.get("description")
#         environment = Environment.query.filter_by(name=req_data.get("environment")).first()
#         ticket = Ticket(title=title, description=description, user_id=user_id, environment_id=environment.id)
#         if not all([user_id, title, description, environment]):
#             return jsonify(code=400, msg="用户未登录或者传入参数不完整")
#         try:
#             # db.session.add(ticket)
#             # db.session.commit()
#             attachment_file = request.files.get('attachment')
#             print(attachment_file)
#             if attachment_file:
#                 # 保存图片到服务器
#                 attachment_name = attachment_file.filename
#                 print(attachment_name)
#                 attachment_file.save(f' C:\\Users\\Administrator\\PycharmProjects\\pythonProject3\\restful-gogndan\\app\\attachment\\{attachment_name}')
#
#                 # 更新工单的图片名和链接字段
#                 ticket.attachment_url = f'C:\\Users\\Administrator\\PycharmProjects\\pythonProject3\\restful-gogndan\\app\\attachment\\{attachment_name}'
#             db.session.add(ticket)
#             db.session.commit()
#             return jsonify(code=200, msg="发布留言成功")
#         except Exception as e:
#             print(e)
#             db.session.rollback()
#             return jsonify(code=400, msg="发布留言失败")

# 修改，删除，查询工单
class ticket(Resource):
    # @user_login_required
    @jwt_required()
    def get(self, ticket_id):
        ticket = Ticket.query.get(ticket_id)
        if ticket:
            return {
                'id': ticket.id,
                'title': ticket.title,
                'description': ticket.description,
                'environment_id': ticket.environment_id,
                'user_id': ticket.user_id,
                'assignee_id': ticket.assignee_id,
                'attachment_url': ticket.attachment_url
            }
        else:
            return {'msg': '工单没有找到'}, 404

    @user_login_required
    def put(self, ticket_id):
        parser = reqparse.RequestParser()
        # parser.add_argument('title', type=str, required=True, location='form')
        parser.add_argument('description', type=str)
        parser.add_argument('environment', type=str, required=True)
        parser.add_argument('assignee', type=str, required=True)
        # parser.add_argument('attachment', type=FileStorage, location='files', required=False)
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'msg': '工单没有找到'}, 404
        user_id = g.user_id
        args = parser.parse_args()
        ticket.description = args['description']
        # 查询输入的环境id号
        environment = Environment.query.filter_by(name=args['environment']).first()
        assignee = Assignee.query.filter_by(name=args['assignee']).first()
        print(environment.id, assignee.id)
        ticket.environment_id = environment.id
        ticket.assignee_id = assignee.id
        db.session.commit()
        return {
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'environment_id': ticket.environment_id,
            'assignee_id': ticket.assignee_id,
            'user_id': user_id
        }

    @user_login_required
    def delete(self, ticket_id):
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'msg': '工单没有找到'}, 404

        db.session.delete(ticket)
        db.session.commit()

        return '已删除', 204


# 查询所有用户
user_fields = {
    'id': fields.Integer,
    'department': fields.String,
    'username': fields.String,
    # 'password': fields.Integer
}
all_users_fields = {
    'code': fields.Integer,
    'status': fields.Integer,
    'msg': fields.String,
    # user对象的字段进行匹配 对一个显示
    # 'data': fields.Nested(user_fields)
    # 下面查询是all 显示全部则加个fields.List
    'data': fields.List(fields.Nested(user_fields))

}


class all_users(Resource):
    @user_login_required
    @marshal_with(all_users_fields)
    def get(self):
        users = User.query.all()
        return {'code': 200, 'status': 1,
                'msg': 'ok',
                'data': users
                }


# 查询环境标签
environment_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'tickets': fields.String
    # 'password': fields.Integer
}
all_environments_fields = {
    'code': fields.Integer,
    'status': fields.Integer,
    'msg': fields.String,
    # user对象的字段进行匹配 对一个显示
    # 'data': fields.Nested(user_fields)
    # 下面查询是all 显示全部则加个fields.List
    'data': fields.List(fields.Nested(environment_fields))
}


class all_environments(Resource):
    @user_login_required
    @marshal_with(all_environments_fields)
    def get(self):
        environments = Environment.query.all()
        return {'code': 200, 'status': 1,
                'msg': 'ok',
                'data': environments
                }


# 查询所有订单
ticket_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'status': fields.String,
    'create_time': fields.DateTime,
    'user_id': fields.Integer,
    'assignee_id': fields.Integer,
    'environment_id': fields.Integer,
    'attachment_url': fields.String
}
all_ticket_fields = {
    'code': fields.Integer,
    'msg': fields.String,
    # user对象的字段进行匹配 对一个显示
    # 'data': fields.Nested(user_fields)
    # 下面查询是all 显示全部则加个fields.List
    'data': fields.List(fields.Nested(ticket_fields))
}


class all_tickets(Resource):
    @user_login_required
    @marshal_with(all_ticket_fields)
    def get(self):
        ticket = Ticket.query.all()
        return {'code': 200, 'status': 1,
                'msg': 'ok',
                'data': ticket
                }


# 查询所有订单的反馈
class add_feedback(Resource):
    @user_login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('comment', type=str, required=True)
        parser.add_argument('ticket_id', type=int, required=True)
        args = parser.parse_args()
        # user_id = g.user_id
        ticket = Ticket.query.filter_by(id=args['ticket_id']).all()
        # # 获取上传的附件文件
        # attachment_file = args['attachment']
        # # 处理附件文件，例如保存到服务器
        # if attachment_file:
        #     filename = secure_filename(attachment_file.filename)
        #     attachment_file.save('C:\\Users\\Administrator\\PycharmProjects\\pythonProject3\\restful-gogndan\\app\\attachment\\' + filename)
        #     attachment_url = f'C:\\Users\\Administrator\\PycharmProjects\\pythonProject3\\restful-gogndan\\app\\attachment\\{filename}'
        # else:
        #     attachment_url = None
        try:
            for i in ticket:
                print(i.user.id, i.user.username, i.assignee.id, i.assignee.name, i.id)
                feedback = Feedback(comment=args['comment'], user_id=i.user.id, assignee_id=i.assignee.id, ticket_id=i.id)
                db.session.add(feedback)
                db.session.commit()
            return {
                       'id': feedback.id,
                       'comment': feedback.comment,
                       'user_id': feedback.user.id,
                       'environment_id': feedback.assignee_id,
                       'ticket_id': feedback.ticket_id
                   }, 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="工单回复失败")


class all_feedbacks(Resource):
    pass
