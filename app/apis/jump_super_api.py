
#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
import requests
from flask import jsonify, current_app
from flask_restful import Resource, fields, marshal_with, reqparse
from xmlrpc.client import ServerProxy


# class jump_supervisor_task(Resource):
#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('hosts', location='json')
#         args = parser.parse_args()
#         hosts_data = args['hosts']
#         print(hosts_data)
#         hosts_list = []
#         for host_info in hosts_data:
#             hosts_list.append({
#                 'id': host_info['id'],
#                 'hostname': host_info['hostname'],
#                 'ip': host_info['ip']
#             })
#         req = 'http://jms.bry666.cn' + '/api/v1/ops/command-executions/'
#         # 提取hosts列表中的所有id
#         #host_ids = [host."id") for host in hosts]
#         print(hosts_list)
#         # data = {
#         #     # 使用jsopa的id进行查询
#         #     "run_as": "b35f9355-212c-4bc4-b8f0-040f3b2ee869",
#         #     "command": 'sudo supervisorctl status',
#         #     # 动态获取资产的id知道名字做查询
#         #     # "hosts": ["763f7644-fca4-4b0f-9c8a-3661cc80a19c", "de6b99cd-e5e9-4af5-9b6a-0fd2832da212"]
#         #     "hosts": host_ids
#         #     # 其他命令执行的参数
#         # }
#         # # 使用 current_app 访问 Jenkins 服务器
#         # jumpserver_auth = current_app.extensions['jumpserver_auth'].auth
#         # jumpserver_headers = current_app.extensions['jumpserver_auth'].headers
#         # response = requests.post(req, auth=jumpserver_auth, data=data, headers=jumpserver_headers)
#         # # 4. 处理响应
#         # if response.status_code == 201:
#         #     result = response.json()
#         #     # print("Command result:", result)
#         #     print("Command execution ID:", result["id"])
#         #     return result["id"]
#         # else:
#         #     print("Command execution failed. Status code:", response.status_code)
#         #     print("Error message:", response.text)
#
#     def command_result(self, jump_id):
#         # JumpServer API URL
#
#         req = 'http://jms.bry666.cn' + '/api/v1/ops/command-executions/' + jump_id + '/'
#         print(req)
#         response = requests.get(req, auth=self.auth, headers=self.headers)
#         # 处理响应
#         if response.status_code == 200:
#             result = response.json()
#             # 处理 result 数据，根据实际需求进行操作
#             print("Command result:", result)
#         else:
#             print("Failed to fetch command result. Status code:", response.status_code)
#             print("Error message:", response.text)

# 或者jump资产
# class jump_assets(Resource):
#     def get(self, hostname):
#         # JumpServer API URL
#         req = 'http://192.168.0.245:8080' + '/api/v1/assets/assets/?search=' + hostname
#         # 使用 current_app 访问 Jenkins 服务器
#         jumpserver_auth = current_app.extensions['jumpserver_auth'].auth
#         jumpserver_headers = current_app.extensions['jumpserver_auth'].headers
#         # 发送 API 请求
#         response = requests.get(req, auth=jumpserver_auth, headers=jumpserver_headers)
#         # 处理响应
#         if response.status_code == 200:
#             assets = response.json()
#             # print(type(assets))
#             asset_list = []
#             for asset in assets:
#                 asset_info = {'id': asset.get('id'), "hostname": asset.get('hostname'), "ip": asset.get('ip')}
#                 # print(asset)
#                 asset_list.append(asset_info)
#             return {'code': 200, 'msg': 'ok', 'data': asset_list}
#         else:
#             return {'msg': '访问失败'}


