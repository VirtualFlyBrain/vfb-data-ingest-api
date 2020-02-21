from neo4jrestclient.client import GraphDatabase
from vfb_curation_api.database.models import Neuron, Dataset, Project, User
import os
import re
import base36
import json
import requests
from vfb_curation_api.vfb.uk.ac.ebi.vfb.neo4j.neo4j_tools import neo4j_connect

class VFBKB():
    def __init__(self):
        self.iri_base = "http://virtualflybrain.org/data/"
        self.db = None
        self.iri_base = "http://virtualflybrain.org/reports/VFB_"
        self.max_base36 = 1679615  # Corresponds to the base36 value of ZZZZZZ
        self.db_client = "vfb"
        self.client_id = os.environ['CLIENT_ID_AUTHORISATION']
        self.client_secret = os.environ['CLIENT_SECRET_AUTHORISATION']
        self.redirect_uri = os.environ['REDIRECT_URI_AUTHORISATION']
        self.authorisation_token_endpoint = os.environ['ENDPOINT_AUTHORISATION_TOKEN']


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
            print(d_in)
            columns = d_in['columns']
            print(columns)
            for rec in d_in['data']:
                d = dict()
                print(rec)
                for i in range(len(columns)):
                    print(i)
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

    def authenticate(self, code, redirect_uri):
        data = {'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'authorization_code',
                'code': "{}".format(code),
                'redirect_uri': redirect_uri }
        print(data)
        # sending post request and saving response as response object
        r = requests.post(url=self.authorisation_token_endpoint, data=data)
        print(r.text)
        d = json.loads(r.text)
        print(d['orcid'])
        # {"access_token","token_type","refresh_token","expires_in","scope","name":"Nicolas Matentzoglu","orcid":"0000-0002-7356-1779"}
        orcid = "https://orcid.org/{}".format(d['orcid'])
        return self.get_user(orcid)

    ################################
    #### Data retrieval ############
    ################################

    # Labels:
    # n: project
    # p: person
    # d: dataset
    # i: neuron


    def valid_user(self, apikey, orcid):
        if self.get_user(orcid, apikey):
            return True
        return False

    def _get_project_permission_clause(self, orcid, project=None):
        q = "MATCH (n:Project "
        if project:
            q = q + "{iri:'http://virtualflybrain.org/project/%s'}" % project
        q = q +")<-[:has_admin_permissions]-(p:Person {iri: '%s'}) " % orcid
        return q

    def _get_project_return_clause(self):
        return " RETURN n.iri as id"

    def _get_dataset_permission_clause(self, orcid, datasetid=None,project=None):
        q = self._get_project_permission_clause(orcid,project)
        q = q + "MATCH (n)<-[:has_associated_project]-(d:DataSet "
        if datasetid:
            q = q + "{iri: '%s'}" % datasetid
        q = q+ ") ";
        return q

    def _get_dataset_return_clause(self):
        return " RETURN d.iri as id, d.short_form as short_form, d.label as title"

    def _get_neuron_permission_clause(self, orcid, neuronid=None, datasetid=None,project=None):
        q = self._get_dataset_permission_clause(orcid,datasetid,project)
        q = q + "MATCH (i  "
        if neuronid:
            q = q + "{iri: '%s'}" % neuronid
        q = q+ ")-[:has_reference]->(d) "
        return q

    def _get_neuron_return_clause(self):
        return " RETURN i.iri as id, i.short_name as primary_name, n.iri as projectid"

    def has_project_write_permission(self, project, orcid):
        if self.get_project(project,orcid):
            return True
        return False

    def has_dataset_write_permission(self, datasetid, orcid):
        if self.get_dataset(datasetid, orcid):
            return True
        return False

    def get_project(self, id, orcid):
        q = self._get_project_permission_clause(orcid,id) + self._get_project_return_clause()
        results = self.query(q=q)
        if len(results) == 1:
            p = Project(id=results[0]['id'])
            return p
        return None


    def get_dataset(self, id, orcid):
        q = self._get_dataset_permission_clause(orcid, id) + self._get_dataset_return_clause()
        results = self.query(q=q)
        if len(results) == 1:
            d = Dataset(id=results[0]['id'], short_name=results[0]['short_form'], title=results[0]['title'])
            return d
        return None

    def get_neuron(self, id, orcid):
        q = self._get_neuron_permission_clause(orcid,id)
        q = q + " RETURN i.iri as id, i.short_name as primary_name, n.iri as projectid"
        results = self.query(q=q)
        if len(results) == 1:
            n = Neuron(id=results[0]['id'],primary_name=results[0]['primary_name'])
            return n
        return None

    def get_user(self, orcid, apikey=None):
        q = "MATCH (p:Person {iri:'%s'" % orcid
        if apikey:
            q = q + ", apikey: '%s'" % apikey
        q = q + "}) RETURN p.iri as id, p.label as primary_name, p.apikey as apikey"
        results = self.query(q=q)
        if len(results) == 1:
            print(results[0])
            return User(results[0]['id'], results[0]['primary_name'], results[0]['apikey'])
        raise InvalidUserException("User with orcid id {} does not exist.".format(orcid))


    def get_all_datasets(self,projectid, orcid):
        q = self._get_dataset_permission_clause(orcid=orcid, project=projectid) + self._get_dataset_return_clause()
        results = self.query(q=q)
        datasets = []
        for row in results:
            #print(row)
            datasets.append(Dataset(id=row['id'], short_name=row['short_form'], title=row['title']))
        return datasets

    def get_all_projects(self,orcid):
        q = self._get_project_permission_clause(orcid=orcid) + self._get_project_return_clause()
        results = self.query(q=q)
        projects = []
        for row in results:
            projects.append(Project(id=row['id']))
        return projects

    def get_all_neurons(self, datasetid, orcid):
        q = self._get_neuron_permission_clause(orcid=orcid) + self._get_neuron_return_clause()
        results = self.query(q=q)
        neurons = []
        for row in results:
            n = Neuron(primary_name=row['primary_name'], id=row['id'])
            n.set_datasets([datasetid])
            n.set_project_id(row['projectid'])
            neurons.append(n)
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
            q = "MATCH (n:Dataset {datasetid:'%s'})<-[:has_associated_project]-(i:Individual) RETURN i.iri" % datasetid
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

class InvalidUserException(Exception):
    def __init__(self, message):
        self.message = message