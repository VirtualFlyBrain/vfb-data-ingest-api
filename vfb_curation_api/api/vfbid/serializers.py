from flask_restplus import fields
from vfb_curation_api.api.restplus import api

dataset = api.model('Dataset', {
    'id': fields.Integer(readOnly=True, description='The unique VFB identifier for this dataset. Will be set automatically.'),
    'orcid': fields.String(required=True, description='Category name'),
    'project': fields.String(required=True, description='Category name'),
    'short_name': fields.String(required=True, description='Short id for dataset. No special characters or spaces.'),
    'title': fields.String(required=True, description='Human-readable name for dataset.'),
    'publication': fields.String(required=False, description='Associated publication (optional).'),
    'source_data': fields.String(required=False, description='URL to dataset (optional).'),
})

pagination = api.model('A page of results', {
    'page': fields.Integer(description='Number of this page of results'),
    'pages': fields.Integer(description='Total number of pages of results'),
    'per_page': fields.Integer(description='Number of items per page of results'),
    'total': fields.Integer(description='Total number of results'),
})

page_of_datasets = api.inherit('Page of datsets', pagination, {
    'items': fields.List(fields.Nested(dataset))
})

neuron = api.model('Blog category', {
    'id': fields.String(readOnly=True, description='The unique VFB identifier for this neuron.'),
    'orcid': fields.String(required=True, description='Category name'),
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

neurons_for_dataset = api.inherit('Neurons for project', dataset, {
    'posts': fields.List(fields.Nested(neuron))
})
