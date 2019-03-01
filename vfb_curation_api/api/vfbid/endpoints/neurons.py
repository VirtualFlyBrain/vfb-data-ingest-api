import logging

from flask import request
from flask_restplus import Resource
from vfb_curation_api.api.vfbid.business import create_neuron
from vfb_curation_api.api.vfbid.serializers import neuron, neurons_for_dataset
from vfb_curation_api.api.restplus import api
from vfb_curation_api.database.repository import db

log = logging.getLogger(__name__)

ns = api.namespace('neuron', description='Operations related to neurons')


@ns.route('/')
class CategoryCollection(Resource):

    @api.marshal_list_with(neuron)
    def get(self):
        """
        Returns list of vfbid categories.
        """
        neurons = db.get_all_neurons()
        return neurons

    @api.response(201, 'Neuron successfully created.')
    @api.expect(neuron)
    def post(self):
        """
        Creates a new vfbid category.
        """
        data = request.json
        id = create_neuron(data)
        return {"vfbid": id}, 201


@ns.route('/<int:id>')
@api.response(404, 'Category not found.')
class DatasetNeuron(Resource):

    @api.marshal_with(neurons_for_dataset)
    def get(self, id):
        """
        Returns a category with a list of posts.
        """
        return db.get_neuron(id)
