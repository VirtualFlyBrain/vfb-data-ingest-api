import logging

from flask_restplus import Resource, reqparse
from vfb_curation_api.api.vfbid.serializers import project
from vfb_curation_api.api.vfbid.business import valid_user
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db


log = logging.getLogger(__name__)

ns = api.namespace('projects', description='Operations related to lists of projects')


@ns.route('/')
@api.response(404, 'No projects found.')
@api.param('apikey','Your API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
class ProjectList(Resource):

    @api.marshal_with(project)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        if valid_user(apikey, orcid):
            m = db.get_all_projects(orcid)
            return m
        return "{ error: 'Invalid API Key' }"
