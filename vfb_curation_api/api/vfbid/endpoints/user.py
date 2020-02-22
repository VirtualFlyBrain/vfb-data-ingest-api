import logging

from flask_restplus import Resource, reqparse
from vfb_curation_api.api.vfbid.serializers import user
from vfb_curation_api.api.vfbid.business import valid_user
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db

log = logging.getLogger(__name__)

ns = api.namespace('user', description='Operations related to user')


@ns.route('/')
@api.param('apikey','Your API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
class UserResource(Resource):
    # @api.response(201, 'User successfully created.')
    # @api.expect(user)
    # @api.marshal_with(user)
    # def post(self):
    #     return "{ error: 'Not supported'}", 201

    @api.marshal_with(user)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        if valid_user(apikey, orcid):
            return db.get_user(orcid)
        return "{ error: 'Invalid API Key' }"