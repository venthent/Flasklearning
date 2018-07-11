from flask import jsonify,request
from . import api
from Flasklearning.flaskyy.app.exceptions import ValidationError


def bad_request(message):
    response=jsonify({'error':'bad requests','message':'message'})
    response.status_code=4040
    return response

def forbiden(message):
    response=jsonify({'error':'forbidden','message':message})
    response.status_code=403
    return response

def unauthorized(message):
    response=jsonify({'error':'unauthorized','message':message})
    response.status_code=401
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
