from neo4jrestclient.client import GraphDatabase
import os

class VFBKB():
    def __init__(self):
        #os.environ["KBserver"] = "http://localhost:7474"
        #os.environ["KBuser"] = "neo4j"
        #os.environ["KBpassword"] = "neo4j/neo"
        kb = os.getenv('KBserver')
        user = os.getenv('KBuser')
        password = os.getenv('KBpassword')

        self.db = GraphDatabase(kb, username=user, password=password)
        pass

    def valid_project_and_permissions(self, project,orcid):
        q = "MATCH (n:Project {projectid:'%s'})<-[has_admin_permissions]-(a:Person {orcid: '%s'}) RETURN count(n)" % (project, orcid)
        print(q)
        results = self.db.query(q=q)
        return results[0][0] == 1

    def get_dataset(self, id):
        q = "MATCH (n:DataSet {iri:'%s'}) RETURN n.iri as vfbid, n.label as primary_name" % id
        print(q)
        results = self.db.query(q=q, data_contents=True)
        return results.rows

    def get_neuron(self, id):
        q = "MATCH (n:DataSet {iri:'%s'}) RETURN n.iri as vfbid, n.label as primary_name" % id
        print(q)
        results = self.db.query(q=q, data_contents=True)
        return results.rows

    def get_all_datasets(self):
        q = "MATCH (n:DataSet) RETURN n LIMIT 10"
        print(q)
        results = self.db.query(q=q, data_contents=True)
        return results.rows

    def get_all_neurons(self):
        q = "MATCH (n:Individual) RETURN n LIMIT 10"
        print(q)
        results = self.db.query(q=q, data_contents=True)
        return results.rows

    def query(self,q):
        return self.db.query(q)

    def prepare_database(self):
        q_orcid_unique = "CREATE CONSTRAINT ON (a:Person) ASSERT a.orcid IS UNIQUE"
        q_projectid_unique = "CREATE CONSTRAINT ON (a:Project) ASSERT a.projectid IS UNIQUE"
        self.db.query(q_orcid_unique)
        self.db.query(q_projectid_unique)


class IllegalProjectError(Exception):
    pass

class DatasetWithSameNameExistsError(Exception):
    pass

class ProjectIDSpaceExhaustedError(Exception):
    pass