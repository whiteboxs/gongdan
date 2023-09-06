from flask import jsonify, request, session, url_for
from flask_restful import Resource, fields, marshal_with, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os
from .models import *
# from flask import Blueprint
from .utils.tools import user_login_required, admin_login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from sqlalchemy import or_, and_
from werkzeug.datastructures import FileStorage
import uuid
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

#
# class hello(Resource):
#     def get(self):
#         session['username'] = 'John'
#         return 'Session data is stored in Redis.'
#
#     def post(self):
#         return 'post request souer'


# flask-restful 字段格式化
# 字段格式化：返回给前端的数据格式
# 下面的字段里对应的是要返回的字段和类型如果注释掉data行，那类里面有 最终也不显示，
# 类里没有但是字典里有则显示 data2是给data修改名称 然后可以注释掉data data2里显示的是data的数据
# ret_fields = {
#     'data': fields.String,
#     'msg': fields.String,
#     'code': fields.Integer,
#     'like': fields.String(default='foot'),
#     'data2': fields.String(attribute='data')
# }
#
#
# class UserResource(Resource):
#     @marshal_with(ret_fields)
#     def get(self):
#         return {'code': '200',
#                 'msg': 'ok',
#                 'data': 'test'}


# usertest2_fields = {
#     'id': fields.Integer,
#     'department': fields.String,
#     'username': fields.String,
#     'password': fields.Integer
# }
# ret_fields_mysql = {
#     'status': fields.Integer,
#     'msg': fields.String,
#     # user对象的字段进行匹配 对一个显示
#     # 'data': fields.Nested(user_fields)
#     # 下面查询是all 显示全部则加个fields.List
#     'data': fields.List(fields.Nested(usertest2_fields))

# }


# class MysqlResource(Resource):
#     @marshal_with(ret_fields_mysql)
#     def get(self):
#         user = User.query.all()
#         return {'status': '1',
#                 'msg': 'ok',
#                 'data': user
#                 }


# --------------前端传入的参数解析
# parser = reqparse.RequestParser()
# parser.add_argument('username', type=str)
# parser.add_argument('password', type=int)
# parser.add_argument('department', type=str)


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


# 用户登录
class user_login(Resource):
    def post(self):
        req_data = request.get_json()
        print(req_data)
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
        # session["user_name"] = username
        # session["user_id"] = user.id
        return jsonify(code="200", username=username, token=token, user_id=user.id, msg="登录成功")

    # 用户添加，查询，修改，


user_fields = {
    'id': fields.Integer,
    'department': fields.String,
    'username': fields.String,
    'create_time': fields.DateTime,
    'tickets': fields.List(fields.Nested({
        'id': fields.Integer,
        'title': fields.String,
        'description': fields.String,
        'environment_id': fields.Integer,
        'user_id': fields.Integer,
        'assignee_id': fields.Integer,
        'status': fields.String,
        'attachment_url': fields.String,
    })),
}


class user(Resource):
    @jwt_required()
    @marshal_with(user_fields)
    def get(self, user_id):
        user = User.query.get(user_id)
        return user





    # 用户退出登录
class user_logout(Resource):
    @jwt_required()
    def get(self):
        # if 'user_id' in session:
        # session.pop('user_id')
        # session.modified = True
        return jsonify(code=200, msg="退出登录")


class environment(Resource):
    # @user_login_required
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
    def __init__(self):
        self.attachment_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attachment')
    @jwt_required()
    def post(self):
        # restful创建传入标准
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, location='form')
        parser.add_argument('description', type=str, location='form')
        parser.add_argument('environment_id', type=int, required=True, location='form')
        parser.add_argument('assignee_id', type=int, required=True, location='form')
        parser.add_argument('attachment', type=list, location='files', _external=False, required=False, action='append')
        args = parser.parse_args()
        user_identity = get_jwt_identity()
        user_id = user_identity['id']
        attachment_files = request.files.getlist('attachment')
        attachment_urls = []
        if attachment_files:
            if not os.path.exists(self.attachment_folder):
                os.makedirs(self.attachment_folder)

            for attachment_file in attachment_files:
                original_filename = secure_filename(attachment_file.filename)
                filename, file_extension = os.path.splitext(original_filename)  # 提取文件名和扩展名
                unique_filename = str(uuid.uuid4()) + file_extension  # 添加扩展名
                attachment_path = os.path.join(self.attachment_folder, unique_filename)
                attachment_file.save(attachment_path)
                attachment_url_path = url_for('attachment_path', filename=filename, _external=True)  # 生成附件访问链接
                print('attachment_url_path', attachment_url_path)
                attachment_urls.append(attachment_url_path)

            attachment_urls = ', '.join(attachment_urls)  # 将列表转换为字符串传入数据库
        else:
            attachment_urls = None
        try:
            ticket = Ticket(title=args['title'], description=args['description'], user_id=user_id, environment_id=args['environment_id'], assignee_id=args['assignee_id'], attachment_url=attachment_urls)
            print(attachment_urls)
            environment = Environment.query.filter_by(id=args['environment_id']).first()
            if environment.name == "开发环境" or environment.name == "测试环境":
                ticket.status = "未完成"
            db.session.add(ticket)
            db.session.commit()
            # 更新工单的附件名和链接字段
            return {
                       'id': ticket.id,
                       'title': ticket.title,
                       'description': ticket.description,
                       'environment': ticket.environment.name,
                       'user_id': ticket.user_id,
                       'assignee': ticket.assignee.id,
                       'status': ticket.status,
                       'attachment_url': ticket.attachment_url,

                   }, 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="发布工单失败")


