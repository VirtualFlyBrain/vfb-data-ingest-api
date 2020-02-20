import logging

from flask_restplus import Resource, reqparse
from vfb_curation_api.api.vfbid.serializers import neuron
from vfb_curation_api.api.vfbid.business import valid_user
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db


log = logging.getLogger(__name__)

ns = api.namespace('neurons', description='Operations related to lists of neurons')


@ns.route('/')
@api.response(404, 'No neurons found.')
@api.param('apikey', 'Your API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
@api.param('datasetid', 'Your ORCID', required=True)
class NeuronList(Resource):

    @api.marshal_with(neuron)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('datasetid', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        datasetid = args['datasetid']
        orcid = args['orcid']
        if valid_user(apikey, orcid):
            return db.get_all_neurons(orcid=orcid,datasetid=datasetid)
        return "{ error: 'Invalid API Key' }"
