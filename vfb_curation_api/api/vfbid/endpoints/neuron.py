import logging

from flask import request
from flask_restplus import Resource
from vfb_curation_api.api.vfbid.business import create_neuron, valid_user
from vfb_curation_api.api.vfbid.serializers import neuron, list_of_neurons
from vfb_curation_api.api.restplus import api
from vfb_curation_api.api.vfbid.errorcodes import INVALID_APIKEY, UNKNOWNERROR
from vfb_curation_api.database.repository import db
from flask_restplus import reqparse, marshal

log = logging.getLogger(__name__)

ns = api.namespace('neuron', description='Operations related to neurons')

parser = reqparse.RequestParser()

@ns.route('/')
@api.param('apikey', 'Your valid API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
class NeuronResource(Resource):
    @api.response(201, 'Neuron successfully created.')
    @api.expect(list_of_neurons)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        out = dict()
        try:
            if valid_user(apikey, orcid):
                nid = create_neuron(request.json, orcid)
                if isinstance(nid,dict) and 'error' in nid:
                    return nid
                else:
                    n = db.get_neuron(nid, orcid=orcid)
                    print("0-0-0-0-0-0")
                    print(n)
                    if isinstance(n, list) \
                            and any(isinstance(n_result, dict) for n_result in n) \
                            and any("error" in n_result for n_result in n):
                        return n, 403
                    elif isinstance(n, dict) and 'error' in n:
                        return n, 403
                    else:
                        out['neurons'] = marshal(n, neuron)
                        return out, 201
            else:
                out['error'] = {
                        "code": INVALID_APIKEY,
                        "message": 'Invalid API Key',
                    }
            return out, 403
        except Exception as e:
            print(e)
            out['error'] = {
                "code": UNKNOWNERROR,
                "message": str(type(e).__name__),
            }
        return out, 403


    @api.param('neuronid', 'Neuron id', required=True)
    @api.response(404, 'Dataset not found.')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('neuronid', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        neuronid = args['neuronid']
        out = dict()
        try:
            if valid_user(apikey, orcid):
                n = db.get_neuron(neuronid, orcid=orcid)
                if isinstance(n,dict) and 'error' in n:
                    return n
                return marshal(n, neuron), 201
            else:
                out['error'] = {
                    "code": INVALID_APIKEY,
                    "message": 'Invalid API Key',
                }
            return out, 403
        except Exception as e:
            print(e)
            out['error'] = {
                "code": UNKNOWNERROR,
                "message": str(type(e).__name__),
            }
        return out, 403