# 修改，删除，查询工单
class ticket(Resource):
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

    @jwt_required()
    def put(self, ticket_id):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, location='form')
        parser.add_argument('description', type=str, location='form')
        parser.add_argument('environment_id', type=int, required=True, location='form')
        parser.add_argument('assignee_id', type=int, required=True, location='form')
        # parser.add_argument('attachment', type=FileStorage, location='files', required=False)
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'msg': '工单没有找到'}, 404
        user_identity = get_jwt_identity()
        user_id = user_identity['id']
        args = parser.parse_args()
        ticket.title = args['title']
        ticket.description = args['description']
        # 查询输入的环境id号,修改的时候不可能知道名称要前端转下应该
        # environment = Environment.query.filter_by(name=args['environment_id']).first()
        # # 经办人id
        # assignee = Assignee.query.filter_by(name=args['assignee_id']).first()
        # print(environment.id, assignee.id)
        ticket.environment_id = args['environment_id']
        ticket.assignee_id = args['assignee_id']
        db.session.commit()
        return {
            'id': ticket.id,
            'title': ticket.title,
            'description': ticket.description,
            'environment': ticket.environment.name,
            'assignee': ticket.assignee.name,
            'user_id': user_id
        }

    @jwt_required()
    def delete(self, ticket_id):
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'msg': '工单没有找到'}, 404
        db.session.delete(ticket)
        db.session.commit()
        return {'msg': '已删除'}, 204


