import logging
import json
from flask import request
from flask_restplus import Resource, reqparse, marshal
from vfb_curation_api.api.vfbid.business import create_split, valid_user
from vfb_curation_api.api.vfbid.errorcodes import INVALID_APIKEY, UNKNOWNERROR
from vfb_curation_api.api.vfbid.serializers import split
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db

log = logging.getLogger(__name__)

ns = api.namespace('split', description='Operations related to split')


@ns.route('/')
@api.param('apikey', 'Your valid API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
class SplitResource(Resource):

    @api.response(201, 'Split successfully created.')
    @api.expect(split)
    def post(self):
        out = dict()
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        if valid_user(apikey, orcid):
            splitid = create_split(request.json)
            if isinstance(splitid, dict) and 'error' in splitid:
                return splitid, 403
            return splitid, 201
        out['error'] = "Invalid API Key"
        out['code'] = INVALID_APIKEY
        return out, 403

    @api.response(404, 'Split not found.')
    @api.param('splitid', 'Split id')
    @api.param('dbd', 'The DBD hemidriver.')
    @api.param('ad', 'The AD hemidriver.')
    # @api.marshal_with(split)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('splitid', type=str)
        parser.add_argument('dbd', type=str)
        parser.add_argument('ad', type=str)
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']

        if valid_user(apikey, orcid):
            if 'splitid' in args and args['splitid']:
                splitid = args['splitid']
            elif 'dbd' in args and 'ad' in args and args['dbd'] and args['ad']:
                splitid = 'VFBexp_' + args['dbd'] + args['ad']
            else:
                return "{ error: 'splitid or (dbd and ad) should be provided' }", 403

            print(splitid)
            ds = db.get_split(splitid, orcid)
            print(json.dumps(marshal(ds, split)))
            return marshal(ds, split), 201
        return "{ error: 'Invalid API Key' }", 403