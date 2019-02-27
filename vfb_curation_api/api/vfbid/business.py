from vfb_curation_api.database.models import Neuron, Dataset
from vfb_curation_api.database.repository.neuron_repository import create_neuron_db
from vfb_curation_api.database.repository.dataset_repository import create_dataset_db

def create_datatset(data):
    orcid = data.get('orcid')
    project = data.get('project')
    short_name = data.get('short_name')
    title = data.get('title')
    publication = data.get('publication')
    source_data = data.get('source_data')
    ds = Dataset(orcid, project, short_name, title, publication, source_data)
    return create_dataset_db(ds)

def create_neuron(data):
    orcid = data.get('orcid')
    project = data.get('project')
    primary_name = data.get('primary_name')
    type_specimen = data.get('type_specimen')
    alternative_names = data.get('alternative_names')
    external_identifiers = data.get('external_identifiers')
    classification = data.get('classification')
    classification_comment = data.get('classification_comment')
    url_skeleton_id = data.get('url_skeleton_id')
    template_id = data.get('template_id')
    imaging_type = data.get('imaging_type')
    n = Neuron(orcid, project, primary_name)
    n.set_type_specimen(type_specimen)
    n.set_alternative_names(alternative_names)
    n.set_classification(classification)
    n.set_external_identifiers(external_identifiers)
    n.set_url_skeleton_id(url_skeleton_id)
    n.set_template_id(template_id)
    n.set_imaging_type(imaging_type)
    n.set_classification_comment(classification_comment)
    return create_neuron_db(n)


