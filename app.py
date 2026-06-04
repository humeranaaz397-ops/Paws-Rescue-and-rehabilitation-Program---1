import os
import time
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = "paws_rescue_rehabilitation_secret_key"

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database credentials configuration and fallback helper
def get_db_connection():
    credentials = [
        # {"host": "localhost", "user": "root", "password": "humera0825", "database": "paws_db"},
        # {"host": "localhost", "user": "root", "password": "", "database": "paws_db"},
        # {"host": "localhost", "user": "root", "password": "root", "database": "paws_db"},
        {"host": "zephyr.proxy.rlwy.net", "user": "root", "password": "axGHWbCCJfVVRBszebRZXiYHXuvitPez", "database": "railway","port":40097}
    ]
    for cred in credentials:
        
        try:
            return mysql.connector.connect(**cred)
        except mysql.connector.Error:
            continue
    raise Exception("Database connection failed. Make sure MySQL is running.")

def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args=()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id

def sync_completed_rescues_to_medical():
    try:
        completed_reports = query_db("SELECT * FROM reports WHERE status IN ('Completed', 'Resolved')")
        for report in completed_reports:
            case_id = report['id']
            existing = query_db("SELECT * FROM medical_care WHERE case_name LIKE %s", (f"% (Case #{case_id})",), one=True)
            if not existing:
                animal_type = report.get('animal_type') or 'Stray Animal'
                description = report.get('description') or 'No description provided.'
                modify_db(
                    "INSERT INTO medical_care (case_name, animal_type, status, description, vet_assigned) "
                    "VALUES (%s, %s, 'Pending', %s, NULL)",
                    (f"Rescued {animal_type} (Case #{case_id})", animal_type, description)
                )
    except Exception as e:
        print(f"Error syncing completed rescues: {e}")

# Automatic database setup and seeding
def init_db():
    credentials = [
        {"host": "localhost", "user": "root", "password": "humera0825"},
        {"host": "localhost", "user": "root", "password": "11012518"},
        {"host": "localhost", "user": "root", "password": ""},
        {"host": "localhost", "user": "root", "password": "root"}
        
    ]
    
    conn = None
    for cred in credentials:
        try:
            conn = mysql.connector.connect(**cred)
            break
        except mysql.connector.Error:
            continue
            
    if not conn:
        print("Could not connect to MySQL server. Please make sure MySQL is running.")
        return
        
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS paws_db")
        conn.commit()
        cursor.close()
        conn.close()
        
        # Connect to paws_db to execute table creations
        conn_db = None
        for cred in credentials:
            try:
                cred_db = cred.copy()
                cred_db["database"] = "paws_db"
                conn_db = mysql.connector.connect(**cred_db)
                break
            except mysql.connector.Error:
                continue
                
        if not conn_db:
            print("Could not connect to paws_db database.")
            return
            
        cursor = conn_db.cursor()
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            if os.path.exists("database.txt"):
                with open("database.txt", "r", encoding="utf-8") as f:
                    sql = f.read()
                # Split statements by semicolon, run them
                statements = re.split(r';\s*\n', sql)
                for stmt in statements:
                    stmt = stmt.strip()
                    if stmt:
                        try:
                            cursor.execute(stmt)
                        except mysql.connector.Error as err:
                            if err.errno != 1050: # Table already exists
                                print(f"SQL Error: {err}")
                conn_db.commit()
                print("Database initialized successfully.")
            else:
                print("database.txt not found. Cannot initialize schema.")
        else:
            # Check and add new columns dynamically if database/tables already exist
            alterations = [
                ("users", "capacity", "ALTER TABLE users ADD COLUMN capacity INT DEFAULT 50"),
                ("users", "cases", "ALTER TABLE users ADD COLUMN cases INT DEFAULT 0"),
                ("users", "status", "ALTER TABLE users ADD COLUMN status VARCHAR(50) DEFAULT 'Active'"),
                ("users", "delete_reason", "ALTER TABLE users ADD COLUMN delete_reason VARCHAR(255) DEFAULT ''"),
                ("shelters", "status", "ALTER TABLE shelters ADD COLUMN status VARCHAR(50) DEFAULT 'Active'"),
                ("shelters", "delete_reason", "ALTER TABLE shelters ADD COLUMN delete_reason VARCHAR(255) DEFAULT ''"),
                ("reports", "resolved_image_filename", "ALTER TABLE reports ADD COLUMN resolved_image_filename VARCHAR(255) DEFAULT ''"),
                ("reports", "animal_type", "ALTER TABLE reports ADD COLUMN animal_type VARCHAR(100) DEFAULT 'Stray Animal'"),
                ("pets", "uploaded_by", "ALTER TABLE pets ADD COLUMN uploaded_by INT DEFAULT NULL")
            ]
            for table, col, alter_stmt in alterations:
                try:
                    cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{col}'")
                    if not cursor.fetchone():
                        cursor.execute(alter_stmt)
                        conn_db.commit()
                except mysql.connector.Error as err:
                    print(f"Error altering table {table}: {err}")
        # Ensure all ngo_members exist in the users table with role 'rescue'
        try:
            cursor.execute("SELECT name, email, phone FROM ngo_members")
            ngo_members_list = cursor.fetchall()
            for m_name, m_email, m_phone in ngo_members_list:
                cursor.execute("SELECT id FROM users WHERE email = %s", (m_email,))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO users (name, email, phone, password, role) VALUES (%s, %s, %s, 'rescue123', 'rescue')",
                        (m_name, m_email, m_phone)
                    )
            conn_db.commit()
        except mysql.connector.Error as err:
            print(f"Error syncing ngo_members to users: {err}")

        cursor.close()
        conn_db.close()
        sync_completed_rescues_to_medical()
    except Exception as e:
        print(f"DB Init Exception: {e}")

# Automatically initialize and migrate database on import/startup
init_db()

