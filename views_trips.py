import flask
from flask import render_template, request, redirect, session, flash, url_for, send_from_directory

import config
from carro_app import app
from models import Trips, Users, Cars, UsersCars, db
from datetime import datetime
from helpers import *
import googlemaps
import time
import helpers
import pytz

from flask_bcrypt import check_password_hash


# implementar botao de endTrip, restrições aos botãos de beginTrip e EndTrip quando necessario, implementar encerramento automatico de viagem. Esconder senha no login. Fazer função de manter logado.
@app.route('/')
def index():
    # se usuario logado abre pagina home
    if isLogged(session):

        # Inicializa informações do usuario
        nickname = session['nickname_usuario_logado']

        # Inicializa carros liberados para usuario
        user = Users.query.filter_by(nickname=nickname).first()
        usersCars = UsersCars.query.filter_by(userNickname=nickname)
        cars = []

        for usercar in usersCars:
            car = Cars.query.filter_by(plate=usercar.carPlate).first()
            cars.append(car)

        # Inicializa ultima viagem do usuario corrigir para ultima viagem do carro selecionado
        trip = Trips.query.filter_by(carPlate=cars[0].plate).order_by(Trips.initialTime.desc()).first()

        # Inicializa informações do carro da ultima viagem
        carTrip = Cars.query.filter_by(plate=trip.carPlate).first()



        # Inicializa formularios adequados
        isLastTripOpen = helpers.isLastTripOpen(carTrip.plate)
        if isLastTripOpen:
            action = 'tripEnder'
            form = formEndTrip(request.form)
            mapsLink=""
        else:
            action = 'tripInitializer'
            form = formInitializeTrip(request.form)
            mapsLink="https://www.google.com.br/maps/search/{address}".format(
                address=trip.endAddress.replace("- ","").replace(" ","+")
        )
            print(mapsLink)

        driverName=Users.query.filter_by(nickname=trip.userNickname).first().name

        # retorna pagina home
        return render_template('home.html', titulo='Viagens',nickname=session['nickname_usuario_logado'] , trip=trip, user=user, carTrip=carTrip, cars=cars,
                               form=form, action=action,mapsLink=mapsLink,driverName=driverName)

    # Caso Contrario vai para login
    else:
        return redirect(url_for('login', proxima=url_for('index')))


@app.route('/index-car', methods=['POST', ])
def indexCar():
    form1 = formInitializeTrip
    print(form1.carPlate.data)
    # se usuario logado abre pagina home
    if isLogged(session):

        # Inicializa informações do usuario
        nickname = session['nickname_usuario_logado']

        # Inicializa ultima viagem do usuario corrigir para ultima viagem do carro selecionado
        trip = Trips.query.filter_by(userNickname=nickname).order_by(Trips.initialTime.desc()).first()

        # Inicializa carros liberados para usuario
        #Cria objeto carro a partir da placa do carro da ultima viagem
        carTrip = Cars.query.filter_by(plate=trip.carPlate).first()
        #Cria usuario a partir do nickname
        user = Users.query.filter_by(nickname=nickname).first()
        #Buscar carros do usuario a partir do nickname
        usersCars = UsersCars.query.filter_by(userNickname=nickname)

        #Adiciona carros disponiveis para o usuario na lista cars
        cars = []
        for usercar in usersCars:
            car = Cars.query.filter_by(plate=usercar.carPlate).first()
            cars.append(car)

        # Inicializa formularios adequados
        isLastTripOpen = helpers.isLastTripOpen(carTrip.plate)
        if isLastTripOpen:
            action = 'tripEnder'
            form = formEndTrip(request.form)
        else:
            action = 'tripInitializer'
            form = formInitializeTrip(request.form)

        # retorna pagina home
        return render_template('home.html', titulo='Viagens', trip=trip, user=user, carTrip=carTrip, cars=cars,
                               form=form, action=action)

    # Caso Contrario vai para login
    else:
        return redirect(url_for('login', proxima=url_for('index')))


