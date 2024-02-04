#!/usr/bin/python
# -*- coding: UTF-8 -*-
# pip install python-jenkins
import datetime
import subprocess
import time
import httpsig.requests_auth
import jenkins
import requests
from flask import jsonify, current_app
# from flask import Blueprint
from flask_jwt_extended import jwt_required
from flask_restful import Resource, fields, marshal_with, reqparse
from .models import *
from xmlrpc.client import ServerProxy
import ast


# 添加 job
class add_k8s_job(Resource):
    @jwt_required()
    def post(self):
        # restful创建传入标准
        parser = reqparse.RequestParser()
        parser.add_argument('job_name', type=str, required=True, location='form')
        parser.add_argument('test_ip', type=str, required=True, location='form')
        parser.add_argument('dev_ip', type=str, required=True, location='form')
        parser.add_argument('git_address', type=str, required=True, location='form')
        args = parser.parse_args()
        # 检查 job_name 是否已存在
        existing_job = K8s_job.query.filter_by(job_name=args['job_name']).first()
        if existing_job:
            return jsonify(code=400, msg="创建的 job 已经存在")
        try:
            k8s_job = K8s_job(job_name=args['job_name'], test_ip=args['test_ip'], dev_ip=args['dev_ip'], git_address=args['git_address'])
            db.session.add(k8s_job)
            db.session.commit()
            # 更新工单的附件名和链接字段
            return {
                       'msg': '创建job完成',
                       'id': k8s_job.id,
                       'job_name': k8s_job.job_name,
                       'build_id': k8s_job.job_build_ids,
                       'test_ip': k8s_job.test_ip,
                       'dev_ip': k8s_job.dev_ip,
                       'git_address': k8s_job.git_address,
                       'create_time': k8s_job.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                       'update_time': k8s_job.update_time.strftime('%Y-%m-%d %H:%M:%S')
                   }, 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="创建job失败")


# 查询,修改，删除单个job
k8sjob_fields = {
    'id': fields.Integer,
    'job_name': fields.String,
    'test_ip': fields.String,
    'dev_ip': fields.String,
    'git_address': fields.String,
    'create_time': fields.DateTime,
    'update_time': fields.DateTime,
    'job_build_ids': fields.List(fields.Nested({
        'job_build_id': fields.Integer,
    })),
}


class k8s_jobinfo(Resource):
    @jwt_required()
    @marshal_with(k8sjob_fields)
    def get(self, job_id):
        k8s_job = K8s_job.query.get(job_id)
        if k8s_job:
            return k8s_job
        else:
            return jsonify(code=404, msg="Job不存在")

    def put(self, job_id):
        parser = reqparse.RequestParser()
        parser.add_argument('job_name', type=str, location='form')
        parser.add_argument('test_ip', type=str, location='form')
        parser.add_argument('dev_ip', type=str, location='form')
        parser.add_argument('git_address', type=str, location='form')
        args = parser.parse_args()
        k8s_job = K8s_job.query.get(job_id)
        if not k8s_job:
            return {'msg': 'job没有找到'}, 404
        try:
            # print(args['job_name'], args['test_ip'], args['dev_ip'], args['git_address'])
            k8s_job.job_name = args['job_name']
            k8s_job.test_ip = args['test_ip']
            k8s_job.dev_ip = args['dev_ip']
            k8s_job.git_address = args['git_address']
            # User.query.filter_by(id=user_id).update({"username": args['username']}, {"department": args['department']}, {"role_id": args['role_id']}, {"password": args['password']})  # 根据user_id查询并更新username
            db.session.commit()
            return jsonify(code=200, job_name=args['job_name'], test_ip=args['test_ip'], dev_ip=args['dev_ip'], git_address=args['git_address'], msg="修改成功")
        except Exception as e:
            print(e)
            db.session.rollback()  # 数据库回滚
            return jsonify(code=400, msg="修改job信息失败")

    def delete(self, job_id):
        print(job_id)
        k8s_job = K8s_job.query.get(job_id)
        print(k8s_job)
        if not k8s_job:
            return {'msg': 'job没有找到', 'code': '404'}, 404
        db.session.delete(k8s_job)
        db.session.commit()
        return {'msg': 'job已删除', 'code': '204'}, 204


# 查询所有k8s_job
job_build_id_fields = {
    'k8s_job_id': fields.Integer,
    'job_build_id': fields.Integer,
    'create_time': fields.String,

}

