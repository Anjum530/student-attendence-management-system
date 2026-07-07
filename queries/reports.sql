-- 1. Display all students
SELECT * FROM students;

-- 2. Display all subjects
SELECT * FROM subjects;

-- 3. Display all attendance records
SELECT * FROM attendance;

-- 4. Student-wise Attendance Report
SELECT
    s.student_id,
    s.name,
    sub.subject_name,
    a.attendance_date,
    a.status
FROM attendance a
JOIN students s
ON a.student_id = s.student_id
JOIN subjects sub
ON a.subject_id = sub.subject_id
ORDER BY s.student_id, a.attendance_date;

-- 5. Subject-wise Attendance Report
SELECT
    sub.subject_code,
    sub.subject_name,
    s.name,
    a.attendance_date,
    a.status
FROM attendance a
JOIN students s
ON a.student_id = s.student_id
JOIN subjects sub
ON a.subject_id = sub.subject_id
ORDER BY sub.subject_id, s.name;

-- 6. Attendance Percentage Report
SELECT
    s.student_id,
    s.name,
    COUNT(*) AS total_classes,
    SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS classes_present,
    ROUND(
        SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    ) AS attendance_percentage
FROM students s
JOIN attendance a
ON s.student_id = a.student_id
GROUP BY s.student_id, s.name
ORDER BY attendance_percentage DESC;

-- 7. Present vs Absent Summary
SELECT
    status,
    COUNT(*) AS total_count
FROM attendance
GROUP BY status;
