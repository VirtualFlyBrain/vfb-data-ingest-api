from flask_restplus import fields
from vfb_curation_api.api.restplus import api

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

dataset = api.model('Dataset', {
    'id': fields.String(readOnly=True, description='The unique VFB identifier for this dataset. Will be set automatically.'),
    'short_name': fields.String(required=True, description='Short id for dataset. No special characters or spaces.'),
    'title': fields.String(required=True, description='Human-readable name for dataset.'),
    'publication': fields.String(required=False, description='Associated publication (optional).'),
    'source_data': fields.String(required=False, description='URL to dataset (optional).'),
})

list_of_datasets = api.model('DatasetList',  {
    'datasets': fields.List(fields.Nested(dataset))
})

page_of_datasets = api.inherit('Page of datasets', pagination, {
    'items': fields.List(fields.Nested(dataset))
})


neuron = api.model('Neuron', {
    'id': fields.String(readOnly=True, description='The unique VFB identifier for this neuron.'),
    'orcid': fields.String(required=True, description='The ORCID of the user'),
    'project': fields.String(required=True, description='Category name'),
    'primary_name': fields.String(required=True, description='Category name'),
    'dataset_id': fields.String(required=True, description='Category name'),
    'type_specimen': fields.String(required=True, description='Category name'),
    'alternative_names': fields.List(fields.String(required=True), description='Category name'),
    'external_identifiers': fields.List(fields.String(required=True), description='Category name'),
    'classification': fields.String(required=True, description='Category name'),
    'classification_comment': fields.String(required=True, description='Category name'),
    'url_skeleton_id': fields.String(required=True, description='Category name'),
    'template_id': fields.String(required=True, description='Category name'),
    'imaging_type': fields.String(required=True, description='Category name'),
})

list_of_neurons = api.model( 'NeuronList',  {
    'neurons': fields.List(fields.Nested(neuron))
})

page_of_neurons = api.inherit('Page of datasets', pagination, {
    'items': fields.List(fields.Nested(dataset))
})

project = api.model('Project', {
    'id': fields.String(readOnly=True, description='The unique identifier for this project.'),
})

list_of_projects = api.model('ProjectList',   {
    'projects': fields.List(fields.Nested(project))
})

page_of_projects = api.inherit('Page of projects', pagination, {
    'items': fields.List(fields.Nested(dataset))
})

user = api.model('User', {
    'id': fields.String(readOnly=True, description='The unique identifier for this user.'),
    'primary_name': fields.String(readOnly=True, description='The name of this user.'),
    'apikey': fields.String(readOnly=True, description='The current API key for this user.'),
})