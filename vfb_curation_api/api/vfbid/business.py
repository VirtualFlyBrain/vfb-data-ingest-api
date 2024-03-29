import sys
from vfb_curation_api.database.models import Neuron, Dataset, Project, NeuronType, Site, Split, SplitDriver
from vfb_curation_api.database.repository import db
from vfb_curation_api.api.vfbid.errorcodes import UNKNOWNERROR


def create_dataset(data, orcid):
    short_name = data.get('short_name')
    title = data.get('title')
    publication = data.get('publication')
    project = data.get('projectid')
    description = data.get('description')
    source_data = data.get('source_data')
    license = data.get('license')
    ds = Dataset(orcid, short_name, title)
    ds.set_project_id(project)
    ds.set_publication(publication)
    ds.set_source_data(source_data)
    ds.set_description(description)
    ds.set_license(license)
    return db.create_dataset(ds, project, orcid)


def create_neuron(data_all, orcid):
    neurons = []
    for data in data_all['neurons']:
        primary_name = data.get('primary_name')
        type_specimen = data.get('type_specimen')
        alternative_names = data.get('alternative_names')
        external_identifiers = data.get('external_identifiers')
        classification = data.get('classification')
        datasetid = data.get('datasetid')
        classification_comment = data.get('classification_comment')
        url_skeleton_id = data.get('url_skeleton_id')
        template_id = data.get('template_id')
        imaging_type = data.get('imaging_type')
        filename = data.get('filename')
        part_of = data.get('part_of')
        driver_line = data.get('driver_line')
        neuropils = data.get('neuropils')
        input_neuropils = data.get('input_neuropils')
        output_neuropils = data.get('output_neuropils')
        comment = data.get('comment')
        n = Neuron(primary_name)
        n.set_type_specimen(type_specimen)
        n.set_alternative_names(alternative_names)
        n.set_classification(classification)
        n.set_external_identifiers(external_identifiers)
        n.set_template_id(template_id)
        n.set_imaging_type(imaging_type)
        n.set_classification_comment(classification_comment)
        n.set_filename(filename)
        n.set_part_of(part_of)
        n.set_driver_line(driver_line)
        n.set_neuropils(neuropils)
        n.set_input_neuropils(input_neuropils)
        n.set_output_neuropils(output_neuropils)
        n.set_comment(comment)
        neurons.append(n)
    try:
        result = db.create_neuron_db(neurons=neurons,datasetid=datasetid,orcid=orcid)
        return result
    except Exception as e:
        db.clear_neo_logs()
        print(e.with_traceback())
        print(sys.exc_info()[2])
        return db.wrap_error(["Unknown error has occured while adding neurons ({})".format(str(type(e)))], UNKNOWNERROR)


def create_project(data):
    projectid = data.get('projectid')
    ds = Project(projectid)
    return db.create_project_db(ds)


def create_neuron_type(data):
    neuron_type_id = data.get('neuron_type_id')
    ds = NeuronType(neuron_type_id)
    return db.create_neuron_type_db(ds)


def valid_user(apikey, orcid):
    return db.valid_user(apikey, orcid)


def create_split(data):
    # split_id = data.get('split_id')
    split = Split(data.get('dbd'), data.get('ad'))
    if 'synonyms' in data:
        split.set_synonyms(data.get('synonyms'))
    if 'xrefs' in data:
        split.set_xrefs(data.get('xrefs'))
    return db.create_split(split)


def create_ep_split(data_all, orcid, ep_split_flp_out=False):
    split_drivers = []
    for data in data_all['split_drivers']:
        primary_name = data.get('primary_name')
        type_specimen = data.get('type_specimen')
        alternative_names = data.get('alternative_names')
        external_identifiers = data.get('external_identifiers')
        classification = data.get('classification')
        datasetid = data.get('datasetid')
        classification_comment = data.get('classification_comment')
        url_skeleton_id = data.get('url_skeleton_id')
        template_id = data.get('template_id')
        imaging_type = data.get('imaging_type')
        filename = data.get('filename')
        part_of = data.get('part_of')
        driver_line = data.get('driver_line')
        neuropils = data.get('neuropils')
        input_neuropils = data.get('input_neuropils')
        output_neuropils = data.get('output_neuropils')
        comment = data.get('comment')
        neurons = data.get('split_drivers')
        sd = SplitDriver(primary_name)
        sd.set_type_specimen(type_specimen)
        sd.set_alternative_names(alternative_names)
        sd.set_classification(classification)
        sd.set_external_identifiers(external_identifiers)
        sd.set_template_id(template_id)
        sd.set_imaging_type(imaging_type)
        sd.set_classification_comment(classification_comment)
        sd.set_filename(filename)
        sd.set_part_of(part_of)
        sd.set_driver_line(driver_line)
        sd.set_neuropils(neuropils)
        sd.set_input_neuropils(input_neuropils)
        sd.set_output_neuropils(output_neuropils)
        sd.set_comment(comment)
        sd.set_has_part(neurons)

        split_drivers.append(sd)
    try:
        result = db.create_split_driver_db(split_drivers=split_drivers, datasetid=datasetid, orcid=orcid,
                                           ep_split_flp_out=ep_split_flp_out)
        return result
    except Exception as e:
        db.clear_neo_logs()
        print(e.with_traceback())
        print(sys.exc_info()[2])
        return db.wrap_error(["Unknown error has occured while adding split driver ({})".format(str(type(e)))], UNKNOWNERROR)
