from flask import jsonify

def bad_request(error_message):
    body = {
        'err': True,
        'message': error_message,
        'status_code': 400
    }
    resp = jsonify(body)
    resp.status_code = 400
    return resp

def unauthorized(error_message):
    body = {
        'err': True,
        'message': error_message,
        'status_code': 401
    }
    resp = jsonify(body)
    resp.status_code = 401
    return resp

def not_found(error_message):
    body = {
        'err': True,
        'message': error_message,
        'status_code': 404
    }
    resp = jsonify(body)
    resp.status_code = 404
    return resp

def conflict(error_message):
    body = {
        'err': True,
        'message': error_message,
        'status_code': 409
    }
    resp = jsonify(body)
    resp.status_code = 409
    return resp

def internal_server(error_message):
    body = {
        'err': True,
        'message': error_message,
        'status_code': 500
    }
    resp = jsonify(body)
    resp.status_code = 500
    return resp
    
    