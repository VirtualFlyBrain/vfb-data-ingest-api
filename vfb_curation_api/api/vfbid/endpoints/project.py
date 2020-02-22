import logging

from flask import request
from flask_restplus import Resource, reqparse
from vfb_curation_api.api.vfbid.business import create_project, valid_user
from vfb_curation_api.api.vfbid.serializers import project
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db

log = logging.getLogger(__name__)

ns = api.namespace('project', description='Operations related to neurons')

@ns.route('/')
@api.param('apikey','Your API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
@api.param('projectid', 'The four letter ID of the project', required=True)
class ProjectResource(Resource):
    @api.response(201, 'Project successfully created.')
    @api.expect(project)
    @api.marshal_with(project)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('projectid', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        pid = create_project(request.json)
        return db.get_project(pid), 201

    @api.marshal_with(project)
    @api.response(404, 'Project not found.')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('projectid', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        projectid = args['projectid']
        if valid_user(apikey, orcid):
            return db.get_project(projectid, orcid)
        return "{ error: 'Invalid API Key' }"
