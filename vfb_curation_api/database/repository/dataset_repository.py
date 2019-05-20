from vfb_curation_api.database.repository.repository import IllegalProjectError, DatasetWithSameNameExistsError
from vfb_curation_api.database.repository import db
import re

iri_base = "http://virtualflybrain.org/data/"


def create_dataset_db(Dataset):
    project = str.upper(Dataset.project)
    if db.valid_project_and_permissions(project, Dataset.orcid):
        q = "MATCH (n:Project {projectid:'%s'})<-[:has_associated_project]-(i:DataSet) RETURN i.iri" % project
        print(q)
        results = db.query(q=q)
        iris = [x[0].replace(iri_base,"") for x in results]
        sn = re.sub('[^0-9a-zA-Z-_]+', '', Dataset.short_name)
        if sn not in iris:
            vfb_id = iri_base + sn
            print(vfb_id)
            q = "MATCH (n:Project {projectid:'%s'}) MERGE (n)<-[:has_associated_project]-(i:DataSet {iri:'%s', short_name:'%s', production: false" % (project,vfb_id, sn)
            if Dataset.source_data:
                q = q+ ", dataset_link: '%s'" % Dataset.source_data
            if Dataset.title:
                q = q+ ", label: '%s'" % Dataset.title
            if Dataset.publication:
                print("Dataset publications are not currently supported")
            q = q + "})"
            print(q)
            db.query(q=q)
            return vfb_id
        else:
            raise DatasetWithSameNameExistsError("The shortname for this dataset ("+sn+") has already been taken. Please use another one!")
    else:
        raise IllegalProjectError('The project %s does not exist, or user with orcid %s does not have the required permissions. '
                                  'Please send an email to info@virtualflybrain.org to register your project.' % (project,Dataset.orcid))
    return id

