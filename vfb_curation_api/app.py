import logging.config

import os
from flask import Flask, Blueprint
from vfb_curation_api import settings
from vfb_curation_api.api.vfbid.endpoints.datasets import ns as datasets_namespace
from vfb_curation_api.api.vfbid.endpoints.dataset import ns as dataset_namespace
from vfb_curation_api.api.vfbid.endpoints.neurons import ns as neurons_namespace
from vfb_curation_api.api.vfbid.endpoints.neuron_type import ns as neuron_type_namespace
from vfb_curation_api.api.vfbid.endpoints.neuron import ns as neuron_namespace
from vfb_curation_api.api.vfbid.endpoints.project import ns as project_namespace
from vfb_curation_api.api.vfbid.endpoints.projects import ns as projects_namespace
from vfb_curation_api.api.vfbid.endpoints.login import ns as login_namespace
from vfb_curation_api.api.vfbid.endpoints.user import ns as user_namespace
from vfb_curation_api.api.vfbid.endpoints.split import ns as split_namespace
from vfb_curation_api.api.restplus import api

app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
    flask_app.config['LOAD_TEST_DATA'] = settings.LOAD_TEST_DATA


def initialize_app(flask_app):
    configure_app(flask_app)
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(login_namespace)
    api.add_namespace(user_namespace)
    api.add_namespace(projects_namespace)
    api.add_namespace(datasets_namespace)
    api.add_namespace(neurons_namespace)
    api.add_namespace(neuron_type_namespace)
    api.add_namespace(project_namespace)
    api.add_namespace(dataset_namespace)
    api.add_namespace(neuron_namespace)
    api.add_namespace(split_namespace)
    flask_app.register_blueprint(blueprint)


def main():
    initialize_app(app)
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(host='0.0.0.0', debug=settings.FLASK_DEBUG)


if __name__ == "__main__":
    main()
