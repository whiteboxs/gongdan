# -*- coding: utf-8 -*-

from flask import jsonify, request, session, send_from_directory
from flask_restful import Resource, fields, marshal_with, reqparse
from werkzeug.utils import secure_filename
import os
from ..models import *
# from flask import Blueprint
from ..utils.tools import user_login_required, admin_login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token, get_jwt
from sqlalchemy import or_
from werkzeug.datastructures import FileStorage
import uuid
from collections import defaultdict

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

# 菜单权限
class all_menus(Resource):
    @jwt_required()
    def get(self):
        menus = Menu.query.all()

        menu_list = []
        for menu in menus:
            menu.info = {
                'id': menu.id,
                'title': menu.menu_name,
                'icon': menu.icon,
                'path': menu.menu_path if menu.menu_path else None,
                'menu_type': menu.menu_type,
                'parentid': menu.parentId,
                'parentname': menu.parentName,
                'permiss': menu.permiss,
                'route_component': menu.route_component,
                'create_time': menu.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            menu_list.append(menu.info)
        return {'code': 200, 'msg': 'ok', 'data': menu_list}




# 读取菜单权限
class menu_permiss(Resource):
    @jwt_required()
    def get(self, role_id):
        menu_permiss = Roletomenu.query.filter_by(role_id=role_id).all()
        menu_permiss_list = [permission.menu_id for permission in menu_permiss]
        return {'access': menu_permiss_list, 'msg': 'ok', 'role_id': role_id}


    def put(self, role_id):
        # 查所有角色当前返回的menu信息
        if Role.query.filter_by(id=role_id).first() is not None:
            role = Role.query.get(role_id)
        else:
            return jsonify({"code": 400, "msg": "角色不存在"})
        menu_ids = request.json.get('access')  # 假设前端传入的菜单id列表存放在一个名为 'menu_ids' 的 JSON 字段
        # 查询列表里在不在库里，如果在则过滤出来
        menu = Menu.query.filter(Menu.id.in_(menu_ids)).all()
        # 识别出来后 赋值给roles.menus菜单，因为menus是中间表入口，所以会自动在中间表中添加关系
        role.menus = menu
        try:
            db.session.add(role)
            db.session.commit()
            menu_permiss = Roletomenu.query.filter_by(role_id=role_id).all()
            menu_permiss_list = [permission.menu_id for permission in menu_permiss]
            return {'access': menu_permiss_list, 'msg': '更新权限成功', 'role_id': role_id}
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="更新权限失败")


# 添加菜单
class add_menu(Resource):
    @jwt_required()
    def post(self):
        # restful创建传入标准
        parser = reqparse.RequestParser()
        parser.add_argument('menu_name', type=str, required=True, location='form')
        parser.add_argument('menu_path', type=str, location='form')
        parser.add_argument('menu_type', type=str, required=True, location='form')
        parser.add_argument('icon', type=str, required=True, location='form')
        parser.add_argument('parentid', type=int, location='form')
        parser.add_argument('parentname', type=str, location='form')
        parser.add_argument('permiss', type=int, location='form')
        parser.add_argument('route_component', type=str, location='form')
        args = parser.parse_args()
        if Menu.query.filter_by(menu_name=args['menu_name']).first() is not None:
            return jsonify({"code": 400, "msg": "菜单名已存在"})
        try:
            menu = Menu(menu_name=args['menu_name'], menu_path=args['menu_path'], menu_type=args['menu_type'], icon=args['icon'], parentId=args['parentid'], parentName=args['parentname'], permiss=args['permiss'], route_component=args['route_component'])
            db.session.add(menu)
            db.session.commit()
            # 更新工单的附件名和链接字段
            return {
                       'msg': '创建菜单完成',
                       'code': 201,
                       'id': menu.id,
                       'menu_name': menu.menu_name,
                       'menu_path': menu.menu_path,
                       'menu_type': menu.menu_type,
                       'icon': menu.icon,
                       'parentid': menu.parentId,
                       'parentname': menu.parentName,
                       'permiss': menu.permiss,
                       'route_component': menu.route_component,
                   }, 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="创建菜单失败")

