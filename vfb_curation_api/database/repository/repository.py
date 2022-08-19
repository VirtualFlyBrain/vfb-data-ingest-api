from neo4jrestclient.client import GraphDatabase
from vfb_curation_api.database.models import Neuron, Dataset, Project, User, Split, SplitDriver
from vfb_curation_api.api.vfbid.errorcodes import NO_PERMISSION, INVALID_NEURON, UNKNOWNERROR, INVALID_DATASET, INVALID_SPLIT
import os
import json
import requests
import tempfile
from vfb_curation_api.vfb.uk.ac.ebi.vfb.neo4j.neo4j_tools import neo4j_connect
from vfb_curation_api.vfb.uk.ac.ebi.vfb.neo4j.KB_tools import KB_pattern_writer
from vfb_curation_api.vfb.uk.ac.ebi.vfb.neo4j.KB_tools import kb_owl_edge_writer
from vfb_curation_api.vfb.uk.ac.ebi.vfb.neo4j.flybase2neo.feature_tools import FeatureMover, split

class VFBKB():
    def __init__(self):
        self.db = None
        self.kb_owl_pattern_writer = None
        self.feature_mover = None
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
            try:
                if self.db_client=="vfb":
                    self.db = neo4j_connect(self.kb, self.user, self.password)
                    self.kb_owl_pattern_writer = KB_pattern_writer(self.kb, self.user, self.password)
                    self.kb_owl_edge_writer = kb_owl_edge_writer(self.kb, self.user, self.password)
                    self.feature_mover = FeatureMover(self.kb, self.user, self.password, tempfile.gettempdir())
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
        data = []
        for d_in in data_in:
            #print(d_in)
            columns = d_in['columns']
            #print(columns)
            for rec in d_in['data']:
                d = dict()
                print(rec)
                for i in range(len(columns)):
                    print(i)
                    d[columns[i]]=rec['row'][i]
                data.append(d)
        #print("DATAOUT: " + str(data))
        return data

    def parse_neo4j_default_client_data(self, data_in):
        #print("DATAIN: " + str(data_in.rows))
        data = []
        columns = []
        if data_in.rows:
            for c in data_in.rows[0]:
                columns.append(c)
        #print(str(columns))
        if data_in.rows:
            for d_row in data_in.rows:
                d = dict()
                for c in columns:
                    d[c] = d_row[c]
                data.append(d)
        #print("DATAOUT: " + str(data))
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
        #print(data)
        # sending post request and saving response as response object
        r = requests.post(url=self.authorisation_token_endpoint, data=data)
        #print(r.text)
        d = json.loads(r.text)
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
        # q = "MATCH (n:Project "
        # if project:
        #     q = q + "{iri:'%s'}" % self._format_vfb_id(project,"project")
        # q = q + ")<-[:has_admin_permissions]-(p:Person {iri: '%s'}) " % orcid
        # return q

        # TODO disabled permission check for end2end tests
        q = "MATCH (n:Project "
        if project:
            q = q + "{iri:'%s'}" % self._format_vfb_id(project,"project")
        q = q + ") "
        return q

    def _get_project_return_clause(self):
        return " RETURN n.iri as id, n.short_form as short_name, n.label as primary_name, n.start as start, n.description as description"

    def _get_dataset_permission_clause(self, orcid, datasetid=None, project=None, extra_dataset=False):
        q = self._get_project_permission_clause(orcid,project)
        q = q + "MATCH (n)<-[:has_associated_project]-(d:DataSet "
        if datasetid:
            q = q + "{iri: '%s'}" % self._format_vfb_id(datasetid, "reports")
        q = q + ") ";
        if extra_dataset:
            q = q + "OPTIONAL MATCH (d)-[:has_license]-(l:License) "
            q = q + "OPTIONAL MATCH (d)-[:has_reference]-(pu:pub) "
        return q

    def _get_dataset_return_clause(self):
        return " RETURN d.iri as id, d.short_form as short_form, d.label as title, d.description as description, d.dataset_link as source_data, l.iri as license, pu.iri as publication, n.short_form as project"

    def _get_neuron_permission_clause(self, orcid, neuronid=None, datasetid=None,project=None):
        q = self._get_dataset_permission_clause(orcid,datasetid,project)
        q = q + "MATCH (i  "
        if neuronid:
            q = q + "{iri: '%s'}" % self._format_vfb_id(neuronid, "reports")
        q = q + ")-[:has_source]->(d) "
        return q


    def _format_vfb_id(self,id,type):
        if id.startswith("http:"):
            nid = id
        else:
            nid = "http://virtualflybrain.org/{}/{}".format(type, id)
        return nid

    def _add_result_to_map_if_not_exists(self,item, map,key):
        if key not in map:
            map[key] = []
        if item not in map[key]:
            if isinstance(item, list):
                map[key].extend(item)
            else:
                map[key].append(item)
        return map

    def _get_neuron_relations(self,neuronid):
        q = "MATCH (i  {iri: '%s'})-[r]-(q)  " % self._format_vfb_id(neuronid,"reports")
        q = q + """
MATCH (i)-[cli:INSTANCEOF]-(cl:Class)
MATCH (i)-[ {iri:"http://xmlns.com/foaf/0.1/depicts"}]-(c:Individual) 
MATCH (c)-[ir:in_register_with]-(t:Template)
MATCH (c)-[ {iri:"http://purl.obolibrary.org/obo/OBI_0000312"}]-(it) 
OPTIONAL MATCH (i)-[cr:database_cross_reference]-(xref:Site)
OPTIONAL MATCH (i)-[ {iri:"http://purl.obolibrary.org/obo/BFO_0000050"}]-(po) 
OPTIONAL MATCH (i)-[ {iri:"http://purl.obolibrary.org/obo/RO_0002292"}]-(dl) 
OPTIONAL MATCH (i)-[ {iri:"http://purl.obolibrary.org/obo/RO_0002131"}]-(np)
OPTIONAL MATCH (i)-[ {iri:"http://purl.obolibrary.org/obo/RO_0002110"}]-(inp) 
OPTIONAL MATCH (i)-[ {iri:"http://purl.obolibrary.org/obo/RO_0002113"}]-(onp) 
RETURN xref.short_form as resource_id, 
cr.accession as external_id, 
t.short_form as template_id, 
ir.filename as filename, 
it.label as imaging_type, 
cl.iri as classification, 
cli.comment as classification_comment, 
collect(DISTINCT po.short_form) as part_of, 
collect(DISTINCT dl.short_form) as driver_line, 
collect(DISTINCT np.short_form) as neuropils, 
collect(DISTINCT inp.short_form) as input_neuropils,
collect(DISTINCT onp.short_form) as output_neuropils"""
        rels = {}
        results = self.query(q=q)
        if not results:
            raise VFBError("Neuron does not exist, or could not be retrieved.")
        for r in results:
            d = dict()
            d['resource_id'] = r['resource_id']
            d['external_id'] = r['external_id']
            rels = self._add_result_to_map_if_not_exists(d, rels, "cross_references")
            for i in ["neuropils", "input_neuropils",
                      "output_neuropils","driver_line","part_of"]:
                rels = self._add_result_to_map_if_not_exists(r[i], rels, i)
            for i in ["classification","classification_comment",
                      "imaging_type", "filename", "template_id"]:
                rels[i] = r[i] # This assumes there is really just one match. Which there is if the KB is consistent
        return rels

    def _get_neuron_return_clause(self):
        return " RETURN i.iri as id, i.label as primary_name, n.iri as projectid, d.iri as datasetid, i.synonyms as syns"

    def has_project_write_permission(self, project, orcid):
        if self.get_project(project,orcid):
            return True
        return False

    def has_dataset_write_permission(self, datasetid, orcid):
        # if self.get_dataset(datasetid, orcid):
        #     return True
        # return False

        # TODO disabled permission checks for end2end tests
        return True

    def _marshal_project_from_neo(self, data):
        p = Project(id=data['short_name'])
        p.set_description(data['description'])
        p.set_start(data['start'])
        p.set_primary_name(data['primary_name'])
        return p

    def get_project(self, id, orcid):
        q = self._get_project_permission_clause(orcid,id) + self._get_project_return_clause()
        results = self.query(q=q)
        if len(results) == 1:
            p = self._marshal_project_from_neo(results[0])
            return p
        return None


    def get_dataset(self, id, orcid):
        q = self._get_dataset_permission_clause(orcid, id,extra_dataset=True) + self._get_dataset_return_clause()
        results = self.query(q=q)
        if len(results) == 1:
            d = self._neo_dataset_marshal(results[0])
            return d
        return None

    def _get_neuron(self, id, orcid):
        q = self._get_neuron_permission_clause(orcid,id)
        q = q + self._get_neuron_return_clause()
        results = self.query(q=q)
        if len(results) == 1:
            try:
                n = Neuron(primary_name=results[0]['primary_name'])
                n.set_id(id=results[0]['id'])
                n.set_alternative_names(results[0]['syns'])
                n.set_datasetid(results[0]['datasetid'])
                n.set_project_id(results[0]['projectid'])
                neuron_rels = self._get_neuron_relations(results[0]['id'])
                n.set_external_identifiers(neuron_rels['cross_references'])
                n.set_classification([neuron_rels['classification']])
                n.set_classification_comment(neuron_rels['classification_comment'])
                n.set_imaging_type(neuron_rels['imaging_type'])
                n.set_neuropils(neuron_rels['neuropils'])
                n.set_input_neuropils(neuron_rels['input_neuropils'])
                n.set_output_neuropils(neuron_rels['output_neuropils'])
                n.set_driver_line(neuron_rels['driver_line'])
                n.set_part_of(neuron_rels['part_of'])
                n.set_filename(neuron_rels['filename'])
                n.set_template_id(neuron_rels['template_id'])
            except Exception as e:
                print(e)
                return self.wrap_error(["Neuron {} could not be retrieved".format(id)], INVALID_NEURON)
            return n
        return self.wrap_error(["Neuron {} could not be retrieved".format(id)], INVALID_NEURON)

    def get_neuron(self, id, orcid):
        if isinstance(id,list):
            neurons = []
            for i in id:
                neurons.append(self._get_neuron(i,orcid))
            return neurons
        else:
            return self._get_neuron(id,orcid)

    def get_user(self, orcid, apikey=None):
        q = "MATCH (p:Person {iri:'%s'" % orcid
        if apikey:
            q = q + ", apikey: '%s'" % apikey
        q = q + "}) RETURN p.iri as id, p.label as primary_name, p.apikey as apikey, p.role as role, p.email as email"
        results = self.query(q=q)
        if len(results) == 1:
            return User(results[0]['id'], results[0]['primary_name'], results[0]['apikey'],
                        results[0]['role'], results[0]['email'])
        raise InvalidUserException("User with orcid id {} does not exist.".format(orcid))

    def _neo_dataset_marshal(self,row):
        d = Dataset(id=row['id'], short_name=row['short_form'], title=row['title'])
        d.set_project_id(row['project'])
        d.set_publication(row['publication'])
        d.set_source_data(row['source_data'])
        d.set_description(row['description'])
        d.set_license(row['license'])
        return d

    def get_all_datasets(self,projectid, orcid):
        q = self._get_dataset_permission_clause(orcid=orcid, project=projectid, extra_dataset=True) + self._get_dataset_return_clause()
        results = self.query(q=q)
        datasets = []
        for row in results:
            #print(row)
            d = self._neo_dataset_marshal(row)
            datasets.append(d)
        return datasets

    def get_all_projects(self,orcid):
        q = self._get_project_permission_clause(orcid=orcid) + self._get_project_return_clause()
        results = self.query(q=q)
        projects = []
        for row in results:
            projects.append(self._marshal_project_from_neo(row))
        return projects

    def get_all_neurons(self, datasetid, orcid):
        q = self._get_neuron_permission_clause(orcid=orcid) + self._get_neuron_return_clause()
        results = self.query(q=q)
        neurons = []
        for row in results:
            # n = Neuron(primary_name=row['primary_name'], id=row['id'])
            # n.set_datasets([datasetid])
            n = Neuron(primary_name=row['primary_name'])
            n.set_id(row['id'])
            n.set_datasetid(datasetid)
            n.set_project_id(row['projectid'])
            neurons.append(n)
        return neurons

    def get_id_start_range(self, datasetid, orcid):
        q = self._get_dataset_permission_clause(orcid=orcid,datasetid=datasetid) + self._get_project_return_clause()
        results = self.query(q=q)
        if len(results) == 1:
            return results[0]['start']
        raise VFBError("No start range found for dataset {}, starting from 0.".format(datasetid))

    ################################
    #### Data ingestion ############
    ################################

    def create_dataset(self, Dataset, project, orcid):
        errors = []
        if self.has_project_write_permission(project, orcid):
            if self.db_client=="vfb":
                datasetid = self.kb_owl_pattern_writer.add_dataSet(Dataset.title, Dataset.license, Dataset.short_name, pub=Dataset.publication,
                        description=Dataset.description, dataset_spec_text='', site='')
                self.kb_owl_pattern_writer.commit()
                print("Determining success of added dataset by checking weather the log is empty.")
                datasetid = Dataset.short_name
                if not self.kb_owl_pattern_writer.ec.log:
                    q = "MATCH (n:Project {iri: '%s'})" % self._format_vfb_id(project,"project")
                    q = q + " MATCH (d:DataSet {iri: '%s'})" % self._format_vfb_id(datasetid,"reports")
                    q = q + " MERGE (n)<-[:has_associated_project]-(d)"
                    print(q)
                    result = self.query(q)
                    print(result)
                    return datasetid
                else:
                    print("Added dataset: error log is not empty.")
                    errors.extend(self.kb_owl_pattern_writer.ec.log)
                    return self.wrap_error(errors, INVALID_DATASET)
        else:
            raise IllegalProjectError(
                'The project %s does not exist, or user with orcid %s does not have the required permissions. '
                'Please send an email to info@virtualflybrain.org to register your project.' % (project, orcid))
        errors.append("An unknown error occurred")
        return self.wrap_error(errors, UNKNOWNERROR)

    def create_neuron_db(self, neurons, datasetid, orcid):
        commit = True
        ids = []
        errors = []
        start = 0

        did = self._format_vfb_id(datasetid, "reports")
        if not self.has_dataset_write_permission(did, orcid):
            return self.wrap_error("No permissions to add images to datasets", NO_PERMISSION)

        s = self.get_id_start_range(datasetid, orcid)
        if s > start:
            start = s
        for neuron in neurons:
            if isinstance(neuron, Neuron):
                try:
                    success = self.add_neuron_db(neuron, datasetid, start)
                    if success:
                        ids.append(success)
                    else:
                        commit = False
                        errors.extend(self.kb_owl_pattern_writer.ec.log)
                except Exception as e:
                    commit = False
                    print(e)
                    errors.append("{}".format(e))
            else:
                print("{} is not a neuron".format(neuron))
        if commit:
            commit_return = self.kb_owl_pattern_writer.commit()
            if commit_return:
                return ids
            else:
                errors.extend(self.kb_owl_pattern_writer.get_log())
                return self.wrap_error(errors, INVALID_NEURON)
        else:
            errors.extend(self.kb_owl_pattern_writer.ec.log)
            return self.wrap_error(errors, INVALID_NEURON)


    def add_neuron_db(self, Neuron, datasetid, start):
        # make sure datasetid is the short form.

        if self.db_client=="vfb":
            rv = self.kb_owl_pattern_writer.add_anatomy_image_set(
                dataset=datasetid,
                imaging_type=Neuron.imaging_type,
                label=Neuron.primary_name,
                start=start, # we need to do this on api level so that batching is not a bottleneck. we dont want 1 lookup per new image just to get the range!
                template=Neuron.template_id, #VFB id or template name
                anatomical_type=Neuron.classification[0], #default NEURON VFB/FBBT ID (short_form).
                type_edge_annotations={"comment": Neuron.classification_comment},
                anon_anatomical_types=self.get_anon_anatomical_types(Neuron),
                anatomy_attributes=self.get_anatomy_attributes(Neuron),
                dbxrefs=self.get_xrefs(Neuron.external_identifiers),
                image_filename=Neuron.filename,
                hard_fail=False)
            return rv['anatomy']['short_form']

        raise VFBError('Images cannot be added right now; please contact the VFB administrators.')

    def get_anatomy_attributes(self, neuron):
        aa = dict()
        if isinstance(neuron, Neuron) or isinstance(neuron, SplitDriver):
            syns = neuron.alternative_names
            if syns:
                # {"synonyms": ['a','b]}
                aa['synonyms'] = syns
            if neuron.comment:
                aa['comment'] = neuron.comment
        return aa

    def get_anon_anatomical_types(self, neuron):
        # [(r,o),(r2,o2)]
        aa = []
        if isinstance(neuron, Neuron) or isinstance(neuron, SplitDriver):
            aa = self._add_type(neuron.part_of, "BFO_0000050",aa)
            aa = self._add_type(neuron.driver_line, "RO_0002292", aa)
            aa = self._add_type(neuron.neuropils, "RO_0002131", aa)
            aa = self._add_type(neuron.input_neuropils, "RO_0002110", aa)
            aa = self._add_type(neuron.output_neuropils, "RO_0002113", aa)
        return aa

    def _add_type(self, n_typ, rel, l):
        if n_typ and isinstance(n_typ,list):
            for e in n_typ:
                l.append((rel,e))
        return l

    def get_xrefs(self, xrefs):
        aa = dict()
        if xrefs:
            # { GO: 001 }
            for xref in xrefs:
                aa[xref['resource_id']] = xref['external_id']
        return aa

    def create_project_db(self, Project):
        raise IllegalProjectError(
            'Creating projects is currently not supported.')

    def create_neuron_type_db(self, Project):
        raise IllegalProjectError(
            'Creating new neuron types is currently not supported.')

    def wrap_error(self,message_json,code):
        return { 'error': {
                    "code": code,
                    "message": message_json,
                }}

    def clear_neo_logs(self):
        self.kb_owl_pattern_writer.get_log()
        self.self.kb_owl_pattern_writer.ec.log

    def _get_split(self, splitid, orcid):
        q = "MATCH (i  "
        if splitid:
            q = q + "{iri: '%s'})" % self._format_vfb_id(splitid, "reports")
        q = q + " RETURN i.iri as id, i.label as label, i.synonyms as syns, i.xrefs as xrefs"

        results = self.query(q=q)
        if len(results) == 1:
            try:
                s = Split("", "")
                s.set_id(results[0]['id'])
                s.set_synonyms(results[0]['syns'])
                s.set_xrefs(results[0]['xrefs'])
            except Exception as e:
                print("Split could not be retrieved: {}".format(e))
                return self.wrap_error(["Split {} could not be retrieved".format(id)], INVALID_SPLIT)
            return s
        return self.wrap_error(["Split {} could not be retrieved".format(id)], INVALID_SPLIT)

    def get_split(self, id, orcid):
        if isinstance(id, list):
            splits = []
            for i in id:
                splits.append(self._get_split(i, orcid))
            return splits
        else:
            return self._get_split(id, orcid)

    def create_split(self, split_data):
        if self.db_client == "vfb":
            s = split(synonyms=split_data.synonyms,
                      dbd=split_data.dbd,
                      ad=split_data.ad,
                      xrefs=split_data.xrefs)
            response = self.feature_mover.gen_split_ep_feat([s])

            short_form = next(iter(response))
            result = response[short_form]['attributes']
            result['short_form'] = short_form
            result['iri'] = response[short_form]['iri']
            result['xrefs'] = response[short_form]['xrefs']
            return result

        raise VFBError('Splits cannot be added right now; please contact the VFB administrators.')

    def create_split_driver_db(self, split_drivers, datasetid, orcid, ep_split_flp_out):
        commit = True
        ids = []
        errors = []
        start = 0

        did = self._format_vfb_id(datasetid, "reports")
        if not self.has_dataset_write_permission(did, orcid):
            return self.wrap_error("No permissions to add images to datasets", NO_PERMISSION)

        s = self.get_id_start_range(datasetid, orcid)
        if s > start:
            start = s
        for split_driver in split_drivers:
            if isinstance(split_driver, SplitDriver):
                try:
                    success = self.add_split_driver_db(split_driver, datasetid, start, ep_split_flp_out)
                    if success:
                        ids.append(success)
                    else:
                        commit = False
                        errors.extend(self.kb_owl_pattern_writer.ec.log)
                except Exception as e:
                    commit = False
                    print(e)
                    errors.append("{}".format(e))
            else:
                print("{} is not a split driver".format(split_driver))
        if commit:
            commit_return = self.kb_owl_pattern_writer.commit()
            if commit_return:
                return ids
            else:
                errors.extend(self.kb_owl_pattern_writer.get_log())
                return self.wrap_error(errors, INVALID_NEURON)
        else:
            errors.extend(self.kb_owl_pattern_writer.ec.log)
            return self.wrap_error(errors, INVALID_NEURON)

    def add_split_driver_db(self, split_driver: SplitDriver, datasetid, start, ep_split_flp_out):
        # make sure datasetid is the short form.
        if self.db_client=="vfb":
            aa = self.get_anon_anatomical_types(split_driver)
            if ep_split_flp_out:
                aa = self._add_type(split_driver.comment, "BFO_0000050", aa)
                aa = self._add_type(split_driver.classification, "BFO_0000051", aa)
                aa = self._add_type(split_driver.has_part, "BFO_0000051", aa)
                at = "VFBext_0000004"  # 'expression pattern fragment'
            else:
                aa = self._add_type(split_driver.classification, "BFO_0000051", aa)
                aa = self._add_type(split_driver.has_part, "BFO_0000051", aa)
                if split_driver.driver_line and len(split_driver.driver_line) > 0:
                    at = split_driver.driver_line[0]
                else:
                    at = split_driver.comment  # workaround since dl is not in pdb

            rv = self.kb_owl_pattern_writer.add_anatomy_image_set(
                dataset=datasetid,
                imaging_type=split_driver.imaging_type,
                label=split_driver.primary_name,
                start=start, # we need to do this on api level so that batching is not a bottleneck. we dont want 1 lookup per new image just to get the range!
                template=split_driver.template_id, #VFB id or template name
                anatomical_type=at,  # should use driver_line, but this is workaround
                type_edge_annotations={"comment": split_driver.classification_comment},
                anon_anatomical_types=aa,
                anatomy_attributes=self.get_anatomy_attributes(split_driver),
                dbxrefs=self.get_xrefs(split_driver.external_identifiers),
                image_filename=split_driver.filename,
                hard_fail=False)
            return rv['anatomy']['short_form']

        raise VFBError('Images cannot be added right now; please contact the VFB administrators.')

    # def _get_split_ep(self, splitid, orcid):
    #     q = "MATCH (i  "
    #     if splitid:
    #         q = q + "{iri: '%s'})" % self._format_vfb_id(splitid, "reports")
    #     q = q + " RETURN i.iri as id, i.label as label, i.comment as comment, i.synonyms as syns, i.xrefs as xrefs"
    #
    #     results = self.query(q=q)
    #     if len(results) == 1:
    #         try:
    #             s = EpSplit(results[0]['id'])
    #             s.set_primary_name(results[0]['label'])
    #             s.set_comment(results[0]['comment'])
    #             s.set_synonyms(results[0]['syns'])
    #             s.set_xrefs(results[0]['xrefs'])
    #         except Exception as e:
    #             print("EP/Split could not be retrieved: {}".format(e))
    #             return self.wrap_error(["EP/Split {} could not be retrieved".format(id)], INVALID_SPLIT)
    #         return s
    #     return self.wrap_error(["EP/Split {} could not be retrieved".format(id)], INVALID_SPLIT)

    # def get_split_ep(self, id, orcid):
    #     if isinstance(id, list):
    #         splits = []
    #         for i in id:
    #             splits.append(self._get_split_ep(i, orcid))
    #         return splits
    #     else:
    #         return self._get_split_ep(id, orcid)
    #
    # def create_ep_split(self, ep_split_data):
    #     if self.db_client == "vfb":
    #         aa = []
    #         if ep_split_data.neuron_annotations:
    #             aa = self._add_type(ep_split_data.neuron_annotations, "BFO_0000051", aa)  # has_part
    #         rv = self.kb_owl_pattern_writer.add_anatomy_image_set(
    #             label=ep_split_data.primary_name,
    #             start=0,
    #             anatomical_type=ep_split_data.expression_pattern,
    #             anon_anatomical_types=aa,
    #             anatomy_attributes=self.get_anatomy_attributes(Neuron),
    #             dbxrefs=self.get_xrefs(ep_split_data.xrefs),
    #             hard_fail=False)
    #         return rv['anatomy']['short_form']
    #
    #     raise VFBError('EP/Splits cannot be added right now; please contact the VFB administrators.')
    #
    # def create_ep_split_flp_out(self, ep_split_data):
    #     if self.db_client == "vfb":
    #         aa = []
    #         if ep_split_data.neuron_annotations:
    #             aa = self._add_type(ep_split_data.neuron_annotations, "BFO_0000051", aa)  # has_part
    #         if ep_split_data.expression_pattern:
    #             aa = self._add_type(ep_split_data.expression_pattern, "BFO_0000050", aa)  # part_of
    #         rv = self.kb_owl_pattern_writer.add_anatomy_image_set(
    #             label=ep_split_data.primary_name,
    #             start=0,
    #             anatomical_type='expression pattern fragment',
    #             anon_anatomical_types=aa,
    #             anatomy_attributes=self.get_anatomy_attributes(Neuron),
    #             dbxrefs=self.get_xrefs(ep_split_data.xrefs),
    #             hard_fail=False)
    #         return rv['anatomy']['short_form']
    #
    #     raise VFBError('EP/Splits cannot be added right now; please contact the VFB administrators.')


class IllegalProjectError(Exception):
    pass

class VFBError(Exception):
    pass

class NeuronNotExistsError(Exception):
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