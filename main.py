import csv
import io
import base64

from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        id_type = request.form.get('ID')
        id_value = request.form.get('id_value', '').strip()
        if not id_type or not id_value:
            return render_template('error.html')

        # Read data.csv and build records, skipping header and parsing marks as int when possible
        records = []
        try:
            with open('data.csv', newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # skip header row
                for row in reader:
                    sid = row[0].strip()
                    cid = row[1].strip()
                    val = row[2].strip()
                    try:
                        m = int(val)
                    except ValueError:
                        m = float(val)
                    records.append({
                        'student_id': sid,
                        'course_id': cid,
                        'marks': m
                    })
        except Exception:
            return render_template('error.html')

        if id_type == 'student_id':
            # Filter by student
            student_records = [r for r in records if r['student_id'] == id_value]
            if not student_records:
                return render_template('error.html')
            total = sum(r['marks'] for r in student_records)
            return render_template('student_details.html',
                                   student_records=student_records,
                                   total_marks=total)

        elif id_type == 'course_id':
            # Filter by course
            course_marks = [r['marks'] for r in records if r['course_id'] == id_value]
            if not course_marks:
                return render_template('error.html')
            avg_marks = sum(course_marks) / len(course_marks)
            max_marks = max(course_marks)

            # Generate histogram PNG
            fig, ax = plt.subplots()
            ax.hist(course_marks)
            ax.set_xlabel('Marks')
            ax.set_ylabel('Frequency')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode()
            plt.close(fig)

            return render_template('course_details.html',
                                   average_marks=avg_marks,
                                   maximum_marks=max_marks,
                                   histogram=img_b64)

        else:
            return render_template('error.html')

    # GET
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
