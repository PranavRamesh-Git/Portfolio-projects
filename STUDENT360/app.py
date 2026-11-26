import os
import math
from datetime import date,timedelta
import uuid

from dotenv import load_dotenv
from flask import (Flask,flash,redirect,render_template,request,url_for,session,jsonify, send_from_directory)
from flask_wtf.csrf import CSRFProtect,generate_csrf
from psycopg.errors import UniqueViolation
from werkzeug.security import (check_password_hash,generate_password_hash)


from db import get_db_connection

load_dotenv()

app = Flask(__name__,template_folder="templates",static_folder="static")

csrf = CSRFProtect(app)

app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REACT_DIST = os.path.join(BASE_DIR,"frontend","dist")


@app.route("/api/csrf-token", methods=["GET"])
def csrf_token():
   return jsonify({
      "csrf_token": generate_csrf()
   })





@app.route("/student360", methods=["GET","POST"])
def login():
   if request.method == "POST":
      info = request.form.get('t-details',"").strip()
      password = request.form.get('password',"")
      with get_db_connection() as connection:
         with connection.cursor() as cursor:
               cursor.execute("select * from teachers where username = %s or email=%s or phonenumber=%s", (info,info,info,))
               user = cursor.fetchone()
               if user is None:
                  flash("Invalid Username or password","error")
                  return redirect(url_for('login'))
               else:
                  if check_password_hash(user['password_hash'],password):
                     session['teacher_id'] = user['teacher_id']
                     session['username'] = user['username']
                     session['role'] = user['role']
                     session.permanent = True
                     flash("Login successfull!!!","success")
                     return redirect(url_for('dashboard'))
                  else:
                     flash("Invalid Username or password","error")
                     return redirect(url_for('login'))   
                                         
   return render_template('login.html')




@app.route("/student360/logout")
def logout():
   session.clear()
   return redirect(url_for('login'))


@app.route("/student360/dashboard")
def dashboard():

   if "teacher_id" not in session:
      return redirect(url_for("login"))

   return send_from_directory(REACT_DIST,"index.html")

@app.route("/assets/<path:filename>")
def react_assets(filename):

   return send_from_directory(os.path.join(REACT_DIST, "assets"),filename)


@app.route("/favicon.svg")
def react_favicon():
   return send_from_directory(REACT_DIST,"favicon.svg")

@app.route('/api/class_access')
def get_classAccess():
   if "teacher_id" not in session:
      return jsonify({
         "error": "Please log in"
      }), 401
   teacher_id = session["teacher_id"]
   with get_db_connection() as connection:
      with connection.cursor() as cursor:
         cursor.execute("select class_access from teachers where teacher_id = %s",(teacher_id,))
         result = cursor.fetchone()
         if not result :
            classes = []
         else:   
            classes = list(result['class_access'])

         return jsonify({
            "classes": classes
         })





@app.route("/api/students")
def students():
   if "teacher_id" not in session:
      return jsonify({
         "error": "Please log in"
      }), 401
   teacher_id = session["teacher_id"]
   search = request.args.get('search','').strip()
   class_name = request.args.get('class_name','').strip()   
   conditions = []
   params = []
   teacher_id = session["teacher_id"]
   with get_db_connection() as connection:
      with connection.cursor() as cursor:
         cursor.execute("select class_access from teachers where teacher_id = %s",(teacher_id,))
         result = cursor.fetchone()
         classes = list(result['class_access'])

         if search:
            conditions.append(""" 
               full_name ilike %s
            """)
            search_value = f"%{search}%"
            params.extend([search_value])

         if class_name:
            conditions.append(" class_name = %s")
            params.extend([class_name])

         if class_name not in classes:
            return jsonify({
               "students": None
            }),403            

         if search and not class_name:
            conditions.append(" class_name = ANY(%s)")
            params.extend([classes])            

         if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
            query = f"select * from view_student_profiles {where_clause} "
            cursor.execute(query,params)
            students = cursor.fetchall()
         else:
            students = []

         return jsonify({
            "students": students
         })

