# urls.py 路由文件

from .exts import api
from .apis import *
# from .pushlist_api import *
# 路由
# 管理员
# api.add_resource(hello, '/api/hello/')
api.add_resource(admin_login, '/api/admin/login')
api.add_resource(admin_session_check, '/api//admin/session')
api.add_resource(admin_logout, '/api/admin/logout')
# 环境标签增删改查
api.add_resource(environment, '/api/environment')




# 用户注册
api.add_resource(user_register, '/api/user/register')
# 用户登录
api.add_resource(user_login, '/api/user/login')

# 新增用户
api.add_resource(add_user, '/api/add_user')

# 用户查询 删除
api.add_resource(userinfo, '/api/user/<int:user_id>')
# #用户修改状态
api.add_resource(userstatus, '/api/user/<int:user_id>/<int:user_status>')
# 用户登出
api.add_resource(user_logout, '/api/user/logout')

# 查询所有用户
api.add_resource(all_users, '/api/all/users')


# 角色查询
api.add_resource(all_roles, '/api/all/roles')


# 查询经办人
api.add_resource(all_assignee, '/api/all/assignees')
# 新增工单
api.add_resource(add_ticket, '/api/ticket')
# 工单删改查
api.add_resource(ticket, '/api/ticket/<int:ticket_id>')

# 查询所有环境标签
api.add_resource(all_environments, '/api/all/environments')
# 查询所有工单
api.add_resource(all_tickets, '/api/all/tickets')
# 查询登录用户订单
api.add_resource(user_tickets, '/api/user_tickets')
# 查询用户需要处理的工单
api.add_resource(ticket_processing, '/api/ticket_processing')

# 新增反馈信息
api.add_resource(ticket_processing_feedbacks, '/api/ticket_processing_feedbacks')

# 附件访问接口
api.add_resource(AttachmentResource, '/attachment/<string:filename>')
# 个人用户上传照片
api.add_resource(myupload, '/my/upload')
# 个人图片浏览
api.add_resource(myview, '/my/view/<string:filename>')