#测试
class menu(Resource):
    @jwt_required()
    def post(self, role_id):
        role = Role.query.get(role_id)
        print("---", role)
        # 查所有角色当前返回的menu信息
        menu = Menu.query.all()
        # 显示课程表名字
        print(menu)
        for i in menu:
            print(i.menu_name)
        # 这里角色的菜单导入到中间表 id1的学生有几门课
        role.menus = menu
        db.session.add(role)
        db.session.commit()
        return jsonify({'message': 'ok'})





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
        if User.query.filter_by(username=username).first() is not None:
            return jsonify({"code": 400, "msg": "账号已存在"})
        user = User(username=username, department=department)
        user.hash_password(password)
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify(code=200, msg="用户注册成功")
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="用户注册失败")


# class admin_login(Resource):
#     def get(self):
#         req_data = request.get_json()
#         username = req_data.get("username")
#         password = req_data.get("password")
#         if not all([username, password]):
#             return jsonify(code=400, msg="登录参数不全")
#         # 查找管理源账号    验证密码
#         admin = Admin.query.filter(Admin.username == username).first()
#         if admin is None or password != admin.password:
#             return jsonify(code=400, msg="管理员或者密码错误,或者没有这个账号")
#         # 保存session
#         session["admin_name"] = username
#         session["admin_id"] = admin.id
#         return jsonify(code=200, msg="登录成功")


class add_user(Resource):
    @jwt_required()
    def post(self):
        # restful创建传入标准
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, location='form')
        parser.add_argument('password', type=str, location='form')
        parser.add_argument('department', type=str, required=True, location='form')
        parser.add_argument('role_id', type=int, required=True, location='form')
        args = parser.parse_args()
        if User.query.filter_by(username=args['username']).first() is not None:
            return jsonify({"code": 400, "msg": "账号已存在"})
        try:
            user = User(username=args['username'], department=args['department'], role_id=args['role_id'])
            user.hash_password(args['password'])
            db.session.add(user)
            db.session.commit()
            # 更新工单的附件名和链接字段
            return {
                       'msg': '创建用户完成',
                       'id': user.id,
                       'username': user.username,
                       'department': user.department,
                       'status': user.status,
                       'role_id': user.role_id
                   }, 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="创建用户失败")


# 用户登录
class user_login(Resource):
    def post(self):
        req_data = request.get_json()
        print(req_data)
        username = req_data.get("username")
        password = req_data.get("password")
        if not all([username, password]):
            return jsonify(code=200, msg="用户登录参数不全")
        if User.query.filter_by(username=username).filter_by(status=True).first() is not None:
            # 查找用户账号    验证密码
            user = User.query.filter(User.username == username).first()
            # 密码效验
            if user.verify_password(password) is True:
                # 保存session
                # 认证成功，创建JWT令牌
                access_token = create_access_token(identity={"user": user.username, "id": user.id})
                refresh_token = create_refresh_token(identity={"user": user.username, "id": user.id})
                # session["user_name"] = username
                # session["user_id"] = user.id
                return jsonify(code=200, username=username, expires_in=60, access_token=access_token, refresh_token=refresh_token, user_id=user.id, role_id=user.role_id, role_name=user.role.role_name, update_time=user.update_time, msg="登录成功")
            else:
                return jsonify(code=400, msg="用户密码错误")
        else:
            return jsonify(code=400, msg="账号已禁用")


# token 刷新
class refresh_token(Resource):
    @jwt_required(refresh=True)  # 刷新token装饰器
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token, msg="ok")


# 用户添加，查询，修改，删除

