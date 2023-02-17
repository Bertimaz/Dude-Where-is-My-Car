from carro_app import db


class Users(db.Model):
    nickname = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    masterUserNickname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name


class Cars(db.Model):
    name = db.Column(db.String(50), primary_key=True)
    plate = db.Column(db.String(10), nullable=False)
    model = db.Column(db.String(20), nullable=False)
    ownerNickname = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name


class Trips(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    initialAddress = db.Column(db.String(100), nullable=False)
    initialTime = db.Column(db.String(30), nullable=False)
    endAddress = db.Column(db.String(100), nullable=True)
    endTime = db.Column(db.String(30), nullable=True)
    userNickname = db.Column(db.String(15), nullable=False)
    carPlate = db.Column(db.String(10), nullable=False)


    def __repr__(self):
        return '<Name %r>' % self.name


class UsersCars(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    userNickname = db.Column(db.String(20), nullable=False)
    carPlate = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name

