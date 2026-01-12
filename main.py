
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap,QIcon
import sys
import pyodbc
import os
import shutil
from PyQt5.QtWidgets import QFileDialog



def get_connection():
        conn = pyodbc.connect(
            
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=192.168.100.7,1433;"  # server IP + port
            "DATABASE=university_db;"          # replace with your database
             "UID=sa;"                        # or your appuser
            "PWD=mssqlserver123456;")
    
        print("Connected to SQL Server!")
      
        return conn

conn = get_connection()
cursor = conn.cursor()



# teacher dashboard
class teacher_profile(QWidget):
    def __init__(self, teacher_dashboard, teacher_user_id):
        super().__init__()
        self.setWindowTitle("Teacher Profile")
        self.resize(1000, 600)

        self.previous_window = teacher_dashboard
        self.teacher_user_id = teacher_user_id

        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName("backbutton_style")
        self.back_button.clicked.connect(self.go_back)

        title = QLabel("TEACHER PROFILE")
        title.setObjectName("admin_student_title")

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()

        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 150)
        self.image_label.setStyleSheet("border:2px solid gray; border-radius:75px;")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.upload_btn = QPushButton("Upload Picture")
        self.upload_btn.setObjectName("admin_student_button")
        self.upload_btn.clicked.connect(self.upload_picture)

        img_layout = QVBoxLayout()
        img_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        img_layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)

        self.username_input = QLineEdit(); self.username_input.setReadOnly(True)
        self.fullname_input = QLineEdit(); self.fullname_input.setReadOnly(True)
        self.email_input = QLineEdit(); self.email_input.setReadOnly(True)
        self.phone_input = QLineEdit(); self.phone_input.setReadOnly(True)
        self.role_input = QLineEdit(); self.role_input.setReadOnly(True)

        self.designation_input = QLineEdit(); self.designation_input.setReadOnly(True)
        self.department_input = QLineEdit(); self.department_input.setReadOnly(True)

        def row(name, widget):
            h = QHBoxLayout()
            lbl1 = QLabel(name)
            lbl1.setFixedWidth(150)
            lbl1.setObjectName("admin_student_label")
            widget.setObjectName("profile_value")
            h.addWidget(lbl1)
            h.addWidget(widget)
            return h

        profile_layout = QVBoxLayout()
        profile_layout.addLayout(row("Username:", self.username_input))
        profile_layout.addLayout(row("Full Name:", self.fullname_input))
        profile_layout.addLayout(row("Email:", self.email_input))
        profile_layout.addLayout(row("Phone:", self.phone_input))
        profile_layout.addLayout(row("Role:", self.role_input))
        profile_layout.addLayout(row("Designation:", self.designation_input))
        profile_layout.addLayout(row("Department ID:", self.department_input))

        self.edit_button = QPushButton("Edit Profile")
        self.edit_button.setObjectName("admin_student_button")
        self.edit_button.clicked.connect(self.enable_editing)

        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("admin_student_button")
        self.save_button.clicked.connect(self.save_profile)
        self.save_button.setEnabled(False)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.edit_button)
        btn_row.addWidget(self.save_button)

        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addLayout(title_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(img_layout)
        main_layout.addLayout(profile_layout)
        main_layout.addSpacing(25)
        main_layout.addLayout(btn_row)

        self.setLayout(main_layout)
        self.load_teacher_profile()

    def upload_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            image_folder = "profile_images"
            os.makedirs(image_folder, exist_ok=True)

            new_path = f"{image_folder}/teacher_{self.teacher_user_id}.png"
            shutil.copyfile(file_path, new_path)

            cursor.execute("""
                UPDATE teacher SET profile_pic = ?
                WHERE user_id = ?
            """, (new_path, self.teacher_user_id))
            conn.commit()

            pixmap = QPixmap(new_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)

            QMessageBox.information(self, "Success", "Picture Updated!")

    def enable_editing(self):
        self.username_input.setReadOnly(False)
        self.fullname_input.setReadOnly(False)
        self.email_input.setReadOnly(False)
        self.phone_input.setReadOnly(False)
        self.designation_input.setReadOnly(False)

        self.edit_button.setEnabled(False)
        self.save_button.setEnabled(True)

        QMessageBox.information(self, "Edit Mode", "You can now edit your profile!")

    def save_profile(self):
            try:
                cursor.execute("""
                    EXEC update_teacher_profile ?, ?, ?, ?, ?
                """, (
                    self.teacher_user_id,
                    self.username_input.text(),
                    self.fullname_input.text(),
                    self.email_input.text(),
                    self.phone_input.text()
                ))

                cursor.execute("""
                    UPDATE teacher
                    SET designation = ?
                    WHERE user_id = ?
                """, (
                    self.designation_input.text(),
                    self.teacher_user_id
                ))

                conn.commit()

                self.enable_readonly()
                QMessageBox.information(self, "Success", "Profile Updated!")

            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def enable_readonly(self):
        self.username_input.setReadOnly(True)
        self.fullname_input.setReadOnly(True)
        self.email_input.setReadOnly(True)
        self.phone_input.setReadOnly(True)
        self.designation_input.setReadOnly(True)

        self.edit_button.setEnabled(True)
        self.save_button.setEnabled(False)

    def load_teacher_profile(self):
        try:
            cursor.execute("EXEC load_teacher_profile ?", (self.teacher_user_id,))
            row = cursor.fetchone()

            if row:
                self.username_input.setText(str(row[1]))
                self.fullname_input.setText(str(row[2]))
                self.email_input.setText(str(row[3]))
                self.phone_input.setText(str(row[4]))
                self.role_input.setText(str(row[5]))
                self.designation_input.setText(str(row[6]))
                self.department_input.setText(str(row[7]))

                if row[8]:
                    pixmap = QPixmap(row[8]).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.image_label.setPixmap(pixmap)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def go_back(self):
        self.previous_window.show()
        self.close()



class teacher_courses(QWidget):
    def __init__(self,teacher_dashboard, teacher_id):
          super().__init__()
          self.teacher_id = teacher_id
          self.setWindowTitle("Assigned Courses")
          self.resize(1000, 600)

          self.previous_window = teacher_dashboard
          self.teacher_user_id = teacher_id

          self.back_button = QPushButton("← Back")
          self.back_button.setObjectName("backbutton_style")
          self.back_button.clicked.connect(self.go_back)

          top_layout = QHBoxLayout()
          top_layout.addWidget(self.back_button)
          top_layout.addStretch()

          title = QLabel("MY COURSES")
          title.setObjectName("admin_student_title")
          title_layout = QHBoxLayout()
          title_layout.addStretch()
          title_layout.addWidget(title)
          title_layout.addStretch()

          main_layout = QVBoxLayout()

          scroll = QScrollArea()
          scroll.setWidgetResizable(True)
          scroll.setVerticalScrollBarPolicy(True)

          container = QWidget()
          self.grid = QGridLayout()
          self.grid.setSpacing(20)

          container.setLayout(self.grid)
          scroll.setWidget(container)

          main_layout.addLayout(top_layout)
          main_layout.addLayout(title_layout)
          main_layout.addWidget(scroll)
          self.setLayout(main_layout)

          self.load_courses()

    def go_back(self):
      self.previous_window.show()
      self.close()

    def create_course_box(self, title, code, program, session, section, semester, credits):

        box = QFrame()
        box.setObjectName("courseCard")
        box.setFixedWidth(300)

        layout = QVBoxLayout()
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("courseTitle")
        layout.addWidget(title_label)

        code_label = QLabel(f"Course Code: {code}")
        code_label.setObjectName("courseTextBold")

        semester_label = QLabel(f"Semester: {semester}")
        semester_label.setObjectName("courseTextBold")

        program_label = QLabel(f"Program: {program}")
        program_label.setObjectName("courseTextBold")

        section_label = QLabel(f"Section: {section}")
        section_label.setObjectName("courseTextBold")

        session_label = QLabel(f"Session: {session}")
        session_label.setObjectName("courseTextBold")

        credits_label = QLabel(f"Credits: {credits}")
        credits_label.setObjectName("courseTextBold")

        layout.addWidget(code_label)
        layout.addWidget(semester_label)
        layout.addWidget(program_label)
        layout.addWidget(section_label)
        layout.addWidget(session_label)
        layout.addWidget(credits_label)

        box.setLayout(layout)
        return box

    def load_courses(self):
        try:
            cursor.execute("EXEC get_teacher_assigned_courses ?", (self.teacher_user_id,))
            courses = cursor.fetchall()
            row = 0
            col = 0
            for course in courses:
                course_code, course_title, semester, program, section, session, credits = course

                box = self.create_course_box(
                    code=course_code,
                    title=course_title,
                    semester=semester,
                    program=program,
                    section=section,
                    session=session,
                    credits=credits
                )
                self.grid.addWidget(box, row, col)
                col += 1
                if col == 3:
                    col = 0
                    row += 1

        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Could not load courses:\n{str(e)}")

class teacher_attendance(QWidget):
    def __init__(self,teacher_dashboard,teacher_user_id):
        super().__init__()
        # Either ALL students attendance saves Or NOTHING saves (no half data)[TRANSACTOION]
        # ✔ Automatically calculate attendance percentage Or prevent duplicate attendance for same lecture[TRIGGER]
        self.setWindowTitle("Teacher Attendance")
        self.resize(1000, 600)
        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName("backbutton_style")
        self.back_button.clicked.connect(self.go_back)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.back_button)
        top_layout.addStretch()

        self.previous_window = teacher_dashboard
        self.teacher_id = teacher_user_id

        self.course_class_combo = QComboBox()
        self.course_class_combo.setObjectName("form_combo")

        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)

        self.start_time = QTimeEdit()
        self.end_time = QTimeEdit()

        self.lecture_title = QLineEdit()
        self.lecture_title.setPlaceholderText("Enter lecture title")

        self.proceed_btn = QPushButton("Proceed Attendance")
        self.proceed_btn.clicked.connect(self.proceed_attendance)

        self.date_edit.setObjectName("form_input")
        self.start_time.setObjectName("form_input")
        self.end_time.setObjectName("form_input")
        self.lecture_title.setObjectName("form_input")
        self.proceed_btn.setObjectName("button_style")

        form_layout = QFormLayout(self)

        form_layout.addRow("Course & Class", self.course_class_combo)
        form_layout.addRow("Date", self.date_edit)
        form_layout.addRow("Start Time", self.start_time)
        form_layout.addRow("End Time", self.end_time)
        form_layout.addRow("Lecture Title", self.lecture_title)
        form_layout.addRow(self.proceed_btn)


        self.setLayout(form_layout)

        main = QVBoxLayout()
        main.addLayout(top_layout)
        main.addLayout(form_layout)
        self.setLayout(main)

        self.load_course_class()

    def load_course_class(self):
        self.course_class_combo.clear()
        cursor.execute("SELECT teacher_id FROM teacher WHERE user_id = ?", (self.teacher_id,))
        row = cursor.fetchone()
        if row:
            self.teacher_own_id = row[0]
        else:
            QMessageBox.critical(self, "Error", "Teacher ID not found!")
            return
        cursor.execute("EXEC teacher_get_classes_attendance ?", (self.teacher_own_id,))
        for row in cursor.fetchall():
            display_text = f"{row.course_title} ({row.class_name})"
            self.course_class_combo.addItem(
                display_text,
                (row.course_id, row.class_id)
            )

    def proceed_attendance(self):
        if self.course_class_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Error", "Select Course & Class")
            return
        course_id, class_id = self.course_class_combo.currentData()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        start = self.start_time.time().toString("HH:mm:ss")
        end = self.end_time.time().toString("HH:mm:ss")
        title = self.lecture_title.text()
        if title.strip() == "":
            QMessageBox.warning(self, "Error", "Enter lecture title")
            return

        self.next_window = MarkAttendanceWindow(
            self.teacher_own_id,
            course_id,
            class_id,
            date,
            start,
            end,
            title
        )
        self.next_window.show()
        self.close()


    def go_back(self):
      self.previous_window.show()
      self.close()

class MarkAttendanceWindow(QWidget):
    def __init__(self, teacher_id, course_id, class_id,
                 lecture_date, start_time, end_time, lecture_title):
        super().__init__()

        self.teacher_id = teacher_id
        self.course_id = course_id
        self.class_id = class_id
        self.lecture_date = lecture_date
        self.start_time = start_time
        self.end_time = end_time
        self.lecture_title = lecture_title

        self.setWindowTitle("Mark Attendance")
        self.resize(1000, 600)

        self.students = []

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Reg No", "Student Name", "Present", "Absent"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.submit_btn = QPushButton("Submit Attendance")
        self.submit_btn.clicked.connect(self.submit_attendance)

        self.table.setObjectName("attendance_table")
        self.submit_btn.setObjectName("button_style")

        # ---- layout ----
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.submit_btn)
        self.setLayout(layout)

        self.load_students()

    def load_students(self):
        self.students.clear()
        self.button_groups = []

        cursor.execute("EXEC get_class_students_attendance ?, ?", (int(self.class_id), int(self.course_id)))
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            student_id, reg_no, name = row
            self.students.append(student_id)

            self.table.setItem(i, 0, QTableWidgetItem(str(reg_no)))
            self.table.setItem(i, 1, QTableWidgetItem(name))

            self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            present = QRadioButton(self.table)
            absent = QRadioButton(self.table)


            group = QButtonGroup(self)
            group.addButton(present)
            group.addButton(absent)
            self.button_groups.append(group)

            self.table.setCellWidget(i, 2, present)
            self.table.setCellWidget(i, 3, absent)

    def submit_attendance(self):
        try:
            for row in range(self.table.rowCount()):
                p = self.table.cellWidget(row, 2).isChecked()
                a = self.table.cellWidget(row, 3).isChecked()
                if not p and not a:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Please mark attendance for all students"
                    )
                    return
            conn.autocommit = False
            for row in range(self.table.rowCount()):
                student_id = self.students[row]
                present = self.table.cellWidget(row, 2).isChecked()
                status = "Present" if present else "Absent"

                cursor.execute(
                    "EXEC insert_attendance ?,?,?,?,?,?,?,?,?",
                    (
                        self.teacher_id,
                        self.course_id,
                        self.class_id,
                        self.lecture_date,
                        self.start_time,
                        self.end_time,
                        self.lecture_title,
                        student_id,
                        status
                    )
                )
            conn.commit()
            QMessageBox.information(self, "Success", "Attendance saved successfully")
            self.close()

        except Exception as e:
            conn.rollback()

            QMessageBox.critical(
                self, "Error", f"Attendance failed\n{str(e)}"
            )

#-----------------------------------------------------