k8s_job_fields = {
    'id': fields.Integer,
    'job_name': fields.String,
    'test_ip': fields.String,
    'dev_ip': fields.String,
    'git_address': fields.String,
    'job_path': fields.String,
    'create_time': fields.String,
    'job_build_ids': fields.List(fields.Nested(job_build_id_fields)),  # 将 fields.Integer 放在 fields.List 内
}
all_k8s_job_fields = {
    'code': fields.Integer,
    'msg': fields.String,
    # user对象的字段进行匹配 对一个显示
    # 'data': fields.Nested(user_fields)
    # 下面查询是all 显示全部则加个fields.List
    'data': fields.List(fields.Nested(k8s_job_fields))

}


class all_k8s_job(Resource):
    @jwt_required()
    @marshal_with(all_k8s_job_fields)
    def get(self):
        k8s_job = K8s_job.query.all()
        return {'code': 200,
                'msg': 'ok',
                'data': k8s_job
                }


# 获取构建版本号
k8s_build_number = {
    'k8s_job_id': fields.String,
    'job_path': fields.String,
    'create_time': fields.String,
    'job_build_ids': fields.List(fields.Nested(job_build_id_fields)),  # 将 fields.Integer 放在 fields.List 内
}
all_k8s_job_fields = {
    'code': fields.Integer,
    'msg': fields.String,
    # user对象的字段进行匹配 对一个显示
    # 'data': fields.Nested(user_fields)
    # 下面查询是all 显示全部则加个fields.List
    'data': fields.List(fields.Nested(k8s_job_fields))

}


class build_number(Resource):
    @jwt_required()
    @marshal_with(all_k8s_job_fields)
    def get(self):
        k8s_build_number = K8s_build_id.query.all()
        return {'code': 200,
                'msg': 'ok',
                'data': k8s_build_number
                }


# 远程分支
class remote_branches(Resource):
    @jwt_required()
    def get(self, job_id):
        # 获取git_address
        k8s_jobinfo = K8s_job.query.filter_by(id=job_id).first()
        if k8s_jobinfo:
            git_address = k8s_jobinfo.git_address
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--heads", git_address],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                # 解析结果，获取分支名
                brancheslist = [line.split()[-1].split("/")[-1] for line in result.stdout.splitlines()]
                print(brancheslist)
                # 转换成列表里包含字典
                branches = [{"BRANCH": branch} for branch in brancheslist]
                return {'code': 200, 'msg': 'ok', 'data': branches}
            else:
                print(f" 'git ls-remote执行失败': {result.stderr}")
                return []
        except Exception as e:
            print(f"git ls-remote执行失败': {e}")


# 构建项目
class build_job(Resource):
    @jwt_required()
    # def __init__(self):
    #     """
    #     jenkins_master ：master地址
    #     jenkins_job ：jenkins_job名字
    #     jenkins_user ：登陆账号
    #     jenkins_passwd ：登陆密码
    #     :rtype: object
    #     """
    #     self.jenkins_master = "http://192.168.0.152:8080"
    #     self.login_user = 'admin'
    #     self.login_passwd = 'bry@NJ12@x'
    #     jkServer = jenkins.Jenkins(self.jenkins_master, self.login_user, self.login_passwd)
    #     self.jenkins_server = jkServer

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('job_name', type=str, location='form')
        parser.add_argument('BRANCH', type=str, location='form')
        args = parser.parse_args()
        job_name = args['job_name']
        # 导入jenkins登录
        #  对比jenkins中有无平台中创建的项目名
        all_jobs = self.jenkins_server.get_all_jobs()

        # jenkins查找名字为 job_name 的项目
        matching_jobs = [job for job in all_jobs if job['name'] == job_name]

        # 如果找到了匹配的项目，执行相关操作
        if matching_jobs:
            token = datetime.now().strftime('%Y%m%d_%H%M%S%f')
            # print(job_name)

            # 组合传入的分支参数， 将字符串转换为字典
            parameters = {'BRANCH': args['BRANCH']}

            # 构建
            self.jenkins_server.build_job(job_name, parameters=parameters, token=token)
            return {'code': 200, 'msg': f'{job_name}项目已经提交构建请求：请等待...'}
        else:
            return {'code': 400, 'msg': f'Jenkins 中找不到项目：{job_name}'}


