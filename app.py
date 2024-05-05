from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
dbuser = os.getenv['DBUSER']
dbpass = os.getenv['DBPASSWD']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{user}:{passwd}@coinpusher-db.root-dynamics.com/coin'.format(
    user=dbuser, passwd=dbuser)
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
socketio = SocketIO(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    plays = db.Column(db.Integer, default=0)
    tickets_won = db.Column(db.Integer, default=0)

class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    coins_left = db.Column(db.Integer, nullable=False)
    machine_status = db.Column(db.Integer, nullable=False, default=1)  # Assuming '1' is active



@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"message": "Invalid credentials"}), 401



@app.route('/machines', methods=['GET'])
def list_machines():
    try:
        # Query all machines
        machines = Machine.query.all()
        # Serialize the data for JSON output
        machines_list = [{
            'id': machine.id,
            'location': machine.location,
            'coins_left': machine.coins_left,
            'status': machine.machine_status
        } for machine in machines]

        return render_template('machines.html', machines=machines)
    except Exception as e:
        return str(e)  # For debugging, in production handle errors appropriately









if __name__ == '__main__':
    socketio.run(app)