class teacher_grading(QWidget):
    def __init__(self, teacher_dashboard, teacher_user_id):
        super().__init__()
        self.setWindowTitle("Teacher Grading")
        self.resize(1000, 600)

        self.previous_window = teacher_dashboard
        self.logged_in_teacher = teacher_user_id

        # ---------------- TOP UI ----------------
        back = QPushButton("← Back")
        back.setObjectName("backbutton_style")
        back.clicked.connect(self.go_back)

        title = QLabel("GRADING")
        title.setObjectName("admin_student_title")

        top = QHBoxLayout()
        top.addWidget(back)
        top.addStretch()

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addLayout(title_layout)

        # ---------- CLASS / COURSE DROPDOWN ----------
        self.class_dropdown = QComboBox()
        self.class_dropdown.setObjectName("form_combo")
        layout.addWidget(QLabel("Select Class / Course:"))
        layout.addWidget(self.class_dropdown)

        self.load_teacher_classes()

        # -------- BUTTONS ---------
        self.quiz_btn = QPushButton("Enter Quiz Marks")
        self.ass_btn = QPushButton("Enter Assignment Marks")
        self.mid_btn = QPushButton("Enter Midterm Marks")
        self.final_btn = QPushButton("Enter Final Marks")

        for b in [self.quiz_btn, self.ass_btn, self.mid_btn, self.final_btn]:
            b.setObjectName("button_style")

        self.quiz_btn.clicked.connect(lambda: self.open_marks_window("quiz"))
        self.ass_btn.clicked.connect(lambda: self.open_marks_window("assignment"))
        self.mid_btn.clicked.connect(lambda: self.open_marks_window("midterm"))
        self.final_btn.clicked.connect(lambda: self.open_marks_window("final"))

        for b in [self.quiz_btn, self.ass_btn, self.mid_btn, self.final_btn]:
            layout.addWidget(b)

        self.setLayout(layout)

    # ---------------- HELPERS ----------------
    def get_selected_class_id(self):
        idx = self.class_dropdown.currentIndex()
        if idx < 0 or self.class_dropdown.currentData() is None:
            QMessageBox.warning(self, "Error", "Please select a class!")
            return None
        return self.class_dropdown.currentData()

    def load_teacher_classes(self):
        try:
            # 1) Get teacher_id
            cursor.execute("SELECT teacher_id FROM teacher WHERE user_id = ?", (self.logged_in_teacher,))
            row = cursor.fetchone()
            if not row:
                QMessageBox.warning(self, "Error", "Teacher record not found.")
                return
            teacher_id = row[0]

            # 2) Fetch assigned classes
            cursor.execute("EXEC get_teacher_courses ?", (teacher_id,))
            rows = cursor.fetchall()
            self.class_dropdown.clear()
            self.class_dropdown.addItem("Select Class", None)

            for (assignment_id, course_id, course_name, class_id, class_name, sem) in rows:
                text = f"{course_name} - {class_name} (Sem {sem})"
                self.class_dropdown.addItem(text, class_id)

        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))

    def open_marks_window(self, assessment_type):
        class_id = self.get_selected_class_id()
        if class_id is None:
            return
        if assessment_type == "quiz":
            self.w = QuizMarksWindow(self, self.logged_in_teacher, class_id)
        elif assessment_type == "assignment":
            self.w = AssignmentMarksWindow(self, self.logged_in_teacher, class_id)
        elif assessment_type == "midterm":
            self.w = MidMarksWindow(self, self.logged_in_teacher, class_id)
        elif assessment_type == "final":
            self.w = FinalMarksWindow(self, self.logged_in_teacher, class_id)

        self.w.show()
        self.hide()

    def go_back(self):
        self.previous_window.show()
        self.close()

