
from flask import Flask, render_template, jsonify
import MySQLdb
import os
dbuser = os.getenv('DBUSER', 'none')
dbpasswd = os.getenv('DBPASSWD', 'none')
app = Flask(__name__)


app.config['MYSQL_HOST'] = 'coinpusher-db.root-dynamics.com'
app.config['MYSQL_USER'] = $dbuser
app.config['MYSQL_PASSWORD'] = $dbpasswd
app.config['MYSQL_DB'] = 'coin'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

def get_db_connection():
    conn = MySQLdb.connect(app)
    return conn

@app.route('/machines')
def list_machines():
    conn = get_db_connection()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)  # Use DictCursor to get results as dictionaries
    try:
        cursor.execute("SELECT id, location, coins_left, machine_status FROM machines")
        machines = cursor.fetchall()  # Fetch all results
        return render_template('machines.html', machines=machines)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)