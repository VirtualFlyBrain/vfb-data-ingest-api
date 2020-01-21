import logging

from flask import request
from flask_restplus import Resource
from vfb_curation_api.api.vfbid.business import create_neuron, valid_user
from vfb_curation_api.api.vfbid.serializers import neuron
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db
from flask_restplus import reqparse

log = logging.getLogger(__name__)

ns = api.namespace('neuron', description='Operations related to neurons')

parser = reqparse.RequestParser()

@ns.route('/')
@api.param('apikey', 'Your valid API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
class NeuronResource(Resource):
    @api.response(201, 'Neuron successfully created.')
    @api.expect(neuron)
    @api.marshal_with(neuron)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        if valid_user(apikey, orcid):
            nid = create_neuron(request.json)
            return db.get_neuron(nid), 201
        return "{ error: 'Invalid API Key' }"

    @api.param('neuronid', 'Neuron id', required=True)
    @api.response(404, 'Dataset not found.')
    @api.marshal_with(neuron)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('neuronid', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        neuronid = args['neuronid']
        if valid_user(apikey, orcid):
            return db.get_neuron(neuronid, orcid)
        return "{ error: 'Invalid API Key' }"