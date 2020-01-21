from neo4jrestclient.client import GraphDatabase
from vfb_curation_api.database.models import Neuron, Dataset, Project, User
import os
import re
import base36
import sys
import json
from vfb_curation_api.vfb.uk.ac.ebi.vfb.neo4j.neo4j_tools import neo4j_connect


class VFBKB():
    def __init__(self):
        self.iri_base = "http://virtualflybrain.org/data/"
        self.db = None
        self.iri_base = "http://virtualflybrain.org/reports/VFB_"
        self.max_base36 = 1679615  # Corresponds to the base36 value of ZZZZZZ
        self.db_client = "vfb"

    ######################
    #### Core methods ####
    ######################

    def init_db(self):
        if not self.db:
            self.kb = os.getenv('KBserver')
            self.user = os.getenv('KBuser')
            self.password = os.getenv('KBpassword')
            print(self.kb)
            print(self.user)
            print(self.password)
            try:
                if self.db_client=="vfb":
                    self.db = neo4j_connect(self.kb, self.user, self.password)
                else:
                    self.db = GraphDatabase(self.kb, username=self.user, password=self.password)
                self.prepare_database()
                if os.getenv('LOAD_TEST_DATA'):
                    self.load_test_data()
                return True
            except Exception as e:
                print("Database could not be initialised: {}".format(e))
                return False
        else:
            return True

    def prepare_database(self):
        q_orcid_unique = "CREATE CONSTRAINT ON (a:Person) ASSERT a.orcid IS UNIQUE"
        q_projectid_unique = "CREATE CONSTRAINT ON (a:Project) ASSERT a.projectid IS UNIQUE"
        self.query(q_orcid_unique)
        self.query(q_projectid_unique)

    def load_test_data(self):
        test_cypher_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../testdata.cypher'))
        with open(test_cypher_path, 'r') as file:
            q_test_data = file.read()
        self.query(q_test_data)

    def parse_vfb_client_data(self, data_in):
        print("DATAIN: "+str(data_in))
        data = []
        for d_in in data_in:
            columns = d_in['columns']
            d = dict()
            for rec in d_in['data']:
                for i in range(len(rec['row'])):
                    d[columns[i]]=rec['row'][i]
            data.append(d)
        print("DATAOUT: " + str(data))
        return data

    def parse_neo4j_default_client_data(self, data_in):
        print("DATAIN: " + str(data_in.rows))
        data = []
        columns = []
        if data_in.rows:
            for c in data_in.rows[0]:
                columns.append(c)
        print(str(columns))
        if data_in.rows:
            for d_row in data_in.rows:
                d = dict()
                for c in columns:
                    d[c] = d_row[c]
                data.append(d)
        print("DATAOUT: " + str(data))
        return data

    def query(self,q):
        print("Q: "+str(q))
        if self.init_db():
            if self.db_client == "vfb":
                x = self.parse_vfb_client_data(self.db.commit_list([q]))
            else:
                x = self.parse_neo4j_default_client_data(self.db.query(q,data_contents=True))
            return x
        else:
            raise DatabaseNotInitialisedError("Database not initialised!")



    ################################
    #### Data retrieval ############
    ################################

    def has_project_write_permission(self, project,orcid):
        q = "MATCH (n:Project {projectid:'%s'})<-[has_admin_permissions]-(a:Person {orcid: '%s'}) RETURN n" % (project, orcid)
        print(q)
        results = self.query(q=q)
        return len(results) >= 1

    def has_dataset_write_permission(self, datasetid, orcid):
        q = "MATCH (n:Project {projectid:'%s'})<-[has_admin_permissions]-(a:Person {orcid: '%s'}) RETURN n" % (
        datasetid, orcid)
        print(q)
        results = self.query(q=q)
        return len(results) >= 1

    def valid_user(self, apikey,orcid):
        q = "MATCH (a:Person {iri: '%s', apikey: '%s'}) RETURN a" % (orcid, apikey)
        print(q)
        print("#####################valid_user:start####################")
        results = self.query(q=q)
        print("#####################valid_user:end####################")
        return len(results) >= 1

    def get_dataset(self, id, orcid):
        q = "MATCH (n:DataSet {iri:'%s'}) RETURN n.iri as id, n.short_form as primary_name, n.label as title" % id
        print(q)
        results = self.query(q=q)
        if len(results) == 1:
            return Dataset(id=results[0]['id'], short_name=results[0]['primary_name'], title=results[0]['title'])
        return None

    def get_neuron(self, id, orcid):
        q = "MATCH (n:Individual {label:'%s'}) RETURN n.label as primary_name" % id
        print(q)
        results = self.query(q=q)
        if len(results) == 1:
            return Neuron(id=results[0]['id'])

    def get_project(self, id, orcid):
        q = "MATCH (n:project {iri:'%s'}) RETURN n.iri as iri" % id
        print(q)
        results = self.query(q=q)
        return Project(id=results[0]['iri'])

    def get_user(self, orcid):
        q = "MATCH (n:Person {iri:'%s'}) RETURN n.iri as id, n.label as primary_name" % id
        print(q)
        results = self.query(q=q)
        return User(results[0]['id'])

    def get_all_datasets(self,projectid, orcid):
        q = "MATCH (n:DataSet) RETURN n.iri as id, n.short_form as primary_name, n.label as title LIMIT 10"
        print(q)
        results = self.query(q=q)
        datasets = []
        for row in results:
            datasets.append(Dataset(id=row['id'], short_name=row['primary_name'], title=row['title']))
        print(datasets)
        return datasets

    def get_all_projects(self,orcid):
        q = "MATCH (n:Project) RETURN n.iri as id LIMIT 10"
        print(q)
        results = self.query(q=q)
        projects = []
        for row in results:
            projects.append(Project(id=row['id']))
        print(projects)
        return projects

    def get_all_neurons(self, datasetid, orcid):
        q = "MATCH (n:Individual) RETURN n.iri as id LIMIT 10"
        print(q)
        results = self.query(q=q)
        neurons = []
        for row in results:
            neurons.append(Neuron(id=row['id']))
        print(neurons)
        return neurons

    ################################
    #### Data ingestion ############
    ################################

    def create_dataset(self, Dataset, project, orcid):
        if self.has_project_write_permission(project, orcid):
            q = "MATCH (n:Project {projectid:'%s'})<-[:has_associated_project]-(i:DataSet) RETURN i.iri" % project
            print(q)
            results = self.query(q=q)
            iris = [x[0].replace(self.iri_base, "") for x in results]
            sn = re.sub('[^0-9a-zA-Z-_]+', '', Dataset.short_name)
            if sn not in iris:
                vfb_id = self.iri_base + sn
                print(vfb_id)
                q = "MATCH (n:Project {projectid:'%s'}) MERGE (n)<-[:has_associated_project]-(i:DataSet {iri:'%s', short_name:'%s', production: false" % (
                project, vfb_id, sn)
                if Dataset.source_data:
                    q = q + ", dataset_link: '%s'" % Dataset.source_data
                if Dataset.title:
                    q = q + ", label: '%s'" % Dataset.title
                if Dataset.publication:
                    print("Dataset publications are not currently supported")
                q = q + "})"
                print(q)
                self.query(q=q)
                return vfb_id
            else:
                raise DatasetWithSameNameExistsError(
                    "The shortname for this dataset (" + sn + ") has already been taken. Please use another one!")
        else:
            raise IllegalProjectError(
                'The project %s does not exist, or user with orcid %s does not have the required permissions. '
                'Please send an email to info@virtualflybrain.org to register your project.' % (project, Dataset.orcid))
        return id

    def create_neuron_db(self, Neuron, datasetid, orcid):
        pro = self.has_dataset_write_permission(datasetid, orcid)
        if pro:
            q = "MATCH (n:Dataset {projectid:'%s'})<-[:has_associated_project]-(i:Individual) RETURN i.iri" % project
            print(q)
            results = self.query(q=q)
            iri_base_project = self.iri_base + project
            iris = [base36.loads(x[0].replace(iri_base_project, "")) for x in results]
            if not iris:
                iris = [0]
            id = max(iris) + 1
            if id <= self.max_base36:
                id = base36.dumps(id)
                idstring = id.zfill(4)
                id = project + str(idstring)
                vfb_id = self.iri_base + id
                print(vfb_id)
                q = "MATCH (n:Project {projectid:'%s'}) MERGE (n)<-[:has_associated_project]-(i:Individual {iri:'%s', short_name:'VFB_%s', production: false" % (
                project, vfb_id, id)

                if Neuron.primary_name:
                    q = q + ", label: '%s'" % Neuron.primary_name
                if Neuron.external_identifiers:
                    ids = ','.join(Neuron.external_identifiers)
                    q = q + ", xrefs: '%s'" % ids
                if Neuron.alternative_names:
                    altids = ','.join(Neuron.alternative_names)
                    q = q + ", synonyms: '%s'" % altids
                if Neuron.type_specimen:
                    print("Neuron type specimens are not currently supported")
                if Neuron.template_id:
                    print("Templates are not currently supported")
                if Neuron.imaging_type:
                    print("Imaging types are not currently supported")
                if Neuron.url_skeleton_id:
                    print("Skeletons are not currently supported")
                q = q + "})"
                print(q)
                self.query(q=q)

                if Neuron.dataset_id:
                    q = "MATCH (n:Individual {iri:'%s'}) MATCH (d:DataSet {iri:'%s'}) MERGE (n)-[:has_reference]-(d)" % (
                    vfb_id, Neuron.dataset_id)
                    self.query(q=q)
                if Neuron.classification:
                    q = "MATCH (n:Individual {iri:'%s'}) MATCH (d:Class {iri:'%s'}) MERGE (n)-[:INSTANCEOF]-(d)" % (
                    vfb_id, Neuron.classification)
                    if Neuron.classification_comment:
                        comment = ":INSTANCEOF {comment: '%s'}" % Neuron.classification_comment
                        q = q.replace(":INSTANCEOF", comment)
                    self.query(q=q)
                return vfb_id
            else:
                raise IllegalProjectError(
                    "This projects (" + project + ") id space is exhausted. Please send an email to info@virtualflybrain.org to obtain a new one. ")
        else:
            raise IllegalProjectError(
                'The project %s does not exist, or user with ORCID %s does not have the required permissions. '
                'Please send an email to info@virtualflybrain.org to register your project.' % (project, Neuron.orcid))
        return id

    def create_project_db(self, Project):
        raise IllegalProjectError(
            'Creating projects is currently not supported.')


class IllegalProjectError(Exception):
    pass

class DatasetWithSameNameExistsError(Exception):
    pass

class ProjectIDSpaceExhaustedError(Exception):
    pass

class DatabaseNotInitialisedError(Exception):
    pass