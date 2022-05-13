import logging
import json
from flask import request
from flask_restplus import Resource, reqparse, marshal
from vfb_curation_api.api.vfbid.business import create_dataset, valid_user
from vfb_curation_api.api.vfbid.errorcodes import INVALID_APIKEY, UNKNOWNERROR
from vfb_curation_api.api.vfbid.serializers import dataset
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db

log = logging.getLogger(__name__)

ns = api.namespace('dataset', description='Operations related to datasets')


@ns.route('/')
@api.param('apikey', 'Your valid API Key', required=True)
@api.param('orcid', 'Your ORCID', required=True)
class DatasetResource(Resource):

    @api.response(201, 'Dataset successfully created.')
    @api.expect(dataset)
    def post(self):
        out = dict()
        parser = reqparse.RequestParser()
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        if valid_user(apikey, orcid):
            datasetid = create_dataset(request.json, orcid)
            if isinstance(datasetid, dict) and 'error' in datasetid:
                return datasetid, 403
            return datasetid, 201
        out['error'] = "Invalid API Key"
        out['code'] = INVALID_APIKEY
        return out, 403

    @api.response(404, 'Dataset not found.')
    @api.param('datasetid', 'Dataset id', required=True)
    @api.marshal_with(dataset)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('datasetid', required=True, type=str)
        parser.add_argument('apikey', type=str, required=True)
        parser.add_argument('orcid', type=str, required=True)
        args = parser.parse_args()
        apikey = args['apikey']
        orcid = args['orcid']
        datasetid = args['datasetid']
        if valid_user(apikey, orcid):
            ds = db.get_dataset(datasetid, orcid)
            print(json.dumps(marshal(ds, dataset)))
            return ds, 201
        return "{ error: 'Invalid API Key' }"
