import json

#import pywhatkit

from carro_app import app
from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField, SelectField, PasswordField
from models import Users, UsersCars, Cars, Trips
import requests
import config
import pytz

from datetime import datetime
from models import Trips, Users, Cars, UsersCars, db
from sqlalchemy import text


def isLastTripOpen(carPlate):
    lastTrip = Trips.query.filter_by(carPlate=carPlate).order_by(Trips.initialTime.desc()).first()
    if (lastTrip.endAddress is None) and (lastTrip.endTime is None):
        return True
    return False


def retrieveTripsByDateAndCar(carPlate, date):
    pass
    # select *
    # from trips  WHERE
    # date(initialTime) = '2022-11-10'
    # and carPlate = 'FLI-4871'

    # sqlStatement=text()


class FormularioEscolheCarro(FlaskForm):
    name = SelectField(label='Escolha o carro')


class FormularioUsuarioCadastro(FlaskForm):
    name = StringField('Name',
                       [validators.data_required(message="Forneca o Nome do Usuário"),
                        validators.Length(min=1, max=20)])

    nickname = StringField('Nickname',
                           [validators.data_required(message="Forneca o Nickname do Usuário"),
                            validators.Length(min=1, max=15)])

    password = StringField('Password',
                           [validators.data_required(message="Forneça o nome do Usuário"),
                            validators.Length(min=1, max=20)])

    email = StringField('E-mail',
                        [validators.data_required(message="Forneça o E-Mail do Usuário"),
                         validators.Length(min=1, max=100)])

    login = SubmitField('Login')


class FormularioUsuarioLogin(FlaskForm):
    nickname = StringField('Nickname',
                           [validators.data_required(message="Forneca o Nickname do Usuário"),
                            validators.Length(min=1, max=15)])

    password = PasswordField('Password',
                             [validators.data_required(message="Forneça o nome do Usuário"),
                              validators.Length(min=1, max=20)])
    login = SubmitField('Login')


class getCar():
    def __init__(self, nickname):
        trip = Trips.query.filter_by(user_nickname=nickname).order_by(Trips.initialTime.desc()).first()
        user = Users.query.filter_by(nickname='Bertimaz').first()  # não ta achando usuario
        usersCars = UsersCars.query.filter_by(userNickname='Bertimaz')
        cars = []
        for usercar in usersCars:
            car = Cars.query.filter_by(plate=usercar.carPlate).first()
            cars.append(car)


class formInitializeTrip(FlaskForm):
    nickname = StringField('Nickname',
                           [validators.DataRequired(message="Forneca o Nickname do Usuário"),
                            validators.Length(min=1, max=15)])
    carPlate = StringField('Placa do Carro',
                           [validators.DataRequired(message="Placa do carro"),
                            validators.Length(min=1, max=10)])
    initialAddress = StringField('Endereço Inicial',
                                 [validators.DataRequired(message="Endereço Inicial"),
                                  validators.Length(min=1, max=100)])
    InitialTime = StringField('Horario de Partida',
                              [validators.DataRequired(message="Horario de Partida"),
                               validators.Length(min=1, max=50)])

    updateTrip = SubmitField('Iniciar Viagem')
    searchTrip = SubmitField('Buscar Viagem')


class formEndTrip(FlaskForm):
    nickname = StringField('Nickname',
                           [validators.DataRequired(message="Forneca o Nickname do Usuário"),
                            validators.Length(min=1, max=15)])
    carPlate = StringField('Placa do Carro',
                           [validators.DataRequired(message="Placa do carro"),
                            validators.Length(min=1, max=10)])
    initialAddress = StringField('Endereço Inicial',
                                 [validators.DataRequired(message="Endereço Inicial"),
                                  validators.Length(min=1, max=100)])
    InitialTime = StringField('Horario de Partida',
                              [validators.DataRequired(message="Horario de Partida"),
                               validators.Length(min=1, max=50)])

    updateTrip = SubmitField('Finalizar Viagem')


class formSearchTripByDate(FlaskForm):
    date = StringField('Data', [validators.data_required(message='Data')])
    searchTrip = SubmitField('Buscar Viagem')


class reverseGeocode():
    def __init__(self, lat, longitude):
        self.lat = lat
        self.longitude = longitude
        self.error = 0
        self.formattedAddress = ''
        base = "https://maps.googleapis.com/maps/api/geocode/json?"
        params = "latlng={lat},{lon}&key={API_KEY}".format(
            lat=self.lat,
            lon=self.longitude,
            API_KEY=config.GOOGLEMAPS_API_KEY
        )

        self.url = "{base}{params}".format(base=base, params=params)
        app.logger.info('Connecting to %s.' % self.url)

        try:
            self.response = requests.get(self.url)
            # Se resposta ok salva o endereço
            if self.response.json()['status'] == 'OK':
                app.logger.info('Connection to %s. Status: %s' % (self.url, self.response.json()['status']))
                #     do stuff
                try:
                    self.formattedAddress = str(self.response.json()['results'][0]['formatted_address'])
                except IndexError as e:
                    app.logger.warning('Formating Address Error: %s' % e)
                    self.error = 2
                    self.formattedAddress = 'error2'
                except:
                    app.logger.warning('Formating Address Error: Unknown Error')
                    self.error = 3
                    self.formattedAddress = 'error3'
            else:
                app.logger.warning('Google Api Connection Error. Error: %s', self.response.json()['status'])

        except requests.ConnectionError as e:
            self.error = 1
            self.formattedAddress = 'error1'
            app.logger.warning('Google Api Connection Error. %s', e)

        finally:
            try:
                self.response.close()
                app.logger.info('Connection to %s closed.' % self.url)
            except:
                pass

    def __str__(self):
        return self.formattedAddress


def isLogged(session):
    if 'nickname_usuario_logado' in session and session['nickname_usuario_logado'] is not None:
        return True
    else:
        return False


def endTrip(timeZoneName, carplate, endAddress):
    # Configura Timezone
    currentTz = pytz.timezone(timeZoneName)
    # Formating Date Time
    formattedDateTime = datetime.now(currentTz).strftime("%Y-%m-%d %H:%M:%S")
    # recupera a trip adiciona informações finais e sobe na DB
    trip = Trips.query.filter_by(carPlate=carplate).order_by(Trips.initialTime.desc()).first()
    trip.endAddress = endAddress.__str__()
    trip.endTime = formattedDateTime
    db.session.commit()
    # Loga e informa usuário
    app.logger.info('Trip ended. %s' % endAddress)


def initiateTrip(initialAddress, timeZoneName, nickname, carplate):
    # formating dateTime
    currentTz = pytz.timezone(timeZoneName)
    formattedDateTime = datetime.now(currentTz).strftime("%Y-%m-%d %H:%M:%S")
    # Creating new Trip and uploading to DB
    trip = Trips(initialAddress=initialAddress.__str__(), initialTime=formattedDateTime, userNickname=nickname,
                 carPlate=carplate)
    db.session.add(trip)
    db.session.commit()
    # Escreve no log
    app.logger.info('Trip Started. %s' % initialAddress)


def isGeoCodingWorking(address):
    if address.error != 0:
        return False
    else:
        return True


def sendWhatsAppMessage(groupName, message):
    pywhatkit.sendwhatmsg_to_group_instantly("Dummy", "Oi")
    pywhatkit.sendwhatmsg_to_group("Dummy", "message", 0, 0)
    # pywhatkit.sendwhatmsg_to_group("AB123CDEFGHijklmn", "Hey All!", 0, 0)
