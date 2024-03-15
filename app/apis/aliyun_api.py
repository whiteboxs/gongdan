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
from ..models import *