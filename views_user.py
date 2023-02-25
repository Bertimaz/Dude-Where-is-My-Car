from flask import render_template, request, redirect, session,flash,url_for
from carro_app import app
from helpers import FormularioUsuarioLogin
from models import Users
from flask_bcrypt import check_password_hash
from helpers import isLogged

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    form = FormularioUsuarioLogin()

    if isLogged(session):
        flash(session.get('nickname_usuario_logado') + ' Já esta logado!')
        return redirect(proxima)


    return render_template('/login.html', proxima=proxima, form=form)


@app.route('/autenticar',methods=['POST',])
def autenticar():
    #inicializa formulario
    form=FormularioUsuarioLogin(request.form)
    #log
    app.logger.info('Autenticando usuario %s' % (form.nickname.data))

    #Encontra usuário pelo nickname
    user = Users.query.filter_by(nickname=form.nickname.data).first()
    #Se existe o user confirma a senha
    if user:
        password = check_password_hash((user.password), form.password.data)
        #Se a senha confere loga o usuario, imprime mensagem de confirmação e vai para a próxima pagins
        if password:
            session['nickname_usuario_logado'] = user.nickname
            flash(user.nickname + ' logou com sucesso!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)

    flash('Nome do usuario e senha não conferem.')
    proxima_pagina=request.form['proxima']
    return redirect(url_for('login', proxima=proxima_pagina))


@app.route('/logout')
def logout():
    # log
    app.logger.info('Usuario deslogado %s' % (session['nickname_usuario_logado']))
    session['nickname_usuario_logado'] = None
    flash('Logout realizado com sucesso')
    return redirect(url_for('login',proxima=url_for('index')))


