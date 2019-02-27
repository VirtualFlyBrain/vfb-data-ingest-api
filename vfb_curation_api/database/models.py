from random import randint

class Dataset():
    def __init__(self, orcid, project, short_name, title, publication, source_data):
        self.id = randint(0, 9999)
        self.short_name = short_name
        self.title = title
        self.publication = publication
        self.source_data = source_data
        self.orcid = orcid
        self.project = project

    def __repr__(self):
        return '<Dataset %r>' % self.title


class Neuron():
    def __init__(self, orcid, project, primary_name):
        self.orcid = orcid
        self.project = project
        self.primary_name = primary_name
        self.dataset_id = ""
        self.type_specimen = ""
        self.alternative_names = []
        self.external_identifiers = []
        self.classification = ""
        self.classification_comment = ""
        self.url_skeleton_id = ""
        self.template_id = ""
        self.imaging_type = ""

    def set_dataset_id(self, dataset_id):
        self.dataset_id = dataset_id

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
        return '<Neuron %r>' % self.name
