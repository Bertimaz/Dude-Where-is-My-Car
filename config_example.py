import os

SECRET_KEY= ''

SQLALCHEMY_DATABASE_URI = \
'{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
    SGBD = 'mysql+mysqlconnector',
    usuario = '',
    senha = '',
    servidor = '',
    database = ''
)


GOOGLEMAPS_API_KEY=""
a