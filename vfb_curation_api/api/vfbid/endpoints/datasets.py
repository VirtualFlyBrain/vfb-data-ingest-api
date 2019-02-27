import logging

from flask import request
from flask_restplus import Resource
from vfb_curation_api.api.vfbid.business import create_datatset
from vfb_curation_api.api.vfbid.serializers import dataset, page_of_datasets
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database import db

log = logging.getLogger(__name__)

ns = api.namespace('dataset', description='Operations related to datasets')


@ns.route('/')
class PostsCollection(Resource):

    @api.marshal_list_with(dataset)
    def get(self):
        """
        Returns list of vfbid categories.
        """
        neurons = db.get_all_datasets()
        return neurons

    @api.expect(dataset)
    def post(self):
        """
        Creates a new vfbid post.
        """
        id = create_datatset(request.json)
        return {"vfbid": id}, 201


@ns.route('/<int:id>')
@api.response(404, 'Post not found.')
class DatasetItem(Resource):

    @api.marshal_with(dataset)
    def get(self, id):
        """
        Returns a vfbid post.
        """
        return db.get_dataset(id)

