from vfb_curation_api.database import db
from vfb_curation_api.database.repository.repository import IllegalProjectError
import base36

iri_base = "http://virtualflybrain.org/reports/VFB_"
max_base36=1679615 #Corresponds to the base36 value of ZZZZZZ

def create_neuron_db(Neuron):
    project = str.upper(Neuron.project)
    pro = db.valid_project_and_permissions(project, Neuron.orcid)
    if pro:
        q = "MATCH (n:Project {projectid:'%s'})<-[:has_associated_project]-(i:Individual) RETURN i.iri" % project
        print(q)
        results = db.query(q=q)
        iri_base_project = iri_base + project
        iris = [base36.loads(x[0].replace(iri_base_project, "")) for x in results]
        if not iris:
            iris = [0]
        id = max(iris) + 1
        if id <= max_base36:
            idstring = f'{id:04}'
            id = project + str(idstring)
            vfb_id = iri_base + id
            print(vfb_id)
            q = "MATCH (n:Project {projectid:'%s'}) MERGE (n)<-[:has_associated_project]-(i:Individual {iri:'%s', short_name:'VFB_%s', production: false" % (project, vfb_id, id)

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
            db.query(q=q)

            if Neuron.dataset_id:
                q = "MATCH (n:Individual {iri:'%s'}) MATCH (d:DataSet {iri:'%s%'}) MERGE (n)-[:has_reference]-(d)" % (vfb_id, Neuron.dataset_id)
                db.query(q=q)
            if Neuron.classification:
                q = "MATCH (n:Individual {iri:'%s'}) MATCH (d:Class {iri:'%s'}) MERGE (n)-[:INSTANCEOF]-(d)" % (vfb_id, Neuron.classification)
                if Neuron.classification_comment:
                    comment = ":INSTANCEOF {comment: '%s'}" % Neuron.classification_comment
                    q = q.replace(":INSTANCEOF",comment)
                db.query(q=q)
            return vfb_id
        else:
            raise IllegalProjectError(
                "This projects (" + project + ") id space is exhausted. Please send an email to info@virtualflybrain.org to obtain a new one. ")
    else:
        raise IllegalProjectError(
            'The project %s does not exist, or user with orcid %s does not have the required permissions. '
            'Please send an email to info@virtualflybrain.org to register your project.' % (project, Neuron.orcid))
    return id