#quiz
class QuizMarksWindow(QWidget):
    def __init__(self, previous, teacher_id, class_id):
        super().__init__()
        self.previous = previous
        self.teacher_id = teacher_id
        self.class_id = class_id

        self.setWindowTitle("Enter Quiz Marks")
        self.resize(1000, 600)
        layout = QVBoxLayout()
        self.setLayout(layout)

        back = QPushButton("← Back")
        back.setObjectName("backbutton_style")
        back.clicked.connect(self.go_back)
        layout.addWidget(back)

        self.table = QTableWidget()
        self.table.setObjectName("attendance_table")
        layout.addWidget(self.table)

        save_btn = QPushButton("Save Marks")
        save_btn.setObjectName("button_style")
        save_btn.clicked.connect(self.save_marks)
        layout.addWidget(save_btn)

        self.assessment_type = "quiz"
        self.load_students()

    def go_back(self):
        self.previous.show()
        self.close()

    def load_students(self):
        cursor.execute("""
            SELECT s.student_id, s.registration_no, u.full_name
            FROM student s
            INNER JOIN users u ON u.user_id = s.user_id
            WHERE s.class_id = ?
        """, self.class_id)
        students = cursor.fetchall()

        self.student_ids = []
        self.table.setRowCount(len(students))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Reg No", "Name", "Q1", "Q2", "Q3", "Q4"])

        for row, (sid, reg, name) in enumerate(students):
            self.student_ids.append(sid)
            self.table.setItem(row, 0, QTableWidgetItem(reg))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            for col in range(2, 6):
                self.table.setItem(row, col, QTableWidgetItem("0"))

    def save_marks(self):
        try:
            for row, sid in enumerate(self.student_ids):
                for i in range(2, self.table.columnCount()):
                    assessment = "quiz"
                    marks_text = self.table.item(row, i).text() or "0"

                    # Convert to number
                    try:
                        marks = float(marks_text)
                    except ValueError:
                        QMessageBox.warning(self, "Invalid Input",
                                            f"Marks for {self.table.item(row, 1).text()} ({assessment}) must be a number.")
                        return

                    # Set max marks per assessment
                    if self.assessment_type == "quiz":
                        max_marks = 10
                    elif self.assessment_type == "assignment":
                        max_marks = 10
                    elif self.assessment_type == "midterm":
                        max_marks = 30
                    elif self.assessment_type == "final":
                        max_marks = 50

                    # Check range
                    if marks < 0 or marks > max_marks:
                        QMessageBox.warning(self, "Invalid Marks",
                                            f"Marks for {self.table.item(row, 1).text()} ({assessment}) must be between 0 and {max_marks}.")
                        return

                    # Save in DB if valid
                    cursor.execute("EXEC insert_marks ?, ?, ?, ?, ?",
                                   (sid, self.class_id, assessment, max_marks, marks))

            conn.commit()
            QMessageBox.information(self, "Saved", "Marks saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

#assignemnet
class AssignmentMarksWindow(QWidget):
    def __init__(self, previous, teacher_id, class_id):
        super().__init__()
        self.previous = previous
        self.teacher_id = teacher_id
        self.class_id = class_id

        self.setWindowTitle("Enter Assignment Marks")
        self.resize(1000, 600)
        layout = QVBoxLayout()
        self.setLayout(layout)

        back = QPushButton("← Back")
        back.setObjectName("backbutton_style")
        back.clicked.connect(self.go_back)
        layout.addWidget(back)

        self.table = QTableWidget()
        self.table.setObjectName("attendance_table")
        layout.addWidget(self.table)

        save_btn = QPushButton("Save Marks")
        save_btn.setObjectName("button_style")
        save_btn.clicked.connect(self.save_marks)
        layout.addWidget(save_btn)

        self.assessment_type = "assignment"
        self.load_students()

    def go_back(self):
        self.previous.show()
        self.close()

    def load_students(self):
        cursor.execute("""
            SELECT s.student_id, s.registration_no, u.full_name
            FROM student s
            INNER JOIN users u ON u.user_id = s.user_id
            WHERE s.class_id = ?
        """, self.class_id)
        students = cursor.fetchall()

        self.student_ids = []
        self.table.setRowCount(len(students))
        self.table.setColumnCount(6)  # Change if you have different number of assignments
        self.table.setHorizontalHeaderLabels(["Reg No", "Name", "A1", "A2", "A3", "A4"])

        for row, (sid, reg, name) in enumerate(students):
            self.student_ids.append(sid)
            self.table.setItem(row, 0, QTableWidgetItem(reg))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            for col in range(2, 6):
                self.table.setItem(row, col, QTableWidgetItem("0"))

    def save_marks(self):
        try:
            for row, sid in enumerate(self.student_ids):
                for i in range(2, self.table.columnCount()):
                    assessment = "assignment"
                    marks_text = self.table.item(row, i).text() or "0"

                    # Convert to number
                    try:
                        marks = float(marks_text)
                    except ValueError:
                        QMessageBox.warning(self, "Invalid Input",
                                            f"Marks for {self.table.item(row, 1).text()} ({assessment}) must be a number.")
                        return

                    # Set max marks per assessment
                    if self.assessment_type == "quiz":
                        max_marks = 10
                    elif self.assessment_type == "assignment":
                        max_marks = 10
                    elif self.assessment_type == "midterm":
                        max_marks = 30
                    elif self.assessment_type == "final":
                        max_marks = 50

                    # Check range
                    if marks < 0 or marks > max_marks:
                        QMessageBox.warning(self, "Invalid Marks",
                                            f"Marks for {self.table.item(row, 1).text()} ({assessment}) must be between 0 and {max_marks}.")
                        return

                    # Save in DB if valid
                    cursor.execute("EXEC insert_marks ?, ?, ?, ?, ?",
                                   (sid, self.class_id, assessment, max_marks, marks))

            conn.commit()
            QMessageBox.information(self, "Saved", "Marks saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

#mid
class MidMarksWindow(QWidget):
    def __init__(self, previous, teacher_id, class_id):
        super().__init__()
        self.previous = previous
        self.teacher_id = teacher_id
        self.class_id = class_id

        self.setWindowTitle("Enter Midterm Marks")
        self.resize(1000, 600)
        layout = QVBoxLayout()
        self.setLayout(layout)

        back = QPushButton("← Back")
        back.setObjectName("backbutton_style")
        back.clicked.connect(self.go_back)
        layout.addWidget(back)

        self.table = QTableWidget()
        self.table.setObjectName("attendance_table")
        layout.addWidget(self.table)

        save_btn = QPushButton("Save Marks")
        save_btn.setObjectName("button_style")
        save_btn.clicked.connect(self.save_marks)
        layout.addWidget(save_btn)

        self.assessment_type = "midterm"
        self.load_students()

    def go_back(self):
        self.previous.show()
        self.close()

    def load_students(self):
        cursor.execute("""
            SELECT s.student_id, s.registration_no, u.full_name
            FROM student s
            INNER JOIN users u ON u.user_id = s.user_id
            WHERE s.class_id = ?
        """, self.class_id)
        students = cursor.fetchall()

        self.student_ids = []
        self.table.setRowCount(len(students))
        self.table.setColumnCount(3)  # Only Midterm 1 and Midterm 2 (if needed)
        self.table.setHorizontalHeaderLabels(["Reg No", "Name", "Midterm"])

        for row, (sid, reg, name) in enumerate(students):
            self.student_ids.append(sid)
            self.table.setItem(row, 0, QTableWidgetItem(reg))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            for col in range(2, 3):
                self.table.setItem(row, col, QTableWidgetItem("0"))

    def save_marks(self):
        try:
            for row, sid in enumerate(self.student_ids):
                for i in range(2, self.table.columnCount()):
                    assessment = "midterm"
                    marks_text = self.table.item(row, i).text() or "0"

                    # Convert to number
                    try:
                        marks = float(marks_text)
                    except ValueError:
                        QMessageBox.warning(self, "Invalid Input",
                                            f"Marks for {self.table.item(row, 1).text()} ({assessment}) must be a number.")
                        return

                    # Set max marks per assessment
                    if self.assessment_type == "quiz":
                        max_marks = 10
                    elif self.assessment_type == "assignment":
                        max_marks = 10
                    elif self.assessment_type == "midterm":
                        max_marks = 30
                    elif self.assessment_type == "final":
                        max_marks = 50

                    # Check range
                    if marks < 0 or marks > max_marks:
                        QMessageBox.warning(self, "Invalid Marks",
                                            f"Marks for {self.table.item(row, 1).text()} ({assessment}) must be between 0 and {max_marks}.")
                        return

                    # Save in DB if valid
                    cursor.execute("EXEC insert_marks ?, ?, ?, ?, ?",
                                   (sid, self.class_id, assessment, max_marks, marks))

            conn.commit()
            QMessageBox.information(self, "Saved", "Marks saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

#final
class FinalMarksWindow(QWidget):
    def __init__(self, previous, teacher_id, class_id):
        super().__init__()
        self.previous = previous
        self.teacher_id = teacher_id
        self.class_id = class_id

        self.setWindowTitle("Enter Final Marks")
        self.resize(1000, 600)
        layout = QVBoxLayout()
        self.setLayout(layout)

        back = QPushButton("← Back")
        back.setObjectName("backbutton_style")
        back.clicked.connect(self.go_back)
        layout.addWidget(back)

        self.table = QTableWidget()
        self.table.setObjectName("attendance_table")
        layout.addWidget(self.table)

        save_btn = QPushButton("Save Marks")
        save_btn.setObjectName("button_style")
        save_btn.clicked.connect(self.save_marks)
        layout.addWidget(save_btn)

        self.assessment_type = "final"
        self.load_students()

    def go_back(self):
        self.previous.show()
        self.close()

    def load_students(self):
        cursor.execute("""
            SELECT s.student_id, s.registration_no, u.full_name
            FROM student s
            INNER JOIN users u ON u.user_id = s.user_id
            WHERE s.class_id = ?
        """, self.class_id)
        students = cursor.fetchall()

        self.student_ids = []
        self.table.setRowCount(len(students))
        self.table.setColumnCount(3)  # Only Final
        self.table.setHorizontalHeaderLabels(["Reg No", "Name", "Final"])

        for row, (sid, reg, name) in enumerate(students):
            self.student_ids.append(sid)
            self.table.setItem(row, 0, QTableWidgetItem(reg))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem("0"))

    def save_marks(self):
        try:
            for row, sid in enumerate(self.student_ids):
                for i in range(2, self.table.columnCount()):
                    assessment = "midterm"
                    marks_text = self.table.item(row, i).text() or "0"

                    try:
                        marks = float(marks_text)
                    except ValueError:
                        QMessageBox.warning(self, "Invalid Input",
                                            f"Marks for {self.table.item(row, 1).text()} ({assessment}) must be a number.")
                        return
                    if self.assessment_type == "quiz":
                        max_marks = 10
                    elif self.assessment_type == "assignment":
                        max_marks = 10
                    elif self.assessment_type == "midterm":
                        max_marks = 30
                    elif self.assessment_type == "final":
                        max_marks = 50

                    if marks < 0 or marks > max_marks:
                        QMessageBox.warning(self, "Invalid Marks",
                                            f"Marks for {self.table.item(row, 1).text()} ({assessment}) must be between 0 and {max_marks}.")
                        return

                    cursor.execute("EXEC insert_marks ?, ?, ?, ?, ?",
                                   (sid, self.class_id, assessment, max_marks, marks))

            conn.commit()
            QMessageBox.information(self, "Saved", "Marks saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


#-------------------------------------------------------------------------------------------------------------------------------
#studnet liat
class teacher_studentlist(QWidget):
    def __init__(self, teacher_dashboard, teacher_user_id):
        super().__init__()
        self.previous_window = teacher_dashboard
        self.logged_in_teacher = teacher_user_id

        self.setWindowTitle("Teacher Student List")
        self.resize(1000, 600)

        self.title_label = QLabel("Teacher Student List")
        self.title_label.setObjectName("admin_student_title")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName('backbutton_style')
        self.back_button.setFixedSize(100, 35)
        self.back_button.clicked.connect(self.go_back)

        # ComboBox to select course/class
        self.class_combo = QComboBox()
        self.class_combo.setObjectName("form_combo")
        self.select_class_label = QLabel("Select Class:")
        self.select_class_label.setObjectName("label_style")

        self.student_table = QTableWidget()
        self.student_table.setColumnCount(3)
        self.student_table.setHorizontalHeaderLabels(['Student ID', 'Registration No', 'Full Name'])
        self.student_table.setObjectName("course_detail_table")
        self.student_table.horizontalHeader().setStretchLastSection(True)
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.back_button)
        sec_layout = QHBoxLayout()
        top_layout.addStretch()
        sec_layout.addWidget(self.select_class_label)
        sec_layout.addWidget(self.class_combo )


        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(sec_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.title_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.student_table)
        self.setLayout(main_layout)

        self.load_assigned_courses()
        self.class_combo.currentIndexChanged.connect(self.load_students_for_class)

    def go_back(self):
        self.previous_window.show()
        self.close()

    def load_assigned_courses(self):
        try:
            cursor.execute("SELECT teacher_id FROM teacher WHERE user_id = ?",
                           (self.logged_in_teacher,))
            teacher_row = cursor.fetchone()
            if teacher_row:
                teacher_id = teacher_row[0]
                cursor.execute("EXEC get_teacher_courses ?", (teacher_id,))
            rows = cursor.fetchall()
            for r in rows:
                assignment_id, course_id, course_name, class_id, class_name, sem = r
                text = f"{course_name} - {class_name} (Sem {sem})"
                self.class_combo.addItem(text, assignment_id)
            if len(rows) == 0:
                QMessageBox.warning(self, "No Courses", "No courses found for this teacher.")
                return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading courses:\n{e}")

    def load_students_for_class(self):
        assignment_id = self.class_combo.currentData()  # Get assignment_id
        if assignment_id is None:
            return

        try:
            cursor.execute("""
                SELECT s.student_id, s.registration_no, u.full_name
                FROM student_class1 sc
                JOIN student s ON sc.student_id = s.student_id
                JOIN users u ON s.user_id = u.user_id
                JOIN teacher_course_assignment tca ON tca.class_id = sc.class_id
                WHERE tca.assignment_id = ?
            """, (assignment_id,))

            rows = cursor.fetchall()
            self.student_table.setRowCount(0)

            for i, row in enumerate(rows):
                self.student_table.insertRow(i)
                self.student_table.setItem(i, 0, QTableWidgetItem(str(row[0])))
                self.student_table.setItem(i, 1, QTableWidgetItem(row[1]))
                self.student_table.setItem(i, 2, QTableWidgetItem(row[2]))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading students:\n{e}")


#--------------------------------------------------------------------------------------------------------------------------------------------------------------

class teacher_announcements(QWidget):
      def __init__(self,teacher_dashboard,teacher_user_id):
        super().__init__()
        self.setWindowTitle("Teacher Announcemnet")
        self.resize(1000, 600)

        self.previous_window = teacher_dashboard
        self.logged_in_teacher = teacher_user_id

        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_button)
        top_bar.addStretch()
        self.back_button.setObjectName('backbutton_style')

        self.course_label = QLabel("Select Course Assigned to You:")
        self.course_dropdown = QComboBox()
        self.course_label.setObjectName("label_style")
        self.course_dropdown.setObjectName("form_combo")
        self.load_assigned_courses_announcements()
        self.btn_text = QPushButton("Create Text Announcement")
        self.btn_text.setObjectName("button_style")
        self.btn_text.clicked.connect(self.open_text_announcement_window)
        self.btn_assignment = QPushButton("Upload Assignment")
        self.btn_assignment.setObjectName("button_style")
        self.btn_assignment.clicked.connect(self.open_assignment_window)

        self.btn_view_uploaded = QPushButton("View Uploaded Assignments")
        self.btn_view_uploaded.setObjectName("button_style")
        self.btn_view_uploaded.clicked.connect(self.open_uploaded_assignments)
        self.btn_view_submissions = QPushButton("View Student Submissions")
        self.btn_view_submissions.setObjectName("button_style")
        self.btn_view_submissions.clicked.connect(self.open_student_submissions)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addSpacing(20)
        layout.addWidget(self.course_label)
        layout.addWidget(self.course_dropdown)
        layout.addSpacing(30)
        layout.addWidget(self.btn_text)
        layout.addWidget(self.btn_assignment)
        layout.addWidget(self.btn_view_uploaded)
        layout.addWidget(self.btn_view_submissions)
        layout.addStretch()
        self.setLayout(layout)

      def load_assigned_courses_announcements(self):
          try:
              cursor.execute("SELECT teacher_id FROM teacher WHERE user_id = ?",
                             (self.logged_in_teacher,))
              teacher_row = cursor.fetchone()
              if teacher_row:
                  teacher_id = teacher_row[0]
                  cursor.execute("EXEC get_teacher_courses ?", (teacher_id,))
              rows = cursor.fetchall()
              for r in rows:
                  assignment_id, course_id, course_name, class_id, class_name, sem = r
                  text = f"{course_name} - {class_name} (Sem {sem})"
                  self.course_dropdown.addItem(text, assignment_id)
              if len(rows) == 0:
                      QMessageBox.warning(self, "No Courses", "No courses found for this teacher.")
                      return
          except Exception as e:
              QMessageBox.critical(self, "Error", f"Error loading courses:\n{e}")

      def open_text_announcement_window(self):
          self.text_window = TextAnnouncementWindow(self)
          self.text_window.show()
          self.hide()

      def open_assignment_window(self):
          self.assignment_window = AssignmentUploadWindow(self)
          self.assignment_window.show()
          self.hide()

      def open_uploaded_assignments(self):
          self.uploaded_win = TeacherOwnAssignmentsWindow(self, self.logged_in_teacher)
          self.uploaded_win.show()
          self.hide()

      def open_student_submissions(self):
          self.submissions_win = TeacherStudentSubmissionsWindow(self, self.logged_in_teacher)
          self.submissions_win.show()
          self.hide()

      def go_back(self):
          self.previous_window.show()
          self.close()
class TeacherStudentSubmissionsWindow(QWidget):
    def __init__(self, previous, teacher_id):
        super().__init__()
        self.previous = previous
        self.teacher_id = teacher_id

        self.setWindowTitle("Student Submissions")
        self.resize(1000, 600)

        back = QPushButton("← Back")
        back.setObjectName("backbutton_style")
        back.clicked.connect(self.go_back)

        top = QHBoxLayout()
        top.addWidget(back)
        top.addStretch()

        self.scroll_layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(self.scroll_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.load_submissions()

    def load_submissions(self):
        try:
            cursor.execute("EXEC get_submissions_for_assignment ?", (self.teacher_id,))
            rows = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            return

        for i in reversed(range(self.scroll_layout.count())):
            w = self.scroll_layout.itemAt(i).widget()
            if w: w.setParent(None)

        for r in rows:
            sub_id, student_name, roll_no, title, file_name, file_path, submitted_at = r

            box = QGroupBox()
            box.setObjectName("groupbox_style")

            layout = QVBoxLayout()
            layout.addWidget(QLabel(f"<b>Student:</b> {student_name} ({roll_no})"))
            layout.addWidget(QLabel(f"<b>Assignment:</b> {title}"))
            layout.addWidget(QLabel(f"<b>Submitted:</b> {submitted_at}"))
            layout.addWidget(QLabel(f"<b>File:</b> {file_name}"))

            btn = QPushButton("Download Submission")
            btn.setObjectName("button_style")
            btn.clicked.connect(lambda _, p=file_path, n=file_name: self.download_file(p, n))
            layout.addWidget(btn)

            box.setLayout(layout)
            self.scroll_layout.addWidget(box)

    def download_file(self, path, name):
        if not os.path.exists(path):
            QMessageBox.critical(self, "Error", "File missing.")
            return

        save, _ = QFileDialog.getSaveFileName(self, "Save", name)
        if save:
            shutil.copy(path, save)
            QMessageBox.information(self, "Done", "Submission downloaded.")

    def go_back(self):
        self.previous.show()
        self.close()

class TeacherOwnAssignmentsWindow(QWidget):
  def __init__(self, teacher_announcements, teacher_id):
      super().__init__()
      self.previous = teacher_announcements
      self.teacher_id = teacher_id

      self.setWindowTitle("Uploaded Assignments")
      self.resize(1000, 600)

      back = QPushButton("← Back")
      back.setObjectName("backbutton_style")
      back.clicked.connect(self.go_back)

      top = QHBoxLayout()
      top.addWidget(back)
      top.addStretch()

      self.scroll_layout = QVBoxLayout()
      container = QWidget()
      container.setLayout(self.scroll_layout)

      scroll = QScrollArea()
      scroll.setWidgetResizable(True)
      scroll.setWidget(container)

      layout = QVBoxLayout()
      layout.addLayout(top)
      layout.addWidget(scroll)
      self.setLayout(layout)

      self.load_uploaded_assignments()

  def load_uploaded_assignments(self):
      try:
          cursor.execute("""
              SELECT ann_id, title, created_at, expires_at, file_name, file_path
              FROM announcement
              WHERE ann_type='assignment' AND created_by=?
              ORDER BY created_at DESC
          """, (self.teacher_id,))
          rows = cursor.fetchall()
      except Exception as e:
          QMessageBox.critical(self, "DB Error", str(e))
          return

      for i in reversed(range(self.scroll_layout.count())):
          w = self.scroll_layout.itemAt(i).widget()
          if w: w.setParent(None)

      for r in rows:
          ann_id, title, created_at, due, file_name, file_path = r

          box = QGroupBox()
          box.setObjectName("groupbox_style")
          layout = QVBoxLayout()

          layout.addWidget(QLabel(f"<b>Title:</b> {title}"))
          layout.addWidget(QLabel(f"<b>Assigned:</b> {created_at}"))
          layout.addWidget(QLabel(f"<b>Due:</b> {due}"))
          layout.addWidget(QLabel(f"<b>File:</b> {file_name}"))

          btn = QPushButton("Download File")
          btn.setObjectName("button_style")
          btn.clicked.connect(lambda _, p=file_path, n=file_name: self.download_file(p, n))
          layout.addWidget(btn)

          box.setLayout(layout)
          self.scroll_layout.addWidget(box)

  def download_file(self, path, name):
      if not os.path.exists(path):
          QMessageBox.critical(self, "Error", "File missing.")
          return

      save, _ = QFileDialog.getSaveFileName(self, "Save", name)
      if save:
          shutil.copy(path, save)
          QMessageBox.information(self, "Done", "Downloaded.")

  def go_back(self):
      self.previous.show()
      self.close()

          # textassignment window
class TextAnnouncementWindow(QWidget):
    def __init__(self,teacher_announcements):
        super().__init__()
        self.previous  = teacher_announcements

        self.setWindowTitle("Create Text Announcement")
        self.resize(1000, 600)

        self.back_button= QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_button)
        top_bar.addStretch()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter announcement title")
        self.title_input.setObjectName("text_box_style")

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter announcement details...")
        self.message_input.setObjectName("text_box_style")
        self.message_input.setObjectName("label_style")

        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["text"])
        self.type_dropdown.setObjectName("form_combo")


        self.save_btn = QPushButton("Post Announcement")
        self.save_btn.clicked.connect(self.save_announcement)
        self.save_btn.setObjectName("button_style")

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        lbl1 = QLabel("Announcement Title:")
        lbl1.setObjectName("label_style")
        layout.addWidget(lbl1)
        layout.addWidget(self.title_input)

        layout.addWidget(QLabel("Announcement Type"))
        layout.addWidget(self.type_dropdown)


        lbl2 = QLabel("Message:")
        lbl2.setObjectName("label_style")
        layout.addWidget(lbl2)
        layout.addWidget(self.message_input)

        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def go_back(self):
        self.previous.show()
        self.close()

    def save_announcement(self):
        try:
            title = self.title_input.text()

            msg = self.message_input.toPlainText()
            assignment_id = self.previous.course_dropdown.currentData()
            ann_type = self.type_dropdown.currentText()
            if not title or not msg:
                QMessageBox.warning(self, "Missing", "Please enter title & message")
                return
            cursor.execute(
                "SELECT class_id FROM teacher_course_assignment WHERE assignment_id=?",
                (assignment_id,)
            )
            class_id_row = cursor.fetchone()
            if not class_id_row:
                QMessageBox.critical(self, "Error", "Class ID not found for this course.")
                return
            class_id = class_id_row[0]
            cursor.execute(
                "EXEC add_text_announcements ?, ?, ?, ?,?",
                (title, msg, self.previous.logged_in_teacher, class_id,ann_type)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Announcement Posted!")
            self.go_back()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{e}")

        #teacher asisgnmnet upload
class AssignmentUploadWindow(QWidget):
    def __init__(self, teacher_announcements):
        super().__init__()
        self.previous = teacher_announcements
        self.file_path = None
        self.setWindowTitle("Upload Assignment")
        self.resize(1000, 600)

        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setObjectName('backbutton_style')
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Assignment Title")
        self.title_input.setObjectName("text_box_style")

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter announcement details...")
        self.message_input.setObjectName("text_box_style")
        self.message_input.setObjectName("label_style")

        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["assignment"])
        self.type_dropdown.setObjectName("form_combo")

        self.start_dt = QDateTimeEdit()
        self.start_dt.setObjectName("form_input")
        self.start_dt.setCalendarPopup(True)

        self.due_dt = QDateTimeEdit()
        self.due_dt.setObjectName("form_input")
        self.due_dt.setCalendarPopup(True)

        l11 = self.file_label = QLabel("No file selected")
        l11.setObjectName("label_style")
        self.file_btn = QPushButton("Choose PDF")
        self.file_btn.clicked.connect(self.choose_file)
        self.file_btn.setObjectName("button_style")

        self.upload_btn = QPushButton("Upload Assignment")
        self.upload_btn.clicked.connect(self.upload_assignment)
        self.upload_btn.setObjectName("button_style")

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(QLabel("Assignment Title:"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Announcement Type"))
        layout.addWidget(self.type_dropdown)
        layout.addWidget(QLabel("Start Date & Time:"))
        layout.addWidget(self.start_dt)
        layout.addWidget(QLabel("Due Date & Time:"))
        layout.addWidget(self.due_dt)
        layout.addSpacing(10)
        l1 = QLabel("Upload PDF File:")
        layout.addWidget(l1)
        l1.setObjectName("label_style")
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_btn)
        layout.addSpacing(15)
        layout.addWidget(self.upload_btn)

        self.setLayout(layout)

    def go_back(self):
        self.previous.show()
        self.close()

    def choose_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Assignment File", "", "PDF Files (*.pdf)")
        if f:
            self.file_path = f
            self.file_label.setText(os.path.basename(f))

    def upload_assignment(self):
        try :
            print("[DEBUG] Starting assignment upload")
            if not self.file_path:
                QMessageBox.warning(self, "Missing File", "Please choose a PDF file.")
                print("[DEBUG] Missing file")
                return

            title = self.title_input.text()
            if not title:
                QMessageBox.warning(self, "Missing Title", "Please enter assignment title.")
                return
            start = self.start_dt.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            due = self.due_dt.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            ann_type = self.type_dropdown.currentText()

            assignment_id = self.previous.course_dropdown.currentData()
            if assignment_id is None:
                QMessageBox.warning(self, "Missing Course", "Please select a course.")
                return

            # get class_id
            cursor.execute(
                "SELECT class_id FROM teacher_course_assignment WHERE assignment_id=?",
                (assignment_id,)
            )
            class_id = cursor.fetchone()[0]

            file_name = os.path.basename(self.file_path)
            file_size = os.path.getsize(self.file_path) // 1024
            save_path = "uploads/" + file_name

            os.makedirs("uploads", exist_ok=True)
            shutil.copy(self.file_path, save_path)
            print(self.file_path)

            cursor.execute("""
                EXEC add_assignment_announcements
                ?, ?, ?, ?, ?, ?, ?, ?
            """, (
                title,
                self.previous.logged_in_teacher,
                class_id,
                start,
                due,
                file_name,
                save_path,
                ann_type
            ))

            conn.commit()
            QMessageBox.information(self, "Success", "Assignment Uploaded!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error occurred:\n{e}")
#--------------------------------------------------------------------------------------------------------------------------------------------------------

class teacher_dashboard(QWidget):

    def __init__(self,Login,teacher_user_id):
        super().__init__()
        self.resize(1000,600)
        self.setWindowTitle("CUI Portal")

        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')

        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        self.logged_in_teacher = teacher_user_id
        self.previous_window = Login
        self.admin_title = QLabel("HELLO TEACHER!")
        self.admin_title.setObjectName('dashboard_title_style')

        self.grid = QGridLayout()
        items = [
            ("Profile", "admin_profile.png",teacher_profile),
            ("Student List", "student.png",teacher_studentlist),
            ("Announcement", "announcement.png",teacher_announcements),
            ("Attendance", "attendance.png",teacher_attendance),
            ("Courses", "course.png",teacher_courses),
            ("Grading", "marks.png",teacher_grading)
        ]

        row = 0
        col = 0

        for title,icon,new_window in items:
            card = self.create_single_card(title,icon,new_window)
            self.grid.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        row1 = QHBoxLayout()

        row1.addWidget(self.admin_title, alignment=Qt.AlignCenter)

        master_layout = QVBoxLayout()
        master_layout.addLayout(top_row)
        master_layout.addLayout(row1)


        grid_widget = QWidget()
        grid_widget.setLayout(self.grid)
        master_layout.addWidget(grid_widget)


        self.outer_frame = QFrame()
        self.outer_frame.setLayout(master_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.outer_frame)
        self.setLayout(main_layout)

    def go_back(self):
        self.previous_window.show()
        self.close()

    def create_single_card(self,title,icon,window_class):
        card_frame = QFrame()
        card_frame.setFixedSize(180, 180)
        layout = QVBoxLayout(card_frame)
        layout.setAlignment(Qt.AlignCenter)

        icon_var = QIcon(icon)
        button = QPushButton()
        button.setIcon(icon_var)
        button.setIconSize(QSize(80,80))
        button.setObjectName('icon_style')


        icon_title = QLabel(title)
        icon_title.setAlignment(Qt.AlignCenter)
        icon_title.setObjectName('title_style')

        layout.addWidget(button)
        layout.addWidget(icon_title)

        button.clicked.connect(lambda: self.open_page(window_class))
        return card_frame

    def open_page(self, window_class):
        self.new_window = window_class(self,self.logged_in_teacher)
        self.new_window.show()

#---------------------------------------------------------------------------------------------------------------------------
# student_dashboard
# course class
class student_courses_details(QWidget):
    def __init__(self,student_registered_courses, student_id):
        super().__init__()
        self.logged_in_student_id = student_id
        self.setWindowTitle("Course Detail")
        self.resize(1000,600)
        label = QLabel("Available Courses")

        self.previous_window = student_registered_courses
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')

        self.title = QLabel("AVAILABLE COURSES")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("dashboard_title_style")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by course title...")
        self.search_input.setObjectName("text_box_style")
        self.search_input.returnPressed.connect(self.get_course)

        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("button_style")
        self.search_btn.clicked.connect(self.get_course)

        sec_row = QHBoxLayout()
        sec_row.addWidget(self.search_input)
        sec_row.addWidget(self.search_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Course Code", "Course Title", "Credit Hours",
            "Department", "Lab", "Elective"
        ])
        self.table.setObjectName("course_detail_table")
        self.table.setSelectionBehavior(QTableWidget.SelectRows)#when u click on row whole line selected automatically
        self.table.horizontalHeader().setDefaultSectionSize(160)#default width of each col to 160px

        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addWidget(self.title)
        main_layout.addSpacing(20)
        main_layout.addLayout(sec_row)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)


    def go_back(self):
            self.previous_window.show()
            self.close()

    def get_course(self):
        search = self.search_input.text().strip()
        #fetching data from database
        if search != "":
            cursor.execute("EXEC search_courses ?", (search,))
            rows = cursor.fetchall()
        else:
            self.show_error("Please enter something to search.")
            return

        #putting data in table after fetching from db

        self.table.setRowCount(0)#clearing previous rows
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            code = QTableWidgetItem(str(row[0]))
            title = QTableWidgetItem(str(row[1]))
            credit_hr = QTableWidgetItem(str(row[2]))
            dept= QTableWidgetItem(str(row[3]))
            is_lab = QTableWidgetItem("Yes" if row[4] else "No")
            is_elective = QTableWidgetItem("Yes" if row[5] else "No")

            for col, j in enumerate([code, title, credit_hr, dept, is_lab, is_elective]):
                j.setFlags(j.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(i, col, j)

        self.table.resizeColumnsToContents()#It makes the columns auto-fit the text.



    def show_error(self, msg):
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setIcon(QMessageBox.Warning)
        box.setText(msg)
        box.exec()


class student_courses_attendance(QWidget):
    def __init__(self, student_registered_courses, student_user_id):
        super().__init__()
        self.logged_in_student_id = student_user_id
        self.setWindowTitle("Course Attendance")
        self.resize(1000, 600)

        self.previous_window = student_registered_courses

        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')
        self.title_label = QLabel("MY ATTENDANCE")
        self.title_label.setObjectName("attendance_title_style")
        self.title_label.setAlignment(Qt.AlignCenter)

        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        self.table = QTableWidget()
        self.table.setObjectName("attendance_table")
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Course",
            "Total Lectures",
            "Present",
            "Absent",
            "Attendance %",
            "Status",
            ""
        ])

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)
        self.attendance()

    def go_back(self):
        self.previous_window.show()
        self.close()

    def attendance(self):
        cursor.execute(
            "SELECT student_id FROM student WHERE user_id = ?",
            (self.logged_in_student_id,)
        )

        result = cursor.fetchone()
        if not result:
            return

        student_id = result[0]
        print(student_id)

        cursor.execute(
            "EXEC coursewise_attendance ?",
            (student_id,)
        )

        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            course, total, present, absent, percent, status = row

            self.table.setItem(row_index, 0, QTableWidgetItem(course))
            self.table.setItem(row_index, 1, QTableWidgetItem(str(total)))
            self.table.setItem(row_index, 2, QTableWidgetItem(str(present)))
            self.table.setItem(row_index, 3, QTableWidgetItem(str(absent)))
            self.table.setItem(row_index, 4, QTableWidgetItem(f"{percent}%"))
            self.table.setItem(row_index, 5, QTableWidgetItem(status))


