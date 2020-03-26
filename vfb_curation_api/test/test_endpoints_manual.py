import os
import requests
import json
import re

# This run of tests is only necessary in absence of a proper testing system which I dont have yet



# api-endpoint
api = "http://localhost:5000/api"

params=dict()
params['orcid']="https://orcid.org/0000-0002-7356-1779"
params['apikey']="xyz"


print("Running endpoint tests")
for file in os.listdir('data'):
    if file.endswith(".json") and file.startswith("payload"):
        # sending get request and saving the response as response object
        with open('data/{}'.format(file)) as f:
            data = json.load(f)
        correct_answer_f = file.replace("payload_","answer_")
        with open('data/{}'.format(correct_answer_f)) as f:
            answer = json.load(f)
        endpoint=file.split("_")[1]
        r = requests.post(url="{}/{}/".format(api,endpoint), json=data,params=params)

        # extracting data in json format
        replacethis = "http[:][/][/]virtualflybrain[.]org[/]reports[/]VFB[_][0-9]+"
        data = r.json()
        data_s = json.dumps(data).strip()
        data_s = re.sub(replacethis, "IRI", data_s)
        answer_s = json.dumps(answer).strip()
        answer_s = re.sub(replacethis, "IRI", answer_s)
        if str(data_s) == str(answer_s):
            print("Test {} passed.".format(file))
        else:
            print("Test {} FAILED.".format(file))
            print(data_s)
            print(answer_s)

print("Testing get user endpoint")
r = requests.get(url="{}/{}/".format(api,"user"), params=params)
data = r.json()
assert data['orcid'] == "https://orcid.org/0000-0002-7356-1779"
assert data['apikey'] == "xyz"
assert 'primary_name' in data
assert 'manages_projects' in data

print("Testing get all projects endpoint")
r = requests.get(url="{}/{}/".format(api,"projects"), params=params)
data = r.json()
assert 'primary_name' in data[0]
assert 'id' in data[0]
assert 'description' in data[0]
assert 'start' in data[0]

print("Testing get project endpoint")
params['projectid'] = "ABCD"
r = requests.get(url="{}/{}/".format(api,"project"), params=params)
data = r.json()
assert 'primary_name' in data
assert data['id'] == "ABCD"
assert 'description' in data
assert 'start' in data

print("Testing get neuron endpoint")
params['neuronid'] = "http://virtualflybrain.org/reports/VFB_0000ABCD"
r = requests.get(url="{}/{}/".format(api,"neuron"), params=params)
data = r.json()
assert 'error' in data




#[{"id": "http://virtualflybrain.org/reports/VFB_00005975", "primary_name": "Neuron XYZ superspaced", "datasetid": "http://virtualflybrain.org/data/Zoglu2020", "projectid": "http://virtualflybrain.org/project/ABCD", "alternative_names": ["Neuron XYZ superspac", "Neuron XY-Z sspac"], "external_identifiers": [{"resource_id": "FlyBrain_NDB", "external_id": "12"}, {"resource_id": "FlyBase", "external_id": "1"}], "classification": "http://purl.obolibrary.org/obo/FBbt_00005106", "classification_comment": null, "template_id": "VFB_00017894", "imaging_type": "computer graphic", "filename": "test1.png", "driver_line": [], "neuropils": [], "part_of": [], "input_neuropils": [], "output_neuropils": []}]