class userinfo(Resource):
    @jwt_required()
    def get(self, user_id):
        user = User.query.get(user_id)
        print(user)
        if user:
            return {'code': 200, 'msg': "ok",
                    'id': user.id,
                    'username': user.username,
                    'department': user.department,
                    'status': user.status,
                    'role_id': user.role_id,
                    'role_name': user.role.role_name,
                    }
        else:
            return jsonify(code=404, msg="user不存在")

    def put(self, user_id):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, location='form')
        parser.add_argument('department', type=str, location='form')
        parser.add_argument('user_status', type=str, location='args')
        parser.add_argument('role_id', type=int, location='form')
        args = parser.parse_args()
        if args['user_status'] is not None:
            print(args['user_status'])
            try:
                # 将 user_status 转换为布尔值
                user_status = args['user_status'].lower() == 'true'  # 将字符串转换为布尔值
                print(user_status)
                # 根据user_id查询并更新user_status
                User.query.filter_by(id=user_id).update({"status": user_status})
                db.session.commit()
                return jsonify(code=200, user_id=user_id, user_status=user_status, msg="修改用户状态成功")
            except Exception as e:
                print(e)
                db.session.rollback()  # 数据库回滚
                return jsonify(code=400, msg="修改用户状态失败")
        elif args['username'] is not None:
            try:
                user = User.query.filter_by(id=user_id).first()
                if user:
                    if user.username != args['username']:
                        existing_user = User.query.filter_by(username=args['username']).first()
                        if existing_user is None:
                            user.username = args['username']
                        else:
                            return jsonify(code=400, msg="用户名已经存在")
                user.username = args['username']
                user.department = args['department']
                user.role_id = args['role_id']
                # user.password = args['password']
                # User.query.filter_by(id=user_id).update({"username": args['username']}, {"department": args['department']}, {"role_id": args['role_id']}, {"password": args['password']})  # 根据user_id查询并更新username
                db.session.commit()
                return jsonify(code=200, username=args['username'], department=args['department'], role_id=args['role_id'], msg="修改成功")
            except Exception as e:
                print(e)
                db.session.rollback()  # 数据库回滚
                return jsonify(code=400, msg="修改用户信息失败")
        else:
            return jsonify(code=400, msg="参数不完整，没有此账号")

    def delete(self, user_id):
        user = User.query.get(user_id)

        if not user:
            return {'msg': '用户没有找到'}, 404
        db.session.delete(user)
        db.session.commit()
        return {'msg': '用户已删除'}, 204


class userstatus(Resource):
    @jwt_required()
    def put(self, user_id, user_status):
        try:
            user = User.objects.get
            print(user.status)
        except User.DoesNotExist:
            return {'error': 'User not found'}, 404

        if not isinstance(user_status, bool):
            return {'error': 'user_status must be a boolean'}, 400

            # Update user status based on the provided user_status
        # Here, you can customize how you update the user status based on your requirements.
        user.is_active = user_status
        user.save()

        return {'message': 'User status updated successfully'}, 200



# 添加 job
class add_role(Resource):
    @jwt_required()
    def post(self):
        # restful创建传入标准
        parser = reqparse.RequestParser()
        parser.add_argument('role_name', type=str, required=True, location='form')
        args = parser.parse_args()
        # 检查 job_name 是否已存在
        existing_role = Role.query.filter_by(role_name=args['role_name']).first()
        if existing_role:
            return jsonify(code=400, msg="创建的角色名已经存在")
        try:
            role = Role(role_name=args['role_name'])
            db.session.add(role)
            db.session.commit()
            return {
                       'msg': '创建角色完成',
                       'id': role.id,
                       'role_name': role.role_name,
                       'create_time': role.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                       'update_time': role.update_time.strftime('%Y-%m-%d %H:%M:%S')
                   }, 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="创建角色失败")


# role查询
role_fields = {
    'id': fields.Integer,
    'role_name': fields.String,
    'create_time': fields.String,
}
all_role_fields = {
    'code': fields.Integer,
    'status': fields.Integer,
    'msg': fields.String,
    # user对象的字段进行匹配 对一个显示
    # 'data': fields.Nested(user_fields)
    # 下面查询是all 显示全部则加个fields.List
    'data': fields.List(fields.Nested(role_fields))

}


class all_roles(Resource):
    @jwt_required()
    @marshal_with(all_role_fields)
    def get(self):
        roles = Role.query.all()
        return {'code': 200,
                'msg': 'ok',
                'data': roles
                }