class student_courses_marks(QWidget):
    def __init__(self, student_registered_courses, user_id):
        super().__init__()
        self.logged_in_student_id = user_id
        self.setWindowTitle("Course Marks")
        self.resize(1000, 600)

        self.previous_window = student_registered_courses
        class_info = self.fetch_student_class_info(self.logged_in_student_id)
        print("DEBUG: class_info =", class_info)
        if class_info is None:
            QMessageBox.critical(self, "Error", "Failed to load student class info.")
            return
        self.class_id = class_info["class_id"]
        self.student_id = class_info["student_id"]
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        main_layout = QVBoxLayout(container)

        # Back button
        back = QPushButton("← Back")
        back.clicked.connect(self.go_back)
        back.setObjectName("backbutton_style")
        main_layout.addWidget(back, alignment=Qt.AlignLeft)

        # Heading
        heading = QLabel("MY MARKS")
        heading.setAlignment(Qt.AlignCenter)
        heading.setObjectName("admin_student_title")
        main_layout.addWidget(heading)

        self.quiz_table = QTableWidget()
        main_layout.addWidget(self.create_simple_section("Quiz", self.quiz_table))

        self.assignment_table = QTableWidget()
        main_layout.addWidget(self.create_simple_section("Assignment", self.assignment_table))

        self.midterm_table = QTableWidget()
        main_layout.addWidget(self.create_simple_section("Midterm", self.midterm_table))

        self.final_table = QTableWidget()
        main_layout.addWidget(self.create_simple_section("Final", self.final_table))

        main_layout.addStretch()

        scroll.setWidget(container)

        layout = QVBoxLayout()
        layout.addWidget(scroll)
        self.setLayout(layout)

        self.load_marks()

    def fetch_student_class_info(self, user_id):
        try:
            cursor.execute("SELECT student_id, class_id FROM student WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            print("DEBUG: fetch_student_class_info row =", row)

            if row:
                return {
                    "class_id": row[1],
                    "student_id": row[0]
                }
        except Exception as e:
            print("Error:", e)
            return None

    def load_marks(self):
        try:
            cursor.execute("SELECT student_id FROM student WHERE user_id = ?", (self.logged_in_student_id,))
            row = cursor.fetchone()
            self.student_own_id = row[0]
            print(self.student_own_id)


            cursor.execute("""
                        SELECT m.assessment_type, m.obtained_marks, m.total_marks
                        FROM marks m
                        INNER JOIN (
                            SELECT assessment_type, MAX(marks_id) as latest_id
                            FROM marks
                            WHERE student_id = ? AND class_id = ?
                            GROUP BY assessment_type
                        ) latest ON m.marks_id = latest.latest_id
                        ORDER BY 
                            CASE 
                                WHEN m.assessment_type LIKE 'quiz%' THEN 1
                                WHEN m.assessment_type LIKE 'assignment%' THEN 2
                                WHEN m.assessment_type LIKE 'midterm%' THEN 3
                                WHEN m.assessment_type = 'final' THEN 4
                                ELSE 5
                            END,
                            m.assessment_type
                    """, (self.student_own_id, self.class_id))

            rows = cursor.fetchall()
            print("DEBUG: Marks rows:", rows)

            # Clear all tables
            self.quiz_table.setRowCount(0)
            self.assignment_table.setRowCount(0)
            self.midterm_table.setRowCount(0)
            self.final_table.setRowCount(0)

            for assessment_type, obtained, total in rows:
                at_lower = assessment_type.lower()
                if at_lower.startswith("quiz"):
                    table = self.quiz_table
                    display_name = assessment_type  # Keep original name like "quiz1"
                elif at_lower.startswith("assignment"):
                    table = self.assignment_table
                    display_name = assessment_type
                elif at_lower.startswith("midterm"):
                    table = self.midterm_table
                    display_name = assessment_type
                elif at_lower == "final":  # "final" is usually exact
                    table = self.final_table
                    display_name = assessment_type
                else:
                    continue

                row = table.rowCount()
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(assessment_type))
                table.setItem(row, 1, QTableWidgetItem(str(obtained)))
                table.setItem(row, 2, QTableWidgetItem(str(total)))

        except Exception as e:
            QMessageBox.critical(self, "Error Loading Marks", str(e))

    def create_simple_section(self, title, table):
        section = QWidget()
        section.setObjectName("section_card")

        layout = QVBoxLayout(section)
        section.setMinimumHeight(220)
        section.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Title
        lbl = QLabel(title)
        lbl.setObjectName("section_title")
        lbl.setAlignment(Qt.AlignLeft)
        layout.addWidget(lbl)

        # Table
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Title", "Obtained", "Total"])
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setObjectName("marks_table")

        layout.addWidget(table)
        layout.setSpacing(10)

        # Add bottom space
        layout.addSpacing(20)

        return section

    # ------------------------- BACK -------------------------
    def go_back(self):
        self.previous_window.show()
        self.close()


class student_courses_announcement(QWidget):
    def __init__(self, student_dashboard, student_user_id):
        super().__init__()
        self.previous_window = student_dashboard
        self.student_logged_in = student_user_id

        self.setWindowTitle("Student Announcements")
        self.resize(1000, 600)

        self.back_btn = QPushButton("←Back")
        self.back_btn.setObjectName("backbutton_style")
        self.back_btn.clicked.connect(self.go_back)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()

        self.btn_text = QPushButton("Text Announcements")
        self.btn_text.setObjectName("button_style")
        self.btn_text.clicked.connect(self.open_text_announcements)

        self.btn_assignment = QPushButton("Assignments")
        self.btn_assignment.setObjectName("button_style")
        self.btn_assignment.clicked.connect(self.open_assignment_list)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addSpacing(12)
        layout.addWidget(self.btn_text)
        layout.addWidget(self.btn_assignment)
        layout.addStretch()
        self.setLayout(layout)

    def open_text_announcements(self):
        self.text_window = StudentTextAnnouncementsWindow(self,self.student_logged_in)
        self.text_window.show()
        self.hide()

    def open_assignment_list(self):
        self.assignment_window = StudentAssignmentListWindow(self, self.student_logged_in)
        self.assignment_window.show()
        self.hide()

    def go_back(self):
        self.previous_window.show()
        self.close()

class StudentTextAnnouncementsWindow(QWidget):
    def __init__(self, student_courses_announcement, student_user_id):
        super().__init__()
        self.previous = student_courses_announcement
        self.student_user_id = student_user_id

        self.setWindowTitle("Text Announcements")
        self.resize(1000,600)

        self.back_btn = QPushButton("←Back")
        self.back_btn.setObjectName("backbutton_style")
        self.back_btn.clicked.connect(self.go_back)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()

        self.scroll_layout = QVBoxLayout()
        container = QWidget()
        container.setObjectName("scroll_container")
        container.setLayout(self.scroll_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setObjectName("scroll_area")
        self.scroll.setWidget(container)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self.scroll)
        self.setLayout(layout)

        self.load_announcements()

    def load_announcements(self):
        try:
            cursor.execute("EXEC get_student_text_announcements ?", (self.student_user_id,))
            rows = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            return

        for i in reversed(range(self.scroll_layout.count())):
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        for r in rows:
            ann_id, title, message, created_at, course_name = r
            box = QGroupBox()
            box.setObjectName("groupbox_style")
            v = QVBoxLayout()

            header_layout = QHBoxLayout()
            header_layout.addStretch()
            label=QLabel(f"{course_name} — {created_at}")
            label.setObjectName("label_style")
            header_layout.addWidget(label)

            lbl_date = QLabel(str(created_at))
            lbl_date.setObjectName("label_style")
            header_layout.addWidget(label)
            v.addLayout(header_layout)

            preview = QLabel(message[:300] + ("..." if len(message)>300 else ""))
            preview.setObjectName("label_style")
            v.addWidget(preview)

            open_btn = QPushButton("Open")
            open_btn.setObjectName("button_style")
            open_btn.clicked.connect(lambda _, a=ann_id, t=title, m=message,c=course_name: self.open_detail(a,t,m,c))
            v.addWidget(open_btn)

            box.setLayout(v)
            self.scroll_layout.addWidget(box)

    def open_detail(self, ann_id, title, message,course_name=None):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.resize(700, 400)

        layout = QVBoxLayout()
        if course_name:
            lbl_course = QLabel(f"Course: {course_name}")
            lbl_course.setObjectName("label_style")
            layout.addWidget(lbl_course)

        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setText(message)
        txt.setObjectName("text_box_style")
        layout.addWidget(txt)

        btn_close = QPushButton("Close")
        btn_close.setObjectName("button_style")
        btn_close.clicked.connect(dlg.close)
        layout.addWidget(btn_close)

        dlg.setLayout(layout)

        # IMPORTANT — keep reference so dialog doesn't instantly close
        self.detail_dialog = dlg

        dlg.exec_()  # modal dialog

    def go_back(self):
        self.previous.show()
        self.close()

class StudentAssignmentListWindow(QWidget):
    def __init__(self, student_courses_announcement, student_user_id):
        super().__init__()
        self.previous = student_courses_announcement
        self.student_user_id = student_user_id

        self.setWindowTitle("Assignments")
        self.resize(1000,600)

        self.back_btn = QPushButton("←Back")
        self.back_btn.setObjectName("backbutton_style")
        self.back_btn.clicked.connect(self.go_back)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.back_btn)
        top_bar.addStretch()

        self.scroll_layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(self.scroll_layout)
        container.setObjectName("scroll_container")

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(container)
        self.scroll.setObjectName("scroll_area")

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self.scroll)
        self.setLayout(layout)

        self.load_assignments()

    def load_assignments(self):
        try:
            cursor.execute("EXEC get_student_assignment_announcements ?", (self.student_user_id,))
            rows = cursor.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))
            return

        for i in reversed(range(self.scroll_layout.count())):
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        for r in rows:
            ann_id, title, message, created_at, due_date, course_id, course_name, file_name, file_path = r

            # --------------- CARD ---------------
            main = QVBoxLayout()
            card = QFrame()
            card.setObjectName("card")
            layout = QVBoxLayout()

            # COURSE NAME
            lbl_title = QLabel(f"{course_name}")
            lbl_title.setObjectName("label_style")
            layout.addWidget(lbl_title)

            # ASSIGNMENT TITLE
            title_label = QLabel(f"{title}")
            title_label.setObjectName("label_style")
            layout.addWidget(title_label)

            # DATES
            date_row = QHBoxLayout()

            assigned_lbl = QLabel(f"<b>Assigned:</b> {created_at}")
            assigned_lbl.setObjectName("label_style")
            date_row.addWidget(assigned_lbl)

            due_lbl = QLabel(f"<b>Due:</b> {due_date}")
            due_lbl.setObjectName("label_style")
            date_row.addWidget(due_lbl)

            date_row.addStretch()
            layout.addLayout(date_row)

            file_name_lbl = QLabel(f"<b>File:</b> {file_name if file_name else 'No File'}")
            file_name_lbl.setObjectName("label_style")
            layout.addWidget(file_name_lbl)

            # FILE & BUTTON ROW
            file_row = QHBoxLayout()

            file_text = QLabel("<b>Assignment File:</b>")
            file_text.setObjectName("label_style")
            file_row.addWidget(file_text)

            # Download button
            download_btn = QPushButton("Download")
            download_btn.setObjectName("button_style")
            download_btn.clicked.connect(
                lambda _, p=file_path, n=file_name: self.download_file(p, n)
            )
            file_row.addWidget(download_btn)

            # Submit button
            submit_btn = QPushButton("Submit")
            submit_btn.setObjectName("button_style")
            submit_btn.clicked.connect(
                lambda _, a=ann_id: self.submit_assignment(a)
            )
            file_row.addWidget(submit_btn)

            file_row.addStretch()
            layout.addLayout(file_row)

            card.setLayout(layout)
            self.scroll_layout.addWidget(card)

    def download_file(self, server_path, file_name):
        if not server_path or not os.path.exists(server_path):
            QMessageBox.critical(self, "Error", "File not found on server.")
            return

        save, _ = QFileDialog.getSaveFileName(self, "Save File", file_name)
        if not save:
            return

        try:
            shutil.copy(server_path, save)
            QMessageBox.information(self, "Success", "File downloaded successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unable to download:\n{e}")

    def submit_assignment(self, ann_id):
        # Choose PDF file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Upload Assignment", "", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        file_name = os.path.basename(file_path)
        file_type = "pdf"
        file_size = os.path.getsize(file_path)

        # Create directory if not exists
        save_dir = "student_submissions"
        os.makedirs(save_dir, exist_ok=True)

        # Create local saved path
        saved_path = os.path.join(save_dir, file_name)

        try:
            # Copy to server folder
            shutil.copy(file_path, saved_path)
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Unable to save file:\n{e}")
            return

        try:
            # Insert into student_assignment_submission table
            cursor.execute("""
                INSERT INTO student_assignment_submission
                (ann_id, student_id, file_name, file_path, file_type, file_size, submitted_at)
                VALUES (
                    ?, 
                    (SELECT student_id FROM student WHERE user_id = ?),
                    ?, ?, ?, ?, GETDATE()
                )
            """, (ann_id, self.student_user_id, file_name, saved_path, file_type, file_size))

            conn.commit()

            QMessageBox.information(self, "Success", "Assignment submitted successfully!")

            # refresh list
            self.load_assignments()

        except Exception as e:
            QMessageBox.critical(self, "DB Error", str(e))

    def go_back(self):
        self.previous.show()
        self.close()

