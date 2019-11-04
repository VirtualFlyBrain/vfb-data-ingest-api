MERGE (n:Project {projectid:'ABCD'})
MERGE (n:Project {projectid:'DCBA'})
MERGE (n:Person {orcid:'1234'})
MERGE (n:Person {orcid:'4321'})

MATCH (n:Project {projectid:'ABCD'})
MERGE (n)<-[:has_admin_permissions]-(a:Person {orcid: '1234'})
MATCH (n:Project {projectid:'DCBA'})
MERGE (n)<-[:has_admin_permissions]-(a:Person {orcid: '4321'})

MATCH (n:Project {projectid:'ABCD'})
MERGE (n)<-[:has_associated_project]-(i:DataSet {iri:'http://virtualflybrain.org/data/Zoglu2020', short_name:'Zoglu2020', production: false})
MERGE (n)<-[:has_associated_project]-(i:DataSet {iri:'http://virtualflybrain.org/data/Zoglu2030', short_name:'Zoglu2030', production: false})
MERGE (n)<-[:has_associated_project]-(i:DataSet {iri:'http://virtualflybrain.org/data/Zoglu2040', short_name:'Zoglu2040', production: false})

MATCH (n:Project {projectid:'DCBA'})
MERGE (n)<-[:has_associated_project]-(i:DataSet {iri:'http://virtualflybrain.org/data/Dos2020', short_name:'Dos2020', production: false})
MERGE (n)<-[:has_associated_project]-(i:Individual {iri:'http://virtualflybrain.org/reports/VFB_0000DCBA', short_name:'VFB_0000DCBA', production: false})

MATCH (n:Project {projectid:'ABCD'})
MERGE (n)<-[:has_associated_project]-(i:Individual {iri:'http://virtualflybrain.org/reports/VFB_0000ABCD', short_name:'VFB_0000ABCD', production: false})
MERGE (n)<-[:has_associated_project]-(i:Individual {iri:'http://virtualflybrain.org/reports/VFB_0001ABCD', short_name:'VFB_0001ABCD', production: false})
MERGE (n)<-[:has_associated_project]-(i:Individual {iri:'http://virtualflybrain.org/reports/VFB_0002ABCD', short_name:'VFB_0002ABCD', production: false})


MATCH (n:Individual {iri:'http://virtualflybrain.org/reports/VFB_0000ABCD'})
MATCH (d:DataSet {iri:'http://virtualflybrain.org/data/Zoglu2020'})
MERGE (n)-[:has_reference]-(d)
MATCH (n:Individual {iri:'http://virtualflybrain.org/reports/VFB_0001ABCD'})
MATCH (d:DataSet {iri:'http://virtualflybrain.org/data/Zoglu2020'})
MERGE (n)-[:has_reference]-(d)
MATCH (n:Individual {iri:'http://virtualflybrain.org/reports/VFB_0002ABCD'})
MATCH (d:DataSet {iri:'http://virtualflybrain.org/data/Zoglu2020'})
MERGE (n)-[:has_reference]-(d)

MATCH (n:Individual {iri:'http://virtualflybrain.org/reports/VFB_0000DCBA'})
MATCH (d:DataSet {iri:'http://virtualflybrain.org/data/Dos2020'})
MERGE (n)-[:has_reference]-(d)

