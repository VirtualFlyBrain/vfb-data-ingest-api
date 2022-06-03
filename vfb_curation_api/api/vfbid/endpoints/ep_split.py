import logging
from flask import request
from flask_restplus import Resource, reqparse, marshal
from vfb_curation_api.api.vfbid.business import create_ep_split, valid_user
from vfb_curation_api.api.vfbid.errorcodes import INVALID_APIKEY, UNKNOWNERROR
from vfb_curation_api.api.vfbid.serializers import list_of_split_drivers, split_driver
from vfb_curation_api.api.vfbid.endpoints.neuron import get_neuron
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db

log = logging.getLogger(__name__)

ns = api.namespace('ep_split', description='Operations related to EP/Split')


@ns.route('/')
@api.param('apikey', 'Your valid API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
class EpSplitResource(Resource):

    @api.response(201, 'EP/Split successfully created.')
    @api.expect(list_of_split_drivers)
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
                nid = create_ep_split(request.json, orcid, False)
                if isinstance(nid,dict) and 'error' in nid:
                    return nid
                else:
                    n = db.get_neuron(nid, orcid=orcid)
                    print(n)
                    if isinstance(n, list) \
                            and any(isinstance(n_result, dict) for n_result in n) \
                            and any("error" in n_result for n_result in n):
                        return n, 403
                    elif isinstance(n, dict) and 'error' in n:
                        return n, 403
                    else:
                        out['neurons'] = marshal(n, split_driver)
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

    @api.param('epsplitid', 'EP/Split id', required=True)
    @api.response(404, 'EP/Split not found.')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('epsplitid', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        epsplitid = args['epsplitid']
        return get_neuron(apikey, orcid, epsplitid)
