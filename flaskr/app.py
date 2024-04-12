from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db=SQLAlchemy(app)

class caretaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    photo=db.Column(db.String(120), nullable=True)   
    def __repr__(self):
        return '<Tenant %r>' % self.name

class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120), nullable=True)
    name=db.Column(db.String(80), nullable=True)
    contact=db.Column(db.String(10), nullable=True)
    house = db.relationship('Apartment', backref=db.backref('house', lazy=True))

    def __repr__(self):
        return '<House %r>' % self.address   

class Apartment(db.Model):
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    rent = db.Column(db.Integer, nullable=False) 
    type = db.Column(db.String(30), nullable=False)
    house_number=db.Column(db.String(10), nullable=False)
    def __repr__(self):
        return '<Apartment %r>' % self.type

@app.route('/')
def view_all():
    houses = House.query.order_by(House.name).all()

    return render_template('index.html',houses=houses)

@app.route('/add_house',methods=['GET','POST'])
def add_house():
    if request.method == 'POST':
        address = request.form['address']
        name = request.form['name']
        contact = request.form['contact']
        house = House(address=address, name=name, contact=contact)
        db.session.add(house)
        db.session.commit()
        return redirect('/')    
    else:
        return render_template('add_house.html')


# @app.route ('/add_apartment/<int:id>',methods=['GET','POST'])
# def add_apartment(id):
#     if request.method == 'POST':
#         house_id = request.form['house_id']
#         rent = request.form['rent']
#         type = request.form['type']
#         house_number = request.form['house_number']
#         apartment = Apartment( house_id=house_id,rent=rent, type=type, house_number=house_number)
        
#         db.session.add(apartment)
#         db.session.commit()
#         return redirect('/')
#     else:
#         houses = House.query.get_or_404(id)
#         return render_template('add_apartment.html',id=houses.id)
@app.route ('/add_apartment/<int:id>',methods=['GET','POST'])
def add_apartment(id):
    if request.method == 'POST':
        house_id = request.form['house_id']
        rent = request.form['rent']
        type = request.form['type']
        house_number = request.form['house_number']

        # Check if the house_id corresponds to an existing House
        house = House.query.get(house_id)
        if house is None:
            # Handle the error: the house_id does not exist
            return "Error: No house with id {}".format(house_id), 400

        apartment = Apartment(house_id=house_id, rent=rent, type=type, house_number=house_number)
        
        db.session.add(apartment)
        db.session.commit()
        return redirect('/')
    else:
        houses = House.query.get_or_404(id)
        return render_template('add_apartment.html', id=houses.id)
    
@app.route('/view_apartment/<int:id>',methods=['GET'])
# viewing all apartments per house
def view_apartment(id):
    apartments = Apartment.query.filter_by(house_id=id).all()
    return render_template('view_apartment.html',apartments=apartments)

if (__name__ == "__main__"):
    app.run(debug=True, port=5000, host='0.0.0.0')
    with app.app_context():
        db.create_all()



    