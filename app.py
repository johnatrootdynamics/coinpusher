
from flask import Flask, render_template, jsonify, session, request, redirect, url_for
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
    def __init__(self, id, username, plays, tickets_won):
        self.id = id
        self.username = username
        self.plays = plays
        self.tickets_won = tickets_won

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        
        return User(id=user['id'], username=user['username'], plays=user['plays'], tickets_won=user['tickets_won'])
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
            user_obj = User(id=user['id'], username=user['username'], plays=user['plays'], tickets_won=user['tickets_won'])
            login_user(user_obj)
            session['user_id'] = user['id']
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

@app.route('/profile/<int:user_id>')
def profile(user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username, plays, tickets_won FROM users WHERE id=%s", (user_id,))
        user_info = cursor.fetchall()
    except Exception as e:
        return("no user found")
    return render_template('profile.html', user_info=user_info)


@app.route('/exchange_tickets', methods=['POST'])
def exchange_tickets():
    cursor = mysql.connection.cursor()
    data = request.get_json()
    tickets_to_exchange = int(data['tickets'])
    tokens_to_add = int(data['tokens'])
    user_id = session['user_id']  # Assuming user_id is stored in cookies

    try:
        # Check if user has enough tickets
        cursor.execute("SELECT tickets_won FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        if result and result[0] >= tickets_to_exchange:
            # Update user tickets and tokens
            new_ticket_count = result[0] - tickets_to_exchange
            cursor.execute("UPDATE users SET tickets_won = %s WHERE id = %s", (new_ticket_count, user_id))
            cursor.execute("UPDATE users SET plays = plays + %s WHERE id = %s", (tokens_to_add, user_id))
            cursor.commit()
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="Not enough tickets"), 400
    except cursor.Error as e:
        cursor.rollback()
        return jsonify(success=False, error=str(e)), 500
    finally:
        cursor.close()


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
@login_required
def machine_page(machine_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, name, location, machine_status FROM machines WHERE id=%s", (machine_id,))
        machine = cursor.fetchall()  # Fetch all results
        user = session['user_id']
        if not machine:
            return "Machine not found", 404
        return render_template('machine.html', machine=machine, user=user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()





@socketio.on('connect', namespace='/machine')
def handle_rpi_connect():
    global raspberry_pi_connected
    raspberry_pi_connected = True
    emit('rpi_status', {'connected': True}, namespace='/webclient', broadcast=True)

@socketio.on('connect', namespace='/webclient')
def handle_webclient_connect():
    global webclient_connected
    weclient_connected = True
    #emit('webclient_status', {'connected': True, 'user_id': data['user_id']}, broadcast=True)

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    # Assuming client sends their identifier as part of the connection request

@socketio.on('client_connected')
def client_connected(data):
    print("Client connected")
    emit('status_updated', data, broadcast=True)

    # Assuming client sends their identifier as part of the connection request


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


@socketio.on('subtract_token', namespace='/machine')
def subtract_token(data):
    emit('subtract_token', data, namespace='/webclient', broadcast=True)

@socketio.on('update_tickets', namespace='/machine')
def handle_myevent(data):
    print("Adding tickets")
    user_id = data['user_id']
    new_tickets = data['tickets']

    

    # Establish a connection to the database
    cursor = mysql.connection.cursor()

    # Fetch the current number of tickets
    cursor.execute("SELECT tickets_won FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        current_tickets = result['tickets_won']
        total_tickets = current_tickets + new_tickets
        # Update the database with the new total
        cursor.execute("UPDATE users SET tickets_won = %s WHERE id = %s", (total_tickets, user_id))
        mysql.connection.commit()
        print("Tickets updated to:", total_tickets)
        # Emit the new total back to the web client
        emit('update_tickets', {'user_id': user_id, 'total_tickets': total_tickets}, namespace='/webclient', broadcast=True)
    else:
        print("User not found")

    cursor.close()










@socketio.on('disconnect')
def handle_disconnect(data):
    cursor = mysql.connection.cursor()
    machine_id = data['machine_id']

    #Update Machines Status in SQL Based on Machine ID
    try:
        cursor.execute("UPDATE machines SET machine_status=%s WHERE id=%s", ("2", machine_id))
        emit('status_updated', {'machine_id': machine_id, 'new_status': '2'}, broadcast=True)
        socketio.send("Updated machine status on disconnect")
    except cursor.Error as e:
        emit('error', {'message': 'Database error: ' + str(e)})
    finally:
        mysql.connection.commit()
        cursor.close()
    print("Disconnected")

@socketio.on('disconnect', namespace='/machine')
def handle_rpi_disconnect():
    global raspberry_pi_connected
    raspberry_pi_connected = False
    emit('rpi_status', {'connected': False}, namespace='/webclient', broadcast=True)

@socketio.on('status_check', namespace='/webclient')
def handle_rpi_statuscheck(data):
    global raspberry_pi_connected
    raspberry_pi_connected = False
    emit('rpi_status', {'connected': raspberry_pi_connected}, namespace='/webclient', broadcast=True)

@socketio.on('button_push', namespace='/webclient')
def handle_button_push(data):
    emit('button_push', data, namespace='/machine', broadcast=True)
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

def check_and_update_tokens(user_id, tokens_to_add):
    # Create a new database cursor
    cursor = mysql.connection.cursor()
    
    # Try to ensure that all database operations and cursor handling are done safely
    try:
        # Execute a query to fetch the current number of plays for the user
        cursor.execute("SELECT plays FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        
        # Check if we got a result and if there are enough plays available
        if result is None or result['plays'] < tokens_to_add:
            return False, 0 if result is None else result['plays']
        
        # Calculate new balance of tokens
        new_balance = result['plays'] - tokens_to_add
        
        # Update the user's plays in the database
        cursor.execute("UPDATE users SET plays = %s WHERE id = %s", (new_balance, user_id))
        mysql.connection.commit()
        
        return True, new_balance
    
    finally:
        # Ensure that the cursor is closed after operation
        cursor.close()




@socketio.on('deposit_tokens',namespace='/webclient')
def handle_deposit_tokens(data):
    user_id = session['user_id']
    # cursor = mysql.connection.cursor()
    # cursor.execute("SELECT plays FROM users WHERE id = %s", (user_id,))
    # result = cursor.fetchone()
    # emit('tokens_update', {'success': True, 'number of tokens': result },namespace='/webclient')

    success, balance = check_and_update_tokens(user_id, data['tokens'])
    if success:
        emit('update_tokens', {'success': True, 'tokens_added': data['tokens'], 'remaining_tokens': balance},namespace='/webclient')
        # Additional emit to Raspberry Pi if needed
        socketio.emit('play_tokens', {'machine_id': 1, 'plays_added': data['tokens']}, namespace='/machine')
    else:
        emit('tokens_update', {'success': False, 'remaining_tokens': balance},namespace='/webclient')


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)