# ==================== VISITOR & AUTH ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = query_db("SELECT * FROM users WHERE email = %s AND password = %s", (email, password), one=True)
        if user:
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_profile_img'] = user['profile_img']
            
            # Redirect based on user role
            if user['role'] == 'user':
                return redirect(url_for('user_dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'ngo':
                return redirect(url_for('ngo_dashboard'))
            elif user['role'] == 'rescue':
                return redirect(url_for('rescue_dashboard'))
        else:
            return render_template('login.html', error="Invalid Credentials")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            return render_template('registration.html', error="Passwords do not match")
            
        # Check if email already registered
        exists = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
        if exists:
            return render_template('registration.html', error="Email is already registered")
            
        modify_db(
            "INSERT INTO users (name, email, phone, password, role) VALUES (%s, %s, %s, %s, 'user')",
            (name, email, phone, password)
        )
        return redirect(url_for('login'))
        
    return render_template('registration.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/visitor/about-us')
def visitor_about_us():
    return render_template('visitor/aboutus-home.html')

@app.route('/visitor/adoption-home')
def visitor_adoption_home():
    return render_template('visitor/adoption-home.html')

@app.route('/visitor/contact')
def visitor_contact():
    return render_template('visitor/contact-home.html')

@app.route('/visitor/pet-adoption')
def visitor_pet_adoption():
    return render_template('visitor/Home-Pet-Adoption.html')

@app.route('/visitor/pets', methods=['GET', 'POST'])
def visitor_pets():
    if request.method == 'POST':
        # Visitor uploads a pet for adoption
        name = request.form.get('name')
        age = request.form.get('age')
        type_ = request.form.get('type')
        breed = request.form.get('breed', '')
        gender = request.form.get('gender')
        location = request.form.get('location')
        contact = request.form.get('contact')
        description = request.form.get('description')
        
        file = request.files.get('image')
        stored_filename = "default_pet.png"
        if file:
            # generate unique filename and save to uploads folder
            filename = str(int(time.time())) + "_" + file.filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            stored_filename = filename

        modify_db(
            "INSERT INTO pets (name, type, gender, age, weight, breed, location, health, description, image_filename, status) "
            "VALUES (%s, %s, %s, %s, 'N/A', %s, %s, 'Healthy', %s, %s, 'Available')",
            (name, type_, gender, age, breed, location, description, stored_filename)
        )
        return jsonify({"success": True})
        
    return render_template('visitor/PET-for-adoption.html')

@app.route('/visitor/safe-shelters')
def visitor_safe_shelters():
    shelters = query_db("SELECT * FROM shelters")
    return render_template('visitor/safe-shelter-home.html', shelters=shelters)

@app.route('/visitor/report-injured', methods=['GET', 'POST'])
def visitor_report_injured():
    if request.method == 'POST':
        location = request.form.get('location')
        lat = request.form.get('latitude') or None
        lng = request.form.get('longitude') or None
        map_link = request.form.get('mapLink')
        description = request.form.get('description')
        
        file = request.files.get('image')
        stored_filename = "default_injured.png"
        if file:
            filename = str(int(time.time())) + "_" + file.filename
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            stored_filename = filename

        modify_db(
            "INSERT INTO reports (image_filename, location, lat, lng, map_link, description, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, 'Pending')",
            (stored_filename, location, lat, lng, map_link, description)
        )
        return jsonify({"success": True})
        
    return render_template('visitor/upload-image-home.html')

@app.route('/visitor/medical-care')
def visitor_medical_care():
    return render_template('visitor/medical-care-homepage.html')

@app.route('/visitor/medical-care/option-1')
def visitor_medical_care_opt1():
    return render_template('visitor/medical-care-option-1-home.html')

@app.route('/visitor/medical-care/option-2')
def visitor_medical_care_opt2():
    return render_template('visitor/medical-care-option-2-home.html')


# ==================== REGISTERED USER ROUTES ====================

def login_required(role=None):
    def wrapper(f):
        def decorator(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('user_role') != role:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        decorator.__name__ = f.__name__
        return decorator
    return wrapper

@app.route('/user/dashboard')
@login_required('user')
def user_dashboard():
    return render_template('User/user-home-page.html')

@app.route('/user/profile', methods=['GET', 'POST'])
@login_required('user')
def user_profile():
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        # Profile image upload
        file = request.files.get('profile_img')
        if file:
            filename = str(int(time.time())) + "_" + file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_img = "/static/uploads/" + filename
            modify_db(
                "UPDATE users SET name=%s, email=%s, phone=%s, location=%s, profile_img=%s WHERE id=%s",
                (name, email, phone, location, profile_img, user_id)
            )
            session['user_profile_img'] = profile_img
        else:
            modify_db(
                "UPDATE users SET name=%s, email=%s, phone=%s, location=%s WHERE id=%s",
                (name, email, phone, location, user_id)
            )
        
        session['user_name'] = name
        session['user_email'] = email
        return redirect(url_for('user_profile'))
        
    user = query_db("SELECT * FROM users WHERE id = %s", (user_id,), one=True)
    return render_template('User/profile.html', user=user)

@app.route('/user/about-us')
@login_required('user')
def user_about_us():
    return render_template('User/user-aboutus.html')

@app.route('/user/contact')
@login_required('user')
def user_contact():
    return render_template('User/user-contact.html')

@app.route('/user/safe-shelters')
@login_required('user')
def user_safe_shelters():
    shelters = query_db("SELECT * FROM shelters")
    return render_template('User/user-safe-shelter.html', shelters=shelters)

@app.route('/user/report-injured', methods=['GET', 'POST'])
@login_required('user')
def user_report_injured():
    if request.method == 'POST':
        location = request.form.get('location')
        lat = request.form.get('latitude') or None
        lng = request.form.get('longitude') or None
        map_link = request.form.get('mapLink')
        description = request.form.get('description')
        user_id = session['user_id']
        
        file = request.files.get('image')
        filename = "default_injured.png"
        if file:
            filename = str(int(time.time())) + "_" + file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename = "/static/uploads/" + filename
            
        modify_db(
            "INSERT INTO reports (image_filename, location, lat, lng, map_link, description, status, reported_by) "
            "VALUES (%s, %s, %s, %s, %s, %s, 'Pending', %s)",
            (filename, location, lat, lng, map_link, description, user_id)
        )
        return jsonify({"success": True})
        
    return render_template('User/user-upload-image.html')

@app.route('/user/medical-care')
@login_required('user')
def user_medical_care():
    return render_template('User/user-medical-care-homepage.html')

@app.route('/user/medical-care/option-1')
@login_required('user')
def user_medical_care_opt1():
    return render_template('User/user-medical-care-option-1.html')

@app.route('/user/medical-care/option-2')
@login_required('user')
def user_medical_care_opt2():
    return render_template('User/user-medical-care-option-2.html')

@app.route('/user/pet-adoption')
@login_required('user')
def user_pet_adoption():
    # Load all available pets from the database to display in the adoption section
    pets = query_db("SELECT * FROM pets")
    return render_template('User/User-PET-Adoption.html', pets=pets)

@app.route('/user/pets')
@login_required('user')
def user_pets():
    # Redirect /user/pets to the unified pet adoption page to show both "Adopt PET" and "Upload PETS for Adoption" options
    return redirect(url_for('user_pet_adoption'))

@app.route('/user/pet-detail/<int:pet_id>')
@login_required('user')
def user_pet_detail(pet_id):
    pet = query_db("SELECT * FROM pets WHERE id = %s", (pet_id,), one=True)
    if not pet:
        return redirect(url_for('user_pets'))
    return render_template('User/petinfo.html', pet=pet)

@app.route('/user/pet-application/<int:pet_id>', methods=['GET', 'POST'])
@login_required('user')
def user_pet_application(pet_id):
    pet = query_db("SELECT * FROM pets WHERE id = %s", (pet_id,), one=True)
    if not pet:
        return redirect(url_for('user_pets'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        location = request.form.get('location')
        home_type = request.form.get('home_type')
        has_pets = request.form.get('has_pets')
        reason = request.form.get('reason')
        user_id = session['user_id']
        
        file = request.files.get('aadhar')
        aadhar_path = ""
        if file:
            filename = str(int(time.time())) + "_" + file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            aadhar_path = "/static/uploads/" + filename
            
        # Insert application
        modify_db(
            "INSERT INTO adoption_applications (user_id, pet_id, full_name, email, phone, location, aadhar_path, home_type, has_pets, reason, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')",
            (user_id, pet_id, full_name, email, phone, location, aadhar_path, home_type, has_pets, reason)
        )
        
        # Update pet status to pending
        modify_db("UPDATE pets SET status = 'Pending' WHERE id = %s", (pet_id,))
        
        return redirect(url_for('user_notifications'))
        
    return render_template('User/pet-application-form.html', pet=pet)

@app.route('/user/upload-pet', methods=['GET', 'POST'])
@login_required('user')
def user_upload_pet():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        type_ = request.form.get('type')
        breed = request.form.get('breed', '')
        gender = request.form.get('gender')
        location = request.form.get('location')
        description = request.form.get('description')
        user_id = session['user_id']
        file = request.files.get('image')
        filename = "default_pet.png"
        if file:
            filename = str(int(time.time())) + "_" + file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filename = "/static/uploads/" + filename
            
        modify_db(
            "INSERT INTO pets (name, type, gender, age, weight, breed, location, health, description, image_filename, status, uploaded_by) "
            "VALUES (%s, %s, %s, %s, 'N/A', %s, %s, 'Healthy', %s, %s, 'Available', %s)",
            (name, type_, gender, age, breed, location, description, filename, user_id)
        )
        return jsonify({"success": True})
        
    return render_template('User/upload-PET-for-Adoption.html')

@app.route('/user/notifications')
@login_required('user')
def user_notifications():
    user_id = session['user_id']
    # 1. Fetch adoption applications submitted by the user
    applications = query_db(
        "SELECT a.*, p.name as pet_name, p.image_filename as pet_image, p.type as pet_type "
        "FROM adoption_applications a JOIN pets p ON a.pet_id = p.id WHERE a.user_id = %s "
        "ORDER BY a.applied_at DESC",
        (user_id,)
    )
    
    # 2. Fetch injured animal reports submitted by the user
    reports = query_db(
        "SELECT * FROM reports WHERE reported_by = %s "
        "ORDER BY reported_at DESC",
        (user_id,)
    )
    
    # 3. Fetch pets uploaded for adoption by the user
    uploaded_pets = query_db(
        "SELECT * FROM pets WHERE uploaded_by = %s",
        (user_id,)
    )
    
    # Safe date formatting in Python
    for app_rec in applications:
        dt = app_rec.get('applied_at')
        if dt:
            if isinstance(dt, str):
                try:
                    dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
            if hasattr(dt, 'strftime'):
                app_rec['formatted_date'] = dt.strftime('%d %b %Y • %I:%M %p')
            else:
                app_rec['formatted_date'] = str(dt)
        else:
            app_rec['formatted_date'] = ''

    for rep in reports:
        dt = rep.get('reported_at')
        if dt:
            if isinstance(dt, str):
                try:
                    dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
            if hasattr(dt, 'strftime'):
                rep['formatted_date'] = dt.strftime('%d %b %Y • %I:%M %p')
            else:
                rep['formatted_date'] = str(dt)
        else:
            rep['formatted_date'] = ''
            
    return render_template(
        'User/notification-user.html',
        applications=applications,
        reports=reports,
        uploaded_pets=uploaded_pets
    )


# ==================== NGO REPRESENTATIVE ROUTES ====================

@app.route('/ngo/dashboard')
@login_required('ngo')
def ngo_dashboard():
    # Counts for dashboard
    rescue_cases_count = query_db("SELECT COUNT(*) as count FROM reports", one=True)['count']
    shelters_count = query_db("SELECT COUNT(*) as count FROM shelters", one=True)['count']
    medical_cases_count = query_db("SELECT COUNT(*) as count FROM medical_care", one=True)['count']
    adoption_requests_count = query_db("SELECT COUNT(*) as count FROM adoption_applications", one=True)['count']
    
    # Simple recent listings
    recent_rescues = query_db("SELECT * FROM reports ORDER BY id DESC LIMIT 5")
    
    return render_template(
        'NGO/NGO_Dashboard.html',
        rescue_count=rescue_cases_count,
        shelters_count=shelters_count,
        medical_count=medical_cases_count,
        adoption_count=adoption_requests_count,
        recent_rescues=recent_rescues
    )

@app.route('/ngo/rescue', methods=['GET', 'POST'])
@login_required('ngo')
def ngo_rescue():
    if request.method == 'POST':
        action = request.form.get('action')
        case_id = request.form.get('case_id')
        
        if action == 'assign':
            member_id = request.form.get('member_id')
            if not member_id or member_id == 'None' or member_id == '':
                member_id = None
            modify_db("UPDATE reports SET assigned_to = %s, status = 'Assigned' WHERE id = %s", (member_id, case_id))
        elif action == 'reject':
            reason = request.form.get('reason')
            modify_db("UPDATE reports SET status = 'Rejected', rejection_reason = %s WHERE id = %s", (reason, case_id))
            
        return redirect(url_for('ngo_rescue'))
        
    cases = query_db(
        "SELECT r.*, u.name as reported_by_name, u.phone as reported_by_phone, "
        "a.name as assigned_name, a.email as assigned_email, a.phone as assigned_phone "
        "FROM reports r "
        "LEFT JOIN users u ON r.reported_by = u.id "
        "LEFT JOIN users a ON r.assigned_to = a.id"
    )
    members = query_db(
        "SELECT u.id as user_id, u.name, u.email, u.phone, "
        "COALESCE(m.role, 'Rescue Member') as role "
        "FROM users u "
        "LEFT JOIN ngo_members m ON u.email = m.email "
        "WHERE u.role = 'rescue'"
    )
    return render_template('NGO/NGO_Rescue.html', cases=cases, members=members)

@app.route('/ngo/shelters')
@login_required('ngo')
def ngo_shelters():
    shelters = query_db("SELECT * FROM shelters")
    return render_template('NGO/NGO_Shelters.html', shelters=shelters)

@app.route('/ngo/adoption')
@login_required('ngo')
def ngo_adoption():
    # Load all applications
    applications = query_db("SELECT a.*, p.name as pet_name FROM adoption_applications a JOIN pets p ON a.pet_id = p.id")
    
    adopted_count = query_db("SELECT COUNT(*) as count FROM adoption_applications WHERE status='Approved'", one=True)['count']
    pending_count = query_db("SELECT COUNT(*) as count FROM adoption_applications WHERE status='Pending'", one=True)['count']
    total_count = len(applications)
    
    return render_template(
        'NGO/NGO_adoption.html', 
        applications=applications, 
        adopted_count=adopted_count,
        pending_count=pending_count,
        total_count=total_count
    )

@app.route('/ngo/adoption/<int:app_id>', methods=['GET', 'POST'])
@login_required('ngo')
def ngo_adoption_review(app_id):
    if request.method == 'POST':
        status = request.form.get('status') # 'Approved' / 'Rejected'
        meeting_time = request.form.get('meeting_time')
        reason = request.form.get('reason')
        
        if status == 'Approved':
            modify_db("UPDATE adoption_applications SET status = 'Approved', meeting_time = %s WHERE id = %s", (meeting_time, app_id))
            # Also update pet status to Adopted
            app_rec = query_db("SELECT pet_id FROM adoption_applications WHERE id = %s", (app_id,), one=True)
            if app_rec:
                modify_db("UPDATE pets SET status = 'Adopted' WHERE id = %s", (app_rec['pet_id'],))
        elif status == 'Rejected':
            modify_db("UPDATE adoption_applications SET status = 'Rejected', rejection_reason = %s WHERE id = %s", (reason, app_id))
            # Put pet back to Available
            app_rec = query_db("SELECT pet_id FROM adoption_applications WHERE id = %s", (app_id,), one=True)
            if app_rec:
                modify_db("UPDATE pets SET status = 'Available' WHERE id = %s", (app_rec['pet_id'],))
        elif status == 'Pending':
            modify_db("UPDATE adoption_applications SET status = 'Pending', meeting_time = NULL, rejection_reason = NULL WHERE id = %s", (app_id,))
            app_rec = query_db("SELECT pet_id FROM adoption_applications WHERE id = %s", (app_id,), one=True)
            if app_rec:
                modify_db("UPDATE pets SET status = 'Pending' WHERE id = %s", (app_rec['pet_id'],))
                
        return redirect(url_for('ngo_adoption_review', app_id=app_id))
        
    app_details = query_db(
        "SELECT a.*, p.name as pet_name, p.type as pet_type, u.name as user_name "
        "FROM adoption_applications a JOIN pets p ON a.pet_id = p.id JOIN users u ON a.user_id = u.id WHERE a.id = %s",
        (app_id,), one=True
    )
    if not app_details:
        return redirect(url_for('ngo_adoption'))
    return render_template('NGO/NGO_adoption_user1.html', app=app_details)

@app.route('/ngo/medical-care', methods=['GET', 'POST'])
@login_required('ngo')
def ngo_medical_care():
    sync_completed_rescues_to_medical()
    if request.method == 'POST':
        case_name = request.form.get('case_name')
        animal_type = request.form.get('animal_type')
        description = request.form.get('description')
        vet_assigned = request.form.get('vet_assigned')
        
        modify_db(
            "INSERT INTO medical_care (case_name, animal_type, status, description, vet_assigned) "
            "VALUES (%s, %s, 'Pending', %s, %s)",
            (case_name, animal_type, description, vet_assigned)
        )
        return redirect(url_for('ngo_medical_care'))
        
    cases = query_db("SELECT * FROM medical_care")
    return render_template('NGO/NGO_medical_care.html', cases=cases)

@app.route('/ngo/medical-care/assign/<int:case_id>', methods=['POST'])
@login_required('ngo')
def ngo_assign_doctor(case_id):
    doctor = request.form.get('doctor')
    modify_db(
        "UPDATE medical_care SET vet_assigned = %s, status = 'Ongoing' WHERE id = %s",
        (doctor, case_id)
    )
    return redirect(url_for('ngo_medical_care'))

@app.route('/ngo/add-rescue-member', methods=['GET', 'POST'])
@login_required('ngo')
def ngo_add_rescue_member():
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Check if already exists
        exists = query_db("SELECT * FROM ngo_members WHERE email = %s", (email,), one=True)
        if not exists:
            modify_db(
                "INSERT INTO ngo_members (name, role, email, phone) VALUES (%s, %s, %s, %s)",
                (name, role, email, phone)
            )
            # Also create user account with role='rescue'
            modify_db(
                "INSERT INTO users (name, email, phone, password, role) VALUES (%s, %s, %s, 'rescue123', 'rescue')",
                (name, email, phone)
            )
        return redirect(url_for('ngo_add_rescue_member'))
        
    members = query_db("SELECT * FROM ngo_members")
    return render_template('NGO/NGO_add_Rescue_Member.html', members=members)

@app.route('/ngo/delete-rescue-member/<int:member_id>', methods=['POST'])
@login_required('ngo')
def ngo_delete_rescue_member(member_id):
    member = query_db("SELECT email FROM ngo_members WHERE id = %s", (member_id,), one=True)
    if member:
        modify_db("DELETE FROM users WHERE email = %s AND role = 'rescue'", (member['email'],))
        modify_db("DELETE FROM ngo_members WHERE id = %s", (member_id,))
    return redirect(url_for('ngo_add_rescue_member'))

@app.route('/ngo/edit-rescue-member/<int:member_id>', methods=['POST'])
@login_required('ngo')
def ngo_edit_rescue_member(member_id):
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    
    current = query_db("SELECT email FROM ngo_members WHERE id = %s", (member_id,), one=True)
    if current:
        modify_db(
            "UPDATE ngo_members SET name = %s, email = %s, phone = %s WHERE id = %s",
            (name, email, phone, member_id)
        )
        modify_db(
            "UPDATE users SET name = %s, email = %s, phone = %s WHERE email = %s AND role = 'rescue'",
            (name, email, phone, current['email'])
        )
    return redirect(url_for('ngo_add_rescue_member'))


# ==================== RESCUE TEAM ROUTES ====================

# ==================== NEW RESCUE STATUS FLOW ROUTES ====================

@app.route('/admin/assign_rescuer', methods=['POST'])
@app.route('/admin/assign-rescuer', methods=['POST'])
def assign_rescuer():
    # Make sure user is logged in as admin or ngo
    if 'user_id' not in session or session.get('user_role') not in ['admin', 'ngo']:
        return redirect(url_for('login'))
        
    case_id = request.form.get('case_id')
    member_id = request.form.get('member_id')
    
    if not member_id or member_id == 'None' or member_id == '':
        member_id = None
        
    # Update assigned rescue member and set status to Assigned
    modify_db("UPDATE reports SET assigned_to = %s, status = 'Assigned' WHERE id = %s", (member_id, case_id))
    
    role = session.get('user_role')
    if role == 'ngo':
        return redirect(url_for('ngo_rescue'))
    return redirect(url_for('admin_rescue'))

@app.route('/rescue/accept_mission', methods=['POST'])
@app.route('/rescue/accept-mission', methods=['POST'])
@login_required('rescue')
def accept_mission():
    case_id = request.form.get('case_id')
    rescue_user_id = session['user_id']
    
    # Update mission status to Accepted
    modify_db("UPDATE reports SET status = 'Accepted' WHERE id = %s AND assigned_to = %s", (case_id, rescue_user_id))
    return redirect(url_for('rescue_dashboard'))

@app.route('/rescue/complete_mission', methods=['POST'])
@app.route('/rescue/complete-mission', methods=['POST'])
@login_required('rescue')
def complete_mission():
    case_id = request.form.get('case_id')
    rescue_user_id = session['user_id']
    
    # Handle resolved image file if uploaded
    file = request.files.get('resolved_image')
    filename = ""
    if file:
        filename = str(int(time.time())) + "_" + file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        filename = "/static/uploads/" + filename
        
    # Update mission status to Completed
    modify_db(
        "UPDATE reports SET status = 'Completed', resolved_image_filename = %s WHERE id = %s AND assigned_to = %s",
        (filename, case_id, rescue_user_id)
    )
    
    # Automatically add rescued animal to medical care for doctor assignment
    existing = query_db("SELECT * FROM medical_care WHERE case_name LIKE %s", (f"% (Case #{case_id})",), one=True)
    if not existing:
        report = query_db("SELECT * FROM reports WHERE id = %s", (case_id,), one=True)
        if report:
            animal_type = report.get('animal_type') or 'Stray Animal'
            description = report.get('description') or 'No description provided.'
            modify_db(
                "INSERT INTO medical_care (case_name, animal_type, status, description, vet_assigned) "
                "VALUES (%s, %s, 'Pending', %s, NULL)",
                (f"Rescued {animal_type} (Case #{case_id})", animal_type, description)
            )
    return redirect(url_for('rescue_dashboard'))


# ==================== RESCUE TEAM ROUTES ====================

@app.route('/rescue/dashboard', methods=['GET', 'POST'])
@login_required('rescue')
def rescue_dashboard():
    rescue_user_id = session['user_id']
    if request.method == 'POST':
        action = request.form.get('action')
        case_id = request.form.get('case_id')
        
        if action == 'accept':
            modify_db("UPDATE reports SET status = 'Accepted' WHERE id = %s AND assigned_to = %s", (case_id, rescue_user_id))
        elif action == 'reject':
            reason = request.form.get('reason')
            modify_db("UPDATE reports SET status = 'Rejected', rejection_reason = %s WHERE id = %s AND assigned_to = %s", (reason, case_id, rescue_user_id))
        elif action == 'resolve':
            file = request.files.get('resolved_image')
            filename = ""
            if file:
                filename = str(int(time.time())) + "_" + file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filename = "/static/uploads/" + filename
            modify_db(
                "UPDATE reports SET status = 'Completed', resolved_image_filename = %s WHERE id = %s AND assigned_to = %s",
                (filename, case_id, rescue_user_id)
            )
            
            # Automatically add rescued animal to medical care for doctor assignment
            existing = query_db("SELECT * FROM medical_care WHERE case_name LIKE %s", (f"% (Case #{case_id})",), one=True)
            if not existing:
                report = query_db("SELECT * FROM reports WHERE id = %s", (case_id,), one=True)
                if report:
                    animal_type = report.get('animal_type') or 'Stray Animal'
                    description = report.get('description') or 'No description provided.'
                    modify_db(
                        "INSERT INTO medical_care (case_name, animal_type, status, description, vet_assigned) "
                        "VALUES (%s, %s, 'Pending', %s, NULL)",
                        (f"Rescued {animal_type} (Case #{case_id})", animal_type, description)
                    )
            
        return redirect(url_for('rescue_dashboard'))
        
    # Get cases assigned to this rescue user (support both new and old statuses)
    cases = query_db(
        "SELECT r.*, u.name as reported_by_name FROM reports r LEFT JOIN users u ON r.reported_by = u.id "
        "WHERE r.assigned_to = %s AND r.status IN ('Assigned', 'Accepted', 'Ongoing', 'Rejected')",
        (rescue_user_id,)
    )
    resolved_cases = query_db(
        "SELECT r.*, u.name as reported_by_name FROM reports r LEFT JOIN users u ON r.reported_by = u.id "
        "WHERE r.assigned_to = %s AND r.status IN ('Completed', 'Resolved')",
        (rescue_user_id,)
    )
    
    total_count = query_db("SELECT COUNT(*) as count FROM reports WHERE assigned_to = %s", (rescue_user_id,), one=True)['count']
    pending_count = query_db("SELECT COUNT(*) as count FROM reports WHERE assigned_to = %s AND status = 'Assigned'", (rescue_user_id,), one=True)['count']
    accepted_count = query_db("SELECT COUNT(*) as count FROM reports WHERE assigned_to = %s AND status IN ('Accepted', 'Ongoing')", (rescue_user_id,), one=True)['count']
    resolved_count = query_db("SELECT COUNT(*) as count FROM reports WHERE assigned_to = %s AND status IN ('Completed', 'Resolved')", (rescue_user_id,), one=True)['count']
    
    return render_template(
        'Rescue/rescue-home-page.html',
        active_cases=cases,
        resolved_cases=resolved_cases,
        total_count=total_count,
        pending_count=pending_count,
        accepted_count=accepted_count,
        resolved_count=resolved_count
    )

@app.route('/rescue/profile', methods=['GET', 'POST'])
@login_required('rescue')
def rescue_profile():
    rescue_user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        # Profile image upload
        file = request.files.get('profile_img')
        if file:
            filename = str(int(time.time())) + "_" + file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            profile_img = "/static/uploads/" + filename
            modify_db(
                "UPDATE users SET name=%s, email=%s, phone=%s, location=%s, profile_img=%s WHERE id=%s",
                (name, email, phone, location, profile_img, rescue_user_id)
            )
            session['user_profile_img'] = profile_img
        else:
            modify_db(
                "UPDATE users SET name=%s, email=%s, phone=%s, location=%s WHERE id=%s",
                (name, email, phone, location, rescue_user_id)
            )
            
        session['user_name'] = name
        session['user_email'] = email
        return redirect(url_for('rescue_profile'))
        
    user = query_db("SELECT * FROM users WHERE id = %s", (rescue_user_id,), one=True)
    return render_template('Rescue/profile-rescue.html', user=user)


# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    users_count = query_db("SELECT COUNT(*) as count FROM users", one=True)['count']
    rescue_cases_count = query_db("SELECT COUNT(*) as count FROM reports", one=True)['count']
    active_cases_count = query_db("SELECT COUNT(*) as count FROM reports WHERE status NOT IN ('Resolved', 'Rejected')", one=True)['count']
    adoption_count = query_db("SELECT COUNT(*) as count FROM pets WHERE status = 'Available'", one=True)['count']
    treatment_count = query_db("SELECT COUNT(*) as count FROM medical_care WHERE status != 'Recovered'", one=True)['count']
    ngos_count = query_db("SELECT COUNT(*) as count FROM users WHERE role = 'ngo'", one=True)['count']
    shelters_count = query_db("SELECT COUNT(*) as count FROM shelters", one=True)['count']
    
    # Simple recent listings
    recent_rescues = query_db("SELECT r.*, u.name as reported_by_name FROM reports r LEFT JOIN users u ON r.reported_by = u.id ORDER BY r.id DESC LIMIT 3")
    recent_adoptions = query_db("SELECT a.*, p.name as pet_name FROM adoption_applications a JOIN pets p ON a.pet_id = p.id ORDER BY a.id DESC LIMIT 3")
    
    return render_template(
        'New-admin/admin_dashboard.html',
        users_count=users_count,
        rescue_count=rescue_cases_count,
        active_cases_count=active_cases_count,
        adoption_count=adoption_count,
        treatment_count=treatment_count,
        ngos_count=ngos_count,
        shelters_count=shelters_count,
        recent_rescues=recent_rescues,
        recent_adoptions=recent_adoptions
    )

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required('admin')
def admin_users():
    if request.method == 'POST':
        action = request.form.get('action')
        target_id = request.form.get('user_id')
        
        if action == 'delete':
            modify_db("DELETE FROM users WHERE id = %s", (target_id,))
        elif action == 'add':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            password = request.form.get('password') or 'user123'
            status = request.form.get('status', 'Active')
            
            # Check if user already exists with the email
            exists = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
            if not exists:
                modify_db(
                    "INSERT INTO users (name, email, phone, password, role, status) "
                    "VALUES (%s, %s, %s, %s, 'user', %s)",
                    (name, email, phone, password, status)
                )
        elif action == 'edit':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            modify_db(
                "UPDATE users SET name = %s, email = %s, phone = %s WHERE id = %s",
                (name, email, phone, target_id)
            )
        elif action == 'block':
            reason = request.form.get('reason') or ''
            modify_db("UPDATE users SET status = 'Blocked', delete_reason = %s WHERE id = %s", (reason, target_id))
        elif action == 'unblock':
            modify_db("UPDATE users SET status = 'Active', delete_reason = '' WHERE id = %s", (target_id,))
            
        return redirect(url_for('admin_users'))
        
    users = query_db("SELECT * FROM users WHERE role = 'user'")
    return render_template('New-admin/admin_Manage_users.html', users=users)

@app.route('/admin/add-ngo', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_ngo():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            password = request.form.get('password')
            location = request.form.get('location')
            capacity = request.form.get('capacity', 50)
            cases = request.form.get('cases', 0)
            
            file = request.files.get('image')
            profile_img = ""
            if file:
                filename = str(int(time.time())) + "_" + file.filename
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                profile_img = filename
                
            exists = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
            if not exists:
                modify_db(
                    "INSERT INTO users (name, email, phone, password, role, location, capacity, cases, profile_img, status) "
                    "VALUES (%s, %s, %s, %s, 'ngo', %s, %s, %s, %s, 'Active')",
                    (name, email, phone, password, location, capacity, cases, profile_img)
                )
                
        elif action == 'edit':
            user_id = request.form.get('user_id')
            name = request.form.get('name')
            location = request.form.get('location')
            capacity = request.form.get('capacity')
            cases = request.form.get('cases')
            
            file = request.files.get('image')
            if file:
                filename = str(int(time.time())) + "_" + file.filename
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                profile_img = filename
                modify_db(
                    "UPDATE users SET name=%s, location=%s, capacity=%s, cases=%s, profile_img=%s WHERE id=%s",
                    (name, location, capacity, cases, profile_img, user_id)
                )
            else:
                modify_db(
                    "UPDATE users SET name=%s, location=%s, capacity=%s, cases=%s WHERE id=%s",
                    (name, location, capacity, cases, user_id)
                )
                
        elif action == 'delete':
            user_id = request.form.get('user_id')
            reason = request.form.get('reason', '')
            modify_db("UPDATE users SET status = 'Deleted', delete_reason = %s WHERE id = %s", (reason, user_id))
            
        elif action == 'restore':
            user_id = request.form.get('user_id')
            modify_db("UPDATE users SET status = 'Active', delete_reason = '' WHERE id = %s", (user_id,))
            
        return redirect(url_for('admin_add_ngo'))
        
    # GET: Load stats and users list
    active_ngos = query_db("SELECT * FROM users WHERE role = 'ngo' AND status = 'Active'")
    deleted_ngos = query_db("SELECT * FROM users WHERE role = 'ngo' AND status = 'Deleted'")
    
    animals_rescued = query_db("SELECT COUNT(*) as count FROM reports WHERE status = 'Resolved'", one=True)['count']
    active_cases = query_db("SELECT COUNT(*) as count FROM reports WHERE status NOT IN ('Resolved', 'Rejected')", one=True)['count']
    total_capacity = query_db("SELECT SUM(capacity) as total FROM users WHERE role = 'ngo' AND status = 'Active'", one=True)['total'] or 0
    adoptions = query_db("SELECT COUNT(*) as count FROM pets WHERE status = 'Adopted'", one=True)['count']
    
    return render_template(
        'New-admin/admin_add_ngo.html',
        active_ngos=active_ngos,
        deleted_ngos=deleted_ngos,
        animals_rescued=animals_rescued,
        active_cases=active_cases,
        total_capacity=total_capacity,
        adoptions=adoptions
    )

@app.route('/admin/rescue', methods=['GET', 'POST'])
@login_required('admin')
def admin_rescue():
    if request.method == 'POST':
        action = request.form.get('action')
        case_id = request.form.get('case_id')
        
        if action == 'assign':
            member_id = request.form.get('member_id')
            if not member_id or member_id == 'None' or member_id == '':
                member_id = None
            modify_db("UPDATE reports SET assigned_to = %s, status = 'Assigned' WHERE id = %s", (member_id, case_id))
        elif action == 'reject':
            reason = request.form.get('reason')
            modify_db("UPDATE reports SET status = 'Rejected', rejection_reason = %s WHERE id = %s", (reason, case_id))
            
        return redirect(url_for('admin_rescue'))
        
    cases = query_db(
        "SELECT r.*, u.name as reported_by_name, u.phone as reported_by_phone, "
        "a.name as assigned_name, a.email as assigned_email, a.phone as assigned_phone "
        "FROM reports r "
        "LEFT JOIN users u ON r.reported_by = u.id "
        "LEFT JOIN users a ON r.assigned_to = a.id"
    )
    members = query_db(
        "SELECT u.id as user_id, u.name, u.email, u.phone, "
        "COALESCE(m.role, 'Rescue Member') as role "
        "FROM users u "
        "LEFT JOIN ngo_members m ON u.email = m.email "
        "WHERE u.role = 'rescue'"
    )
    
    pending_count = query_db("SELECT COUNT(*) as count FROM reports WHERE status = 'Pending'", one=True)['count']
    in_progress_count = query_db("SELECT COUNT(*) as count FROM reports WHERE status IN ('Assigned', 'In Progress', 'Ongoing', 'Accepted')", one=True)['count']
    rescued_count = query_db("SELECT COUNT(*) as count FROM reports WHERE status IN ('Resolved', 'Completed')", one=True)['count']
    adoption_count = query_db("SELECT COUNT(*) as count FROM pets WHERE status = 'Available'", one=True)['count']
    
    return render_template(
        'New-admin/admin_rescue.html',
        cases=cases,
        members=members,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        rescued_count=rescued_count,
        adoption_count=adoption_count
    )

@app.route('/admin/shelters', methods=['GET', 'POST'])
@login_required('admin')
def admin_shelters():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            location = request.form.get('location')
            contact = request.form.get('contact', '040-12345678')
            capacity = request.form.get('capacity', 50)
            status = request.form.get('status', 'Active')
            description = request.form.get('description', '')
            
            file = request.files.get('image')
            image_filename = "https://images.unsplash.com/photo-1548767797-d8c844163c4c"
            if file:
                filename = str(int(time.time())) + "_" + file.filename
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                image_filename = filename
                
            modify_db(
                "INSERT INTO shelters (name, location, contact, capacity, occupied, description, image_filename, status) "
                "VALUES (%s, %s, %s, %s, 0, %s, %s, %s)",
                (name, location, contact, capacity, description, image_filename, status)
            )
            
        elif action == 'edit':
            shelter_id = request.form.get('shelter_id')
            name = request.form.get('name')
            location = request.form.get('location')
            capacity = request.form.get('capacity')
            status = request.form.get('status')
            contact = request.form.get('contact', '040-12345678')
            description = request.form.get('description', '')
            
            file = request.files.get('image')
            if file:
                filename = str(int(time.time())) + "_" + file.filename
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                image_filename = filename
                modify_db(
                    "UPDATE shelters SET name=%s, location=%s, capacity=%s, status=%s, image_filename=%s, contact=%s, description=%s WHERE id=%s",
                    (name, location, capacity, status, image_filename, contact, description, shelter_id)
                )
            else:
                modify_db(
                    "UPDATE shelters SET name=%s, location=%s, capacity=%s, status=%s, contact=%s, description=%s WHERE id=%s",
                    (name, location, capacity, status, contact, description, shelter_id)
                )
                
        elif action == 'delete':
            shelter_id = request.form.get('shelter_id')
            reason = request.form.get('reason', '')
            modify_db("UPDATE shelters SET status = 'Deleted', delete_reason = %s WHERE id = %s", (reason, shelter_id))
            
        elif action == 'restore':
            shelter_id = request.form.get('shelter_id')
            modify_db("UPDATE shelters SET status = 'Active', delete_reason = '' WHERE id = %s", (shelter_id,))
            
        return redirect(url_for('admin_shelters'))

    # GET request
    active_shelters = query_db("SELECT * FROM shelters WHERE status != 'Deleted'")
    deleted_shelters = query_db("SELECT * FROM shelters WHERE status = 'Deleted'")
    
    total_shelters = len(active_shelters)
    active_capacity = sum([s['capacity'] for s in active_shelters if s['status'] == 'Active'])
    total_capacity = sum([s['capacity'] for s in active_shelters])
    adoption_ready = query_db("SELECT COUNT(*) as count FROM pets WHERE status = 'Available'", one=True)['count']
    
    return render_template(
        'New-admin/admin_shelter.html',
        active_shelters=active_shelters,
        deleted_shelters=deleted_shelters,
        total_shelters=total_shelters,
        active_capacity=active_capacity,
        total_capacity=total_capacity,
        adoption_ready=adoption_ready
    )

@app.route('/admin/adoption')
@login_required('admin')
def admin_adoption():
    applications = query_db(
        "SELECT a.*, p.name as pet_name, u.name as user_name "
        "FROM adoption_applications a "
        "JOIN pets p ON a.pet_id = p.id "
        "JOIN users u ON a.user_id = u.id"
    )
    
    adopted_count = query_db("SELECT COUNT(*) as count FROM adoption_applications WHERE status='Approved'", one=True)['count']
    pending_count = query_db("SELECT COUNT(*) as count FROM adoption_applications WHERE status='Pending'", one=True)['count']
    total_count = len(applications)
    
    return render_template(
        'New-admin/admin_adoption.html', 
        applications=applications, 
        adopted_count=adopted_count,
        pending_count=pending_count,
        total_count=total_count
    )

@app.route('/admin/adoption/<int:app_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_adoption_review(app_id):
    if request.method == 'POST':
        status = request.form.get('status')
        meeting_time = request.form.get('meeting_time')
        reason = request.form.get('reason')
        
        if status == 'Approved':
            modify_db("UPDATE adoption_applications SET status = 'Approved', meeting_time = %s WHERE id = %s", (meeting_time, app_id))
            app_rec = query_db("SELECT pet_id FROM adoption_applications WHERE id = %s", (app_id,), one=True)
            if app_rec:
                modify_db("UPDATE pets SET status = 'Adopted' WHERE id = %s", (app_rec['pet_id'],))
        elif status == 'Rejected':
            modify_db("UPDATE adoption_applications SET status = 'Rejected', rejection_reason = %s WHERE id = %s", (reason, app_id))
            app_rec = query_db("SELECT pet_id FROM adoption_applications WHERE id = %s", (app_id,), one=True)
            if app_rec:
                modify_db("UPDATE pets SET status = 'Available' WHERE id = %s", (app_rec['pet_id'],))
        elif status == 'Pending':
            modify_db("UPDATE adoption_applications SET status = 'Pending', meeting_time = NULL, rejection_reason = NULL WHERE id = %s", (app_id,))
            app_rec = query_db("SELECT pet_id FROM adoption_applications WHERE id = %s", (app_id,), one=True)
            if app_rec:
                modify_db("UPDATE pets SET status = 'Pending' WHERE id = %s", (app_rec['pet_id'],))
                
        return redirect(url_for('admin_adoption_review', app_id=app_id))
        
    app_details = query_db(
        "SELECT a.*, p.name as pet_name, p.type as pet_type, u.name as user_name "
        "FROM adoption_applications a JOIN pets p ON a.pet_id = p.id JOIN users u ON a.user_id = u.id WHERE a.id = %s",
        (app_id,), one=True
    )
    if not app_details:
        return redirect(url_for('admin_adoption'))
    return render_template('New-admin/admin_adoption_user1.html', app=app_details)

@app.route('/admin/medical-care')
@login_required('admin')
def admin_medical_care():
    sync_completed_rescues_to_medical()
    cases = query_db("SELECT * FROM medical_care")
    return render_template('New-admin/medical_care.html', cases=cases)

@app.route('/admin/medical-care/assign/<int:case_id>', methods=['POST'])
@login_required('admin')
def admin_assign_doctor(case_id):
    doctor = request.form.get('doctor')
    modify_db(
        "UPDATE medical_care SET vet_assigned = %s, status = 'Ongoing' WHERE id = %s",
        (doctor, case_id)
    )
    return redirect(url_for('admin_medical_care'))


if __name__ == '__main__':
    # Initialize the database
    init_db()
    
    # Run the application
    app.run(debug=True, port=5000)
