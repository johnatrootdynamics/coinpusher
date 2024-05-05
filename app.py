
from flask import Flask, render_template, jsonify
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from flask_socketio import SocketIO, join_room, leave_room, emit
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
        cursor.execute("SELECT name, location, machine_status FROM machines WHERE id=%s", (machine_id,))
        machine = cursor.fetchall()  # Fetch all results
        if not machine:
            return "Machine not found", 404
        return render_template('machine.html', machine=machine)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()



@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    socketio.send("Message received")
    sys.stdout.write('got message  ')
    os.write(1, b'got message  ')

@socketio.on('my event')
def handle_myevent(data):
    print("Sayin client is connected dawg")
    socketio.send("got it dawg")

@socketio.on('disconnect')
def handle_disconnect():
    print("Disconnected")

@socketio.on('update_machine')
def handle_connect(data):
    print("Client sent machine update")
    sys.stdout.write('got update_machine message  ')
    os.write(1, b'got update_machine message ')
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
        cursor.commit()
        emit('status_updated', {'machine_id': machine_id, 'new_status': new_status}, broadcast=True)
        socketio.send("Updated machien status")
    except cursor.Error as e:
        emit('error', {'message': 'Database error: ' + str(e)})
    finally:
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