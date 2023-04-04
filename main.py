from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from distutils.util import strtobool
import random
import os

app = Flask(__name__)
API_KEY = os.getenv('API_KEY')
##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration

with app.app_context():
    class Cafe(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(250), unique=True, nullable=False)
        map_url = db.Column(db.String(500), nullable=False)
        img_url = db.Column(db.String(500), nullable=False)
        location = db.Column(db.String(250), nullable=False)
        seats = db.Column(db.String(250), nullable=False)
        has_toilet = db.Column(db.Boolean, nullable=False)
        has_wifi = db.Column(db.Boolean, nullable=False)
        has_sockets = db.Column(db.Boolean, nullable=False)
        can_take_calls = db.Column(db.Boolean, nullable=False)
        coffee_price = db.Column(db.String(250), nullable=True)

        def to_dict(self):
            dictionary = {}
            for column in self.__table__.columns:
                dictionary[column.name] = getattr(self, column.name)
            return dictionary
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record


@app.route('/random', methods=['GET'])
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())
    pass


@app.route('/all', methods=['GET'])
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    print(all_cafes)
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route('/search')
def get_cafe_location():
    query_location = request.args.get('location')
    cafes = db.session.query(Cafe).filter_by(location=query_location).all()
    if cafes:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"not fount": "no cafe at this location"})


## HTTP POST - Create Record


@app.route("/add", methods=["POST", "GET"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        has_sockets=bool(request.form.get("sockets")),
        can_take_calls=bool(request.form.get("calls")),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record


@app.route('/update-price/<int:cafe_id>', methods=["PATCH", 'GET'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


## HTTP DELETE - Delete Record

@app.route('/delete-cafe/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")
    if api_key == API_KEY:
        cafe_to_delete = db.session.query(Cafe).get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"Success": "Successfully deleted from the database"})
        else:
            return jsonify(error={"Not found": "cafe id does not exist"})
    else:
        return jsonify(error={"Forbidden": "You do not have permission to delete"})


if __name__ == '__main__':
    app.run(debug=True)
