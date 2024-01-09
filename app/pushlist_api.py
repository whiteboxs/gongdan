#!/usr/bin/python
# -*- coding: UTF-8 -*-
# pip install python-jenkins
import datetime
from .exts import jenkins_init

from flask import jsonify, request, session, send_from_directory
from flask_restful import Resource, fields, marshal_with, reqparse
from werkzeug.utils import secure_filename
import os
from .models import *
# from flask import Blueprint
from .utils.tools import user_login_required, admin_login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from sqlalchemy import or_, and_
from werkzeug.datastructures import FileStorage
import uuid


# jk = jenkins_init(jenkins_job)

# 添加 job
class add_k8s_job(Resource):
    @jwt_required()
    def post(self):
        # restful创建传入标准
        parser = reqparse.RequestParser()
        parser.add_argument('job_name', type=str, required=True, location='form')
        args = parser.parse_args()
        try:
            k8s_job = K8s_job(job_name=args['job_name'])
            db.session.add(k8s_job)
            db.session.commit()
            # 更新工单的附件名和链接字段
            return {
                       'msg': '创建job完成',
                       'job_id': k8s_job.id,
                       'job_name': k8s_job.job_name,
                       'build_id': k8s_job.job_build_ids,
                       'create_time': k8s_job.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                       'update_time': k8s_job.update_time.strftime('%Y-%m-%d %H:%M:%S')
                   }, 201
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify(code=400, msg="创建job失败")


# 查询所有k8s_job
job_build_id_fields = {
    'k8s_job_id': fields.Integer,
    'job_build_id': fields.Integer,

}

k8s_job_fields = {
    'id': fields.Integer,
    'job_name': fields.String,
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





# 构建项目
class build_job(Resource):
    @jwt_required()
    def post(self, job_name, parameters=None):
        token = datetime.datetime.now().strftime('%Y%m%d_%H%M%S%f')
        # 获取分支
        k8s_job = K8s_job.query.all()
        print(k8s_job.path)

        parameters = {"BRANCH": "develop-k8s"}
        print(parameters)
        if parameters:  # ##带参数构建触发，参数必须是字典类型
            return self.jenkins_server.build_job(job_name, parameters=parameters, token=token)
        return self.jenkins_server.build_job(job_name, token=token)  ## 无参数构建触发



class jenkins_init(object):



    def getLastJobId(self):
        '''
        role : 获取job名为job_name的job的最后次构建号
        '''
        return self.jenkins_server.get_job_info(self.jenkins_job)['lastBuild']['number']

    def getJobResultStatus(self, jobId):
        '''
        role:获取job名为job_name的job的某次构建的执行结果状态
        SUCCESS : job执行成功
        FAILURE ：job执行失败
        ABORTED ：人为结束构建
        None : 正在构建中
        '''
        return self.jenkins_server.get_build_info(self.jenkins_job, jobId)['result']

    def getJobBuilding(self, jobId):
        '''
        role:判断job名为job_name的job的某次构建是否还在构建中
        True:正在构建
        Fase:构建结束
        '''
        return self.jenkins_server.get_build_info(self.jenkins_job, jobId)['building']

    def getJobinfo(self, jobId):
        '''
        获取控制台的日志
        '''
        # print(self.jenkins_server.get_build_info(self.jenkins_job, jobId)['url'])
        return self.jenkins_server.get_build_console_output(self.jenkins_job, jobId)

    # data = {"params.BRANCH": "develop-k8s"}

    # jk.build_job(data)
    # # time.sleep(20)  # api出发怕jenkin没来得及响应
    #
    # jobid = jk.getLastJobId()
    #
    # print("job id", jobid)
    # print("console-log-info", jk.getJobinfo(jobid))
    # print("job result status", jk.getJobResultStatus(jobid))
    # print("job building result", jk.getJobBuilding(jobid))
    # print('---------------')
