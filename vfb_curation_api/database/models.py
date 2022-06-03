from enum import Enum


class Dataset:
    def __init__(self, id, short_name, title):
        self.id = id
        self.short_name = short_name
        self.title = title
        self.publication = ""
        self.projectid = ""
        self.source_data = ""
        self.description = ""
        self.license = ""


    def set_publication(self, publication):
        self.publication = publication

    def set_source_data(self, source_data):
        self.source_data = source_data

    def set_project_id(self, projectid):
        self.projectid = projectid

    def set_description(self, description):
        self.description = description

    def set_license(self, license):
        self.license = license

    def __repr__(self):
        return '<Dataset %r>' % self.title


class Neuron:
    def __init__(self, primary_name):
        self.primary_name = primary_name  # label
        self.id = ""
        self.datasetid = ""
        self.projectid = ""
        # self.type_specimen = ""  # Removed for now, deal with this via add NeuronType
        self.alternative_names = []
        self.external_identifiers = []
        # self.external_identifiers = dict() # { GO: 001 }
        self.classification = "" # http://
        self.classification_comment = ""
        # self.url_skeleton_id = ""
        self.template_id = "" # "grc2018"
        self.filename = ""
        self.imaging_type = "" #computer graphic
        self.part_of = []  # part_of http://purl.obolibrary.org/obo/BFO_0000050
        self.driver_line = []  # expresses http://purl.obolibrary.org/obo/RO_0002292
        self.neuropils = []  # overlaps’ http://purl.obolibrary.org/obo/RO_0002131
        self.input_neuropils = []  # ‘has postsynaptic terminal in’ http://purl.obolibrary.org/obo/RO_0002110
        self.output_neuropils = []  # ‘has presynaptic terminal in’  http://purl.obolibrary.org/obo/RO_0002113
        self.comment = ""

    def set_id(self, id):
        self.id = id

    def set_datasetid(self, datasetid):
        self.datasetid = datasetid

    def set_project_id(self, projectid):
        self.projectid = projectid

    def set_type_specimen(self, type_specimen):
        self.type_specimen = type_specimen

    def set_alternative_names(self, alternative_names):
        self.alternative_names = alternative_names

    def set_external_identifiers(self, external_identifiers):
        self.external_identifiers = external_identifiers

    def set_classification(self, classification):
        self.classification = classification

    def set_filename(self, filename):
        self.filename = filename

    def set_neuropils(self, neuropils):
        self.neuropils = neuropils

    def set_input_neuropils(self, input_neuropils):
        self.input_neuropils = input_neuropils

    def set_output_neuropils(self, output_neuropils):
        self.output_neuropils = output_neuropils

    def set_driver_line(self, driver_line):
        self.driver_line = driver_line

    def set_part_of(self, part_of):
        self.part_of = part_of

    def set_classification_comment(self, classification_comment):
        self.classification_comment = classification_comment

    # def set_url_skeleton_id(self, url_skeleton_id):
    #   self.url_skeleton_id = url_skeleton_id

    def set_template_id(self, template_id):
        self.template_id = template_id

    def set_imaging_type(self, imaging_type):
        self.imaging_type = imaging_type

    def set_comment(self, comment):
        self.comment = comment

    def __repr__(self):
        return '<Neuron %r>' % self.primary_name


class Project:
    def __init__(self, id):
        self.id = id
        self.primary_name = ""
        self.description = ""
        self.start = 0

    def set_primary_name(self, primary_name):
        self.primary_name = primary_name

    def set_description(self, description):
        self.description = description

    def set_start(self, start):
        self.start = start

    def __repr__(self):
        return '<Project %r>' % self.id


class User:
    def __init__(self, orcid, primary_name, apikey, role=None, email=None):
        self.orcid = orcid
        self.primary_name = primary_name
        self.apikey = apikey
        self.role = role
        self.email = email
        self.manages_projects = []

    def __repr__(self):
        return '<User %r>' % self.id


Role = Enum('Role', 'admin user')


class NeuronType:
    def __init__(self, id):
        self.id = id
        self.synonyms = []
        self.parent = ""
        # self.supertype = "" Why neeed that?
        self.label = ""
        self.exemplar = ""


class Site:
    def __init__(self, id):
        self.id = id
        self.url = ""
        self.short_form = ""


class Split:
    def __init__(self, dbd, ad):
        self.id = ""
        self.dbd = dbd
        self.ad = ad
        self.synonyms = []
        self.xrefs = []

    def set_id(self, split_id):
        self.id = split_id

    def set_dbd(self, dbd):
        self.dbd = dbd

    def set_ad(self, ad):
        self.ad = ad

    def set_synonyms(self, synonyms):
        self.synonyms = synonyms

    def set_xrefs(self, xrefs):
        self.xrefs = xrefs

    def __repr__(self):
        return '<Split %r>' % self.id


class SplitDriver(Neuron):

    def __init__(self, primary_name):
        super().__init__(primary_name)
        self.has_part = []

    def set_has_part(self, has_part):
        self.has_part = has_part