# 传入hosts字典，各host上业务信息
class service_status(Resource):
    def post(self, hostname):
        # JumpServer API URL
        req = 'http://192.168.0.245:8080' + '/api/v1/assets/assets/?search=' + hostname
        # 使用 current_app 访问 Jenkins 服务器
        jumpserver_auth = current_app.extensions['jumpserver_auth'].auth
        jumpserver_headers = current_app.extensions['jumpserver_auth'].headers
        # 发送 API 请求
        response = requests.get(req, auth=jumpserver_auth, headers=jumpserver_headers)
        # 处理响应
        if response.status_code == 200:
            assets = response.json()
            # print(type(assets))
            asset_list = []
            for asset in assets:
                asset_info = {'id': asset.get('id'), "hostname": asset.get('hostname'), "ip": asset.get('ip')}
                # print(asset)
                asset_list.append(asset_info)
        # parser = reqparse.RequestParser()
        # parser.add_argument('hosts', type=str, location='json')
        # args = parser.parse_args()
        # hosts_str = args['hosts']
        # # 传入字段解析成列表
        # hosts_data = ast.literal_eval(hosts_str)
        hosts_list = []
        for host in asset_list:
            super_server = ServerProxy("http://user:123@" + host['ip'] + ":9001/RPC2")
            service_status = super_server.supervisor.getAllProcessInfo()
            # print(service_status)
            sp_status_info = host['hostname'].split('_')[0]
            # print('hostname', sp_status_info)
            for status_info in service_status:
                if sp_status_info in status_info['name']:
                    # print('对比', sp_status_info, status_info['name'])
                    hosts_list.append({
                        'hostname': host['hostname'],
                        'ip': host['ip'],
                        'description': status_info['description'],
                        'state': status_info['statename'],
                        'program': status_info['name']
                    })
        return {'code': 200, 'msg': 'ok', 'data': hosts_list}



# node重启
class node_restart(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ip', type=str, location='json')
        parser.add_argument('program', type=str, location='json')
        args = parser.parse_args()
        program = args['program']
        ip = args['ip']
        super_server = ServerProxy("http://user:123@" + ip + ":9001/RPC2")
        node_list = super_server.supervisor.getProcessInfo(program)
        if node_list['statename'] != 'RUNNING':
            super_server.supervisor.startProcess(program)
            time.sleep(1)
            node_list = super_server.supervisor.getProcessInfo(program)
            if node_list['statename'] == 'RUNNING':
                return {'code': 200, 'msg': '完成重启操作'}
            else:
                return {'code': 200, 'msg': '重启操作失败'}
        else:
            super_server.supervisor.stopProcess(program)
            time.sleep(1)
            node_list = super_server.supervisor.getProcessInfo(program)
            if node_list['statename'] == 'STOPPED':
                super_server.supervisor.startProcess(program)
                time.sleep(1)
                node_list = super_server.supervisor.getProcessInfo(program)
                if node_list['statename'] == 'RUNNING':
                    return {'code': 200, 'msg': '完成重启操作'}
                else:
                    return {'code': 200, 'msg': '重启操作失败'}
            else:
                return {'code': 200, 'msg': '重启操作失败'}


# node 启动
class node_start(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ip', type=str, location='json')
        parser.add_argument('program', type=str, location='json')
        args = parser.parse_args()
        program = args['program']
        ip = args['ip']
        super_server = ServerProxy("http://"
                                   "user:123@" + ip + ":9001/RPC2")
        node_list = super_server.supervisor.getProcessInfo(program)
        if node_list['statename'] == 'RUNNING':
            return {'code': 200, 'msg': '程序已经启动'}
        else:
            super_server.supervisor.startProcess(program)
            time.sleep(1)
            node_list = super_server.supervisor.getProcessInfo(program)
            if node_list['statename'] == 'RUNNING':
                return {'code': 200, 'msg': '完成启动操作'}
            else:
                return {'code': 200, 'msg': '启动失败'}


# node 关闭
class node_stop(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('ip', type=str, location='json')
        parser.add_argument('program', type=str, location='json')
        args = parser.parse_args()
        program = args['program']
        ip = args['ip']
        super_server = ServerProxy("http://user:123@" + ip + ":9001/RPC2")
        node_list = super_server.supervisor.getProcessInfo(program)
        if node_list['statename'] == 'STOPPED':
            return {'code': 200, 'msg': '程序已经关闭'}
        else:
            super_server.supervisor.stopProcess(program)
            time.sleep(1)
            node_list = super_server.supervisor.getProcessInfo(program)
            if node_list['statename'] == 'STOPPED':
                return {'code': 200, 'msg': '完成关闭操作'}
            else:
                return {'code': 200, 'msg': '关闭失败'}



# 获取node节点 阿里云模块使用上用
class node_list(Resource):
    def get(self):
        # JumpServer API URL
        req = 'http://192.168.0.245:8080' + '/api/v1/assets/nodes/' + hostname
        # 使用 current_app 访问 Jenkins 服务器
        jumpserver_auth = current_app.extensions['jumpserver_auth'].auth
        jumpserver_headers = current_app.extensions['jumpserver_auth'].headers
        # 发送 API 请求
        response = requests.get(req, auth=jumpserver_auth, headers=jumpserver_headers)
        print(response)
        return response