# 查询所有用户
user_fields = {
    'id': fields.Integer,
    'department': fields.String,
    'username': fields.String,
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
    @jwt_required()
    @marshal_with(all_users_fields)
    def get(self):
        users = User.query.all()
        return {'code': 200,
                'msg': 'ok',
                'data': users
                }


# 查询环境标签
environment_fields = {
    # 'tickets': fields.String
    'name': fields.String,
    'id': fields.Integer
}
all_environments_fields = {
    'code': fields.Integer,
    'msg': fields.String,
    # user对象的字段进行匹配 对一个显示
    # 'data': fields.Nested(user_fields)
    # 下面查询是all 显示全部则加个fields.List
    'data': fields.List(fields.Nested(environment_fields))
}


class all_environments(Resource):
    @jwt_required()
    @marshal_with(all_environments_fields)
    def get(self):
        environments = Environment.query.all()
        return {'code': 200,
                'msg': 'ok',
                'data': environments
                }


# 查询所有经办人
assignee_fields = {
    'id': fields.Integer,
    'name': fields.String,
    # 'password': fields.Integer
}
all_assignee_fields = {
    'code': fields.Integer,
    'msg': fields.String,
    # user对象的字段进行匹配 对一个显示
    # 'data': fields.Nested(user_fields)
    # 下面查询是all 显示全部则加个fields.List
    'data': fields.List(fields.Nested(assignee_fields))

}


class all_assignee(Resource):
    @jwt_required()
    @marshal_with(all_assignee_fields)
    def get(self):
        assignees = Assignee.query.all()
        return {'code': 200,
                'msg': 'ok',
                'data': assignees
                }


# 查询所有订单
class all_tickets(Resource):
    @jwt_required()
    def get(self):
        page = request.args.get('pagenum', default=1, type=int)  # 获取请求中的页码参数，默认为第一页
        per_page = request.args.get('pagesize', default=10, type=int)  # 获取每页显示条数参数，默认为10条
        # 查询数据库中的所有订单，并按照创建时间降序排序
        tickets = Ticket.query.order_by(Ticket.create_time.desc()).paginate(page=page, per_page=per_page)
        total_count = tickets.total  # 获取总记录数
        # tickets = Ticket.query.all(.order_by(Feedback.create_time.desc()))
        ticket_list = []
        for ticket in tickets.items:
            ticket_info = {
                'id': ticket.id,
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'create_time': ticket.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'update_time': ticket.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                'attachment_url': ticket.attachment_url,
                'reporter': ticket.user.username,
                'reporter_id': ticket.user.id,
                'environment': ticket.environment.name if ticket.environment else None,
                'assignee': ticket.assignee.name if ticket.assignee else None
            }
            ticket_list.append(ticket_info)
            # 对 ticket_list 进行降序排序，根据 create_time
            sorted_tickets = sorted(ticket_list, key=lambda x: x['create_time'], reverse=True)

        return {'code': 200, 'msg': 'ok', 'count': total_count, 'page': page, "per_page": per_page, 'data': sorted_tickets}

# 查询登录账号的工单
class user_tickets(Resource):
    @jwt_required()
    def get(self):
        page = request.args.get('pagenum', default=1, type=int)
        per_page = request.args.get('pagesize', default=10, type=int)
        user_identity = get_jwt_identity()
        user_id = user_identity['id']

        # 获取搜索关键字
        keyword = request.args.get('keyword', '')

        # 创建查询对象
        query = Ticket.query.filter_by(user_id=user_id)

        # 根据关键字进行搜索
        if keyword:
            query = query.filter(
                or_(
                    Ticket.title.contains(keyword),
                    Ticket.description.contains(keyword)
                )
            )
        # 分页查询
        tickets = query.order_by(Ticket.create_time.desc()).paginate(page=page, per_page=per_page)
        total_count = tickets.total
        ticket_list = []

        for ticket in tickets.items:
            ticket_info = {
                'ticket_id': ticket.id,
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'create_time': ticket.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'update_time': ticket.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                'attachment_url': ticket.attachment_url,
                'reporter': ticket.user.username,
                'reporter_id': ticket.user.id,
                'environment': ticket.environment.name if ticket.environment else None,
                'assignee': ticket.assignee.name if ticket.assignee else None
            }
            ticket_list.append(ticket_info)

        return {'code': 200, 'msg': 'ok', 'count': total_count, 'page': page, "per_page": per_page, 'data': ticket_list}

class ticket_processing(Resource):
    @jwt_required()
    def get(self):
        page = request.args.get('pagenum', default=1, type=int)
        per_page = request.args.get('pagesize', default=10, type=int)
        user_identity = get_jwt_identity()
        loginname = user_identity['user']
        print(loginname)
        # 获取搜索关键字
        keyword = request.args.get('keyword', '')
        # 对登录用户和经办人id进行匹配
        # 创建查询对象
        query = Ticket.query.filter(Ticket.assignee.has(Assignee.name == loginname))

        # 根据关键字进行搜索
        if keyword:
            query = query.filter(
                or_(
                    Ticket.title.contains(keyword),
                    Ticket.description.contains(keyword)
                )
            )
        # 分页查询
        tickets = query.order_by(Ticket.create_time.desc()).paginate(page=page, per_page=per_page)
        total_count = tickets.total
        ticket_list = []

        for ticket in tickets.items:
            ticket_info = {
                'ticket_id': ticket.id,
                'title': ticket.title,
                'description': ticket.description,
                'status': ticket.status,
                'create_time': ticket.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'update_time': ticket.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                'attachment_url': ticket.attachment_url,
                'reporter': ticket.user.username,
                'reporter_id': ticket.user.id,
                'environment': ticket.environment.name if ticket.environment else None,
                'assignee': ticket.assignee.name if ticket.assignee else None,
                'comment': [],
            }
            for feedback in ticket.feedbacks:
                comment_info = {
                    'comment_id': feedback.id,
                    'comment': feedback.comment,
                    'create_time': feedback.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'attachment_url': feedback.attachment_url
                }
                ticket_info['comments'].append(comment_info)
            ticket_list.append(ticket_info)

        return {'code': 200, 'msg': 'ok', 'count': total_count, 'page': page, "per_page": per_page, 'data': ticket_list}


# 进行工单创建
class ticket_processing_feedbacks(Resource):
    @jwt_required()
    def post(self):
        page = request.args.get('pagenum', default=1, type=int)
        per_page = request.args.get('pagesize', default=10, type=int)
        # 获取登录者的id
        user_identity = get_jwt_identity()
        user_id = user_identity['id']
        # 对登录用户和经办人id进行匹配
        condition = Feedback.assignee_id == user_id

        feedback = Feedback.query.filter(condition).order_by(Feedback.create_time.desc()).paginate(page=page, per_page=per_page, error_out=False)

        # 分页查询
        total_count = feedback.total
        feedback_list = []

        for item in feedback.items:
            ticket_info = {
                'ticket_id': item.ticket.id,
                'title': item.ticket.title,
                'description': item.ticket.description,
                'status': item.ticket.status,
                'ticket_create_time': item.ticket.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'ticket_attachment_url': item.ticket.attachment_url,
                'reporter': item.ticket.user.username,
                'reporter_id': item.ticket.user.id,
                'ticket_environment': item.ticket.environment.name if item.ticket.environment else None,
                'assignee': item.ticket.assignee.name if item.ticket.assignee else None,
                'feedback_id': item.id,
                'comment': item.comment,
                'feedback_create_time': item.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'feedback_update_time': item.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                'feedback_attachment_url': item.attachment_url
            }
            feedback_list.append(ticket_info)

        return {'code': 200, 'msg': 'ok', 'count': total_count, 'page': page, "per_page": per_page, 'data': feedback_list}





class all_feedbacks(Resource):
    pass