@app.route('/api/studentDetails', methods=["GET","POST"])
def student_details():
   if "teacher_id" not in session:
      return redirect(url_for('login'))
   teacher_id = session["teacher_id"]
   data = request.get_json()
   student_id = int(data["student_id"]);
   class_name = data["class_name"]
   with get_db_connection() as connection:
      with connection.cursor() as cursor:

         cursor.execute("select * from view_student_profiles where student_id = %s and class_name = %s",(student_id,class_name))  
         student_details = cursor.fetchone()
         if student_details:
            return jsonify({
               "status": "success",
               "student_details": student_details
            })
         else:
            return jsonify({
               "status": "failure",
               "student_details": []
            })            
         
            
@app.route('/api/studentMarksheet', methods=["POST"])
def student_marksheet():
   if "teacher_id" not in session:
      return jsonify({"error": "Please log in"}), 401
   teacher_id = session["teacher_id"]
   data = request.get_json(silent=True)

   
   if not isinstance(data,dict):
      return jsonify({
         "error": "Invalid JSON"
      }),400

   try:
      student_id = int(data.get("student_id"))
   except (TypeError, ValueError):
      return jsonify({
         "error": "Invalid student_id"
      }),400

   if student_id <= 0:
      return jsonify({
         "error": "Invalid student_id"
      }),400

   student_id = int(data["student_id"])
   class_name = data.get('class_name')
   if not isinstance(class_name,str) or not class_name.strip():
         return jsonify({
         "error": "Invalid class_name"
      }),400   

   class_name = class_name.strip()
   marks = {}



   with get_db_connection() as connection:
      with connection.cursor() as cursor:

         cursor.execute("select * from teachers where teacher_id = %s and %s = ANY(class_access)",(teacher_id,class_name,))  
         result = cursor.fetchone()
         if not result:
            return jsonify({
            "error": "class access not given"
         }),403                      

         cursor.execute("select sub1,sub2,sub3,sub4,sub5 from view_student_profiles where student_id = %s and class_name = %s",(student_id,class_name))  
         subjects = cursor.fetchone()
         if subjects is None:
            return jsonify({"error": "Student not found"}), 404

         subs = [sub for sub in subjects.values() if sub]
         if subjects:
            for sub in subjects.values():
               if not sub:
                  continue
               cursor.execute("select * from view_student_marks where student_id = %s and class_name = %s and subject = %s",(student_id,class_name,sub))  
               result = cursor.fetchall()
               marks[sub] = result

            cursor.execute("select * from view_student_rank where student_id = %s",(student_id,))  
            stats = cursor.fetchone()

            cursor.execute("select * from subject_wise_marks where student_id = %s",(student_id,))  
            result = cursor.fetchall()
            subMarks = {}
            for sub in result:
               subMarks[sub["subject"]] = sub

            return jsonify({
               "status": "success",
               "totalMarks": marks,
               "subMarks": subMarks,
               "stats": stats,
               "subs": subs
            })
         else:
            return jsonify({
               "status": "failure",
               "marks": {}
            }),404    
         
