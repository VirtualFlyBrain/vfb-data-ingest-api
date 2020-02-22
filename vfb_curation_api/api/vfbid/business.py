from vfb_curation_api.database.models import Neuron, Dataset, Project
from vfb_curation_api.database.repository import db

def create_dataset(data, project, orcid):
    short_name = data.get('short_name')
    title = data.get('title')
    publication = data.get('publication')
    source_data = data.get('source_data')
    ds = Dataset(orcid, short_name, title)
    ds.set_publication(publication)
    ds.set_source_data(source_data)
    return db.create_dataset(ds, project, orcid)


def create_neuron(data):
    orcid = data.get('orcid')
    project = data.get('project')
    primary_name = data.get('primary_name')
    type_specimen = data.get('type_specimen')
    alternative_names = data.get('alternative_names')
    external_identifiers = data.get('external_identifiers')
    classification = data.get('classification')
    dataset_id = data.get('dataset_id')
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
    n.set_dataset_id(dataset_id)
    return db.create_neuron_db(n)


def create_project(data):
    projectid = data.get('projectid')
    ds = Project(projectid)
    return db.create_project_db(ds)


def valid_user(apikey, orcid):
    return db.valid_user(apikey, orcid)