# 查询，删除单个角色
class role(Resource):
    @jwt_required()
    def get(self, role_id):
        role = Role.query.get(role_id)
        if role:
            if role_id == 1:  # 如果 role_id 为 1，则返回所有菜单
                all_menus = Menu.query.all()
                menulist = []
                for menu in all_menus:
                    menu_data = {
                        'id': menu.id,
                        'title': menu.menu_name,
                        'icon': menu.icon,
                        'path': menu.menu_path,
                        'menu_type': menu.menu_type,
                        'parentid': menu.parentId,
                        'parentname': menu.parentName,
                        'permiss': menu.permiss,
                        'route_component': menu.route_component,
                        'create_time': menu.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    menulist.append(menu_data)
                return {
                    'msg': 'ok',
                    'menus': menulist,
                }
            else:
                userlist = []
                for user in role.users:
                    user_data = {
                        'username': user.username,
                        'id': user.id
                    }
                    userlist.append(user_data)
                menulist = []
                for menu in role.menus:
                    menu_data = {
                        'id': menu.id,
                        'title': menu.menu_name,
                        'icon': menu.icon,
                        'path': menu.menu_path,
                        'menu_type': menu.menu_type,
                        'parentid': menu.parentId,
                        'parentname': menu.parentName,
                        'permiss': menu.permiss,
                        'route_component': menu.route_component,
                        'create_time': menu.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    menulist.append(menu_data)
                return {
                    'msg': 'ok',
                    'id': role.id,
                    'role_name': role.role_name,
                    'users': userlist,
                    'menus': menulist,
                }
        else:
            return {'msg': '角色没有找到'}, 404

    @jwt_required()
    def delete(self, role_id):
        role = Role.query.get(role_id)
        if not role:
            return {'msg': '角色没有找到', 'code': '404'}, 404
        db.session.delete(role)
        db.session.commit()
        return {'msg': '角色已删除', 'code': '204'}, 204


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
        self.attachment_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../attachment')

    @jwt_required()
    def post(self):
        # restful创建传入标准
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, location='form')
        parser.add_argument('description', type=str, location='form')
        parser.add_argument('environment_id', type=int, required=True, location='form')
        parser.add_argument('assignee_id', type=int, required=True, location='form')
        parser.add_argument('attachment', type=FileStorage, location='files', required=False, action='append')
        args = parser.parse_args()
        user_identity = get_jwt_identity()
        user_id = user_identity['id']
        attachment_files = request.files.getlist('attachment')
        attachment_urls = []
        if attachment_files:
            if not os.path.exists(self.attachment_folder):
                os.makedirs(self.attachment_folder)

            for attachment_file in attachment_files:
                original_filename = attachment_file.filename
                filename, file_extension = os.path.splitext(original_filename)  # 提取文件名和扩展名
                print('file_extension', file_extension)
                unique_filename = str(uuid.uuid4()) + file_extension  # 添加扩展名
                print('扩展名', filename, file_extension, unique_filename)
                attachment_path = os.path.join(self.attachment_folder, unique_filename)
                attachment_file.save(attachment_path)
                attachment_url_path = request.host_url + 'attachment/' + unique_filename  # 生成附件访问链接
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


# 工单附件访问
class AttachmentResource(Resource):

    def __init__(self):
        self.attachment_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../attachment')
        if not os.path.exists(self.attachment_folder):
            os.makedirs(self.attachment_folder)

    def get(self, filename):
        attachment_path = os.path.join(self.attachment_folder)
        print(attachment_path)
        return send_from_directory(attachment_path, filename)


# 用户图片信息上传和查询 这些图片的路径不进入数据库

class myupload(Resource):
    @jwt_required()
    def __init__(self):
        self.upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../upload')
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    def post(self,user_id):
        if 'file' not in request.files:
            return 'No file part in the request', 400

        image = request.files['file']

        if image.filename == '':
            return 'No selected file', 400

        if image:
            filename = str(uuid.uuid4()) + '.' + image.filename.rsplit('.', 1)[1].lower()
            print(111, filename)
            image.save(os.path.join(self.upload_folder, filename))
            try:
                User.query.filter_by(id=user_id).update({"userPic": filename})
                db.session.commit()
                return {'image': filename, 'msg': 'iamge上传完成', "code": 200}
            except Exception as e:
                print(e)
                db.session.rollback()  # 数据库回滚
                return jsonify(code=400, msg="上传失败")


# 浏览个人图片
class myview(Resource):
    def __init__(self):
        self.upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../upload')
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    def get(self, filename):
        upload_path = os.path.join(self.upload_folder)
        print(222, upload_path)
        return send_from_directory(upload_path, filename)


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
                'attachment_url': ticket.attachment_url,
                'ticket_status': ticket.status,
            }
        else:
            return {'msg': '工单没有找到'}, 404

    @jwt_required()
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, location='form')
        parser.add_argument('description', type=str, location='form')
        parser.add_argument('status', type=str, location='form')
        parser.add_argument('environment_id', type=int, required=True, location='form')
        parser.add_argument('assignee_id', type=int, required=True, location='form')
        # parser.add_argument('attachment', type=FileStorage, location='files', required=False)
        ticket = Ticket.query.get
        if not ticket:
            return {'msg': '工单没有找到'}, 404
        user_identity = get_jwt_identity()
        user_id = user_identity['id']
        args = parser.parse_args()
        ticket.title = args['title']
        ticket.description = args['description']
        # ticket.status = args['status']
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
            'environment': ticket.environment.id,
            'assignee': ticket.assignee.id,
            'user_id': user_id,
            'status': ticket.status
        }

    @jwt_required()
    def delete(self):
        ticket = Ticket.query.get
        if not ticket:
            return {'msg': '工单没有找到'}, 404
        db.session.delete(ticket)
        db.session.commit()
        return {'msg': '已删除'}, 204


