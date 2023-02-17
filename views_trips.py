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

from flask_bcrypt import check_password_hash


# implementar botao de endTrip, restrições aos botãos de beginTrip e EndTrip quando necessario, implementar encerramento automatico de viagem. Esconder senha no login. Fazer função de manter logado.
@app.route('/')
def index():
    # se usuario logado abre pagina home
    if 'nickname_usuario_logado' in session and session['nickname_usuario_logado'] is not None:

        # Inicializa informações do usuario
        nickname = session['nickname_usuario_logado']

        # Inicializa ultima viagem do usuario corrigir para ultima viagem do carro selecionado
        trip = Trips.query.filter_by(userNickname=nickname).order_by(Trips.initialTime.desc()).first()
        carTrip = Cars.query.filter_by(plate=trip.carPlate).first()

        # Inicializa carros liberados para usuario
        user = Users.query.filter_by(nickname=nickname).first()
        usersCars = UsersCars.query.filter_by(userNickname=nickname)
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


@app.route('/index-car', methods=['POST', ])
def indexCar():
    form1 = formInitializeTrip
    print(form1.carPlate.data)
    # se usuario logado abre pagina home
    if 'nickname_usuario_logado' in session and session['nickname_usuario_logado'] is not None:

        # Inicializa informações do usuario
        nickname = session['nickname_usuario_logado']

        # Inicializa ultima viagem do usuario corrigir para ultima viagem do carro selecionado
        trip = Trips.query.filter_by(userNickname=nickname).order_by(Trips.initialTime.desc()).first()

        # Inicializa carros liberados para usuario
        carTrip = Cars.query.filter_by(plate=trip.carPlate).first()
        user = Users.query.filter_by(nickname=nickname).first()
        usersCars = UsersCars.query.filter_by(userNickname=nickname)
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

    # Se usuario Logado
    if 'nickname_usuario_logado' in session and session['nickname_usuario_logado'] is not None:
        # Pega dados do formulario e do usuario

        nickname = session['nickname_usuario_logado']
        initialLatitude = request.form.get('latitude')
        initialLongitude = request.form.get('longitude')
        try:
            app.logger.info('Recovering Address from coordinates: %f,%f'% (initialLatitude, initialLongitude))
        except:
            try:
                app.logger.info('Recovering Address from coordinates: %s,%s' % (initialLatitude, initialLongitude))
            except:
                app.logger.info('Coordinates invalid')



        # Salva endereço a partir das coordenadas
        initialAddress = helpers.reverseGeocode(initialLatitude, initialLongitude)

        # Checa erro no geocodding
        if initialAddress.error != 0:
            flash('Geocoding Error: Try Again Later')
            return redirect('/')

        else:
            # cria a trip e sobe na DB
            trip = Trips(initialAddress=initialAddress.__str__(), initialTime=datetime.now(), userNickname=nickname,
                         carPlate=request.form.get("cars"))
            db.session.add(trip)
            db.session.commit()
            app.logger.info('New Trip Uploaded. %s' % initialAddress)

            # Imprime mensagem
            flash('Viagem Iniciada!')

            # Abre a home novamente
            return redirect('/')


    else:
        flash('Você precisa estar logado para iniciar uma viagem!')
        return redirect('/')


@app.route('/trip-ender', methods=['POST', ])
def tripEnder():
    # Se usuario Logado
    if 'nickname_usuario_logado' in session and session['nickname_usuario_logado'] is not None:
        # Pega dados do formulario e do usuario
        form = formInitializeTrip
        nickname = session['nickname_usuario_logado']
        finalLatitude = request.form.get('latitude')
        finalLongitude = request.form.get('longitude')

        # Salva endereço a partir das coordenadas
        print("latitude:%s longitude:%s", finalLatitude, finalLongitude)
        endAddress = helpers.reverseGeocode(finalLatitude, finalLongitude)

        # Checa erro no geocodding
        if endAddress.error != 0:
            flash('Geocoding Error. Try Again Later')
            return redirect('/')

        else:
            # recupera a trip adiciona informações finais e sobe na DB
            trip = Trips.query.filter_by(carPlate=request.form.get("cars")).order_by(Trips.initialTime.desc()).first()
            trip.endAddress = endAddress.__str__()
            trip.endTime = datetime.now()
            db.session.commit()

            app.logger.info('New Trip ended. %s' % endAddress)

            # Imprime mensagem
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
    if 'nickname_usuario_logado' in session and session['nickname_usuario_logado'] is not None:

        # Inicializa informações do usuario
        nickname = session['nickname_usuario_logado']

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