@app.route('/api/analytics/SectionSpecific', methods=["POST"])
def analytics_SectionSpecific():
   if "teacher_id" not in session:
      return jsonify({"error": "Please log in"}), 401
   teacher_id = session["teacher_id"]
   data = request.get_json(silent=True)

   
   if not isinstance(data,dict):
      return jsonify({
         "error": "Invalid JSON"
      }),400

   class_name = data.get('class_name')
   assessment_class = data.get('assessment_class')
   if not isinstance(assessment_class,str) or not assessment_class.strip():
         return jsonify({
         "error": "Invalid class_name"
      }),400   

   assesment_class = assessment_class.strip()
   if not isinstance(class_name,str) or not class_name.strip():
         return jsonify({
         "error": "Invalid class_name"
      }),400   

   class_name = class_name.strip()   
   senior = ["ENG" ,"MATH", "PHY", "CHEM",  "BIO", "CS","ECO", "ACCOUNTS", "BS", "BUSINESSMATH"]
   junior = ["ENG" ,"MATH", "SCIENCE" ,"SST", "HINDI", "FRENCH", "GERMAN","TAMIL", "SPANISH"]
   try:
      with get_db_connection() as connection:
         with connection.cursor() as cursor:
            cursor.execute("select student_id,class_name,full_name,total_percentage,class_rank as rank from view_student_rank where class_name = %s order by class_rank",(class_name,))
            ranked_students = cursor.fetchall()

            cursor.execute("select max(total_percentage) as max_percent ,min(total_percentage) as min_percent,ROUND(AVG(total_percentage),2) as avg_percent from view_student_rank where class_name =%s",(class_name,))
            overall = cursor.fetchone()

            subData = {}

            if assesment_class in ('11','12'):
               if class_name == '12A':
                  senior = ["ENG" ,"MATH", "PHY", "CHEM", "CS"]
               elif class_name == '12B':
                  senior = ["ENG" ,"MATH", "PHY", "CHEM",  "BIO"]
               elif class_name == '12C':
                  senior = ["ENG" ,"MATH", "PHY", "CHEM",  "BIO", "ECO"]
               elif class_name == '12D':
                  senior = ["ENG" ,"MATH", "ECO", "ACCOUNTS", "BS", "BUSINESSMATH"]

               for sub in senior:
                  cursor.execute("select max(subject_percentage) as max_percent, min(subject_percentage) as min_percent, ROUND(AVG(subject_percentage),2) as avg_percent from subject_wise_marks where class_name = %s and subject = %s",(class_name,sub,))
                  ans = cursor.fetchone()
                  if not ans or not ans["max_percent"] or not ans["min_percent"] or not ans["avg_percent"]:
                     continue
                  subData[sub] = ans

            else:
               for sub in junior:
                  cursor.execute("select max(subject_percentage) as max_percent, min(subject_percentage) as min_percent, ROUND(AVG(subject_percentage),2) as avg_percent from subject_wise_marks where class_name = %s and subject = %s",(class_name,sub,))
                  ans = cursor.fetchone()
                  if not ans:
                     continue
                  subData[sub] = ans

            return jsonify({
               "status": "success",
               "ranked_list": ranked_students,
               "overall": overall,
               "subData": subData
            }) 
   except:                          
         return jsonify({
            "status": "failure",
         })               

@app.route('/api/analytics/ClassOverall', methods=["POST"])
def analytics_overall():
   if "teacher_id" not in session:
      return jsonify({"error": "Please log in"}), 401
   teacher_id = session["teacher_id"]
   data = request.get_json(silent=True)

   
   if not isinstance(data,dict):
      return jsonify({
         "error": "Invalid JSON"
      }),400


   assessment_class = data.get('assessment_class')
   if not isinstance(assessment_class,str) or not assessment_class.strip():
         return jsonify({
         "error": "Invalid class_name"
      }),400   

   assessment_class = assessment_class.strip()
   senior = ["ENG" ,"MATH", "PHY", "CHEM",  "BIO", "CS","ECO", "ACCOUNTS", "BS", "BUSINESSMATH"]
   junior = ["ENG" ,"MATH", "SCIENCE" ,"SST", "HINDI", "FRENCH", "GERMAN","TAMIL", "SPANISH"]

   try:
      with get_db_connection() as connection:
         with connection.cursor() as cursor:
            cursor.execute("select full_name,total_percentage,student_id,class_name,overall_rank as rank from view_student_rank where assessment_class = %s order by overall_rank",(assessment_class,))
            ranked_students = cursor.fetchall()

            cursor.execute("select max(total_percentage) as max_percent ,min(total_percentage) as min_percent,ROUND(AVG(total_percentage),2) as avg_percent from view_student_rank where assessment_class =%s",(assessment_class,))
            overall = cursor.fetchone()
            subData = {}

            if assessment_class in ('11','12'):           
               for sub in senior:
                  cursor.execute("select max(subject_percentage) as max_percent, min(subject_percentage) as min_percent, ROUND(AVG(subject_percentage),2) as avg_percent from subject_wise_marks where assessment_class = %s and subject = %s",(assessment_class,sub,))
                  ans = cursor.fetchone()
                  if not ans:
                     continue
                  subData[sub] = ans

            else:
               for sub in junior:
                  cursor.execute("select max(subject_percentage) as max_percent, min(subject_percentage) as min_percent, ROUND(AVG(subject_percentage),2) as avg_percent from subject_wise_marks where assessment_class = %s and subject = %s",(assessment_class,sub,))
                  ans = cursor.fetchone()
                  if not ans:
                     continue
                  subData[sub] = ans

            return jsonify({
               "status": "success",
               "ranked_list": ranked_students,
               "overall": overall,
               "subData": subData
            })
   except:
         return jsonify({
            "status": "failure",
         })               

               


if __name__ == "__main__":
   app.run(host='0.0.0.0',debug=True)




