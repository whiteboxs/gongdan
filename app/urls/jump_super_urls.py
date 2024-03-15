from ..exts import api
from ..apis.jump_super_api import *

# jumpserver查询
# api.add_resource(jump_assets, '/api/jump_allassets/<hostname>')
# api.add_resource(jump_supervisor_task, '/api/jump_command/')
api.add_resource(node_list, '/api/jump_node_list')
# supervisor_api接口
api.add_resource(service_status, '/api/service_status/<hostname>')
api.add_resource(node_restart, '/api/node_restart')
api.add_resource(node_start, '/api/node_start')
api.add_resource(node_stop, '/api/node_stop')

