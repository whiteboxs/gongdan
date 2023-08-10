# urls.py 路由文件

from .exts import api
from .apis import *

# 路由
# 管理员
# api.add_resource(hello, '/api/hello/')
api.add_resource(admin_login, '/api/admin/login')
api.add_resource(admin_session_check, '/api//admin/session')
api.add_resource(admin_logout, '/api/admin/logout')
# 环境标签增删改查
api.add_resource(environment, '/api/environment')


# 工单删改查
api.add_resource(ticket, '/api/ticket/<int:ticket_id>')
# 工单增加
api.add_resource(add_ticket, '/api/ticket')
# 用户注册
api.add_resource(user_register, '/api/user/register')
# 用户登录
api.add_resource(user_login, '/api/user/login')
# 用户状态
api.add_resource(user_session_check, '/api//user/session')
# 用户登出
api.add_resource(user_logout, '/api/user/logout')

# 查询所有用户
api.add_resource(all_users, '/api/all/users')
# 查询经办人
api.add_resource(all_assignee, '/api/all/assignees')

# 查询所有环境标签
api.add_resource(all_environments, '/api/all/environments')
# 查询所有工单
api.add_resource(all_tickets, '/api/all/tickets')


# 新增反馈表
api.add_resource(add_feedback, '/api/feedback')
# 查询所有反馈
api.add_resource(all_feedbacks, '/api/all/feedbacks')


