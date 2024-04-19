from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases.db'
db=SQLAlchemy(app)
migrate = Migrate(app, db)
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg'}  # Define allowed file extensions


class caretaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    photo=db.Column(db.String(120), nullable=True)   
    def __repr__(self):
        return '<Tenant %r>' % self.name

class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120), nullable=False)
    name=db.Column(db.String(80), nullable=False)
    contact=db.Column(db.String(10), nullable=False)
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

# uploading an image
class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))  # Store the filename
    filepath = db.Column(db.String(255))  # Store the file path

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




# Check if the filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST','GET'])
def upload_file():
    upload_folder = 'static/uploads'
    app.config['UPLOAD_FOLDER'] = upload_folder

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    if request.method=='POST':

        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        # Save the uploaded file to a specific directory
        # file.save( os.path.join(  'static/uploads',  file.filename))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Store the file location in the database
            uploaded_file = UploadedFile(filename=filename, filepath=filepath)
            # db.session.add(uploaded_file)
            # db.session.commit()

            return redirect('/upload')     
    else:
        # def findImage():
        
        uploaded_files = UploadedFile.query.all()
            # return uploaded_files
        return render_template('upload.html',files=uploaded_files)



if (__name__ == "__main__"):
    app.run(debug=True, port=5000, host='0.0.0.0')
    with app.app_context():
        db.create_all()



    