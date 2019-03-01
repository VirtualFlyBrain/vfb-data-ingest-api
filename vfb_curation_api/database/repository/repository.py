from neo4jrestclient.client import GraphDatabase
import os

class VFBKB():
    def __init__(self):
        #os.environ["KBserver"] = "http://localhost:7474"
        #os.environ["KBuser"] = "neo4j"
        #os.environ["KBpassword"] = "neo4j/neo"
        self.kb = os.getenv('KBserver')
        self.user = os.getenv('KBuser')
        self.password = os.getenv('KBpassword')
        self.db = None

    def init_db(self):
        if not self.db:
            try:
                self.db = GraphDatabase(self.kb, username=self.user, password=self.password)
                self.prepare_database()
                return True
            except:
                print("Database could not be created.")
                return False
        else:
            return True

    def valid_project_and_permissions(self, project,orcid):
        q = "MATCH (n:Project {projectid:'%s'})<-[has_admin_permissions]-(a:Person {orcid: '%s'}) RETURN count(n)" % (project, orcid)
        print(q)
        results = self.query(q=q)
        return results[0][0] == 1

    def get_dataset(self, id):
        q = "MATCH (n:DataSet {iri:'%s'}) RETURN n.iri as vfbid, n.label as primary_name" % id
        print(q)
        results = self.db.query(q=q, data_contents=True)
        return results.rows


    def get_neuron(self, id):
        q = "MATCH (n:DataSet {iri:'%s'}) RETURN n.iri as vfbid, n.label as primary_name" % id
        print(q)
        results = self.query(q=q, data_contents=True)
        return results.rows

    def get_all_datasets(self):
        q = "MATCH (n:DataSet) RETURN n LIMIT 10"
        print(q)
        results = self.query(q=q, data_contents=True)
        return results.rows

    def get_all_neurons(self):
        q = "MATCH (n:Individual) RETURN n LIMIT 10"
        print(q)
        results = self.query(q=q, data_contents=True)
        return results.rows

    def query(self,q, data_contents=None):
        if self.init_db():
            return self.db.query(q,data_contents=data_contents)
        else:
            raise DatabaseNotInitialisedError("Database not initialised!")

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

class DatabaseNotInitialisedError(Exception):
    pass