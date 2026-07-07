CREATE DATABASE attendance_db;

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    semester INT
);

CREATE TABLE subjects (
    subject_id INT PRIMARY KEY,
    subject_name VARCHAR(100),
    subject_code VARCHAR(20)
);

CREATE TABLE attendance (
    attendance_id INT PRIMARY KEY,
    student_id INT,
    subject_id INT,
    attendance_date DATE,
    status VARCHAR(10),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

