import os
from vfb_curation_api.database.repository.repository import VFBKB
print("SETTTTTTIIINNNNG ENVIRONMENT PLEASE KILL ME.")
print("SETTTTTTIIINNNNG ENVIRONMENT PLEASE KILL ME.")
print("SETTTTTTIIINNNNG ENVIRONMENT PLEASE KILL ME.")
print("SETTTTTTIIINNNNG ENVIRONMENT PLEASE KILL ME.")
os.environ["KBserver"] = "http://localhost:7474"
os.environ["KBuser"] = "neo4j"
os.environ["KBpassword"] = "neo"
os.environ["LOAD_TEST_DATA"] = "True"
os.environ['CLIENT_ID_AUTHORISATION'] = "APP-ENQTIY7Z904S6O1W"
os.environ['CLIENT_SECRET_AUTHORISATION'] = "4ad3c8ae-2359-44c1-af6a-59c3ce50e3f6"
os.environ['REDIRECT_URI_AUTHORISATION'] = "http://localhost:8080/dataingest-ui/login"
os.environ['ENDPOINT_AUTHORISATION_TOKEN'] = "https://orcid.org/oauth/token"
db = VFBKB()