
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename

app = Flask(__name__)
api = Api(app)

# 定义工单资源
class OrderResource(Resource):
    def post(self):
        # 获取JSON数据
        json_data = request.form.to_dict()
        #json_data = request.get_json()
        #json_data = request.get_data()
        title = json_data.get('title')
        description = json_data.get('description')
        print(title, description)
        # 获取上传的附件文件
        attachment_file = request.files.get('attachment')

        # 处理附件文件，例如保存到服务器
        if attachment_file:
            filename = secure_filename(attachment_file.filename)
            attachment_file.save('C:\\Users\\Administrator\\PycharmProjects\\pythonProject3\\restful-gogndan\\app\\attachment\\' + filename)
            # 设置附件URL，可以根据实际情况存储完整的URL或相对路径
            attachment_url = f'C:\\Users\\Administrator\\PycharmProjects\\pythonProject3\\restful-gogndan\\app\\attachment\\{filename}'
        else:
            attachment_url = None

        # 处理JSON数据和其他操作，例如将数据存入数据库

        return {'message': 'Order created successfully',
                'title': title,
                'description': description,
                'filename': filename,
                'succuer': 'ok'}, 201

# 添加资源到API
api.add_resource(OrderResource, '/create_order')

if __name__ == '__main__':
    app.run()
