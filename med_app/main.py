from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from datetime import datetime
from sqlite import SQLite
from logs import Logger

db_driver = SQLite.get_driver("./", "database.db")

""" *** FOR POSTGRESQL DB *** 
    -> uncomment these lines and comment line 7 and 4
from postgresql import PostgreSQL
db_driver   = PostgreSQL("your_host", "your_database", "user_name", "password")

"""
app = Flask(__name__, static_url_path='/static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
Logger.init("CMS", debug_mode=True)


try:
    """ Application Root"""
    @app.route('/')
    def index():
        ''' index page '''
        user = session.get("user", None)
        if user:
            if user["type"] == 0:
                return redirect("/usersite")

            elif user["type"] == 1:
                return redirect("/doctorsite")

            elif user["type"] == 2:
                return redirect("/adminsite")

            else:
                return redirect("/login")

        else:
            return redirect("/login")

    @app.route("/login", methods=['POST', 'GET'])
    def login():
        """ login user and redirect to respactive site"""
        if request.method == 'POST':
            username = request.form['uname']
            password = request.form['password']
            where = f"username='{username}' AND password='{password}'"
            user = db_driver.read("user", "*", where=where)
            if user is None or len(user) == 0:
                return render_template("login.html")

            else:
                user = user[0]
                session["user"] = user.copy()
                return redirect("/")

        else:
            return render_template("login.html")

    @app.route("/logout")
    def logout():
        ''' logout the user '''
        session["user"] = None
        return redirect("/login")

    # Admin Site
    @app.route('/edituser/<id>')
    def edit_user(id):
        pass

    @app.route('/deleteuser/<id>')
    def delete_user(id):
        pass

    @app.route("/manageuser")
    def manage_user():
        """ render admin site """
        user = session.get("user", None)
        if user and user['type'] == 2:
            query = f""" SELECT u.id, u.username, ud.fname, ud.lname, ud.address, ud.phone
                                FROM user as u JOIN userDetails as ud 
                                ON u.id = ud.userid 
                                WHERE u.type=0"""
            user_details = db_driver.execute_select(query, True)
            user_details = [] if user_details is None else user_details
            ids = [ud['id'] for ud in user_details]

            users = db_driver.read("user", "*", where='type=0')
            users = [] if users is None else users
            users = [u for u in users if u['id'] not in ids]

            data = {"users": users, "user_details": user_details}
            return render_template("manage_user.html", data=data)

        else:
            return redirect("/login")

    @app.route("/createuser", methods=['POST', 'GET'])
    def create_user():
        """ add user detail """
        if request.method == 'POST':
            userdetail = {}
            userdetail["userid"] = request.form['user']
            userdetail["fname"] = request.form['fname']
            userdetail["lname"] = request.form['lname']
            userdetail["address"] = request.form['addr']
            userdetail["phone"] = request.form['phone']

            db_driver.save("userDetails", userdetail)

        return redirect("/manageuser")

    @app.route('/editdoctor/<id>')
    def edit_doctor(id):
        pass

    @app.route('/deletedoctor/<id>')
    def delete_doctor(id):
        pass

    @app.route('/managedoctor')
    def manage_doctor():
        user = session.get("user", None)
        if user and user["type"] == 2:
            query = f""" SELECT u.id, u.username, dd.name, dd.specialization, dd.avlFrom, 
                            dd.avlTo
                            FROM user as u JOIN doctorDetails as dd 
                            ON u.id = dd.userid 
                            WHERE u.type=1"""
            doctors = db_driver.execute_select(query, True)
            doctors = [] if doctors is None else doctors
            ids = [d['id'] for d in doctors]

            doctor_users = db_driver.read(
                "user", ["id", "username"], where=f"type=1")
            doctor_users = [] if doctor_users is None else doctor_users
            doctor_users = [d for d in doctor_users if d['id'] not in ids]

            specs = db_driver.read("specializations", ["id", "spname"])
            specs = [] if specs is None else specs

            for d in doctors:
                sid = d["specialization"]
                spec = [s["spname"] for s in specs if s['id'] == sid]
                d["specialization"] = sid if len(spec) == 0 else spec[0]

            data = {"doctors": doctors,
                    "doctor_users": doctor_users, "specs": specs}
            return render_template("manage_doctor.html", data=data)

        else:
            return redirect("/login")

    @app.route("/createdoctor", methods=['POST', 'GET'])
    def create_doctor():
        user = session.get("user", None)
        if user and user["type"] == 2:
            if request.method == 'POST':
                doctor_detail = {}
                doctor_detail["userid"] = request.form['user']
                doctor_detail["name"] = request.form['docname']
                doctor_detail["specialization"] = request.form['spec']
                doctor_detail["avlFrom"] = request.form['avlFrom']
                doctor_detail["avlTo"] = request.form['avlTo']

                db_driver.save("doctorDetails", doctor_detail)
            return redirect("/managedoctor")

        else:
            return redirect("/login")

    @app.route("/registeruser", methods=['POST', 'GET'])
    def register_user():
        user = session.get("user", None)
        if user and user["type"] == 2:
            if request.method == 'POST':
                u = {}
                u['username'] = request.form['username']
                u['password'] = request.form['password']
                u['type'] = request.form['type']

                db_driver.save("user", u)

            return redirect("/adminsite")

        else:
            return redirect("/login")

    @app.route("/adminsite")
    def adminsite():
        user = session.get("user", None)
        if user and user["type"] == 2:
            spects = db_driver.read("specializations", "*")
            spects = [] if spects is None else spects
            return render_template("adminsite.html", spects=spects)

        else:
            return redirect("/login")

    @app.route("/deletespecialization/<id>")
    def delete_specialization(id):
        """ delete a specialization """

        user = session.get("user", None)
        if user and user["type"] == 2:
            db_driver.remove("specializations", where=f"id={id}")
            return redirect('/adminsite')

        else:
            return redirect("/login")

    @app.route("/addspecialization", methods=['POST', 'GET'])
    def add_specialization():
        user = session.get("user")
        if user and user['type'] == 2:
            if request.method == 'POST':
                s = {}
                s["spname"] = str(request.form['spname'])
                print(s)
                db_driver.save("specializations", s)

            return redirect("/adminsite")

        else:
            return redirect("/login")

    # User Site
    @app.route("/createlog", methods=['POST', 'GET'])
    def createlog():
        """ save daily log """
        user = session.get("user", None)
        if user and user["type"] == 0:
            if request.method == 'POST':
                log = {}
                log['bp'] = request.form['bp']
                log['userid'] = user["id"]
                log['medicine'] = request.form['medicine']
                log['temp'] = request.form['temp']
                log['mood'] = request.form['gmood']
                log['logdate'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                db_driver.save("logs", log)

            else:
                Logger.error("invalid request, it should be POST")

            return redirect("/usersite")

        else:
            return redirect("/login")

    @app.route("/usersite", methods=['POST', 'GET'])
    def usersite():
        """ view usersite"""
        user = session.get("user", None)
        if user and user["type"] == 0:
            user_loges = db_driver.read(
                "logs", "*", where=f"userid={user['id']}")
            user_loges = [] if user_loges is None else user_loges
            return render_template("usersite.html", user_loges=user_loges)

        else:
            return redirect("/login")

    @app.route("/viewdoctors")
    def viewdoctors():
        """ view all available doctors """

        user = session.get("user", None)
        if user and user["type"] == 0:
            query = """ SELECT dd.id, dd.name, sp.spname, dd.avlFrom, dd.avlTo 
                           FROM doctorDetails as dd JOIN specializations as sp 
                           ON dd.specialization = sp.id """
            # query   = """ SELECT dd.id, ud.fname, ud.lname, dd.specialization, dd.avlFrom,
            #                 dd.avlTo FROM doctorDetails as dd JOIN specializations as sp
            #                 ON dd.userid = ud.userid """
            doctors = db_driver.execute_select(query, True)
            doctors = [] if doctors is None else doctors
            return render_template("viewdoctors.html", doctors=doctors)

        else:
            return redirect("/login")

    @app.route("/create_appointment", methods=['POST', 'GET'])
    def create_appointment():
        """ request appointment by patient """
        user = session.get("user", None)
        if user and user["type"] == 0:
            if request.method == 'POST':
                _app = {}
                _app["userid"] = user["id"]
                _app["doctor_id"] = request.form['doctor']
                _app["day"] = request.form['date']
                _app["timefrom"] = request.form['mf']
                _app["timeto"] = request.form['mt']
                _app["status"] = 0
                db_driver.save("UserAppointment", _app)

            return redirect("/appointment")

        else:
            return redirect("/login")

    @app.route("/appointment")
    def appointment():
        ''' display all appointments with create new appointment form '''
        user = session.get("user", None)
        if user and user["type"] == 0:
            # read appointments

            query = f""" SELECT ua.id, ua.timefrom, ua.timeto, ua.day, ua.status, 
                            ud.fname, ud.lname 
                            FROM UserAppointment as ua JOIN userDetails as ud 
                            ON ua.doctor_id = ud.userid 
                            WHERE ua.userid={user['id']}"""
            appointments = db_driver.execute_select(query, True)
            if appointments is None or len(appointments) == 0:
                appointments = []

            else:
                c = {0: "Requested", 1: "Approved", 2: "Not Approved"}
                for ap in appointments:
                    ap["status"] = c[ap["status"]]

            # read doctors
            query = """ SELECT dd.userid, ud.fname, ud.lname
                            FROM doctorDetails as dd JOIN userDetails as ud 
                            ON dd.userid = ud.userid """
            doctors = db_driver.execute_select(query, True)
            doctors = [] if doctors is None else doctors
            return render_template("appointment.html", appointments=appointments, doctors=doctors)

        else:
            return redirect("/login")

    # Doctor Site
    @app.route('/updateappointment/<id>/<status>')
    def update_appointment(id, status):
        user = session.get("user", None)
        if user and user["type"] == 1:
            ap = db_driver.read("userAppointment", "*",
                                where=f"id={id}", single=True)
            if ap:
                if ap["doctor_id"] == user["id"]:
                    ap["status"] = status
                    db_driver.update("userAppointment", ap, where=f"id={id}")
            return redirect("/doctorsite")

        else:
            return redirect("/login")

    @app.route("/schedmeetings")
    def sched_meetings():
        user = session.get("user", None)
        if user and user["type"] == 1:
            query = f""" SELECT ua.id, ua.userid, ua.doctor_id, ud.fname, ud.lname, ua.timefrom, 
                            ua.timeto, ua.day
                            FROM UserAppointment as ua JOIN userDetails as ud 
                            ON ua.userid = ud.userid 
                            WHERE ua.doctor_id={user['id']} AND ua.status=2"""
            data = db_driver.execute_select(query, True)
            appointments = [] if data is None else data

            return render_template("sched_meetings.html", appointments=appointments)

        else:
            return redirect("/login")

    @app.route("/doctorsite")
    def doctor_site():
        user = session.get("user", None)
        if user and user["type"] == 1:
            query = f""" SELECT ua.id, ua.userid, ua.doctor_id, ud.fname, ud.lname, ua.timefrom, 
                            ua.timeto, ua.day
                            FROM UserAppointment as ua JOIN userDetails as ud 
                            ON ua.userid = ud.userid 
                            WHERE ua.doctor_id={user['id']} AND ua.status=0"""
            data = db_driver.execute_select(query, True)
            appointments = [] if data is None else data
            return render_template("doctor_site.html", appointments=appointments)

        else:
            return redirect("/login")


except Exception as error:
    print(error)


if __name__ == "__main__":
    app.run(debug=True)
