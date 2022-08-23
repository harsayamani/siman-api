from flask import jsonify

def data(data, success_message):
    body = {
        "err": False,
        "message": success_message,
        "data": data,
        "status_code": 200
    }
    resp = jsonify(body)
    resp.status_code = 200  
    return resp
