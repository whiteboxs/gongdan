import requests
data = {
    'title': '工单标题',
    'description': '工单描述',
}
data2 = {"title": "测试环境上线", "environment": "测试环境", "description": "现在点上线"}
data3 = {"environment": "灰度环境2"}
files = {'attachment': open(r'C:\Users\Administrator\Desktop\行驶证.png', 'rb')}
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY5MDM1MDYxNiwianRpIjoiM2U3MTM2NzYtNTk4Yi00MGY5LTljMDAtOWE0YzQ5N2M2OTEyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Inh1eGlhbmciLCJuYmYiOjE2OTAzNTA2MTYsImV4cCI6MTY5MDM1NDIxNn0.F8SaMxm8jYE6Qq4AypsqaLJms82PAWlI_hv6rMIVzCU'
headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
# 使用requests发送带有JSON数据和附件的POST请求
#response = requests.post('http://127.0.0.1:5000/create_order', data=data, files=files)


#response = requests.post('http://127.0.0.1:9002/ticket/', data=data2, files=files)
response = requests.post('http://127.0.0.1:9002/environment/', headers=headers, json=data3)
print(response.status_code)
print(response.json())