@app.route('/trip-initializer', methods=['POST', ])
def tripInitializer():
    form = formInitializeTrip

    # Se usuario Logado Salvar viagem
    if isLogged(session):
        # Pega dados do formulario e do usuario
        nickname = session['nickname_usuario_logado']
        geoLocationStatus=request.form.get("geoLocationError")
        initialLatitude = request.form.get('latitude')
        initialLongitude = request.form.get('longitude')

        app.logger.info('Browser Geolocation Status:' + str(geoLocationStatus))

        #Se não tiver informação do geoLocation voltar para home
        if geoLocationStatus==None or geoLocationStatus=="":
            flash('Problema com a localização do navegador. Erro desconhecido')
            app.logger.info('Browser Geolocation error:' + str(geoLocationStatus))
            return redirect('/')

        #Se tiver probemas com a geolocalização ir para home
        if geoLocationStatus==1 or geoLocationStatus==2:
            flash('Problema com a localização do navegador. Erro nº= %d!' % geoLocationStatus)
            app.logger.info('Browser Geoocation error: %d' % (geoLocationStatus))
            return redirect('/')

        # Se não tem probemas com a localização, mandas as informações para o logger
        else:
            try:
                app.logger.info('Recovering Address from coordinates: %f,%f'% (initialLatitude, initialLongitude))
            except:
                try:
                    app.logger.info('Recovering Address from coordinates: %s,%s' % (initialLatitude, initialLongitude))
                except:
                    app.logger.info('Coordinates invalid')
                    flash('Problema com a localização do navegador. Erro nº= %d!' % geoLocationStatus)
                    return redirect('/')



            # Salva endereço a partir das coordenadas
            initialAddress = helpers.reverseGeocode(initialLatitude, initialLongitude)

            # Checa erro no geocodding
            if initialAddress.error != 0:
                flash('Geocoding Error: Try Again Later')
                return redirect('/')

            else:

                currentTzName="America/Sao_Paulo"
                # cria a trip e sobe na DB
                initiateTrip(initialAddress,currentTzName,nickname,request.form.get("cars"))

                # Imprime mensagem e escreve no log
                app.logger.info('New Trip Uploaded. %s' % initialAddress)
                flash('Viagem Iniciada!')

                # Abre a home novamente
                return redirect('/')

    #Se usuario não logado voltar para home
    else:
        flash('Você precisa estar logado para iniciar uma viagem!')
        return redirect('/')

#Como copiar codigo da trip initializer para atualizar mensagens de erro?
## Mandar mensagem no grupo
### Send a WhatsApp Message to a Group instantly
###pywhatkit.sendwhatmsg_to_group_instantly("AB123CDEFGHijklmn", "Hey All!")
@app.route('/trip-ender', methods=['POST', ])
def tripEnder():
    # Se usuario Logado
    if isLogged(session):
        # Pega dados do formulario e do usuario
        form = formInitializeTrip
        nickname = session['nickname_usuario_logado']
        finalLatitude = request.form.get('latitude')
        finalLongitude = request.form.get('longitude')
        geoLocationStatus = request.form.get("geoLocationError")

        app.logger.info('Browser Geolocation Status:' + str(geoLocationStatus))
        # Se não tiver informação do geoLocation voltar para home
        if geoLocationStatus == None or geoLocationStatus == "":
            flash('Problema com a localização do navegador. Erro desconhecido')
            app.logger.info('Browser Geolocation error:' + str(geoLocationStatus))
            return redirect('/')

        # Salva endereço a partir das coordenadas
        print("latitude:%s longitude:%s", finalLatitude, finalLongitude)
        endAddress = helpers.reverseGeocode(finalLatitude, finalLongitude)



        # Checa erro no geocodding
        if endAddress.error != 0:
            flash('Geocoding Error. Try Again Later')
            return redirect('/')

        else:
            # Configura Timezone e encerra viagem
            currentTzName="America/Sao_Paulo"
            endTrip(currentTzName,request.form.get("cars"),endAddress.__str__())
            # Imprime mensagem e sobe no log
            app.logger.info('New Trip ended. %s' % endAddress)
            flash('Viagem Finalizada!')
            # Abre a home novamente
            return redirect('/')


    else:
        flash('Você precisa estar logado para iniciar uma viagem!')
        return redirect('/')


@app.route('/search-trip', methods=['GET', 'POST'])
def searchTrip():
    trip = Trips(id=1, initialAddress="Rua")

    print(trip.initialAddress)

    # se usuario logado abre pagina home
    if isLogged(session):

        # Inicializa informações do usuario
        nickname = session['nickname_usuario_logado']
        #Inicializa Formulario
        form = formSearchTripByDate()

        # Inicializa carros liberados para usuario
        user = Users.query.filter_by(nickname=nickname).first()
        usersCars = UsersCars.query.filter_by(userNickname=nickname)
        cars = []
        for usercar in usersCars:
            car = Cars.query.filter_by(plate=usercar.carPlate).first()
            cars.append(car)

        if flask.request.method == 'POST':
            # Inicializa formularios adequados
            formAnterior=formSearchTripByDate(request.form)


            #Procura Viagens
            # qry = DBSession.query(User).filter(User.birthday.between('1985-01-17', '1988-01-17'))
            trips = Trips.query.filter_by(carPlate=request.form.get("cars"), ).order_by(Trips.initialTime.desc())
            # retorna pagina home
            return render_template('searchTrip.html', form=form, cars=cars, trips=trips)
        else:
            # retorna pagina home
            return render_template('searchTrip.html', form=form, cars=cars)

        # retorna pagina home



    # Caso Contrario vai para login
    else:
        return redirect(url_for('login', proxima=url_for('index')))