#course dashboard
class student_registered_courses(QWidget):

    def __init__(self,student_dashboard,student_id):
        super().__init__()
        self.resize(1000,600)
        self.setWindowTitle("CUI Portal")

        self.logged_in_student_id = student_id
        self.previous_window = student_dashboard
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')

        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        self.admin_title = QLabel("Courses")
        self.admin_title.setObjectName('dashboard_title_style')


        self.grid = QGridLayout()
        items = [
            ("Details", "details.png",student_courses_details),
            ("Marks", "marks.png",student_courses_marks),
            ("Attendance", "attendance.png",student_courses_attendance),
            ("Announcement", "assignment.png",student_courses_announcement)
        ]

        row = 0
        col = 0

        for title,icon,new_window in items:
            card = self.create_single_card(title,icon,new_window)
            self.grid.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        row1 = QHBoxLayout()

        row1.addStretch()
        row1.addWidget(self.admin_title)
        row1.addStretch()

        master_layout = QVBoxLayout()
        master_layout.addLayout(row1)


        grid_widget = QWidget()
        grid_widget.setLayout(self.grid)
        master_layout.addWidget(grid_widget)


        self.outer_frame = QFrame()
        self.outer_frame.setObjectName("login_box_loc_style")
        self.outer_frame.setLayout(master_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addWidget(self.outer_frame)
        self.setLayout(main_layout)


    def go_back(self):
        self.previous_window.show()
        self.close()

    def create_single_card(self,title,icon,window_class):
        card_frame = QFrame()
        card_frame.setFixedSize(180, 180)
        layout = QVBoxLayout(card_frame)
        layout.setAlignment(Qt.AlignCenter)

        icon_var = QIcon(icon)
        button = QPushButton()
        button.setIcon(icon_var)
        button.setIconSize(QSize(80,80))
        button.setObjectName('icon_style')


        icon_title = QLabel(title)
        icon_title.setAlignment(Qt.AlignCenter)
        icon_title.setObjectName('title_style')

        layout.addWidget(button)
        layout.addWidget(icon_title)

        button.clicked.connect(lambda _, w=window_class: self.open_page(w))
        return card_frame

    def open_page(self, window_class):
        self.new_window = window_class(self, self.logged_in_student_id)
        self.new_window.show()
        self.close()
# end of courses class
# --------------------------------------------reg card------------------------------------------------------------------------------
class student_registration_card(QWidget):
    def __init__(self,student_dashboard_courses,student_id):
        super().__init__()
        self.setWindowTitle("Course Registration")
        self.resize(1000,600)

        self.previous_window = student_dashboard_courses
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')

        self.logged_in_student_id = student_id

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(20)

        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()
        self.main_layout.addLayout(top_row)


        title = QLabel("Available Courses for Registration")
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)
        title.setObjectName("dashboard_title_style")

        scroll = QScrollArea()
        scroll.setObjectName("course_detail_table")
        scroll_content = QWidget()
        self.courses_layout = QVBoxLayout(scroll_content)
        self.courses_layout.setSpacing(15)

        scroll.setWidget(scroll_content)
        scroll.setWidgetResizable(True)
        self.main_layout.addWidget(scroll)

        registered_title = QLabel("Registered Courses")
        registered_title.setAlignment(Qt.AlignCenter)
        registered_title.setObjectName("dashboard_title_style")
        self.main_layout.addWidget(registered_title)

        self.registered_scroll = QScrollArea()
        self.registered_scroll.setObjectName("course_detail_table")

        registered_content = QWidget()
        self.registered_layout = QVBoxLayout(registered_content)
        self.registered_layout.setSpacing(15)

        self.registered_scroll.setWidget(registered_content)
        self.registered_scroll.setWidgetResizable(True)
        self.main_layout.addWidget(self.registered_scroll)


        self.setLayout(self.main_layout)

        self.get_course()
        self.get_registered_courses()

    def get_course(self):
        cursor.execute("exec get_all_courses")
        rows = cursor.fetchall()

        for row in rows:
            course = {
                "course_id": row[0],
                "course_name": row[1],
                "semester": row[2],
                "credit_hours": row[3]
            }
            self.courses_layout.addWidget(self.create_course_card(course))


    def create_course_card(self, course):
        card = QFrame()
        card.setObjectName("courseCard")
        card.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout()
        course_name = QLabel(f"Course: {course['course_name']}")
        course_name.setObjectName("courseTitle")
        semester = QLabel(f"Semester: {course['semester']}")
        semester.setObjectName("courseText")
        credit = QLabel(f"Credit Hours: {course['credit_hours']}")
        credit.setObjectName("courseText")
        register_btn = QPushButton("Register")
        register_btn.setObjectName("registerButton")
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.clicked.connect(lambda: self.enrol(course))
        layout.addWidget(course_name)
        layout.addWidget(semester)
        layout.addWidget(credit)
        layout.addWidget(register_btn, alignment=Qt.AlignCenter)
        card.setLayout(layout)
        return card

    def enrol(self, course):
        course_id = course["course_id"]

        cursor.execute("exec get_student_id ?", (self.logged_in_student_id,))
        result  = cursor.fetchone()
        student_id = result[0]

        try:
            cursor.execute("exec enroll_student ?, ?", (student_id, course_id))
            conn.commit()
            QMessageBox.information(self, "success", "course registered successfully!")

        except:
            QMessageBox.warning(self, "already enrolled", "you are already enrolled.")

        self.get_registered_courses()

    def get_registered_courses(self):
        # CLEAR OLD WIDGETS FIRST
        while self.registered_layout.count():
            child = self.registered_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        cursor.execute("exec get_student_id ?", (self.logged_in_student_id,))
        result = cursor.fetchone()
        student_id = result[0]

        cursor.execute("exec get_registered_courses ?", (student_id,))
        rows = cursor.fetchall()

        if not rows:
            label = QLabel("No courses registered yet.")
            self.registered_layout.addWidget(label)
            return

        for row in rows:
            card = QFrame()
            card.setObjectName("courseCard")

            layout = QVBoxLayout()

            student_id = QLabel(f"Student ID: {row[0]}")
            student_id.setObjectName("courseText")

            student_name = QLabel(f"Student Name: {row[1]}")
            student_name .setObjectName("courseTitle")

            title = QLabel(f"Course: {row[2]}")
            title.setObjectName("courseTitle")

            semester = QLabel(f"Semester: {row[3]}")
            semester.setObjectName("courseText")

            credit = QLabel(f"Credit Hours: {row[4]}")
            credit.setObjectName("courseText")

            layout.addWidget(student_id)
            layout.addWidget(student_name)
            layout.addWidget(title)
            layout.addWidget(semester)
            layout.addWidget(credit)

            card.setLayout(layout)
            self.registered_layout.addWidget(card)


    def go_back(self):
        self.previous_window.show()
        self.close()

