import logging

from flask_restplus import Resource, reqparse
from vfb_curation_api.api.vfbid.serializers import dataset
from vfb_curation_api.api.vfbid.business import valid_user
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db


log = logging.getLogger(__name__)

ns = api.namespace('datasets', description='Operations related to lists of datasets')


@ns.route('/')
@api.response(404, 'No datasets found.')
@api.param('apikey','Your API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
@api.param('projectid', 'The VFB Project ID', required=True)
class DatasetList(Resource):

    @api.marshal_with(dataset)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('projectid', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        projectid = args['projectid']
        orcid = args['orcid']
        if valid_user(apikey, orcid):
            return db.get_all_datasets(projectid, orcid)
        return "{ error: 'Invalid API Key' }"
