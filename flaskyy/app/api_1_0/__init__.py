from flask import Blueprint

api=Blueprint('api',__name__)

from Flasklearning.flaskyy.app.api_1_0 import posts,users,errors,decorators,comments,authentication