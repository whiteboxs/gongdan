from functools import wraps
from flask import jsonify, session, g


# 装饰器


def admin_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 在这里执行登录检查逻辑,判断用户的登录状态
        admin_id = session.get("admin_id")
        #print(user_id)
        if admin_id is not None:
            # 将user_id保存到g对象中 在apis中可以通过g对象获取保存数据
            g.user_id = admin_id
            result = func(*args, **kwargs)
            return result
        else:
            return jsonify(code=400, msg="用户未登录")

    return wrapper


def user_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 在这里执行登录检查逻辑,判断用户的登录状态
        user_id = session.get("user_id")
        #print(user_id)
        if user_id is not None:
            # 将user_id保存到g对象中 在apis中可以通过g对象获取保存数据
            g.user_id = user_id
            result = func(*args, **kwargs)
            return result
        else:
            return jsonify(code=400, msg="用户未登录")

    return wrapper