# 查询构建状态
class build_status(Resource):
    @jwt_required()
    def __init__(self):
        self.jenkins_master = "http://192.168.0.152:8080"
        self.login_user = 'admin'
        self.login_passwd = 'bry@NJ12@x'
        jkServer = jenkins.Jenkins(self.jenkins_master, self.login_user, self.login_passwd)
        self.jenkins_server = jkServer

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('job_name', type=str, location='form')
        parser.add_argument('BRANCH', type=str, location='form')
        args = parser.parse_args()
        job_name = args['job_name']
        #  对比jenkins中有无平台中创建的项目名
        all_jobs = self.jenkins_server.get_all_jobs()

        # jenkins查找名字为 job_name 的项目
        matching_jobs = [job for job in all_jobs if job['name'] == job_name]
        # 如果找到了匹配的项目，执行相关操作
        if matching_jobs:
            # 获取job名为job_name的job的最后次构建号,正在构建的应该也算
            time.sleep(5)
            jk_job_id = self.jenkins_server.get_job_info(job_name)['lastBuild']['number']
            '''
              role:判断job名为job_name的job的某次构建是否还在构建中
              True:正在构建
              Fase:构建结束
              '''
            build_status = self.jenkins_server.get_build_info(job_name, jk_job_id)['building']
            '''
               role:获取job名为job_name的job的某次构建的执行结果状态
               SUCCESS : job执行成功
               FAILURE ：job执行失败
               ABORTED ：人为结束构建
               None : 正在构建中
               '''
            build_result = self.jenkins_server.get_build_info(job_name, jk_job_id)['result']
            # 判定构建状态和是否进行构建中
            if build_status is False:
                print(f'构建结束,状态为：{build_result}')
                return {'job_name': job_name, 'branch': args['BRANCH'], 'msg': '构建结束', 'status': build_result}
            else:
                print(f'构建中,请等待!状态:{build_result}')
                return {'job_name': job_name, 'branch': args['BRANCH'], 'msg': '构建中，请等待！', 'status': build_result}
            print('等待超时，请检查jenkins配置')
            return {'msg': '等待超时，请检查jenkins配置'}
        else:
            return {'job_name': job_name, 'branch': args['BRANCH'], 'code': 400, 'msg': f'Jenkins 中找不到项目：{job_name}'}, 400


class save_build_id(Resource):
    @jwt_required()
    # def __init__(self):
    #     self.jenkins_master = "http://192.168.0.152:8080"
    #     self.login_user = 'admin'
    #     self.login_passwd = 'bry@NJ12@x'
    #     jkServer = jenkins.Jenkins(self.jenkins_master, self.login_user, self.login_passwd)
    #     self.jenkins_server = jkServer

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('job_name', type=str, location='form')
        args = parser.parse_args()
        job_name = args['job_name']
        # 使用 current_app 访问 Jenkins 服务器
        jenkins_server = current_app.extensions['jenkins'].jenkins_server
        #  对比jenkins中有无平台中创建的项目名
        all_jobs = jenkins_server.get_all_jobs()
        # all_jobs = self.jenkins_server.get_all_jobs()
        # jenkins查找名字为 job_name 的项目
        matching_jobs = [job for job in all_jobs if job['name'] == job_name]
        # 查询k8s_job表里job_name的id
        k8s_job = K8s_job.query.filter_by(job_name=job_name).first()
        # 如果找到了匹配的项目，执行相关操作
        if matching_jobs:
            jk_job_id = jenkins_server.get_job_info(job_name)['lastBuild']['number']

            try:
                k8s_build_id = K8s_build_id(k8s_job_id=k8s_job.id, job_build_id=jk_job_id)
                db.session.add(k8s_build_id)
                db.session.commit()
                # 更新工单的附件名和链接字段
                return {'code': 201,
                        'msg': '存入job_build信息完成',
                        'id': k8s_build_id.id,
                        'job_name': k8s_job.job_name,
                        'k8s_job_id': k8s_job.id,
                        'job_build_id': jk_job_id,
                        'create_time': k8s_job.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'update_time': k8s_job.update_time.strftime('%Y-%m-%d %H:%M:%S')
                        }, 201
            except Exception as e:
                print(e)
                db.session.rollback()
                return jsonify(code=400, msg="存入job_build信息失败")


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
        super_server = ServerProxy("http://user:123@" + ip + ":9001/RPC2")
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
