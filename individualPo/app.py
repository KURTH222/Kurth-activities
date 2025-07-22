from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'basta'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="wa"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user'] = user['fullname']
            return redirect('/home')
        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = (
            request.form['fullname'],
            request.form['email'],
            request.form['phone'],
            request.form['address'],
            request.form['username'],
            generate_password_hash(request.form['password'])
        )
        cursor.execute("INSERT INTO users (fullname, email, phone, address, username, password) VALUES (%s,%s,%s,%s,%s,%s)", data)
        db.commit()
        flash("Account created! You can now login.", "success")
        return redirect('/login')
    return render_template('signup.html')

@app.route('/home')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    return render_template('home.html', employees=employees)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = (
        request.form['name'],
        request.form['position'],
        request.form['salary']
    )
    cursor.execute("INSERT INTO employees (name, position, salary) VALUES (%s, %s, %s)", data)
    db.commit()
    return redirect('/home')

@app.route('/edt/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['position'],
            request.form['salary'],
            id
        )
        cursor.execute("UPDATE employees SET name=%s, position=%s, salary=%s WHERE id=%s", data)
        db.commit()
        return redirect('/dashboard')
    cursor.execute("SELECT * FROM employees WHERE id = %s", (id,))
    emp = cursor.fetchone()
    return render_template('edit_employee.html', employee=emp)

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    cursor.execute("DELETE FROM employees WHERE id = %s", (id,))
    db.commit()
    return redirect('/home')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
