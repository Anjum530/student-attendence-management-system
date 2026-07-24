from flask import Flask
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "attendance-project-secret-key"


def get_connection():
    return psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)


@app.route("/")
def home():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM students")
        student_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM subjects")
        subject_count = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM attendance WHERE status = 'Present'"
        )
        present_count = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM attendance WHERE status = 'Absent'"
        )
        absent_count = cur.fetchone()[0]

        cur.close()
        conn.close()

        return render_template(
            "index.html",
            student_count=student_count,
            subject_count=subject_count,
            present_count=present_count,
            absent_count=absent_count
        )

    except Exception as error:
        return f"Home page database error: {error}"


@app.route("/students", methods=["GET", "POST"])
def students():
    try:
        conn = get_connection()
        cur = conn.cursor()

        if request.method == "POST":
            student_id = request.form["student_id"]
            name = request.form["name"]
            department = request.form["department"]
            semester = request.form["semester"]

            cur.execute(
                """
                INSERT INTO students
                (student_id, name, department, semester)
                VALUES (%s, %s, %s, %s)
                """,
                (student_id, name, department, semester)
            )

            conn.commit()

            cur.close()
            conn.close()

            flash("Student added successfully.")
            return redirect(url_for("students"))

        cur.execute(
            """
            SELECT student_id, name, department, semester
            FROM students
            ORDER BY student_id
            """
        )

        student_list = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "students.html",
            students=student_list
        )

    except Exception as error:
        return f"Students error: {error}"


@app.route("/delete-student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM attendance WHERE student_id = %s",
            (student_id,)
        )

        cur.execute(
            "DELETE FROM students WHERE student_id = %s",
            (student_id,)
        )

        conn.commit()

        cur.close()
        conn.close()

        flash("Student deleted successfully.")

        return redirect(url_for("students"))

    except Exception as error:
        return f"Delete student error: {error}"


@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    try:
        conn = get_connection()
        cur = conn.cursor()

        if request.method == "POST":
            subject_id = request.form["subject_id"]
            subject_code = request.form["subject_code"]
            subject_name = request.form["subject_name"]

            cur.execute(
                """
                INSERT INTO subjects
                (subject_id, subject_name, subject_code)
                VALUES (%s, %s, %s)
                """,
                (subject_id, subject_name, subject_code)
            )

            conn.commit()

            cur.close()
            conn.close()

            flash("Subject added successfully.")
            return redirect(url_for("subjects"))

        cur.execute(
            """
            SELECT subject_id, subject_code, subject_name
            FROM subjects
            ORDER BY subject_id
            """
        )

        subject_list = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "subjects.html",
            subjects=subject_list
        )

    except Exception as error:
        return f"Subjects error: {error}"


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    try:
        conn = get_connection()
        cur = conn.cursor()

        if request.method == "POST":
            student_id = request.form["student_id"]
            subject_id = request.form["subject_id"]
            attendance_date = request.form["attendance_date"]
            status = request.form["status"]

            cur.execute(
                """
                SELECT COALESCE(MAX(attendance_id), 0) + 1
                FROM attendance
                """
            )

            attendance_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO attendance
                (
                    attendance_id,
                    student_id,
                    subject_id,
                    attendance_date,
                    status
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    attendance_id,
                    student_id,
                    subject_id,
                    attendance_date,
                    status
                )
            )

            conn.commit()

            cur.close()
            conn.close()

            flash("Attendance marked successfully.")
            return redirect(url_for("attendance"))

        cur.execute(
            """
            SELECT student_id, name
            FROM students
            ORDER BY name
            """
        )
        student_list = cur.fetchall()

        cur.execute(
            """
            SELECT subject_id, subject_code, subject_name
            FROM subjects
            ORDER BY subject_id
            """
        )
        subject_list = cur.fetchall()

        cur.execute(
            """
            SELECT
                a.attendance_id,
                s.name,
                sub.subject_code,
                sub.subject_name,
                a.attendance_date,
                a.status
            FROM attendance a
            JOIN students s
                ON a.student_id = s.student_id
            JOIN subjects sub
                ON a.subject_id = sub.subject_id
            ORDER BY a.attendance_date DESC, a.attendance_id DESC
            """
        )
        attendance_list = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "attendance.html",
            students=student_list,
            subjects=subject_list,
            attendance_records=attendance_list
        )

    except Exception as error:
        return f"Attendance error: {error}"


@app.route("/reports")
def reports():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT
                s.student_id,
                s.name,
                COUNT(a.attendance_id) AS total_classes,
                SUM(
                    CASE
                        WHEN a.status = 'Present' THEN 1
                        ELSE 0
                    END
                ) AS classes_present,
                ROUND(
                    SUM(
                        CASE
                            WHEN a.status = 'Present' THEN 1
                            ELSE 0
                        END
                    ) * 100.0 /
                    NULLIF(COUNT(a.attendance_id), 0),
                    2
                ) AS attendance_percentage
            FROM students s
            LEFT JOIN attendance a
                ON s.student_id = a.student_id
            GROUP BY s.student_id, s.name
            ORDER BY attendance_percentage DESC NULLS LAST
            """
        )

        report_list = cur.fetchall()

        cur.close()
        conn.close()

        return render_template(
            "reports.html",
            reports=report_list
        )

    except Exception as error:
        return f"Reports error: {error}"


if __name__ == "__main__":
    app.run(debug=True)