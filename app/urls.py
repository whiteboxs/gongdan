# urls.py 路由文件

from .exts import api
from .apis import *

# 路由
# 管理员
api.add_resource(hello, '/hello/')
api.add_resource(admin_login, '/admin/login/')
api.add_resource(admin_session_check, '/admin/session/')
api.add_resource(admin_logout, '/admin/logout/')
# 环境标签增删改查
api.add_resource(environment, '/environment/')


# 工单删改查
api.add_resource(ticket, '/ticket/<int:ticket_id>')
# 工单增
api.add_resource(add_ticket, '/ticket/')
# 用户注册
api.add_resource(user_register, '/user/register/')
# 用户登录
api.add_resource(user_login, '/user/login/')
# 用户状态
api.add_resource(user_session_check, '/user/session/')
# 用户登出
api.add_resource(user_logout, '/user/logout/')

# 查询所有用户
api.add_resource(all_users, '/all/users')
# 查询所有环境标签
api.add_resource(all_environments, '/all/environments/')
# 查询所有工单
api.add_resource(all_tickets, '/all/tickets/')


# 新增反馈表
api.add_resource(add_feedback, '/feedback/')
# 查询所有反馈
api.add_resource(all_feedbacks, '/all/feedbacks/')



