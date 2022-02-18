import logging

from flask_restplus import Resource, reqparse
from vfb_curation_api.api.vfbid.serializers import user
from vfb_curation_api.api.vfbid.business import valid_user
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db
from vfb_curation_api.database.models import Role

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


@ns.route('/admin/', doc=False)
@api.param('admin_apikey', 'Admin API Key', required=True)
@api.param('admin_orcid', 'Admin ORCID', required=True)
@api.param('user_orcid', 'User ORCID to query', required=True)
class UserAdmin(Resource):

    @api.marshal_with(user)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('admin_apikey', type=str, required=True)
        parser.add_argument('admin_orcid', type=str, required=True)
        parser.add_argument('user_orcid', type=str, required=True)
        args = parser.parse_args()
        admin_apikey = args['admin_apikey']
        admin_orcid = args['admin_orcid']
        user_orcid = args['user_orcid']
        if valid_user(admin_apikey, admin_orcid):
            if db.get_user(admin_orcid).role == Role.admin.name:
                return db.get_user(user_orcid)
            else:
                return "{ error: 'Not authorized Admin request' }"
        return "{ error: 'Invalid API Key' }"
