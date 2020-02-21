from flask_restplus import fields
from vfb_curation_api.api.restplus import api

# pagination = api.model('A page of results', {
#     'page': fields.Integer(description='Number of this page of results'),
#     'pages': fields.Integer(description='Total number of pages of results'),
#     'per_page': fields.Integer(description='Number of items per page of results'),
#     'total': fields.Integer(description='Total number of results'),
# })

dataset = api.model('Dataset', {
    'id': fields.String(readOnly=True, description='The unique VFB identifier for this dataset. Will be set automatically.'),
    'short_name': fields.String(required=True, description='Short id for dataset. No special characters or spaces. Example: WoodHartenstein2018.'),
    'title': fields.String(required=True, description='Human-readable name for dataset. Example: "L3 neuropils (WoodHartenstein2018)".'),
    'publication': fields.String(required=False, description='Associated publication (optional).'),
    'source_data': fields.String(required=False, description='URL to dataset (optional). Example: "http://flybase.org/reports/FBrf0221438.html"'),
    'description': fields.String(required=False, description='Short description dataset (optional).'),
    'license': fields.String(required=False, description='License of dataset (optional).'),
})

neuron = api.model('Neuron', {
    'id': fields.String(readOnly=True, description='The unique VFB identifier for this neuron.'),
    'orcid': fields.String(required=True, description='The ORCID of the user'),
    'primary_name': fields.String(required=True, description='Primary name of the neuron.'),
    'dataset_id': fields.List(fields.String(required=True), description='List of IDs of datasets this Neuron image belongs to.'),
    'type_specimen': fields.String(required=False, description='Type specimen of the neuron (optional)'),
    'alternative_names': fields.List(fields.String(required=False), description='List of alternative names / synonyms.'),
    'external_identifiers': fields.List(fields.String(required=True), description='List of external identifiers.'),
    'classification': fields.String(required=True, description='Type/Superclass of the neuron.'),
    'classification_comment': fields.String(required=False, description='Additional comment about the type/superclass of the Neuron.'),
    'template_id': fields.String(required=True, description='ID of the template used (can be found on VFB website)'),
    'imaging_type': fields.String(required=False, description='Imaging Type'),
    'filename': fields.String(required=True, description='Name of the file uploaded to VFB (with extension).'),
    'driver_line': fields.List(fields.String(required=False), description='Driver line'),
    'neuropils': fields.List(fields.String(required=False), description='Neuropils'),
    'input_neuropils': fields.List(fields.String(required=False), description='Input neuropils'),
    'output_neuropils': fields.List(fields.String(required=False), description='Output neuropils'),
})

# list_of_neurons = api.model( 'NeuronList',  {
#     'neurons': fields.List(fields.Nested(neuron))
# })
#
# page_of_neurons = api.inherit('Page of datasets', pagination, {
#     'items': fields.List(fields.Nested(dataset))
# })

project = api.model('Project', {
    'id': fields.String(readOnly=True, description='The unique identifier for this project.'),
    'primary_name': fields.String(readOnly=True, description='The unique identifier for this project.'),
    'description': fields.String(readOnly=True, description='Short description of this project project.'),
})

user = api.model('User', {
    'orcid': fields.String(readOnly=True, description='The ORCID for this user.'),
    'primary_name': fields.String(readOnly=True, description='The name of this user.'),
    'apikey': fields.String(readOnly=True, description='The current API key for this user.'),
    'manages_projects': fields.List(fields.String(readOnly=True), description='A list of project ids this user manages.'),
})

neuron_type = api.model('NeuronType', {
    'id': fields.String(readOnly=True, description='The unique identifier for this neuron type.'),
    'parent': fields.String(readOnly=True, description='The unique identifier of the parent of this neuron type.'),
    'label': fields.String(readOnly=True, description='Unique name for this neuron type.'),
    'exemplar': fields.String(readOnly=True, description='VFB ID of image which serves as the exemplar for this type.'),
    'synonyms': fields.List(fields.String(readOnly=True), description='List of synonyms of this neuron type.'),
})

site = api.model('Site', {
    'id': fields.String(readOnly=True, description='The unique identifier for this site or web resource.'),
    'url': fields.String(readOnly=True, description='The unique identifier for this site or web resource.'),
    'short_form': fields.String(readOnly=True, description='Short description of this site or web resource.'),
})
