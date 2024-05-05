
from flask import Flask, render_template, jsonify
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from flask_socketio import SocketIO
import os
dbuser = os.getenv('DBUSER', 'none')
dbpasswd = os.getenv('DBPASSWD', 'none')
dbhost = os.getenv('DBHOST', 'none')
app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['MYSQL_HOST'] = dbhost
app.config['MYSQL_USER'] = dbuser
app.config['MYSQL_PASSWORD'] = dbpasswd
app.config['MYSQL_DB'] = 'coin'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


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
        cursor.execute("SELECT id, name, location, machine_status FROM machines")
        machine = cursor.fetchall()  # Fetch all results
        if not machine:
            return "Machine not found", 404
        return render_template('machine.html', machine=machine)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=80, allow_unsafe_werkzeug=True)