# 查询所有用户


class all_users(Resource):
    @jwt_required()
    def get(self):
        users = User.query.all()
        user_list = []
        for user in users:  # 这里直接遍历 users，而不是 users.items
            user_info = {
                'id': user.id,
                'username': user.username,
                'department': user.department,
                'status': user.status,
                'role_name': user.role.role_name if hasattr(user, 'role') else None,  # 添加对 user.role 的检查
                'userPic': user.userPic if user.userPic else None,
                'create_time': user.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            user_list.append(user_info)
            # 对 user_list 进行降序排序，根据 create_time
            sorted_users = sorted(user_list, key=lambda x: x['create_time'], reverse=True)
            # print(sorted_users)
        return {'code': 200, 'msg': 'ok', 'data': sorted_users}


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
                'comments': [],
            }
            for feedback in ticket.feedbacks:
                comment_info = {
                    'comment_id': feedback.id,
                    'comment': feedback.comment,
                    'create_time': feedback.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    # 'attachment_url': feedback.attachment_url
                }
                ticket_info['comments'].append(comment_info)
            ticket_list.append(ticket_info)

        return {'code': 200, 'msg': 'ok', 'count': total_count, 'page': page, "per_page": per_page, 'data': ticket_list}


# 新增反馈信息
class ticket_processing_feedbacks(Resource):
    def __init__(self):
        self.attachment_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../attachment')

    @jwt_required()
    def post(self):
        # restful创建传入标准
        parser = reqparse.RequestParser()
        parser.add_argument('comment', type=str, required=True, location='form')
        parser.add_argument('ticket_id', type=int, required=True, location='form')
        parser.add_argument('ticket_status', type=str, required=True, location='form')
        # parser.add_argument('attachment', type=FileStorage, location='files', required=False, action='append')
        args = parser.parse_args()
        # user_identity = get_jwt_identity()
        # user_id = user_identity['id']
        try:
            feedback = Feedback(comment=args['comment'], ticket_id=args['ticket_id'])
            db.session.add(feedback)
            db.session.commit()
            # 通过feedback的ticket_id找到对应的Ticket对象并更新其status字段
            ticket = Ticket.query.get
            if ticket:
                ticket.status = args['ticket_status']
                db.session.commit()
                return {
                           'feedback_id': feedback.id,
                           'ticket_id': ticket.id,
                           'status': ticket.status,
                           'comment': feedback.comment
                       }, 201
            else:
                return jsonify(code=404, msg="未找到对应的工单"), 404
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="工单回复失败")


class all_feedbacks(Resource):
    pass
