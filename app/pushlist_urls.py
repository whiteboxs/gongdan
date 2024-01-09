# urls.py 路由文件

from .exts import api
from .pushlist_api import *

# jenkins
# 创建k8s_job
api.add_resource(add_k8s_job, '/api/add_k8s_job')
# 查询all-k8s_job
api.add_resource(all_k8s_job, '/api/all/k8s_job')
# 查询job的构建数信息
api.add_resource(build_number, '/api/build_number')
