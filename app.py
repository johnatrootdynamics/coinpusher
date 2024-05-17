
from flask import Flask, render_template, jsonify, session, request
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import sys

dbuser = os.getenv('DBUSER', 'none')
dbpasswd = os.getenv('DBPASSWD', 'none')
dbhost = os.getenv('DBHOST', 'none')
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['MYSQL_HOST'] = dbhost
app.config['MYSQL_USER'] = dbuser
app.config['MYSQL_PASSWORD'] = dbpasswd
app.config['MYSQL_DB'] = 'coin'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(id=user['id'], username=user['username'])
    return None       

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        bucket = 'pushers'
        # Get form data
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='scrypt')

        # if 'picture' in request.files:
        #     picture = request.files['picture']
        # # If the user does not select a file, the browser submits an
        # # empty file without a filename.
        #     if picture.filename != "":
        #         picture = request.files['picture']
        #         if picture and allowed_file(picture.filename):
        #             filename = secure_filename(picture.filename)
        #             size = os.fstat(picture.fileno()).st_size
        #             picture_path = MINIO_API_HOST + '/drivers/' + filename
        #             upload_object(filename, picture, size, bucket)
        #         else:
        #             flash('Invalid File Type','danger')
        #             picture_path = 'firstnone'
        #     else:
        #         picture_path = 'secondnone'
        # else: picture_path = 'thirdone'

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)",
        (email ,username, hashed_password))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            user_obj = User(id=user['id'], username=user['username'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/machines')
def list_machines():
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT id, name, location, machine_status FROM machines")
        machines = cursor.fetchall()  # Fetch all results
        return render_template('machines.html', machines=machines)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@app.route('/machine/<int:machine_id>')
def machine_page(machine_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, name, location, machine_status FROM machines WHERE id=%s", (machine_id,))
        machine = cursor.fetchall()  # Fetch all results
        if not machine:
            return "Machine not found", 404
        return render_template('machine.html', machine=machine)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()






@socketio.on('connect')
def handle_connect():
    print("Client connected")
    # Assuming client sends their identifier as part of the connection request

@socketio.event
def joinroom(sid):
    socketio.enter_room(sid, 'clients')

@socketio.on('session_data')
def session_data(data):
    ndata = data['machine_id']
    socketio.send("_____________GOT SESSION DATA______________")
    as_bytes = bytes(ndata, 'utf8')
    os.write(1, as_bytes)

@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    socketio.send("Message received from client")
    sys.stdout.write('got message  ')
    os.write(1, b'__Function on server = message__  ')

@socketio.on('my event')
def handle_myevent(data):
    print("Sayin client is connected dawg")
    socketio.send('got "my event"')

@socketio.on('update_tickets')
def handle_myevent(data):
    print("adding tickets")
    socketio.send('got "more tickets"')

@socketio.on('disconnect')
def handle_disconnect():
    # cursor = mysql.connection.cursor()
    # machine_id = '1'

    # #Update Machines Status in SQL Based on Machine ID
    # try:
    #     cursor.execute("UPDATE machines SET machine_status=%s WHERE id=%s", ("2", machine_id))
    #     emit('status_updated', {'machine_id': machine_id, 'new_status': '2'}, broadcast=True)
    #     socketio.send("Updated machine status on disconnect")
    # except cursor.Error as e:
    #     emit('error', {'message': 'Database error: ' + str(e)})
    # finally:
    #     mysql.connection.commit()
    #     cursor.close()
     print("Disconnected")

@socketio.on('button_push')
def handle_button_push(data):
    emit('button_push', data ,broadcast=True)
    os.write(1, b'got button_push from webclient ')

@socketio.on('update_machine')
def handle_update_machine(data):
    print("Client sent machine update")
    sys.stdout.write('got update_machine message123  ')
    os.write(1, b'got update_machine message456 ')
    print(data)
    if data:
        socketio.send(f"rsssssssssssssssssssssssssssseceived {data}")
        socketio.send(data['machine_id'])
        socketio.send(data['machine_status'])
    cursor = mysql.connection.cursor()
    machine_id = data['machine_id']
    new_status = data['machine_status']

    #Update Machines Status in SQL Based on Machine ID
    try:
        cursor.execute("UPDATE machines SET machine_status=%s WHERE id=%s", (new_status, machine_id))
        emit('status_updated', {'machine_id': machine_id, 'new_status': new_status}, broadcast=True)
        socketio.send("Updated machien status on update_machine")
    except cursor.Error as e:
        emit('error', {'message': 'Database error: ' + str(e)})
    finally:
        mysql.connection.commit()
        cursor.close()

# @socketio.on('update_machine_status')
# def handle_update_status(data):
#     cursor = mysql.connection.cursor()
    
#     machine_id = data['machine_id']
#     new_status = data['new_status']
    
#     # Updating the machine's status in the database
#     sql_update_query = """
#     UPDATE machines
#     SET status = %s
#     WHERE id = %s
#     """
#     try:
#         cursor.execute(sql_update_query, (new_status, machine_id))
#         cursor.commit()
#         emit('status_updated', {'machine_id': machine_id, 'new_status': new_status}, broadcast=True)
#     except MySQLdb.Error as e:
#         emit('error', {'message': 'Database error: ' + str(e)})
#     finally:
#         cursor.close()






if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)