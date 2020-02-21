from random import randint

class Dataset():
    def __init__(self, id, short_name, title):
        self.id = id
        self.short_name = short_name
        self.title = title
        self.publication = ""
        self.source_data = ""
        self.description = ""
        self.license = ""
        self.project = ""

        def set_publication(self, publication):
            self.publication = publication

        def set_source_data(self, source_data):
            self.source_data = source_data

        def set_description(self, description):
            self.description = description

        def set_license(self, license):
            self.license = license

        def set_project(self, project):
            self.project = project



    def __repr__(self):
        return '<Dataset %r>' % self.title


class Neuron():
    def __init__(self, primary_name, id):
        self.primary_name = primary_name
        self.id = id
        self.datasets = []
        #self.project = ""
        self.type_specimen = ""
        self.alternative_names = []
        self.external_identifiers = [] # { GO: 001 }
        self.classification = ""
        self.classification_comment = ""
        #self.url_skeleton_id = ""
        self.template_id = ""
        self.filename = ""
        self.imaging_type = ""
        self.driver_line = []
        self.neuropils = []
        self.input_neuropils = []
        self.output_neuropils = []


    def set_datasets(self, datasets):
        self.datasets = datasets

    def set_project_id(self, project_id):
        self.project = project_id

    def set_type_specimen(self, type_specimen):
        self.type_specimen = type_specimen

    def set_alternative_names(self, alternative_names):
        self.alternative_names = alternative_names

    def set_external_identifiers(self, external_identifiers):
        self.external_identifiers = external_identifiers

    def set_classification(self, classification):
        self.classification = classification

    def set_type_specimen(self, type_specimen):
        self.type_specimen = type_specimen

    def set_classification_comment(self, classification_comment):
        self.classification_comment = classification_comment

    def set_url_skeleton_id(self, url_skeleton_id):
        self.url_skeleton_id = url_skeleton_id

    def set_template_id(self, template_id):
        self.template_id = template_id

    def set_imaging_type(self, imaging_type):
        self.imaging_type = imaging_type

    def __repr__(self):
        return '<Neuron %r>' % self.primary_name


class Project():
    def __init__(self, id):
        self.id = id
        self.primary_name = ""
        self.description = ""

    def __repr__(self):
        return '<Project %r>' % self.id


class User():
    def __init__(self, orcid, primary_name, apikey):
        self.orcid = orcid
        self.primary_name = primary_name
        self.apikey = apikey
        self.manages_projects = []

    def __repr__(self):
        return '<User %r>' % self.id

class NeuronType:
    def __init__(self, id):
        self.id = id
        self.synonyms = []
        self.parent = ""
        #self.supertype = "" Why neeed that?
        self.label = ""
        self.exemplar = ""

class Site:
    def __init__(self, id):
        self.id = id
        self.url = ""
        self.short_form = ""