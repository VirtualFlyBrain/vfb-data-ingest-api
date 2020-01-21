import logging
import traceback

from flask_restplus import Api
from vfb_curation_api import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API'
    },
    'oauth2': {
        'type': 'oauth2',
        'flow': 'accessCode',
        'tokenUrl': 'https://orcid.org/oauth/token',
        'authorizationUrl': 'https://orcid.org/oauth/authorize',
        'redirect_uri' : 'http://localhost:5000/api',
        'scopes': {
            '/authenticate': 'No API call. Client retrieves access token only.',
        }
    }
}

api = Api(version='1.0', title='VFB Identifier API',
          description='An API for creating and updating VFB identifiers.', authorizations=authorizations)



@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    log.warning(traceback.format_exc())
    return {'message': 'A database result was required but none was found.'}, 404