# class student_result_card(QWidget):

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
class student_profile(QWidget):
    def __init__(self, student_dashboard, student_user_id):
        super().__init__()
        self.setWindowTitle("Student Profile")
        self.resize(1000, 600)

        self.previous_window = student_dashboard
        self.student_user_id = student_user_id

        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName("backbutton_style")
        self.back_button.clicked.connect(self.go_back)

        title = QLabel("STUDENT PROFILE")
        title.setObjectName("admin_student_title")

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()

        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 150)
        self.image_label.setStyleSheet("border:2px solid gray; border-radius:75px;")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.upload_btn = QPushButton("Upload Picture")
        self.upload_btn.setObjectName("admin_student_button")
        self.upload_btn.clicked.connect(self.upload_picture)

        img_layout = QVBoxLayout()
        img_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        img_layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)

        self.username_input = QLineEdit(); self.username_input.setReadOnly(True)
        self.fullname_input = QLineEdit(); self.fullname_input.setReadOnly(True)
        self.email_input = QLineEdit(); self.email_input.setReadOnly(True)
        self.phone_input = QLineEdit(); self.phone_input.setReadOnly(True)
        self.reg_no_input = QLineEdit(); self.reg_no_input.setReadOnly(True)
        self.semester_input = QLineEdit(); self.semester_input.setReadOnly(True)
        self.program_input = QLineEdit(); self.program_input.setReadOnly(True)

        def row(name, widget):
            h = QHBoxLayout()
            lbl1 = QLabel(name)
            lbl1.setFixedWidth(160)
            lbl1.setObjectName("admin_student_label")
            widget.setObjectName("profile_value")
            h.addWidget(lbl1)
            h.addWidget(widget)
            return h

        profile_layout = QVBoxLayout()
        profile_layout.addLayout(row("Username:", self.username_input))
        profile_layout.addLayout(row("Full Name:", self.fullname_input))
        profile_layout.addLayout(row("Email:", self.email_input))
        profile_layout.addLayout(row("Phone:", self.phone_input))
        profile_layout.addLayout(row("Registration No:", self.reg_no_input))
        profile_layout.addLayout(row("Semester:", self.semester_input))
        profile_layout.addLayout(row("Program:", self.program_input))

        self.edit_button = QPushButton("Edit Profile")
        self.edit_button.setObjectName("admin_student_button")
        self.edit_button.clicked.connect(self.enable_editing)

        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("admin_student_button")
        self.save_button.clicked.connect(self.save_profile)
        self.save_button.setEnabled(False)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.edit_button)
        btn_row.addWidget(self.save_button)

        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addLayout(title_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(img_layout)
        main_layout.addLayout(profile_layout)
        main_layout.addSpacing(25)
        main_layout.addLayout(btn_row)
        self.setLayout(main_layout)
        self.load_student_profile()

    def enable_editing(self):
        self.username_input.setReadOnly(False)
        self.fullname_input.setReadOnly(False)
        self.email_input.setReadOnly(False)
        self.phone_input.setReadOnly(False)

        self.edit_button.setEnabled(False)
        self.save_button.setEnabled(True)

        QMessageBox.information(self, "Edit Mode", "You can now edit your profile!")

    def save_profile(self):
        try:
            cursor.execute("""
                EXEC update_student_profile ?, ?, ?, ?, ?
            """, (
                self.student_user_id,
                self.username_input.text(),
                self.fullname_input.text(),
                self.email_input.text(),
                self.phone_input.text()
            ))

            conn.commit()

            self.set_readonly()

            QMessageBox.information(self, "Success", "Profile Updated Successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def set_readonly(self):
        self.username_input.setReadOnly(True)
        self.fullname_input.setReadOnly(True)
        self.email_input.setReadOnly(True)
        self.phone_input.setReadOnly(True)

        self.edit_button.setEnabled(True)
        self.save_button.setEnabled(False)

    def load_student_profile(self):
        try:
            cursor.execute("EXEC load_student_profile ?", (self.student_user_id,))
            row = cursor.fetchone()

            if row:
                self.username_input.setText(str(row[1]))
                self.fullname_input.setText(str(row[2]))
                self.email_input.setText(str(row[3]))
                self.phone_input.setText(str(row[4]))
                self.reg_no_input.setText(str(row[5]))
                self.semester_input.setText(str(row[6]))
                self.program_input.setText(str(row[7]))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def upload_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            image_folder = "profile_images"
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)

            new_path = f"{image_folder}/student_{self.student_user_id}.png"
            shutil.copyfile(file_path, new_path)

            pixmap = QPixmap(new_path).scaled(
                150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)

            QMessageBox.information(self, "Success", "Profile picture updated!")

    def go_back(self):
        self.previous_window.show()
        self.close()


class student_gpa_calculator(QWidget):
    def __init__(self, student_dashboard,user_id):
        super().__init__()
        print("INIT CALLED")
        self.student_user_id = user_id
        self.setWindowTitle("GPA Calculation")
        self.resize(1000, 600)

        title = QLabel("GPA CALCULATION")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("admin_student_title")

        self.single_btn = QPushButton("Single Course GPA")
        self.single_btn.setObjectName("button_style")
        self.semester_btn = QPushButton("Semester GPA")
        self.semester_btn.setObjectName("button_style")

        self.single_btn.clicked.connect(self.open_single)
        self.semester_btn.clicked.connect(self.open_semester)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addWidget(self.single_btn)
        layout.addWidget(self.semester_btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
    def open_single(self):
        try:
            self.sc = single_course_gpa(self.student_user_id)
            self.sc.show()
        except Exception as e:
            print("Single GPA crash:", e)

    def open_semester(self):
        try:
            self.sg = semester_gpa(self.student_user_id)
            self.sg.show()
        except Exception as e:
            print("Semester GPA crash:", e)


class single_course_gpa(QWidget):
    def __init__(self, student_user_id):
        super().__init__()
        self.student_user_id = student_user_id

        self.setWindowTitle("Single Course GPA Calculation")
        self.resize(1000, 600)

        title = QLabel("SINGLE COURSE GPA CALCULATION")
        title.setObjectName("admin_student_title")
        title.setAlignment(Qt.AlignCenter)
        self.course = QLineEdit()
        self.course.setObjectName("text_box_style")
        self.credit = QLineEdit()
        self.credit.setObjectName("text_box_style")
        self.quiz_obt = [QLineEdit() for _ in range(4)]
        self.quiz_total = [QLineEdit("10") for _ in range(4)]

        self.assi_obt = [QLineEdit() for _ in range(4)]
        self.assi_total = [QLineEdit("10") for _ in range(4)]
        for q in self.quiz_obt:
            q.setObjectName("text_box_style")


        for a in self.assi_obt:
            a.setObjectName("text_box_style")

        self.mid_obt = QLineEdit()
        self.mid_obt.setObjectName("text_box_style")

        self.mid_total = QLineEdit("30")
        self.mid_total.setObjectName("readonly_box")

        self.final_obt = QLineEdit()
        self.final_obt.setObjectName("text_box_style")

        self.final_total = QLineEdit("40")
        self.final_total.setObjectName("readonly_box")

        self.calc_btn = QPushButton("Calculate GPA")
        self.calc_btn.setObjectName("button_style")
        self.calc_btn.clicked.connect(self.calculate_single_course_gpa)

        form = QFormLayout()
        form.addRow("Course Title:", self.course)
        form.addRow("Credit Hours:", self.credit)

        for i in range(4):
            row = QHBoxLayout()
            row.addWidget(self.quiz_obt[i])
            row.addWidget(QLabel("/"))
            row.addWidget(self.quiz_total[i])
            form.addRow(f"Quiz {i+1}:", row)

        for i in range(4):
            row = QHBoxLayout()
            row.addWidget(self.assi_obt[i])
            row.addWidget(QLabel("/"))
            row.addWidget(self.assi_total[i])
            form.addRow(f"Assignment {i+1}:", row)

        row_mid = QHBoxLayout()
        row_mid.addWidget(self.mid_obt)
        row_mid.addWidget(QLabel("/"))
        row_mid.addWidget(self.mid_total)
        form.addRow("Mid:", row_mid)

        row_final = QHBoxLayout()
        row_final.addWidget(self.final_obt)
        row_final.addWidget(QLabel("/"))
        row_final.addWidget(self.final_total)
        form.addRow("Final:", row_final)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(form)
        layout.addSpacing(20)
        layout.addWidget(self.calc_btn)

        self.setLayout(layout)

    def calculate_single_course_gpa(self):
        try:
            quizzes = [
                int(self.quiz_obt[i].text()) for i in range(4)
            ]
            assi = [
                int(self.assi_obt[i].text()) for i in range(4)
            ]

            mid = int(self.mid_obt.text())
            final = int(self.final_obt.text())
            cursor.execute(
                "SELECT student_id FROM student WHERE user_id = ?",
                (self.student_user_id,)
            )

            result = cursor.fetchone()
            self.student_own_id = result[0]

            cursor.execute("""
                EXEC calculate_course_gpa ?,?,?,?,?,?,?,?,?,?,?,?,?
            """, (
                self.student_own_id,
                self.course.text(),
                int(self.credit.text()),

                quizzes[0], quizzes[1], quizzes[2], quizzes[3],
                assi[0], assi[1], assi[2], assi[3],
                mid,
                final
            ))

            row = cursor.fetchone()
            conn.commit()

            if row:
                QMessageBox.information(
                    self,
                    "Course GPA Result",
                    f"Course: {row[0]}\n"
                    f"Percentage: {row[1]}%\n"
                    f"GPA: {row[2]}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


class semester_gpa(QWidget):
    def __init__(self, student_user_id):
        super().__init__()
        self.student_user_id = student_user_id
        self.setWindowTitle("Semester GPA Calculation")

        self.resize(1000, 600)

        # ---------- Title ----------
        title = QLabel("SEMESTER GPA CALCULATION")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("admin_student_title")

        # ---------- No of courses ----------
        self.no_courses = QLineEdit()
        self.no_courses.setPlaceholderText("Enter number of courses")
        self.no_courses.setObjectName("text_box_style")

        self.create_btn = QPushButton("Create Courses")
        self.create_btn.clicked.connect(self.create_courses)
        self.create_btn.setObjectName("button_style")

        top_form = QFormLayout()
        top_form.addRow("Number of Courses:", self.no_courses)
        top_form.addRow(self.create_btn)

        # ---------- Scroll Area ----------
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.container = QWidget()
        self.vbox = QVBoxLayout(self.container)
        self.scroll.setWidget(self.container)

        # ---------- Calculate Button ----------
        self.calc_btn = QPushButton("Calculate Semester GPA")
        self.calc_btn.clicked.connect(self.calculate_semester_gpa)
        self.calc_btn.setObjectName("button_style")
        self.calc_btn.setEnabled(False)

        # ---------- Main Layout ----------
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(top_form)
        layout.addWidget(self.scroll)
        layout.addWidget(self.calc_btn)
        self.setLayout(layout)

        self.course_blocks = []

    # ---------- Create Dynamic Course Sections ----------
    def create_courses(self):
        try:
            for i in reversed(range(self.vbox.count())):
                self.vbox.itemAt(i).widget().setParent(None)

            self.course_blocks.clear()

            total = int(self.no_courses.text())

            for i in range(total):
                block = self.create_course_block(i + 1)
                self.course_blocks.append(block)
                self.vbox.addWidget(block["frame"])

            self.calc_btn.setEnabled(True)

        except:
            QMessageBox.critical(self, "Error", "Enter valid number of courses")

    # ---------- Single Course Section ----------
    def create_course_block(self, index):
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setObjectName("courseCard")

        title = QLabel(f"Course {index}")
        title.setObjectName("subtitle_style")

        course = QLineEdit()
        course.setObjectName("text_box_style")
        credit = QLineEdit()
        credit.setObjectName("text_box_style")

        quizzes = [QLineEdit() for _ in range(4)]
        for q in quizzes:
            q.setObjectName("text_box_style")  #

        assi = [QLineEdit() for _ in range(4)]
        for a in assi:
            a.setObjectName("text_box_style")
        mid = QLineEdit()
        mid.setObjectName("text_box_style")
        final = QLineEdit()
        final.setObjectName("text_box_style")

        form = QFormLayout()
        form.addRow(title)
        form.addRow("Course Name:", course)
        form.addRow("Credit Hours:", credit)

        for i in range(4):
            form.addRow(f"Quiz {i+1} (out of 10):", quizzes[i])

        for i in range(4):
            form.addRow(f"Assignment {i+1} (out of 10):", assi[i])


        form.addRow("Mid (out of 30):", mid)
        form.addRow("Final (out of 40):", final)

        frame.setLayout(form)

        return {
            "frame": frame,
            "course": course,
            "credit": credit,
            "q": quizzes,
            "a": assi,
            "mid": mid,
            "final": final
        }

    def calculate_semester_gpa(self):
        try:
            for c in self.course_blocks:
                cursor.execute(
                    "SELECT student_id FROM student WHERE user_id = ?",
                    (self.student_user_id,)
                )

                result = cursor.fetchone()
                self.student_own_id = result[0]
                cursor.execute("EXEC calculate_course_gpa ?,?,?,?,?,?,?,?,?,?,?,?,?", (self.student_own_id,
                    c["course"].text(),
                    int(c["credit"].text()),

                    int(c["q"][0].text()), int(c["q"][1].text()),
                    int(c["q"][2].text()), int(c["q"][3].text()),

                    int(c["a"][0].text()), int(c["a"][1].text()),
                    int(c["a"][2].text()), int(c["a"][3].text()),

                    int(c["mid"].text()),
                    int(c["final"].text())
                ))

            conn.commit()

            cursor.execute(
                "SELECT student_id FROM student WHERE user_id = ?",
                (self.student_user_id,)
            )

            result = cursor.fetchone()
            self.student_own_id = result[0]

            cursor.execute("EXEC calculate_semester_gpa ?", (self.student_own_id,))

            row = cursor.fetchone()

            if row and row[0] is not None:
                QMessageBox.information(
                    self,
                    "Semester GPA",
                    f"Your Semester GPA is {round(row[0], 2)}"
                )
            else:
                QMessageBox.warning(self, "Error", "GPA not calculated")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class student_dashboard(QWidget):

    def __init__(self,Login, student_user_id):
        super().__init__()
        self.resize(1000,600)
        self.setWindowTitle("CUI Portal")

        self.admin_title = QLabel("HELLO STUDENT!")
        self.admin_title.setObjectName('dashboard_title_style')
        self.logged_in_student_id = student_user_id

        self.previous_window =Login
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')

        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()


        self.grid = QGridLayout()
        items = [
            ("Profile", "admin_profile.png",student_profile),
            ("Courses", "course.png",student_registered_courses),
            ("Reg Card", "reg_card.png",student_registration_card),
            ("GPA Calculator", "result.png",student_gpa_calculator)
        ]

        row = 0
        col = 0

        for title,icon,new_window in items:
            card = self.create_single_card(title,icon,new_window)
            self.grid.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

        row1 = QHBoxLayout()

        row1.addWidget(self.admin_title, alignment=Qt.AlignCenter)


        master_layout = QVBoxLayout()
        master_layout.addLayout(row1)


        grid_widget = QWidget()
        grid_widget.setLayout(self.grid)
        master_layout.addWidget(grid_widget)



        self.outer_frame = QFrame()
        self.outer_frame.setLayout(master_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addWidget(self.outer_frame)
        self.setLayout(main_layout)


    def open_page(self, window_class):
        self.new_window = window_class(self, self.logged_in_student_id)
        self.new_window.show()
        self.close()

    def go_back(self):
        self.previous_window.show()
        self.close()

    def create_single_card(self,title,icon,window_class):
        card_frame = QFrame()
        card_frame.setFixedSize(180, 180)
        layout = QVBoxLayout(card_frame)
        layout.setAlignment(Qt.AlignCenter)

        icon_var = QIcon(icon)
        button = QPushButton()
        button.setIcon(icon_var)
        button.setIconSize(QSize(80,80))
        button.setObjectName('icon_style')


        icon_title = QLabel(title)
        icon_title.setAlignment(Qt.AlignCenter)
        icon_title.setObjectName('title_style')

        layout.addWidget(button)
        layout.addWidget(icon_title)

        button.clicked.connect(lambda: self.open_page(window_class))
        return card_frame


#---------------------------------------------------------------------------------------------------------

# admin_dashboard
class admin_student(QWidget):
    def __init__(self,admin_dashboard,admin_user_id):
        super().__init__()
        self.setWindowTitle("Admin Student Management")
        self.resize(1000, 600)

        self.previous_window = admin_dashboard
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')

        form_layout = QGridLayout()

        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setObjectName("admin_student_input")
        self.password_input = QLineEdit()
        self.password_input.setObjectName("admin_student_input")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.email_input = QLineEdit()
        self.email_input.setObjectName("admin_student_input")
        self.phone_input = QLineEdit()
        self.phone_input.setObjectName("admin_student_input")
        self.full_name_input = QLineEdit()
        self.full_name_input.setObjectName("admin_student_input")
        self.registration_no_input = QLineEdit()
        self.registration_no_input.setObjectName("admin_student_input")
        self.semester_input = QSpinBox()
        self.semester_input.setRange(1, 8)
        self.semester_input.setObjectName("admin_student_combo")
        self.program_combo = QComboBox()
        self.program_combo.setObjectName("admin_student_combo")
        self.department_combo = QComboBox()
        self.department_combo.setObjectName("admin_student_combo")
        self.class_combo = QComboBox()
        self.class_combo.setObjectName("admin_student_combo")
        self.load_classes()

        self.father_name_input = QLineEdit()
        self.father_name_input.setObjectName("admin_student_input")
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate())
        self.dob_input.setObjectName("admin_student_input")
        self.cnic_input = QLineEdit()
        self.cnic_input.setObjectName("admin_student_input")

        # ================= LABELS =================
        def lbl(text):
            label = QLabel(text)
            label.setObjectName("admin_student_label")
            return label

        # ================= ADD TO GRID =================
        form_layout.addWidget(lbl("Username:"), 0, 0)
        form_layout.addWidget(self.username_input, 0, 1)

        form_layout.addWidget(lbl("Password:"), 0, 2)
        form_layout.addWidget(self.password_input, 0, 3)

        form_layout.addWidget(lbl("Email:"), 1, 0)
        form_layout.addWidget(self.email_input, 1, 1)

        form_layout.addWidget(lbl("Phone:"), 1, 2)
        form_layout.addWidget(self.phone_input, 1, 3)

        form_layout.addWidget(lbl("Full Name:"), 2, 0)
        form_layout.addWidget(self.full_name_input, 2, 1)

        form_layout.addWidget(lbl("Registration No:"), 2, 2)
        form_layout.addWidget(self.registration_no_input, 2, 3)

        form_layout.addWidget(lbl("Semester:"), 3, 0)
        form_layout.addWidget(self.semester_input, 3, 1)

        form_layout.addWidget(lbl("Program Name:"), 3, 2)
        form_layout.addWidget(self.program_combo, 3, 3)

        form_layout.addWidget(lbl("Department Name:"), 4, 0)
        form_layout.addWidget(self.department_combo, 4, 1)

        form_layout.addWidget(lbl("Father Name:"), 4, 2)
        form_layout.addWidget(self.father_name_input, 4, 3)

        form_layout.addWidget(lbl("Date of Birth:"), 5, 0)
        form_layout.addWidget(self.dob_input, 5, 1)

        form_layout.addWidget(lbl("CNIC:"), 5, 2)
        form_layout.addWidget(self.cnic_input, 5, 3)

        form_layout.addWidget(lbl("Class:"), 6, 0)
        form_layout.addWidget(self.class_combo, 6, 1)

        self.submit_button = QPushButton("Add Student")
        self.submit_button.setObjectName("admin_student_button")
        self.submit_button.clicked.connect(self.add_student)


        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        title = QLabel("ADMIN STUDENT PANEL")
        title.setObjectName("admin_student_title")

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()

        # ================= MAIN LAYOUT =================
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addLayout(title_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)

        button_row = QHBoxLayout()

        self.list_button = QPushButton("List")
        self.list_button.setObjectName("admin_student_button")
        self.list_button.clicked.connect(self.open_student_list)

        button_row.addWidget(self.list_button)
        button_row.addStretch()
        button_row.addWidget(self.submit_button)

        main_layout.addLayout(button_row)

        self.setLayout(main_layout)
        self.load_programs()
        self.load_departments()

        self.password_input.setPlaceholderText("Max 8 characters")
        self.email_input.setPlaceholderText("abc@gmail.com")
        self.phone_input.setPlaceholderText("11 digit number")
        self.registration_no_input.setPlaceholderText("sp24-bse-051...")
        self.cnic_input.setPlaceholderText("35302-6891236-5")
        self.cnic_input.setInputMask("00000-0000000-0")

    def load_classes(self):
        self.class_combo.clear()
        self.class_combo.addItem("Select Class", None)

        cursor.execute("SELECT class_id, CONCAT(session,' ',program,' ',section) FROM class_section")
        for cid, cname in cursor.fetchall():
            self.class_combo.addItem(cname, cid)
    def load_programs(self):
        try:
            self.program_combo.clear()
            self.program_combo.addItem("Select Program", None)

            cursor.execute("SELECT program_id, program_name FROM [program]")
            data = cursor.fetchall()

            for pid, pname in data:
                self.program_combo.addItem(pname, pid)
        except Exception as e:
            QMessageBox.critical(self, "Program Load Error", str(e))

    def load_departments(self):
        try:
            self.department_combo.clear()
            self.department_combo.addItem("Select Department", None)

            cursor.execute("SELECT department_id, dept_name FROM department")
            data = cursor.fetchall()

            for did, dname in data:
                self.department_combo.addItem(dname, did)
        except Exception as e:
            QMessageBox.critical(self, "Department Load Error", str(e))

    def add_student(self):

        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        full_name = self.full_name_input.text()
        reg_no = self.registration_no_input.text()
        semester = self.semester_input.value()
        program_id = self.program_combo.currentData()
        department_id = self.department_combo.currentData()
        father_name = self.father_name_input.text()
        dob = self.dob_input.date().toString("yyyy-MM-dd")
        cnic = self.cnic_input.text()
        class_id = self.class_combo.currentData()

        if not all([username, password, email, full_name, reg_no]):
            QMessageBox.warning(self, "Error", "Fill all required fields!")
            return

        if len(password) > 8 or not password.isalnum():
            QMessageBox.warning(self, "Password Error", "Password must be max 8 letters/numbers only!")
            return

        if class_id is None:
            QMessageBox.warning(self, "Error", "Select Class!")
            return

        if "@" not in email or "." not in email or email.startswith("@") or email.endswith("@"):
            QMessageBox.warning(self, "Email Error", "Invalid email format! Example: abc@gmail.com")
            return

        if (
                not phone.isdigit() or
                len(phone) != 11 or
                not phone.startswith("033")
        ):
            QMessageBox.warning(
                self,
                "Phone Error",
                "Phone number must start with 033 and contain exactly 11 digits.\nExample: 03351234567"
            )
            return

        parts = reg_no.split("-")
        if len(parts) != 3:
            QMessageBox.warning(self, "Reg No Error", "Invalid Reg No format! Example: sp24-bse-051")
            return

        session, program, roll = parts
        if not roll.isdigit() or len(roll) != 3:
            QMessageBox.warning(self, "Reg No Error", "Invalid Reg No format! Example: sp24-bse-051")
            return
        #35302-6891231-5
        cnic_parts = cnic.split("-")

        if (
                len(cnic_parts) != 3 or
                not cnic_parts[0].isdigit() or len(cnic_parts[0]) != 5 or
                not cnic_parts[1].isdigit() or len(cnic_parts[1]) != 7 or
                not cnic_parts[2].isdigit() or len(cnic_parts[2]) != 1
        ):
            QMessageBox.warning(
                self,
                "CNIC Error",
                "CNIC must be in format: 35302-6891231-5"
            )
            return

        if program_id is None or department_id is None:
            QMessageBox.warning(self, "Error", "Select Program and Department!")
            return
    #stored procedure
        cursor.execute("""
            EXEC dbo.admin_add_record
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?
        """, (
            username,
            password,
            email,
            phone,
            full_name,
            reg_no,
            semester,
            program_id,
            department_id,
            father_name,
            dob,
            cnic,
            class_id
        ))

        conn.commit()
        QMessageBox.information(self, "Success", "Student Added Successfully!")


    def go_back(self):
        self.previous_window.show()
        self.close()

    def open_student_list(self):
        self.student_list_window = StudentListWindow()
        self.student_list_window.show()

#student list
class StudentListWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("All Students")
        self.resize(1200, 600)

        layout = QVBoxLayout()

        title = QLabel("STUDENT LIST")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("admin_student_title")

        self.table = QTableWidget()
        self.table.setObjectName("course_detail_table")   # ✅ YOUR QSS APPLIED
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "User ID",
            "Username",
            "Email",
            "Phone",
            "Full Name",
            "Reg No",
            "Semester",
            "Program",
            "Department",
            "Father Name",
            "DOB",
            "CNIC"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        layout.addWidget(title)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.load_students()

    def load_students(self):
        try:
            cursor.execute("EXEC dbo.admin_get_all_students")
            data = cursor.fetchall()

            self.table.setRowCount(len(data))

            for row, student in enumerate(data):
                for col, value in enumerate(student):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))

        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))



