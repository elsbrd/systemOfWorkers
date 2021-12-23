import re

import bcrypt
from flask import render_template, flash, request, redirect, url_for, session, jsonify, json
from flask_mysqldb import MySQL, MySQLdb
from model import create_app

mysql = MySQL()
app = create_app()
mysql.init_app(app)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users inner join roles on users.role_id = roles.role_id WHERE email=%s ", (email,))
        user = cur.fetchone()
        cur.close()
        print(user)
        if user is not None:

            # if len(user) > 0:
            if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
                session['user_id'] = user['user_id']
                session['first_name'] = user['first_name']
                session['surname_name'] = user['surname_name']
                session['email'] = user['email']


                session['role'] = user['role']
                if user['role'] == 'basic':
                    return redirect("/seeorders")
                if user['role'] == 'admin':
                    return redirect("/adminPanel ")

            else:
                flash('Error user not found')
                return render_template('login.html')
                # return "Error password and email not match"

        else:
            # return "Error user not found"
            flash('Error user not found')
            return render_template('login.html')
    else:
        return render_template("login.html", error={})


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("buyingWork.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    else:
        first_name = request.form['first_name']
        surname_name = request.form['surname_name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        print(email)
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        cursor.execute("SELECT * FROM users WHERE surname_name LIKE %s", [surname_name])
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            flash("Account already exists!", "danger")
            return redirect(url_for('register'))
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash("Invalid email address!", "danger")
            return redirect(url_for('register'))
        elif not re.match(r'[A-Za-z0-9]+', surname_name):
            flash("Username must contain only characters and numbers!", "danger")
            return redirect(url_for('register'))
        elif not surname_name or not password or not email:
            flash("Incorrect username/password!", "danger")
            return redirect(url_for('register'))
        else:
        #cur = mysql.connection.cursor()
            cursor.execute("INSERT INTO users (first_name, surname_name, email, password) VALUES (%s,%s,%s,%s)",
                        (first_name, surname_name, email, hash_password,))
            mysql.connection.commit()
            flash("You have successfully registered!", "success")
            # if email is not None:
            #     flash('Error user exists')
            #     return redirect(url_for('register'))
            return redirect(url_for('login'))



@app.route('/')
def index():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur.execute("SELECT * FROM selectWork ")
    # selectWorklist = cur.fetchall()
    # cur.execute("SELECT * FROM technology ")
    # technologylist = cur.fetchall()
    # return render_template('buyingWork.html', selectWorklist=selectWorklist, technologylist=technologylist)
    return redirect(url_for('register'))


@app.route("/insert", methods=["POST", "GET"])
def insert():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        description = request.form['description']
        # technology = request.form['technology']
        date_posted = request.form['date_posted']
        deadline_date = request.form['deadline_date']
        price = request.form['price']
        work_type = request.form['work_type_id']
        technologies_name = request.form['technologies_id']


        try:
            cur.execute(
                "INSERT INTO orders (description,date_posted, deadline_date, price, work_type_id, technologies_id) VALUES (%s,%s, %s,%s,%s,%s)",
                (description, date_posted, deadline_date, price, work_type, technologies_name))
            # input = cur.fetchone()
            cur.close()

            # if input is  None:
            #     return "Error password and email not match"



        except Exception as e:
            s = str(e)
            response = app.response_class(response=json.dumps(s), status=201, mimetype='application/json')
            return response
        # data = {"message": 'New Records added successfully'}
        # response = app.response_class(response=json.dumps(data), status=201, mimetype='application/json')
        mysql.connection.commit()
        cur.close()
        return jsonify('New Records added successfully')



@app.route('/adminOrders')
def adminOrders():
    if session.get('user_id') == None:
        return redirect('/login')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id = session.get('user_id')
    # order by a specific full name
    # fullname = request.form['fullname']
    # cur.execute('SELECT * FROM tbl_user WHERE email=%s', fullname)

    cur.execute(
        "SELECT * FROM orders o left outer join technologies t on o.technologies_id = t.technologies_id left outer join work_types wt on o.work_type_id = wt.work_type_id  left outer join status s on o.status_id = s.status_id ")

    data = cur.fetchall()
    return render_template('orderPage.html', orders=data)


@app.route('/adminPanel')
def adminPanel():
    if session.get('user_id') == None or session.get('role') != 'admin':
        return redirect('/login')
    return render_template('AdminPanel.html')


@app.route('/adminPage')
def adminPage():
    if session.get('user_id') == None or session.get('role') != 'admin':
        return redirect('/login')
    user_id = session.get('user_id')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id = session.get('user_id')
    # order by a specific full name
    # fullname = request.form['fullname']
    # cur.execute('SELECT * FROM tbl_user WHERE email=%s', fullname)

    cur.execute(
        "SELECT * FROM users inner join roles on users.role_id = roles.role_id ")

    data = cur.fetchall()
    return render_template('adminPage.html', user_id=user_id, users=data)


@app.route('/seeorders')
def seeorders():
    # print(session.get('user_id'))
    if session.get('user_id') == None:
        return redirect('/login')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id = session.get('user_id')
    # order by a specific full name
    # fullname = request.form['fullname']
    # cur.execute('SELECT * FROM tbl_user WHERE email=%s', fullname)
    cur.execute(
        """SELECT * FROM orders o left outer join technologies t on o.technologies_id = t.technologies_id left outer join work_types wt on o.work_type_id = wt.work_type_id  left outer join status s on o.status_id = s.status_id where user_id =%s""",
        (user_id,))
    data = cur.fetchall()
    print('text', data)
    cur.execute("SELECT * FROM work_types ")
    work_typeslist = cur.fetchall()
    cur.execute("SELECT * FROM technologies ")
    technologieslist = cur.fetchall()

    return render_template('index.html', employee=data, work_typeslist=work_typeslist,
                           technologieslist=technologieslist)


@app.route('/add_contact', methods=['POST'])
def add_employee():
    # conn = mysql.connect()
    # cur = conn.cursor(pymysql.cursors.DictCursor)

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        if session.get('user_id') == None:
            return redirect('/login')
        print(request.form)
        user_id = session.get('user_id')
        description = request.form['description']
        deadline_date = request.form['deadline_date']
        work_type_id = request.form['work_type_id']
        technologies_id = request.form['technologies_id']
        price = request.form['price']

        if not description or not deadline_date or not price:
            flash('You have not added the new information!')
            return redirect("/seeorders")
        # fullname, email
        cur.execute(
            # "INSERT INTO orders (description,date_posted, deadline_date, price, work_type_id, technologies_id) VALUES (%s,%s, %s,%s,%s,%s)",
            # (description,  date_posted, deadline_date, price,work_type, technologies_name))
            "INSERT INTO orders (user_id, description,deadline_date, price, work_type_id, technologies_id) VALUES (%s, %s, %s,%s,%s,%s)",
            (user_id, description, deadline_date, price, work_type_id, technologies_id))
        # conn.commit()
        # mysql.connection.commit()
        mysql.connection.commit()
        cur.close()
        flash('New order successfully added')
        return redirect("/seeorders")


@app.route('/edit/<id>', methods=['POST', 'GET'])
def get_employee(id):
    # conn = mysql.connect()
    # cur = conn.cursor(pymysql.cursors.DictCursor)
    if session.get('user_id') == None:
        return redirect('/login')
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute(""" select if ((select user_id from orders where order_id = %s) =%s , TRUE, FALSE) as result """,
                (id, user_id))
    can = cur.fetchall()
    # print(can[0]["result"])
    if can[0]["result"] == 0:
        return redirect('/seeorders')

    cur.execute('SELECT * FROM orders WHERE order_id = %s', (id))
    data = cur.fetchall()

    if data[0]['status_id'] == 1:
        cur.execute("SELECT * FROM status ")
        statuslist = cur.fetchall()

        cur.execute("SELECT * FROM work_types ")
        work_typeslist = cur.fetchall()
        cur.execute("SELECT * FROM technologies ")
        technologieslist = cur.fetchall()
        cur.close()
        data[0]['deadline_date'] = data[0]['deadline_date'].strftime("%Y-%m-%dT%H:%M:%S")
        return render_template('edit.html', order=data[0], statuslist=statuslist, work_typeslist=work_typeslist,
                               technologieslist=technologieslist)
    else:
        flash('You can not edit the orders cuz this order is in process')
        return redirect("/seeorders")


# is not editing what is totake
@app.route('/editorder/<id>', methods=['POST', 'GET'])
def get_Admin(id):
    if session.get('user_id') == None:
        return redirect('/login')
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM status ")
    statuslist = cur.fetchall()
    cur.execute(""" select * from orders where order_id = %s """, (id,))
    order = cur.fetchall()
    cur.close()
    return render_template('editAdmin.html', order=order[0], statuslist=statuslist)


@app.route('/changeorder/<id>', methods=['POST', 'GET'])
def change_order(id):
    if session.get('user_id') == None:
        return redirect('/login')
    user_id = session.get('user_id')
    cur = mysql.connection.cursor()
    cur.execute(""" select if ((select user_id from orders where order_id = %s) =%s , TRUE, FALSE) as result """,
                (id, user_id))
    # can = cur.fetchall()
    # print(can[0]["result"])

    cur.execute('SELECT * FROM orders WHERE order_id = %s', (id))
    data = cur.fetchall()
    cur.execute('SELECT * FROM  WHERE order_id = %s', (id))
    data = cur.fetchall()
    cur.execute("SELECT * FROM status ")
    statusList = cur.fetchall()

    data[0]['deadline_date'] = data[0]['deadline_date'].strftime("%Y-%m-%dT%H:%M:%S")
    return render_template('editAdmin.html', order=data[0], statuslist=statusList)


@app.route('/changeAdmin/<id>', methods=['POST', 'GET'])
def change_Admin(id):
    if session.get('user_id') == None or session.get('role') != 'admin':
        return redirect('/login')
    user_id = session.get('user_id')
    if user_id == int(id):
        return redirect('/adminPage')
    cur = mysql.connection.cursor()
    # can = cur.fetchall()
    # # print(can[0]["result"])
    #
    cur.execute("""SELECT * FROM users where user_id = %s""", (id,))
    user = cur.fetchall()
    #
    cur.execute("SELECT * FROM roles")
    roleslist = cur.fetchall()
    cur.close()
    return render_template('changingAdmin.html', user=user[0], roleslist=roleslist)


@app.route('/update/<id>', methods=['POST'])
def update_employee(id):
    if request.method == 'POST':
        if session.get('user_id') == None:
            return redirect('/login')
        user_id = session.get('user_id')
        description = request.form['description']
        deadline_date = request.form['deadline_date']
        work_type_id = request.form['work_type_id']
        technologies_id = request.form['technologies_id']
        price = request.form['price']
        # conn = mysql.connect()
        # cur = conn.cursor(pymysql.cursors.DictCursor)
        # if (select user_id from orders where order_id = %s) =%s then

        cur = mysql.connection.cursor()
        cur.execute(""" select if ((select user_id from orders where order_id = %s) =%s , TRUE, FALSE) as result """,
                    (id, user_id))
        can = cur.fetchall()
        print(can[0]["result"])
        if can[0]["result"] == 0:
            return redirect('/seeorders')
        cur.execute("""
                        UPDATE orders
                        SET description = %s,
                            deadline_date = %s,
                            price = %s,
                            work_type_id = %s,
                            technologies_id = %s
                        WHERE order_id = %s
                    """, (description, deadline_date, price, work_type_id, technologies_id, id))

        flash('Order Updated Successfully')
        # conn.commit()
        mysql.connection.commit()
        cur.close()
        return redirect("/seeorders")


@app.route('/updateAdmin/<id>', methods=['POST'])
def update_Admin(id):
    if request.method == 'POST':
        if session.get('user_id') == None or session.get('role') != 'admin':
            return redirect('/login')
        user_id = session.get('user_id')
        status_id = request.form['status_id']
        cur = mysql.connection.cursor()
        # try{}except(err){}
        cur.execute("""
                        UPDATE orders
                        SET status_id = %s, maker_id = %s
                        WHERE order_id = %s
                    """, (status_id, user_id, id))

        flash('Status Updated Successfully')
        # conn.commit()
        mysql.connection.commit()
        cur.close()
        return redirect("/adminOrders")


@app.route('/newAdmin/<id>', methods=['POST'])
def newAdmin(id):
    if request.method == 'POST':
        if session.get('user_id') == None or session.get('role') != 'admin':
            return redirect('/login')
        user_id = session.get('user_id')
        role_id = request.form['role_id']
        cur = mysql.connection.cursor()
        cur.execute("""
                        UPDATE users
                        SET role_id = %s
                        WHERE user_id = %s
                    """, (role_id, id))

        flash('Status Updated Successfully')
        # conn.commit()
        mysql.connection.commit()
        cur.close()
        return redirect("/adminPage")


@app.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete_employee(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('DELETE FROM orders WHERE order_id = {0}'.format(id))
    # conn.commit()
    mysql.connection.commit()
    flash('Order Removed Successfully')
    return redirect("/seeorders")


if __name__ == '__main__':
    app.secret_key = "caircocoders-ednalan"
    app.run(debug=True)
