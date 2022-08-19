from flask_restplus import fields
from vfb_curation_api.api.restplus import api

# pagination = api.model('A page of results', {
#     'page': fields.Integer(description='Number of this page of results'),
#     'pages': fields.Integer(description='Total number of pages of results'),
#     'per_page': fields.Integer(description='Number of items per page of results'),
#     'total': fields.Integer(description='Total number of results'),
# })

dataset = api.model('Dataset', {
    'id': fields.String(readonly=True, description='The unique VFB identifier for this dataset. Will be set automatically.'),
    'short_name': fields.String(required=True, description='Short id for dataset. No special characters or spaces. Example: WoodHartenstein2018.'),
    'projectid': fields.String(required=True, description='The four letter ID of your Project.'),
    'title': fields.String(required=True, description='Human-readable name for dataset. Example: "L3 neuropils (WoodHartenstein2018)".'),
    'publication': fields.String(required=False, description='Associated publication (optional).'),
    'source_data': fields.String(required=False, description='URL to dataset (optional). Example: "http://flybase.org/reports/FBrf0221438.html"'),
    'description': fields.String(required=False, description='Short description dataset (optional).'),
    'license': fields.String(required=False, description='License of dataset (optional).'),
})

datasetid = api.model('DatasetID', {
    'id': fields.String(readonly=True, description='The unique VFB identifier for this dataset.',skip_none=True),
})

external_identifier = api.model('ExternalID', {
    'resource_id': fields.String(description='The ID of an external resource, such as a website or database (must be valid in VFB).',skip_none=True),
    'external_id': fields.String(description='The unique identifier of an object, such as a neuron, in the context of the resource.',skip_none=True),
})



neuron = api.model('Neuron', {
    'id': fields.String(readonly=True, description='The unique VFB identifier for this neuron - will be ignored when posting new neurons.'),
    #'orcid': fields.String(required=True, description='The ORCID of the user'),
    'primary_name': fields.String(required=True, description='Primary name of the neuron.'),
    'datasetid': fields.String(required=True, description='Dataset ID.'),
    'projectid': fields.String(required=False, description='Project ID.'),
    #'type_specimen': fields.String(required=False, description='Type specimen of the neuron (optional)'),
    'alternative_names': fields.List(fields.String(required=False), description='List of alternative names / synonyms.'),
    'external_identifiers': fields.List(fields.Nested(external_identifier), description='List of external identifiers.'),
    'classification': fields.List(fields.String(required=True), description='Type/Superclass of the neuron.'),
    'classification_comment': fields.String(required=False, description='Additional comment about the type/superclass of the Neuron.'),
    'template_id': fields.String(required=True, description='ID of the template used (can be found on VFB website)'),
    'imaging_type': fields.String(required=False, description='Imaging Type'),
    'filename': fields.String(required=True, description='Name of the file uploaded to VFB (with extension).'),
    'driver_line': fields.List(fields.String(required=False), description='Driver line'),
    'neuropils': fields.List(fields.String(required=False), description='Neuropils'),
    'part_of': fields.List(fields.String(required=False), description='Part of'),
    'input_neuropils': fields.List(fields.String(required=False), description='Input neuropils'),
    'output_neuropils': fields.List(fields.String(required=False), description='Output neuropils'),
    'comment': fields.String(required=True, description='Comment about the neuron'),
})

list_of_neurons = api.model('NeuronList',  {
     'neurons': fields.List(fields.Nested(neuron))
})
#
# page_of_neurons = api.inherit('Page of datasets', pagination, {
#     'items': fields.List(fields.Nested(dataset))
# })

project = api.model('Project', {
    'id': fields.String(readonly=True, description='The unique, four-letter identifier for this project.'),
    'primary_name': fields.String(readonly=False, description='The primary name for this project.'),
    'description': fields.String(readonly=False, description='Short description of this project project.'),
    'start': fields.Integer(readonly=False, min=0, description='The start id range for this project.')
})

user = api.model('User', {
    'orcid': fields.String(readonly=True, description='The ORCID for this user.'),
    'primary_name': fields.String(readonly=False, description='The name of this user.'),
    'apikey': fields.String(readonly=False, description='The current API key for this user.'),
    'role': fields.String(readonly=False, description='The role of this user.'),
    'email': fields.String(readonly=False, description='The email of this user.'),
    'manages_projects': fields.List(fields.String(readonly=False), description='A list of project ids this user manages.'),
})

neuron_type = api.model('NeuronType', {
    'id': fields.String(readonly=True, description='The unique identifier for this neuron type.'),
    'parent': fields.String(readonly=False, description='The unique identifier of the parent of this neuron type.'),
    'label': fields.String(readonly=False, description='Unique name for this neuron type.'),
    'exemplar': fields.String(readonly=False, description='VFB ID of image which serves as the exemplar for this type.'),
    'synonyms': fields.List(fields.String(readonly=False), description='List of synonyms of this neuron type.'),
})

site = api.model('Site', {
    'id': fields.String(readonly=True, description='The unique identifier for this site or web resource.'),
    'url': fields.String(readonly=False, description='The unique identifier for this site or web resource.'),
    'short_form': fields.String(readonly=False, description='Short description of this site or web resource.'),
})

split = api.model('Split', {
    'id': fields.String(readonly=True, description='The unique identifier for this split.'),
    'dbd': fields.String(readonly=False, description='The DNA-binding domain (DBD) hemidriver.'),
    'ad': fields.String(readonly=False, description='The activation domain (AD) hemidriver.'),
    'synonyms': fields.List(fields.String(readonly=False), description='List of synonyms of this split.'),
    'xrefs': fields.List(fields.String(required=False), description='Associated xrefs.'),
})

split_driver = api.model('SplitDriver', {
    'id': fields.String(readonly=True, description='The unique VFB identifier for this split driver - will be ignored when posting new split drivers.'),
    #'orcid': fields.String(required=True, description='The ORCID of the user'),
    'primary_name': fields.String(required=True, description='Primary name of the split driver.'),
    'datasetid': fields.String(required=True, description='Dataset ID.'),
    'projectid': fields.String(required=False, description='Project ID.'),
    #'type_specimen': fields.String(required=False, description='Type specimen of the neuron (optional)'),
    'alternative_names': fields.List(fields.String(required=False), description='List of alternative names / synonyms.'),
    'external_identifiers': fields.List(fields.Nested(external_identifier), description='List of external identifiers.'),
    'classification': fields.List(fields.String(required=True), description='Type/Superclass of the split driver.'),
    'classification_comment': fields.String(required=False, description='Additional comment about the type/superclass of the split driver.'),
    'template_id': fields.String(required=True, description='ID of the template used (can be found on VFB website)'),
    'imaging_type': fields.String(required=False, description='Imaging Type'),
    'filename': fields.String(required=True, description='Name of the file uploaded to VFB (with extension).'),
    'driver_line': fields.List(fields.String(required=False), description='Driver line'),
    'neuropils': fields.List(fields.String(required=False), description='Neuropils'),
    'part_of': fields.List(fields.String(required=False), description='Part of'),
    'input_neuropils': fields.List(fields.String(required=False), description='Input neuropils'),
    'output_neuropils': fields.List(fields.String(required=False), description='Output neuropils'),
    'comment': fields.String(required=True, description='Comment about the split driver'),
    'has_part': fields.List(fields.String(required=False), description='List of neurons to annotate via has_part'),
})

list_of_split_drivers = api.model('SplitDriverList',  {
     'split_drivers': fields.List(fields.Nested(split_driver))
})