class admin_teacher(QWidget):
    def __init__(self, admin_dashboard, admin_user_id):
        super().__init__()
        self.setWindowTitle("Admin Teacher Management")
        self.resize(1000, 600)

        self.previous_window = admin_dashboard

        # ================= BACK BUTTON =================
        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName("backbutton_style")
        self.back_button.clicked.connect(self.go_back)

        form_layout = QGridLayout()

        # ================= INPUTS =================
        self.username_input = QLineEdit()
        self.username_input.setObjectName("admin_student_input")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("admin_student_input")

        self.email_input = QLineEdit()
        self.email_input.setObjectName("admin_student_input")

        self.phone_input = QLineEdit()
        self.phone_input.setObjectName("admin_student_input")

        self.full_name_input = QLineEdit()
        self.full_name_input.setObjectName("admin_student_input")

        self.designation_input = QLineEdit()
        self.designation_input.setObjectName("admin_student_input")

        self.department_combo = QComboBox()
        self.department_combo.setObjectName("admin_student_combo")

        self.password_input.setPlaceholderText("Max 8 characters")
        self.email_input.setPlaceholderText("abc@gmail.com")
        self.phone_input.setPlaceholderText("11 digit number")

        # ================= LABEL FUNCTION =================
        def lbl(text):
            label = QLabel(text)
            label.setObjectName("admin_student_label")
            return label

        # ================= ADD TO GRID =================
        form_layout.addWidget(lbl("Username:"), 0, 0)
        form_layout.addWidget(self.username_input, 0, 1)

        form_layout.addWidget(lbl("Password:"), 0, 2)
        form_layout.addWidget(self.password_input, 0, 3)

        form_layout.addWidget(lbl("Email:"), 1, 0)
        form_layout.addWidget(self.email_input, 1, 1)

        form_layout.addWidget(lbl("Phone:"), 1, 2)
        form_layout.addWidget(self.phone_input, 1, 3)

        form_layout.addWidget(lbl("Full Name:"), 2, 0)
        form_layout.addWidget(self.full_name_input, 2, 1)

        form_layout.addWidget(lbl("Designation:"), 2, 2)
        form_layout.addWidget(self.designation_input, 2, 3)

        form_layout.addWidget(lbl("Department:"), 3, 0)
        form_layout.addWidget(self.department_combo, 3, 1)

        # ================= SUBMIT BUTTON =================
        self.submit_button = QPushButton("Add Teacher")
        self.submit_button.setObjectName("admin_student_button")
        self.submit_button.clicked.connect(self.add_teacher)

        # ================= TOP ROW =================
        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        # ================= TITLE =================
        title = QLabel("ADMIN TEACHER PANEL")
        title.setObjectName("admin_student_title")

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addLayout(title_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(20)

        button_row = QHBoxLayout()

        self.list_button = QPushButton("List")
        self.list_button.setObjectName("admin_student_button")
        self.list_button.clicked.connect(self.open_teacher_list)

        button_row.addWidget(self.list_button)
        button_row.addStretch()
        button_row.addWidget(self.submit_button)
        main_layout.addLayout(button_row)
        self.setLayout(main_layout)

        self.load_departments()

    def open_teacher_list(self):
        self.teacher_list_window = TeacherListWindow()
        self.teacher_list_window.show()

    def load_departments(self):
        try:
            self.department_combo.clear()
            self.department_combo.addItem("Select Department", None)

            cursor.execute("SELECT department_id, dept_name FROM department")
            for did, dname in cursor.fetchall():
                self.department_combo.addItem(dname, did)

        except Exception as e:
            QMessageBox.critical(self, "Department Load Error", str(e))

    def add_teacher(self):
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        full_name = self.full_name_input.text()
        designation = self.designation_input.text()
        department_id = self.department_combo.currentData()

        if not all([username, password, email, full_name, designation]):
            QMessageBox.warning(self, "Error", "Fill all required fields!")
            return

        if len(password) > 8 or not password.isalnum():
            QMessageBox.warning(
                self,
                "Password Error",
                "Password must be max 8 characters and contain only letters & numbers!"
            )
            return

        if "@" not in email or "." not in email or email.startswith("@") or email.endswith("@"):
            QMessageBox.warning(
                self,
                "Email Error",
                "Invalid email format!\nExample: abc@gmail.com"
            )
            return

        if (
                not phone.isdigit() or
                len(phone) != 11 or
                not phone.startswith("033")
        ):
            QMessageBox.warning(
                self,
                "Phone Error",
                "Phone must start with 033 and contain exactly 11 digits.\nExample: 03351234567"
            )
            return

        if department_id is None:
            QMessageBox.warning(self, "Error", "Select Department!")
            return

        cursor.execute("""
        EXEC dbo.admin_add_teacher
            ?, ?, ?, ?, ?, ?, ?
    """, (
        username,
        password,
        email,
        phone,
        full_name,
        designation,
        department_id
    ))
        conn.commit()
        QMessageBox.information(self, "Success", "Teacher Added Successfully!")


    def go_back(self):
        self.previous_window.show()
        self.close()

############################################################
class TeacherListWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("All Teachers")
        self.resize(1000, 600)

        main_layout = QVBoxLayout(self)

        title = QLabel("ALL TEACHERS LIST")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("admin_student_title")
        main_layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setObjectName("course_detail_table")
        self.table.setHorizontalHeaderLabels([
            "User ID",
            "Username",
            "Email",
            "Phone",
            "Full Name",
            "Designation",
            "Department"
        ])

        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        main_layout.addWidget(self.table)

        self.load_teachers()

    def load_teachers(self):
        try:
            cursor.execute("EXEC dbo.admin_get_all_teachers")
            data = cursor.fetchall()

            self.table.setRowCount(len(data))

            for row, teacher in enumerate(data):
                for col, value in enumerate(teacher):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))

        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))
#####################################################################

class admin_profile(QWidget):
    def __init__(self, admin_dashboard, admin_user_id):
        super().__init__()
        self.setWindowTitle("Admin Profile")
        self.resize(1000, 600)

        self.previous_window = admin_dashboard
        self.admin_user_id = admin_user_id

        # ================= BACK BUTTON =================
        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName("backbutton_style")
        self.back_button.clicked.connect(self.go_back)

        # ================= TITLE =================
        title = QLabel("ADMIN PROFILE")
        title.setObjectName("admin_student_title")

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()

        #profile pic
        self.image_label = QLabel()
        self.image_label.setFixedSize(150, 150)
        self.image_label.setStyleSheet("border:2px solid gray; border-radius:75px;")
        self.image_label.setAlignment(Qt.AlignCenter)

        self.upload_btn = QPushButton("Upload Picture")
        self.upload_btn.setObjectName("admin_student_button")
        self.upload_btn.clicked.connect(self.upload_picture)

        img_layout = QVBoxLayout()
        img_layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        img_layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)

        # ================= PROFILE FIELDS =================
        self.username_input = QLineEdit()
        self.username_input.setReadOnly(True)  # default read-only

        self.fullname_input = QLineEdit()
        self.fullname_input.setReadOnly(True)

        self.email_input = QLineEdit()
        self.email_input.setReadOnly(True)

        self.phone_input = QLineEdit()
        self.phone_input.setReadOnly(True)

        self.role_input = QLineEdit()
        self.role_input.setReadOnly(True)

        self.office_input = QLineEdit()
        self.office_input.setReadOnly(True)

        def row(name, widget):
            h = QHBoxLayout()
            lbl1 = QLabel(name)
            lbl1.setFixedWidth(150)
            lbl1.setObjectName("admin_student_label")
            widget.setObjectName("profile_value")
            h.addWidget(lbl1)
            h.addWidget(widget)
            return h

        profile_layout = QVBoxLayout()
        profile_layout.addLayout(row("Username:", self.username_input))
        profile_layout.addLayout(row("Full Name:", self.fullname_input))
        profile_layout.addLayout(row("Email:", self.email_input))
        profile_layout.addLayout(row("Phone:", self.phone_input))
        profile_layout.addLayout(row("Role:", self.role_input))
        profile_layout.addLayout(row("Office:", self.office_input))

        # ================= EDIT BUTTON =================
        self.edit_button = QPushButton("Edit Profile")
        self.edit_button.setObjectName("admin_student_button")
        self.edit_button.clicked.connect(self.enable_editing)

        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("admin_student_button")
        self.save_button.clicked.connect(self.save_profile)
        self.save_button.setEnabled(False)#only enable after pressing edit

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.edit_button)
        btn_row.addWidget(self.save_button)

        # ================= TOP ROW =================
        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        # ================= MAIN LAYOUT =================
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addLayout(title_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(img_layout)
        main_layout.addLayout(profile_layout)
        main_layout.addSpacing(25)
        main_layout.addLayout(btn_row)


        self.setLayout(main_layout)

        self.load_admin_profile()

    def upload_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            image_folder = "profile_images"
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)

            new_path = f"{image_folder}/admin_{self.admin_user_id}.png"
            # shell utilities (high-level file)
            shutil.copyfile(file_path, new_path)

            cursor.execute("""
                UPDATE admin SET profile_pic = ?
                WHERE user_id = ?
            """, (new_path, self.admin_user_id))

            conn.commit()

            pixmap = QPixmap(new_path).scaled(
                150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)

            QMessageBox.information(self, "Success", "Profile picture updated!")


    def enable_editing(self):
        self.username_input.setReadOnly(False)
        self.fullname_input.setReadOnly(False)
        self.email_input.setReadOnly(False)
        self.phone_input.setReadOnly(False)
        self.role_input.setReadOnly(False)
        self.office_input.setReadOnly(False)

        self.edit_button.setEnabled(False)
        self.save_button.setEnabled(True)

        QMessageBox.information(self, "Edit Mode", "You can now edit your profile!")

    def save_profile(self):
        try:

            cursor.execute("""
                        EXEC update_admin_profile ?, ?, ?, ?, ?, ?, ?
                    """, (
                self.admin_user_id,
                self.username_input.text(),
                self.fullname_input.text(),
                self.email_input.text(),
                self.phone_input.text(),
                self.role_input.text(),
                self.office_input.text()
            ))
            conn.commit()

            # disable editing again
            self.username_input.setReadOnly(True)
            self.fullname_input.setReadOnly(True)
            self.email_input.setReadOnly(True)
            self.phone_input.setReadOnly(True)
            self.role_input.setReadOnly(True)
            self.office_input.setReadOnly(True)

            self.edit_button.setEnabled(True)
            self.save_button.setEnabled(False)

            QMessageBox.information(self, "Success", "Profile updated successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not update profile:\n{str(e)}")


    def load_admin_profile(self):
        try:
            cursor.execute("EXEC load_admin_profile ?", (self.admin_user_id,))
            row = cursor.fetchone()

            if row:
                self.username_input.setText(str(row[1]))
                self.fullname_input.setText(str(row[2]))
                self.email_input.setText(str(row[3]))
                self.phone_input.setText(str(row[4]))
                self.role_input.setText(str(row[5]))
                self.office_input.setText(str(row[6]))
            if len(row) > 7 and row[7]:
                pixmap = QPixmap(row[7]).scaled(
                    150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.image_label.setPixmap(pixmap)
                self.image_label.setPixmap(pixmap)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def go_back(self):
        self.previous_window.show()
        self.close()

class admin_courses(QWidget):
    def __init__(self,admin_dashboard,admin_user_id):
        super().__init__()
        self.setWindowTitle("Admin Course Management")
        self.resize(1000, 600)
        self.previous_window = admin_dashboard

        self.back_button = QPushButton("← Back")
        self.back_button.setObjectName("backbutton_style")
        self.back_button.clicked.connect(self.go_back)

        title = QLabel("TEACHER COURSE ASSIGNMENT")
        title.setObjectName("admin_student_title")
        title.setContentsMargins(0, 10, 0, 20)
        title.setAlignment(Qt.AlignCenter)

        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()

        self.teacher_combo = QComboBox()
        self.teacher_combo.setObjectName("admin_student_combo")
        self.course_combo = QComboBox()
        self.course_combo.setObjectName("admin_student_combo")
        self.class_combo = QComboBox()
        self.class_combo.setObjectName("admin_student_combo")
        self.semester_combo = QComboBox()
        self.semester_combo.setObjectName("admin_student_combo")
        self.semester_combo.addItems([str(i) for i in range(1, 9)])

        def lbl(text):
            label = QLabel(text)
            label.setObjectName("admin_student_label")
            label.setFixedWidth(120)
            return label

        form_layout = QGridLayout()
        form_layout.addWidget(lbl("Teacher:"), 0, 0)
        form_layout.addWidget(self.teacher_combo, 0, 1)

        form_layout.addWidget(lbl("Course:"), 1, 0)
        form_layout.addWidget(self.course_combo, 1, 1)

        form_layout.addWidget(lbl("Class:"), 2, 0)
        form_layout.addWidget(self.class_combo, 2, 1)

        form_layout.addWidget(lbl("Semester:"), 3, 0)
        form_layout.addWidget(self.semester_combo, 3, 1)

        self.assign_button = QPushButton("Assign Course")
        self.assign_button.setObjectName("admin_student_button")
        self.assign_button.clicked.connect(self.assign_course)

        self.view_assignments_btn = QPushButton("View Teacher Assignments")
        self.view_assignments_btn.setObjectName("admin_student_button")
        self.view_assignments_btn.clicked.connect(self.open_assignment_list)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.assign_button)
        button_layout.addSpacing(15)
        button_layout.addWidget(self.view_assignments_btn)

        main_layout = QVBoxLayout()
        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        main_layout.addLayout(top_row)
        main_layout.addLayout(title_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(30)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)

        self.load_teachers()
        self.load_courses()
        self.load_classes()
        self.clear_form()

    def open_assignment_list(self):
        self.assignment_window = TeacherAssignmentListWindow()
        self.assignment_window.show()

    def load_teachers(self):
        try:
            cursor.execute("EXEC load_teacher_assi")
            data = cursor.fetchall()

            self.teacher_combo.clear()
            for row in data:
                self.teacher_combo.addItem(str(row[1]), row[0])
        except Exception as e:
            QMessageBox.critical(self, "Teacher Load Error", str(e))

    def load_courses(self):
        try:
            cursor.execute("EXEC load_courses_teacher_assi")
            data = cursor.fetchall()

            self.course_combo.clear()
            for row in data:
                self.course_combo.addItem(str(row[1]), row[0])
        except Exception as e:
            QMessageBox.critical(self, "Course Load Error", str(e))

    def load_classes(self):
        try:
            cursor.execute("EXEC load_class_teacher_assi")
            data = cursor.fetchall()

            self.class_combo.clear()
            for row in data:
                self.class_combo.addItem(str(row[1]), row[0])
        except Exception as e:
            QMessageBox.critical(self, "Class Load Error", str(e))

    def assign_course(self):
          teacher_id = self.teacher_combo.currentData()
          course_id = self.course_combo.currentData()
          class_id = self.class_combo.currentData()
          semester = self.semester_combo.currentText()

          if None in (teacher_id, course_id, class_id) or not semester:
              QMessageBox.warning(
                  self,
                  "Input Error",
                  "Please select Teacher, Course, Class, and Semester!"
              )
              return
          semester = int(semester)
          try:
              cursor.execute("EXEC assign_course ?, ?, ?, ?", (teacher_id, course_id, class_id, semester))
              conn.commit()
              QMessageBox.information(self, "Success", "Course assigned successfully!")
              self.load_teachers()
              self.load_courses()
              self.load_classes()
          except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def clear_form(self):
        self.teacher_combo.setCurrentIndex(-1)
        self.course_combo.setCurrentIndex(-1)
        self.class_combo.setCurrentIndex(-1)
        self.semester_combo.setCurrentIndex(-1)

    def go_back(self):
            self.previous_window.show()
            self.close()
