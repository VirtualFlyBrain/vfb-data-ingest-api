import logging

from flask_restplus import Resource, reqparse
from vfb_curation_api.api.vfbid.serializers import user
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db


log = logging.getLogger(__name__)

ns = api.namespace('login', description='Authentication')


@ns.route('/')
@api.response(404, 'User could not be authenticated.')
@api.param('code','Your ORCID authorisation code')
class Login(Resource):
    @api.marshal_with(user)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code', type=str, required=True)
        args = parser.parse_args()
        return db.get_api_token(args['code'])

