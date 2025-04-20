from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import csv
from flask import Response
from xhtml2pdf import pisa
from io import BytesIO
from flask import make_response


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # سر الجلسة (مطلوب لتخزين الـsession)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # بيانات تسجيل دخول بسيطة (ممكن تتحط في قاعدة بيانات بعدين)
        if username == 'admin' and password == 'pass123':
            session['user'] = username  # تخزين الجلسة
            return redirect('/report')
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# صفحة عرض الفورم
@app.route('/')
def form():
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    # جلب كل المدارس
    cursor.execute("SELECT id, school_name FROM locations")
    locations = cursor.fetchall()

    conn.close()
    return render_template('intervention_form.html', locations=locations)

# استقبال البيانات
@app.route('/submit', methods=['POST'])
def submit():
    data = {
        'location_id': request.form.get('location_id'),
        'reported_by': request.form.get('reported_by'),
        'contact_person': request.form.get('contact_person'),
        'problem_description': request.form.get('problem_description'),
        'config_reviewed': 'config_reviewed' in request.form,
        'onsite_visit': 'onsite_visit' in request.form,
        'final_completed': 'final_completed' in request.form,
        'intervention_date': request.form.get('intervention_date')
    }

    # تخزين البيانات في قاعدة البيانات
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO interventions 
        (location_id, reported_by, school_contact_person, problem_description, configuration_reviewed,
         onsite_visit, final_completed, intervention_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['location_id'],
        data['reported_by'],
        data['contact_person'],
        data['problem_description'],
        int(data['config_reviewed']),
        int(data['onsite_visit']),
        int(data['final_completed']),
        data['intervention_date']
    ))

    conn.commit()
    conn.close()

    return f"<h2>✅ Intervention by {data['reported_by']} for school ID {data['location_id']} saved successfully!</h2>"
@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user' not in session:
        return redirect('/login')

    # باقي الكود زي ما هو

    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    # جلب كل المدارس عشان نحطهم في الـDropdown
    cursor.execute("SELECT id, school_name FROM locations")
    schools = cursor.fetchall()

    # لو المستخدم اختار مدرسة
    selected_school = None
    if request.method == 'POST':
        selected_school = request.form.get('school_filter')
        cursor.execute('''
            SELECT i.id, l.school_name, i.reported_by, i.intervention_date,
                   i.configuration_reviewed, i.onsite_visit, i.final_completed,
                   i.problem_description
            FROM interventions i
            JOIN locations l ON i.location_id = l.id
            WHERE l.id = ?
            ORDER BY i.intervention_date DESC
        ''', (selected_school,))
    else:
        cursor.execute('''
            SELECT i.id, l.school_name, i.reported_by, i.intervention_date,
                   i.configuration_reviewed, i.onsite_visit, i.final_completed,
                   i.problem_description
            FROM interventions i
            JOIN locations l ON i.location_id = l.id
            ORDER BY i.intervention_date DESC
        ''')

    interventions = cursor.fetchall()
    conn.close()

    return render_template('report.html', interventions=interventions, schools=schools, selected_school=selected_school)


@app.route('/download_csv')
def download_csv():
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.school_name, i.reported_by, i.intervention_date,
               i.configuration_reviewed, i.onsite_visit, i.final_completed,
               i.problem_description
        FROM interventions i
        JOIN locations l ON i.location_id = l.id
        ORDER BY i.intervention_date DESC
    ''')
    rows = cursor.fetchall()
    conn.close()

    def generate():
        data = csv.writer(Response())
        yield ','.join(['School', 'Reported By', 'Date', 'Reviewed', 'Visited', 'Completed', 'Problem']) + '\n'
        for row in rows:
            yield ','.join(str(cell) for cell in row) + '\n'

    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=interventions.csv"})
@app.route('/download_pdf')
def download_pdf():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.school_name, i.reported_by, i.intervention_date,
               i.configuration_reviewed, i.onsite_visit, i.final_completed,
               i.problem_description
        FROM interventions i
        JOIN locations l ON i.location_id = l.id
        ORDER BY i.intervention_date DESC
    ''')
    data = cursor.fetchall()
    conn.close()

    # HTML لعرض البيانات في PDF
    html = render_template("report_pdf.html", interventions=data)

    # توليد PDF
    result = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=result)

    response = make_response(result.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=intervention_report.pdf"
    return response

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=10000)