#________________________________________________________________________________________________
class TeacherAssignmentListWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teacher Course Assignments")
        self.resize(1000, 600)

        main_layout = QVBoxLayout(self)

        title = QLabel("TEACHER COURSE ASSIGNMENT LIST")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("admin_student_title")
        main_layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setObjectName("course_detail_table")
        self.table.setHorizontalHeaderLabels([
            "Teacher ID",
            "Teacher Name",
            "Course",
            "Class",
            "Semester"
        ])

        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        main_layout.addWidget(self.table)

        self.load_assignments()


    def load_assignments(self):
        try:
            cursor.execute("EXEC admin_get_teacher_course_assignments")
            data = cursor.fetchall()

            self.table.setRowCount(len(data))

            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))

        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))

#-----------admin class course asignment----------
class admin_classes(QWidget):
      def __init__(self,admin_dashboard,admin_user_id):
        super().__init__()
        self.setWindowTitle("Admin Class Management")
        self.resize(1000, 600)

        self.previous_window = admin_dashboard
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')

        title = QLabel("STUDENT CLASS ASSIGNMENT")
        title.setObjectName("admin_student_title")
        title.setAlignment(Qt.AlignCenter)
        title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        title.setContentsMargins(0, 10, 0, 20)
        title.setAlignment(Qt.AlignCenter)

        self.student_combo = QComboBox()
        self.student_combo.setObjectName("admin_student_combo")

        self.selected_student_label = QLabel("")
        self.selected_student_label.setObjectName("admin_student_label")
        self.class_combo = QComboBox()
        self.class_combo.setObjectName("admin_student_combo")
        self.program_input = QLineEdit()
        self.program_input.setReadOnly(True)
        self.program_input.setObjectName("admin_student_input")
        self.semester_input = QLineEdit()
        self.semester_input.setReadOnly(True)
        self.semester_input.setObjectName("admin_student_input")

        def lbl(text):
            label = QLabel(text)
            label.setObjectName("admin_student_label")
            label.setFixedWidth(120)
            return label

        form_layout = QGridLayout()
       #want a drop down showing reg no as well as student name
        form_layout.addWidget(lbl("Student:"), 0, 0)
        form_layout.addWidget(self.student_combo, 0, 1)

        form_layout.addWidget(lbl("Program:"), 1, 0)
        form_layout.addWidget(self.program_input, 1, 1)

        form_layout.addWidget(lbl("Semester:"), 2, 0)
        form_layout.addWidget(self.semester_input, 2, 1)

        form_layout.addWidget(lbl("Class:"), 3, 0)
        form_layout.addWidget(self.class_combo, 3, 1)

        self.assign_btn = QPushButton("Assign Class")
        self.assign_btn.clicked.connect(self.assign_class)
        self.assign_btn.setObjectName("admin_student_button")


        self.view_btn = QPushButton("View Student List")
        self.view_btn.clicked.connect(self.open_student_list)
        self.view_btn.setObjectName("admin_student_button")

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.assign_btn)
        button_layout.addSpacing(15)
        button_layout.addWidget(self.view_btn)

        main_layout = QVBoxLayout()
        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        main_layout.addLayout(top_row)
        main_layout.addWidget(title)
        main_layout.addSpacing(20)
        main_layout.addLayout(form_layout)
        main_layout.addSpacing(25)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        self.load_students()
        self.student_combo.currentTextChanged.connect(self.show_semester_student)
        self.load_classes()

      def load_students(self):
          try:
              cursor.execute("EXEC load_students")
              data = cursor.fetchall()

              self.student_combo.clear()

              for row in data:
                  # row[0] = student_id
                  # row[1] = reg_no
                  # row[2] = student_name
                  display_text = f"{row[1]} - {row[2]}"
                  self.student_combo.addItem(display_text, row[0])

          except Exception as e:
              QMessageBox.critical(self, "Student Load Error", str(e))

      def show_semester_student(self, text):
          if "-" not in text:
              return
          reg_no = text.split("-")[0].strip()  # SP24
          full = text.split("-")[0:3]  # ['SP24', 'BSE', '051']
          session = full[0]  # SP24
          program = full[1]  # BSE

          self.program_input.setText(program)
          try:
              cursor.execute("EXEC get_student_semester ?", (f"{session}-{program}-{full[2]}",))
              row = cursor.fetchone()
              if row:
                  self.semester_input.setText(str(row[0]))
              else:
                  self.semester_input.clear()
          except Exception as e:
              QMessageBox.critical(self, "Semester Error", str(e))
          self.load_classes_by_session_and_program(session, program)

      def load_classes_by_session_and_program(self, session, program):
          try:
              cursor.execute("EXEC load_class_by_session_and_program ?, ?", (session, program))
              data = cursor.fetchall()
              self.class_combo.clear()
              if not data:
                  self.class_combo.addItem("No such class present")
                  self.assign_btn.setEnabled(False)
                  QMessageBox.warning(self, "No Class Found",
                                      f"No class found for {session}-{program}")
                  return
              self.assign_btn.setEnabled(True)
              for row in data:
                  self.class_combo.addItem(row[1], row[0])
          except Exception as e:
              QMessageBox.critical(self, "Class Load Error", str(e))

      def load_classes(self):
          try:
              cursor.execute("EXEC load_class_sections")  # your procedure
              data = cursor.fetchall()
              self.class_combo.clear()
              for row in data:
                  self.class_combo.addItem(row[1], row[0])  # name, id
          except Exception as e:
              QMessageBox.critical(self, "Error", str(e))


      def assign_class(self):
          reg = self.student_combo.currentData()
          class_id = self.class_combo.currentData()
          if not reg:
              QMessageBox.warning(self, "Input Error", "Select a valid student!")
              return
          if not class_id:
              QMessageBox.warning(self, "Input Error", "No valid class available!")
              return
          try:
              cursor.execute("EXEC assign_student_class ?, ?", (reg, class_id))
              conn.commit()
              QMessageBox.information(self, "Success", "Class Assigned!")
          except Exception as e:
              QMessageBox.critical(self, "Error", str(e))

      def open_student_list(self):
          self.win = StudentClassListWindow()
          self.win.show()

      def go_back(self):
            self.previous_window.show()
            self.close()
#--------------------------------stiudent course list
class StudentClassListWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Class List")
        self.resize(1000, 600)

        main_layout = QVBoxLayout(self)

        title = QLabel("STUDENT CLASS ASSIGNMENT LIST")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("admin_student_title")
        main_layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setObjectName("course_detail_table")
        self.table.setHorizontalHeaderLabels([
            "Student ID", "Student Name", "Reg No", "Class"
        ])

        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        main_layout.addWidget(self.table)

        self.load_list()

    def load_list(self):
        try:
            cursor.execute("EXEC admin_get_student_class_list")
            data = cursor.fetchall()
            print("DATA FROM DB:", data)
            self.table.setRowCount(len(data))
            for row, record in enumerate(data):
                for col, value in enumerate(record):
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))



class admin_dashboard(QWidget):

    def __init__(self,login,admin_user_id):
        super().__init__()
        self.resize(1000,600)
        self.setWindowTitle("CUI Portal")
        self.logged_in_admin_id = admin_user_id

        self.admin_title = QLabel("HELLO ADMIN!")
        self.admin_title.setObjectName('dashboard_title_style')

        self.previous_window = login
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')

        self.grid = QGridLayout()
        items = [
            ("Profile", "admin_profile.png",admin_profile),
            ("Students", "student.png",admin_student),
            ("Teachers", "teacher.png",admin_teacher),
            ("Courses", "course.png",admin_courses),
            ("Classses", "class.png",admin_classes)

        ]
        row = 0
        col = 0

        for title,icon,new_window in items:
            card = self.create_single_card(title,icon,new_window)
            self.grid.addWidget(card, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1


        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        row1 = QHBoxLayout()

        row1.addWidget(self.admin_title, alignment=Qt.AlignCenter)

        master_layout = QVBoxLayout()
        master_layout.addLayout(top_row)
        master_layout.addLayout(row1)


        grid_widget = QWidget()
        grid_widget.setLayout(self.grid)
        master_layout.addWidget(grid_widget)

        self.outer_frame = QFrame()
        self.outer_frame.setLayout(master_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.outer_frame)
        self.setLayout(main_layout)

    def create_single_card(self,title,icon,window_class):
        card_frame = QFrame()
        card_frame.setFixedSize(180, 180)
        layout = QVBoxLayout(card_frame)
        layout.setAlignment(Qt.AlignCenter)

        icon_var = QIcon(icon)
        button = QPushButton()
        button.setIcon(icon_var)
        button.setIconSize(QSize(80,80))
        button.setObjectName('icon_style')


        icon_title = QLabel(title)
        icon_title.setAlignment(Qt.AlignCenter)
        icon_title.setObjectName('title_style')

        layout.addWidget(button)
        layout.addWidget(icon_title)

        button.clicked.connect(lambda: self.open_page(window_class))
        return card_frame

    def go_back(self):
        self.previous_window.show()
        self.close()

    def open_page(self, window_class):
        self.new_window = window_class(self, self.logged_in_admin_id)
        self.new_window.show()
        self.close()


#________________________________________________________________________--------------------------------------------------------------------------------------------------
# login

class Login(QWidget):
    def __init__(self,RoleSelection,usertype):
        super().__init__()
        self.resize(1000,600)
        self.setWindowTitle("CUI Portal")

        self.user_type = usertype

        self.previous_window = RoleSelection
        self.back_button = QPushButton("← Back")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setObjectName('backbutton_style')


        self.welcome_text = QLabel("Login Your Account")
        self.welcome_text.setAlignment(Qt.AlignCenter)
        self.welcome_text.setObjectName('title_style')

        self.username = QLineEdit(self)
        self.username.setPlaceholderText("USERNAME")
        self.username.setObjectName('text_box_style')

        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("PASSWORD")
        self.show_password = QCheckBox("Show Password")
        self.show_password.stateChanged.connect(self.toggle_password)
        self.show_password.setObjectName('checkbox_style')

        self.password.setObjectName('text_box_style')
        self.username.returnPressed.connect(self.password.setFocus)


        self.robot_check = QCheckBox("I'm not a robot")
        self.robot_check.setObjectName("checkbox_style")



        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("button_style")
        self.login_button.clicked.connect(self.login_fun)

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()
        row4 = QHBoxLayout()
        row5 = QHBoxLayout()
        master_layout = QVBoxLayout()

        row1.addWidget(self.welcome_text)
        row2.addWidget(self.username)
        row3.addWidget(self.password)
        row3.addWidget(self.show_password)
        row4.addWidget(self.robot_check)
        row5.addWidget(self.login_button)

        master_layout.addLayout(row1)
        master_layout.addLayout(row2)
        master_layout.addLayout(row3)
        master_layout.addLayout(row4)
        master_layout.addLayout(row5)

        self.login_box_loc = QFrame()
        self.login_box_loc.setLayout(master_layout)
        self.login_box_loc.setFixedWidth(400)
        self.login_box_loc.setFixedHeight(300)
        self.login_box_loc.setObjectName("login_box_loc_style")

    # top row for back button
        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_row)
        main_layout.addStretch()
        main_layout.addWidget(self.login_box_loc,alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def toggle_password(self):
        if self.show_password.isChecked() and self.password.text()== "":
            self.show_error("Please enter password first!")
            return
        if self.show_password.isChecked():
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.password.setEchoMode(QLineEdit.Password)

    def go_back(self):
        self.previous_window.show()
        self.close()

    def show_error(self, msg):
        box = QMessageBox()
        box.setWindowTitle("Error")
        box.setIcon(QMessageBox.Warning)
        box.setText(msg)
        box.exec()

    def login_fun(self):
        username = self.username.text()
        password = self.password.text()
        if username == "":
            self.show_error("Enter username.")
            return
        if password == "":
            self.show_error("Enter password.")
            return
        if not self.robot_check.isChecked():
            self.show_error("Check 'I am not robot'.")
            return
        result = self.check_login(username, password)
        if result == "USERNAME_WRONG":
            self.show_error("Username is wrong")
            return

        elif result == "PASSWORD_WRONG":
            self.show_error("Password is wrong")
            return
        user_id, db_role = result
        if db_role != self.user_type:
            self.show_error(f"Access denied! You are not a {self.user_type}.")
            return

        if db_role == "admin":
            self.dashboard = admin_dashboard(self, user_id)

        elif db_role == "teacher":
            self.dashboard = teacher_dashboard(self, user_id)

        elif db_role == "student":
            self.dashboard = student_dashboard(self, user_id)

        self.dashboard.show()
        self.close()

    def check_login(self,username,password):
        cursor.execute("exec login_procedure ?", (username,))
        result = cursor.fetchone()
        if result is None:
            return "USERNAME_WRONG"
        user_id = result[0]
        role = result[1]
        db_password = result[2]
        if password != db_password:
            return "PASSWORD_WRONG"
        return user_id,role


class RoleSelection(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1000,600)
        self.setWindowTitle("CUI Portal")

        self.CUIlabel = QLabel("CUI PORTAL")
        self.CUIlabel.setAlignment(Qt.AlignCenter)
        self.CUIlabel.setObjectName("cuiportal_style")

        self.admin_selection = QPushButton("Admin")
        self.teacher_selection = QPushButton("Teacher")
        self.student_selection = QPushButton("Student")

        for selection in [self.admin_selection, self.teacher_selection, self.student_selection]:
            selection.setFixedSize(200,200)


        self.admin_selection.setObjectName("admin_button")
        self.teacher_selection.setObjectName("teacher_button")
        self.student_selection.setObjectName("student_button")

        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        master_layout = QVBoxLayout()

        row1.addWidget(self.CUIlabel)
        row2.addWidget(self.admin_selection)
        row2.addSpacing(40)
        row2.addWidget(self.teacher_selection)
        row2.addSpacing(40)
        row2.addWidget(self.student_selection)
        row2.addStretch()

        master_layout.addLayout(row1)
        master_layout.addLayout(row2)


        self.role_box_loc= QFrame()
        self.role_box_loc.setLayout(master_layout)
        self.role_box_loc.setFixedWidth(700)
        self.role_box_loc.setFixedHeight(500)


        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addWidget(self.role_box_loc,alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.admin_selection.clicked.connect(lambda: self.open_login("admin"))
        self.teacher_selection.clicked.connect(lambda: self.open_login("teacher"))
        self.student_selection.clicked.connect(lambda: self.open_login("student"))


    def open_login(self,usertype):
        self.login_window = Login(self,usertype)
        self.login_window.show()
        self.hide()



app = QApplication(sys.argv)
with open("style_cuiportal.qss", "r") as f:
    app.setStyleSheet(f.read())
main_window = RoleSelection()
main_window.show()
app.exec_()