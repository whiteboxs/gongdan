# 模型 和数据库有关系
from .exts import db
from datetime import datetime


# from wtforms.validators import DataRequired

# 删除重建数据库
# DROP DATABASE restful;
# CREATE DATABASE restful CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
# 进入项目根目录
# flask db init  第一次表单写好后执行，就执行一次
# flask db migrate 生产迁移文件
# flask db upgrade 执行迁移文件中的升级
# flask db downgrade 执行迁移文件中的降级=撤回命令


# 管理员表
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)  # id号(独一无二的)
    username = db.Column(db.String(64), nullable=False, unique=True)  # 账号用户名
    password = db.Column(db.String(64), nullable=False)  # 密码
    # 枚举 只能存的是枚举里面设置的内容 不是设置的规定的内容的话 是会报错的
    power = db.Column(db.Enum("超级管理员", "普通管理员"), nullable=False, default="普通管理员")  # 管理员权限
    status = db.Column(db.Boolean, nullable=False, default=True)  # 真假代表正常异常状态
    # index 设置的是什么 设置的是索引 索引就是帮助你更快地找到对应的数据
    create_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间
    # onupdate 自动更新 每一次 增删查改这个表都会 自动更新一下时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 最近一次登录时间
    # 认领 关联
    # tags = db.relationship("Tag", backref="admin")  # 1对多对应外键 在在tags.admin.username用户名


# 标签
class Environment(db.Model):
    # 表名
    __tablename__ = "environment"
    id = db.Column(db.Integer, primary_key=True)  # 主键没有提升要硬输入
    name = db.Column(db.String(32), nullable=False, unique=True)  # 用户名 nullable 是否可以为空
    create_time = db.Column(db.DateTime, index=True, default=datetime.now)
    # user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # 外键 放在多的类里 多对一
    # admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))
    # 多对一
    tickets = db.relationship('Ticket', backref='environment')


# 用户表
class User(db.Model):
    # 表名
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键没有提升要硬输入
    department = db.Column(db.String(16), nullable=False)
    username = db.Column(db.String(32), nullable=False, unique=True)  # 用户名 nullable 是否可以为空,unique=True保证字段唯一
    password = db.Column(db.String(64), nullable=False)  # 密码 nullable 是否可以为空
    status = db.Column(db.Boolean, nullable=False, default=True)  # 真假代表正常异常状态
    create_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # 多对一
    tickets = db.relationship('Ticket', backref='user')
    feedbacks = db.relationship('Feedback', backref='user')
    # tags = db.relationship('Tag', backref='user')


# 经办人表
class Assignee(db.Model):
    __tablename__ = "assignee"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), nullable=False, unique=True)
    create_time = db.Column(db.DateTime, index=True, default=datetime.now)
    # 多对一，一个经办人有多个工单，外建放在了工单表里
    tickets = db.relationship('Ticket', backref='assignee')


class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum("待审核", "未完成", "已完成"), nullable=False, default="待审核")
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    attachment_url = db.Column(db.String(255))
    # 1对多
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    environment_id = db.Column(db.Integer, db.ForeignKey('environment.id'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('assignee.id'))
    # 多对一
    feedbacks = db.relationship('Feedback', backref='ticket')

    # 多对多
    # tags = db.relationship("Tag", secondary="ticket_to_tag", backref="ticket")


# # 定义表单类
# class OrderForm(FlaskForm):
#     title = StringField('title', validators=[DataRequired()])
#     description = StringField('description', validators=[DataRequired()])
#     attachment = FileField('attachment')


class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    attachment_url = db.Column(db.String(255))
    # 一对多
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('assignee.id'))


# 中间表
# class TickettoFeedback(db.Model):
#     # 表名
#     __tablename__ = "ticket_to_feedback"
#     id = db.Column(db.Integer, primary_key=True)  # 主键没有提升要硬输入
#     ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"))  # 多对多的关系表，加入要关系的2个外键id
#     tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"))  # 多对多的关系表，加入要关系的2个外键id


#  搜索表
class SearchHistory(db.Model):
    __tablename__ = "search_history"
    id = db.Column(db.Integer, primary_key=True)  # id号(独一无二的)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
    keyword = db.Column(db.String(64), nullable=False)  # 关键字搜索
    # index 设置的是什么 设置的是索引 索引就是帮助你更快地找到对应的数据
    create_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间

# # 评论表
# class Comment(db.Model):
#     __tablename__ = "comment"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id号(独一无二的)
#     sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户评论者
#     blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))  # 所属博客
#     content = db.Column(db.Text, nullable=False)  # 内容 Text存很多数据
#     status = db.Column(db.Boolean, nullable=False, default=True)  # 真假代表展示、不展示状态
#     # index 设置的是什么 设置的是索引 索引就是帮助你更快地找到对应的数据
#     create_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间
#
#
# #  反馈表
# class Message(db.Model):
#     __tablename__ = "message"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id号(独一无二的)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户发送者
#     admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 指派人
#     content = db.Column(db.Text, nullable=False)  # 内容 Text存很多数据
#     status = db.Column(db.Boolean, nullable=False, default=True)  # 真假代表展示、不展示状态
#     # index 设置的是什么 设置的是索引 索引就是帮助你更快地找到对应的数据
#     create_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间
#
# # 工单表
# class Workorder(db.Model):
#     # 表名
#     __tablename__ = "workorder"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键没有提升要硬输入
#     title = db.Column(db.String(64), nullable=False)  # 标题
#     summary = db.Column(db.String(64), nullable=False)  # 简介
#     content = db.Column(db.Text, nullable=False)  # 详细内容
#     create_time = db.Column(db.DateTime, index=True, default=datetime.now)  # 创建时间
#     user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # 外键
#     tags = db.relationship("Tag", secondary="order_to_tag", backref="order")  # 多对多关链  tags对应tag类 secondary写关系表
#     status = db.Column(db.Enum("待审核", "未完成", "已完成"), nullable=False, default="待审核")
#     # 关联
#
#     # backref写之前之前的对多以的另外一个关系表里的orderid
#
#
# # 中间表
# class OrdertoTag(db.Model):
#     # 表名
#     __tablename__ = "order_to_tag"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键没有提升要硬输入
#     order_id = db.Column(db.Integer, db.ForeignKey("order.id"))  # 多对多的关系表，加入要关系的2个外键id
#     tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"))  # 多对多的关系表，加入要关系的2个外键id
#
#
