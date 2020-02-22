import logging
import json
from flask import request
from flask_restplus import Resource, reqparse, marshal
from vfb_curation_api.api.vfbid.business import create_neuron_type, valid_user
from vfb_curation_api.api.vfbid.serializers import neuron_type
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db

log = logging.getLogger(__name__)

ns = api.namespace('neuron_type', description='Operations related to neuron types')


@ns.route('/')
@api.param('apikey', 'Your valid API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
class DatasetResource(Resource):

    @api.response(201, 'Dataset successfully created.')
    @api.expect(neuron_type)
    @api.marshal_with(neuron_type)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        if valid_user(apikey, orcid):
            neuron_type_id = create_neuron_type(request.json, orcid)
            return db.get_neuron_type(neuron_type_id, orcid), 201
        return "{ error: 'Invalid API Key' }"

    @api.response(404, 'Dataset not found.')
    @api.param('neuron_type_id', 'VFB id of neuron type', required=True)
    @api.marshal_with(neuron_type)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        parser.add_argument('neuron_type_id', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        neuron_type_id = args['neuron_type_id']
        if valid_user(apikey, orcid):
            ds = db.get_neuron_type(neuron_type_id, orcid)
            print(json.dumps(marshal(ds, neuron_type)))
            return ds, 201
        return "{ error: 'Invalid API Key' }"
