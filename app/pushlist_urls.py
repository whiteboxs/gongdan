# urls.py 路由文件

from .exts import api
from .pushlist_api import *

# jenkins
# 创建k8s_job
api.add_resource(add_k8s_job, '/api/add_k8s_job')
# 查询，修改 删除 单个job
api.add_resource(k8s_jobinfo, '/api/k8s_jobinfo/<int:job_id>')

# 查询all-k8s_job
api.add_resource(all_k8s_job, '/api/all/k8s_job')

# 获取分支信息
api.add_resource(remote_branches, '/api/remote_branches/<int:job_id>')
# 构建
api.add_resource(build_job, '/api/build')
# 查询构建状态
api.add_resource(build_status, '/api/build_status')
# 查询job的构建数信息
# api.add_resource(build_number, '/api/build_number')
# 存入jobbuild_id信息
api.add_resource(save_build_id, '/api/save_build_id')

# jumpserver查询
# api.add_resource(jump_assets, '/api/jump_allassets/<hostname>')
# api.add_resource(jump_supervisor_task, '/api/jump_command/')

# supervisor_api接口
api.add_resource(service_status, '/api/service_status/<hostname>')
api.add_resource(node_restart, '/api/node_restart')
api.add_resource(node_start, '/api/node_start')
api.add_resource(node_stop, '/api/node_stop')
