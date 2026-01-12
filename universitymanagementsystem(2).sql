use master;
go

if db_id('university_db') 
begin
    alter database university_db set single_user with rollback immediate;
    drop database university_db;
end
go

create database university_db;
go

use university_db;
go

--core tables

-- users
create table users (
    user_id      bigint identity(1,1) primary key,
    username     nvarchar(50) unique not null,
    password     nvarchar(255) not null,
    email        nvarchar(100) unique not null,
    phone        nvarchar(20),
    full_name    nvarchar(100) not null,
    role         nvarchar(20) check (role in ('student','teacher','admin')) not null,
    is_active    bit default 1,
    created_at   datetime default getdate()
);
create nonclustered index idx_user_role on users(role); 
go

-- department
create table department (
    department_id bigint identity(1,1) primary key,
    dept_code     nvarchar(10) unique not null,
    dept_name     nvarchar(100) not null,
    head_id       bigint null,
    building      nvarchar(50),
    office_no     nvarchar(20)
);
create nonclustered index idx_dept_code on department(dept_code); 
go

-- program
create table program (
    program_id     bigint identity(1,1) primary key,
    program_name   nvarchar(100) not null,
    department_id  bigint not null,
    foreign key (department_id) references department(department_id)
);
create nonclustered index idx_program_dept on program(department_id); 
go

-- course
create table course (
    course_id     bigint identity(1,1) primary key,
    course_code   nvarchar(15) unique not null,
    course_title  nvarchar(150) not null,
    credit_hours  tinyint not null check (credit_hours between 1 and 6),
    department_id bigint not null,
    is_lab        bit default 0,
    is_elective   bit default 0,
    semester      int,
    foreign key (department_id) references department(department_id)
);
create nonclustered index idx_course_code on course(course_code);        
create nonclustered index idx_course_dept on course(department_id);      
create nonclustered index idx_course_semester on course(semester);        
go

-- class_section
create table class_section (
    class_id bigint identity(1,1) primary key,
    session nvarchar(10) not null,      
    program nvarchar(10) not null,       
    section nvarchar(5) not null,       
    department_id bigint not null,
    unique(session, program, section),
    foreign key (department_id) references department(department_id)
);
create nonclustered index idx_class_dept on class_section(department_id); 
go

-- teacher
create table teacher (
    teacher_id    bigint identity(1,1) primary key,
    user_id       bigint unique not null,
    designation   nvarchar(50) not null,
    department_id bigint not null,
    profile_pic nvarchar(255),
    foreign key (user_id) references users(user_id) on delete cascade, 
    foreign key (department_id) references department(department_id)
);
create nonclustered index idx_teacher_dept on teacher(department_id); 
create nonclustered index idx_teacher_designation on teacher(designation); 
go

-- department head link
alter table department add constraint fk_head 
foreign key (head_id) references teacher(teacher_id);
go

-- student
create table student (
    student_id       bigint identity(1,1) primary key,
    user_id          bigint unique not null,
    registration_no  nvarchar(20) unique not null,
    current_semester tinyint default 1,
    program_id       bigint not null, 
    department_id    bigint not null,
    father_name      nvarchar(100),
    dob              date,
    class_id bigint null,
    cnic             nvarchar(15) unique,
    status           nvarchar(20) default 'active',
    foreign key (user_id) references users(user_id) on delete cascade,
    foreign key (program_id) references program(program_id),
    foreign key (department_id) references department(department_id),
    foreign key (class_id) references class_section(class_id)
);
create nonclustered index idx_student_reg on student(registration_no);  
create nonclustered index idx_student_class on student(class_id);            
create nonclustered index idx_student_program on student(program_id);        
create nonclustered index idx_student_dept on student(department_id);        
go

-- admin
create table admin (
    admin_id bigint identity(1,1) primary key,
    user_id  bigint unique not null,
    office   nvarchar(50),
    profile_pic nvarchar(255),
    foreign key (user_id) references users(user_id) on delete cascade
);
go

-- teacher_course_assignmnet
create table teacher_course_assignment (
    assignment_id bigint identity(1,1) primary key,
    teacher_id bigint not null,
    course_id bigint not null,
    class_id bigint not null,
    semester tinyint not null,          
    unique(teacher_id, course_id, class_id), 
    foreign key (teacher_id) references teacher(teacher_id),
    foreign key (course_id) references course(course_id),
    foreign key (class_id) references class_section(class_id)
);
create nonclustered index idx_tca_course_class on teacher_course_assignment(course_id, class_id); 
create nonclustered index idx_tca_teacher on teacher_course_assignment(teacher_id);               
go

-- enrollmenttt
create table enrollmenttt (
    enrollment_id bigint identity(1,1) primary key,
    student_id bigint ,
    course_id  bigint , 
    enrollment_date date default getdate(),
    constraint fk_enrollment_student 
        foreign key (student_id) 
        references student(student_id) 
        on delete cascade,

    constraint fk_enrollment_course 
        foreign key (course_id) 
        references course(course_id) 
        on delete cascade,
    constraint sid_cid
        unique (student_id, course_id)
);
create nonclustered index idx_enrollment_student on enrollmenttt(student_id); 
create nonclustered index idx_enrollment_course on enrollmenttt(course_id);   
go

-- final_marks 
create table final_marks (
    final_id        bigint identity(1,1) primary key,
    student_id      bigint not null,
    class_id        bigint not null,
    total_obtained  decimal(5,2) default 0,
    grade           nvarchar(2) null,
    gpa             decimal(3,2) null,
    last_updated    datetime default getdate(),
    
    constraint fk_final_student foreign key (student_id) references student(student_id),
    constraint fk_final_class   foreign key (class_id) references class_section(class_id),
    constraint uq_final_student_class unique(student_id, class_id)
);
create nonclustered index idx_final_student_class on final_marks(student_id, class_id); 
go

-- marks
create table marks (
    marks_id        bigint identity(1,1) primary key,
    student_id      bigint not null,
    class_id        bigint not null,
    assessment_type  nvarchar(50) not null,
    total_marks     decimal(5,2) not null,
    obtained_marks  decimal(5,2) not null,
    weightage       decimal(5,2) default 100,
    assessment_date  date,
    foreign key (student_id) references student(student_id) ,
    foreign key (class_id) references class_section(class_id) 
);
alter table marks
add semester varchar(10),
    academic_year varchar(9);
create nonclustered index idx_marks_student_class on marks(student_id, class_id);
go

-- announcement
create table announcement (
    ann_id        bigint identity(1,1) primary key,
    title         nvarchar(200) not null,
    message       nvarchar(max) not null,
    created_by    bigint not null,
    created_at    datetime default getdate(),
    ann_type nvarchar(20) check (ann_type in ('text', 'assignment')),
    audience_type nvarchar(20) not null check (audience_type in ('class', 'program', 'all')),
    target_id     bigint null,
    expires_at    datetime null,
    file_name nvarchar(255),
    file_path nvarchar(max),
    foreign key (created_by) references users(user_id) on delete cascade
);
create nonclustered index idx_announcement_target on announcement(audience_type, target_id); 
go

-- student_assignment_submission
create table student_assignment_submission
(
    submission_id bigint identity(1,1) primary key,
    ann_id bigint not null, 
    student_id bigint not null,
    file_name nvarchar(255),
    file_path nvarchar(max),
    file_type nvarchar(20),
    file_size int,
    submitted_at datetime default getdate(),
    grade decimal(5,2) null, 
    foreign key (ann_id) references announcement(ann_id),
    foreign key (student_id) references student(student_id),
    unique (ann_id, student_id)
);
create nonclustered index idx_sas_ann_id on student_assignment_submission(ann_id);     
create nonclustered index idx_sas_student_id on student_assignment_submission(student_id); 
go

-- student_class1
create table student_class1 (
    id int primary key identity(1,1),
    student_id bigint not null unique,
    class_id bigint not null,
    foreign key (student_id) references student(student_id),
    foreign key (class_id) references class_section(class_id)
);
create nonclustered index idx_sc1_class on student_class1(class_id); 
go

-- attendance_lecture
create table attendance_lecture (
    lecture_id int identity primary key,
    teacher_id bigint,
    class_id bigint,
    course_id bigint,
    lecture_date date,
    start_time time,
    end_time time,
    lecture_title varchar(100),
    foreign key (teacher_id) references teacher(teacher_id),
    foreign key (class_id) references class_section(class_id),
    foreign key (course_id) references course(course_id)
);
create nonclustered index idx_al_date on attendance_lecture(lecture_date); 
go

-- student_attendance
create table student_attendance (
    attendance_id int identity primary key,
    lecture_id int not null,
    student_id bigint not null,
    status varchar(10) check (status in ('present', 'absent', 'leave')) not null, 
    foreign key (lecture_id) references attendance_lecture(lecture_id),
    foreign key (student_id) references student(student_id),
    unique (lecture_id, student_id) 
);
create nonclustered index idx_sa_student_id on student_attendance(student_id); 
go

-- attendance
create table attendance (
    id bigint identity(1,1) primary key,
    student_id bigint not null,
    course_id bigint not null,
    class_id bigint not null,
    attendance_date date not null,
    status nvarchar(10) not null,
    foreign key (student_id) references student(student_id),
    foreign key (course_id) references course(course_id),
    foreign key (class_id) references class_section(class_id),
    unique (student_id, course_id, class_id, attendance_date)
);
go

-- cgpa calculator tables
create table course_gpa (
    course_id int identity primary key,
    student_id int,
    course_name nvarchar(50),
    credit_hours int,
    total_marks int,
    gpa float
);

create table semester_gpa (
    student_id int primary key,
    semester_gpa float
);

create table semester_course_temp (
    id int identity primary key,
    student_id int,
    credit_hours int,
    course_gpa float
);
go

-- view
create or alter view vw_semester_quality_points
as
select
    student_id,
    credit_hours,
    (gpa * credit_hours) as quality_points
from course_gpa;
go

--  sample data insertion 

-- users 
insert into users (username, password, email, phone, full_name, role) values
('admin01', 'hash_admin', 'admin@uni.edu', '03001234567', 'the database admin', 'admin'),
('dr.khan', 'hash_teacher1', 'dr.khan@uni.edu', '03011111111', 'dr. adil khan', 'teacher'),
('pro.ali', 'hash_teacher2', 'pro.ali@uni.edu', '03022222222', 'prof. sara ali', 'teacher'),
('std.faizan', 'hash_student1', 'faizan@uni.edu', '03033333333', 'faizan ahmed', 'student'),
('std.zainab', 'hash_student2', 'zainab@uni.edu', '03044444444', 'zainab bibi', 'student');
go

-- admin
insert into admin (user_id, office) values (1, 'admin block, a-101');
go

-- department
insert into department (dept_code, dept_name, building, office_no) values
('cs', 'computer science', 'it block', '101'),
('ee', 'electrical engineering', 'engineering block', '202');
go

-- program
insert into program (program_name, department_id) values
('bs computer science', 1),
('ms software engineering', 1),
('bs electrical engineering', 2);
go

-- course
insert into course (course_code, course_title, credit_hours, department_id, is_lab, semester) values
('cs101', 'introduction to programming', 3, 1, 1, 1),
('cs202', 'database systems', 3, 1, 1, 3),
('ee110', 'circuit analysis', 3, 2, 0, 1),
('cs700', 'advanced data structures', 3, 1, 0, 7);
go

-- teacher
insert into teacher (user_id, designation, department_id) values
(2, 'associate professor', 1),
(3, 'assistant professor', 2);
go

-- update head of department
update department set head_id = 1 where dept_code = 'cs';
go
select * from class_section
-- class_section
insert into class_section (session, program, section, department_id) values
('f2024', 'bscs', 'a', 1), -- class_id 1
('f2024', 'bsee', 'b', 2), -- class_id 2
('s2024', 'msse', 'a', 1); -- class_id 3
go
select * from class_section
-- student
insert into student (user_id, registration_no, current_semester, program_id, department_id, father_name, dob, cnic, class_id) values
(4, 'l24-0001', 1, 1, 1, 'mr. arshad', '2005-01-15', '12345-6789012-3', 1), -- student_id 1
(5, 'l24-0002', 1, 3, 2, 'mr. bilal', '2004-10-20', '32109-8765432-1', 2); -- student_id 2
go

-- student_class1
insert into student_class1 (student_id, class_id) values
(1, 1),
(2, 2);
go

-- teacher_course_assignment
insert into teacher_course_assignment (teacher_id, course_id, class_id, semester) values
(1, 1, 1, 1), -- dr. khan, cs101, f2024-bscs-a
(2, 3, 2, 1); -- pro. ali, ee110, f2024-bsee-b
go

-- enrollmenttt
insert into enrollmenttt (student_id, course_id) values 
(1, 1), -- faizan, cs101
(1, 2), -- faizan, cs202
(2, 3); -- zainab, ee110
go

-- announcement
insert into announcement (title, message, created_by, ann_type, audience_type, target_id, expires_at) values
('welcome to cs101', 'please ensure you have read the course outline on the lms.', 2, 'text', 'class', 1, null); -- ann_id 1

insert into announcement (title, message, created_by, ann_type, audience_type, target_id, expires_at, file_name, file_path) values
('assignment 1: data types', 'implement a simple calculator in c++.', 2, 'assignment', 'class', 1, dateadd(day, 7, getdate()), 'assignment1.pdf', '/uploads/path/assign1.pdf'); -- ann_id 2
go

-- student_assignment_submission 
insert into student_assignment_submission (ann_id, student_id, file_name, file_path, file_type, file_size, grade) values
(2, 1, 'faizan_assign1.zip', '/submissions/faizan/assign1.zip', 'zip', 1024, 85.50);
go

-- final_marks 
insert into final_marks (student_id, class_id, total_obtained, grade, gpa) values
(1, 1, 3.50, 'a', 3.66),
(2, 2, 3.00, 'b', 3.00);
go

-- marks 
insert into marks (student_id, class_id, assessment_type, total_marks, obtained_marks, semester, academic_year) values
(1, 1, 'midterm', 50.00, 42.50, 'fall', '2024-2025'),
(1, 1, 'quiz 1', 10.00, 8.00, 'fall', '2024-2025'),
(2, 2, 'midterm', 50.00, 35.00, 'fall', '2024-2025');
go

-- attendance lecture
insert into attendance_lecture (teacher_id, class_id, course_id, lecture_date, start_time, end_time, lecture_title) values
(1, 1, 1, '2025-12-15', '09:00:00', '10:00:00', 'lecture 1: intro'); -- lecture_id 1
go

-- student attendance
insert into student_attendance (lecture_id, student_id, status) values
(1, 1, 'present'),
(1, 2, 'absent');
go

-- dummy attendance 
insert into attendance (student_id, course_id, class_id, attendance_date, status) values
(1, 1, 1, getdate(), 'present');
go


-- stored procedures 

-- 1
create or alter procedure login_procedure
    @username varchar(50)
as
begin
    select user_id, role, password
    from users
    where username = @username;
end
go

-- 2 
create or alter procedure search_courses
    @search varchar(100)
as
begin
    select
        c.course_code,
        c.course_title,
        c.credit_hours,
        d.dept_name,
        c.is_lab,
        c.is_elective
    from course c
    left join department d 
        on c.department_id = d.department_id
    where c.course_title like '%' + @search + '%'
    order by c.course_title;
end
go

-- 2 
create or alter procedure get_all_courses
as
begin
    select course_id, course_title, semester, credit_hours
    from course;
end
go

-- 3
create or alter procedure get_student_id
    @user_id int
as
begin
    select student_id
    from student
    where user_id = @user_id;
end
go

create or alter procedure teacher_get_classes_attendance
    @teacher_id bigint
as
begin
    select
        c.course_id,
        c.course_title,
        cs.class_id,
        cs.session + '-' + cs.program + '-' + cs.section as class_name
    from teacher_course_assignment tca
    join course c on tca.course_id = c.course_id
    join class_section cs on tca.class_id = cs.class_id
    where tca.teacher_id = @teacher_id;
end;
go
-- 4
create or alter procedure enroll_student
    @student_id int,
    @course_id int
as
begin
    insert into enrollmenttt (student_id, course_id)
    values (@student_id, @course_id);
end
go

-- 5
create or alter procedure get_registered_courses
    @student_id int
as
begin
    select 
        s.student_id, 
        u.username, 
        c.course_title, 
        c.semester, 
        c.credit_hours
    from enrollmenttt e
    join student s on e.student_id = s.student_id
    join users u on s.user_id = u.user_id
    join course c on e.course_id = c.course_id
    where e.student_id = @student_id;
end
go

-- 6
create or alter procedure add_student
    @username nvarchar(50),
    @password nvarchar(255),
    @email nvarchar(100),
    @phone nvarchar(20),
    @full_name nvarchar(100),
    @registration_no nvarchar(20),
    @current_semester tinyint,
    @program_id bigint,
    @department_id bigint,
    @father_name nvarchar(100),
    @dob date,
    @cnic nvarchar(15)
as
begin
    begin transaction;
    begin try

        insert into users (username, password, email, phone, full_name, role)
        values (@username, @password, @email, @phone, @full_name, 'student');

        declare @user_id bigint = scope_identity();

        insert into student
        (user_id, registration_no, current_semester, program_id,
         department_id, father_name, dob, cnic)
        values
        (@user_id, @registration_no, @current_semester,
         @program_id, @department_id, @father_name, @dob, @cnic);

        commit transaction;
        select 'success' as result;

    end try
    begin catch
        rollback transaction;
        select error_message() as errormessage;
    end catch
end;
go

-- 7
create or alter procedure mark_attendance
    @student_id bigint,
    @course_id  bigint,
    @class_id   bigint,
    @attendance_date date,
    @status nvarchar(10)
as
begin
    if exists (
        select 1
        from attendance
        where student_id = @student_id
          and course_id = @course_id
          and class_id = @class_id
          and attendance_date = @attendance_date
    )
    begin
        raiserror('attendance already marked for this student in this class on this date!', 16, 1);
        return;
    end

    insert into attendance (student_id, course_id, class_id, attendance_date, status)
    values (@student_id, @course_id, @class_id, @attendance_date, @status);
end;
go

-- 8
create or alter procedure get_all_students
as
begin
    select 
        s.student_id,
        s.registration_no,
        u.username,
        s.current_semester,
        p.program_name,
        d.dept_name,
        s.status
    from student s
    join users u on s.user_id = u.user_id
    join program p on s.program_id = p.program_id
    join department d on s.department_id = d.department_id
end;
go

-- 9
create or alter procedure search_student
    @value nvarchar(100)
as
begin
    select 
        s.student_id,
        s.registration_no,
        u.username,
        s.current_semester,
        p.program_name,
        d.dept_name,
        s.status
    from student s
    join users u on s.user_id = u.user_id
    join program p on s.program_id = p.program_id
    join department d on s.department_id = d.department_id
    where 
        s.registration_no like '%' + @value + '%'
        or u.username like '%' + @value + '%'
        or s.cnic like '%' + @value + '%'
end;
go

-- 10
create or alter procedure get_all_programs
as
begin
    select program_id, program_name
    from program
    order by program_name
end;
go

-- 11
create or alter procedure get_all_departments
as
begin
    select department_id, dept_name
    from department
    order by dept_name
end;
go

-- 12
create or alter procedure admin_add_record
    @username nvarchar(50),
    @password nvarchar(255),
    @email nvarchar(100),
    @phone nvarchar(20),
    @full_name nvarchar(100),
    @registration_no nvarchar(20),
    @semester tinyint,
    @program_id bigint,
    @department_id bigint,
    @father_name nvarchar(100),
    @dob date,
    @cnic nvarchar(15),
    @class_id bigint
as
begin
    set nocount on;

    begin transaction;
    begin try

        insert into users (username, password, email, phone, full_name, role)
        values (@username, @password, @email, @phone, @full_name, 'student');

        declare @user_id bigint = scope_identity();

        insert into student
        (user_id, registration_no, current_semester, program_id,
         department_id, father_name, dob, cnic, class_id)
        values
        (@user_id, @registration_no, @semester,
         @program_id, @department_id, @father_name, @dob, @cnic, @class_id);

        insert into student_class1 (student_id, class_id)
        values (scope_identity(), @class_id);

        commit transaction;

    end try
    begin catch
        rollback transaction;
        throw;
    end catch
end;
go
--  triggers

-- 1. prevent_duplicate_enrollment 
if object_id('prevent_duplicate_enrollment') is not null
    drop trigger prevent_duplicate_enrollment;
go

create trigger prevent_duplicate_enrollment
on enrollmenttt
instead of insert
as
begin
    if exists (
        select 1
        from enrollmenttt e
        join inserted i
            on e.student_id = i.student_id
           and e.course_id = i.course_id
    )
    begin
        raiserror ('already enrolled!', 16, 1)
        return
    end

    insert into enrollmenttt (student_id, course_id)
    select student_id, course_id from inserted;
end
go

-- 2. trg_attendance_duplicate
if object_id('trg_attendance_duplicate') is not null
    drop trigger trg_attendance_duplicate;
go

create trigger trg_attendance_duplicate
on student_attendance
after insert
as
begin
    if exists (
        select lecture_id, student_id
        from student_attendance
        group by lecture_id, student_id
        having count(*) > 1
    )
    begin
        rollback;
        raiserror('duplicate attendance not allowed',16,1);
    end
end
go

-- 13
create or alter procedure admin_add_teacher
    @username nvarchar(50),
    @password nvarchar(255),
    @email nvarchar(100),
    @phone nvarchar(20),
    @full_name nvarchar(100),
    @designation nvarchar(50),
    @department_id bigint
as
begin
    begin transaction;
    begin try

        insert into users (username, password, email, phone, full_name, role)
        values (@username, @password, @email, @phone, @full_name, 'teacher');

        declare @user_id bigint = scope_identity();

        insert into teacher (user_id, designation, department_id)
        values (@user_id, @designation, @department_id);

        commit transaction;

    end try
    begin catch
        rollback transaction;
        throw;
    end catch
end;
go

-- 14 
create or alter procedure admin_get_all_teachers
as
begin
    set nocount on;

    select 
        u.user_id,
        u.username,
        u.email,
        u.phone,
        u.full_name,
        t.designation,
        d.dept_name
    from teacher t
    join users u on t.user_id = u.user_id
    join department d on t.department_id = d.department_id;
end;
go
UPDATE class_section
SET term = 'fa24'
WHERE term = 'f2024';

UPDATE class_section
SET term = 'sp24'
WHERE term = 's2024';

select * from users
select * from teacher
select * from admin
select * from class_section
-- 14 
create or alter procedure get_students_by_class
    @class_id bigint
as
begin
    select 
        s.student_id,
        s.registration_no,
        u.full_name as name
    from student s
    join users u on u.user_id = s.user_id
    join student_class1 sc on sc.student_id = s.student_id 
    where sc.class_id = @class_id;
end;
go

-- 15
create or alter procedure admin_get_all_students
as
begin
    select 
        u.user_id,
        u.username,
        u.email,
        u.phone,
        u.full_name,
        s.registration_no,
        s.current_semester,
        p.program_name,
        d.dept_name,
        s.father_name,
        s.dob,
        s.cnic
    from student s
    join users u on s.user_id = u.user_id
    join program p on s.program_id = p.program_id
    join department d on s.department_id = d.department_id
    where u.role = 'student'
end;
go

-- 16
create or alter procedure load_admin_profile
    @user_id bigint
as
begin
    select 
        u.user_id,
        u.username,
        u.full_name,
        u.email,
        u.phone,
        u.role,
        a.office,
        a.profile_pic
    from users u
    join admin a on u.user_id = a.user_id
    where u.user_id = @user_id;
end;
go

-- 17
create or alter procedure update_admin_profile
    @user_id bigint,
    @username nvarchar(50),
    @full_name nvarchar(100),
    @email nvarchar(100),
    @phone nvarchar(20),
    @role nvarchar(20),
    @office nvarchar(50)
as
begin
update users
set username = @username,
    full_name = @full_name,
    email = @email,
    phone = @phone,
    role = @role
where user_id = @user_id;
update admin
set office = @office
where user_id = @user_id;
end;
go

-- 18
create or alter procedure load_teacher_assi
as
begin
     select t.teacher_id, u.full_name
    from teacher t
    inner join users u on t.user_id = u.user_id
    where u.role = 'teacher'
end
go


-- 19
create or alter procedure load_courses_teacher_assi
as
begin
    select course_id, course_title
    from course;
end
go

-- 20
create or alter procedure load_class_teacher_assi 
as
begin
    select class_id, session + '-' + program + '-' + section as class_name
    from class_section;
end
go

-- 21
create or alter procedure assign_course
    @teacher_id bigint,
    @course_id bigint,
    @class_id bigint,
    @semester int
as
begin
    insert into teacher_course_assignment (teacher_id, course_id, class_id, semester)
    values (@teacher_id, @course_id, @class_id, @semester);
end
go

-- 22
create or alter procedure admin_get_teacher_course_assignments
as
begin
    select 
        t.teacher_id,
        u.full_name as teacher_name,
        c.course_title,
        cs.session + '-' + cs.program + '-' + cs.section as class_name, 
        a.semester
    from teacher_course_assignment a
    join teacher t on a.teacher_id = t.teacher_id
    join users u on t.user_id = u.user_id
    join course c on a.course_id = c.course_id
    join class_section cs on a.class_id = cs.class_id
end
go

-- 23
create or alter procedure load_students
as
begin
    select 
        s.student_id,     
        s.registration_no,        
        u.full_name      
    from student s
    inner join users u 
        on s.user_id = u.user_id
end
go

-- 24
create or alter procedure load_class_sections
as
begin
    select 
        class_id,                     
        session + '-' + program + '-' + section as class_name  
    from class_section
end
go

-- 25
create or alter procedure assign_student_class
    @student_id bigint,
    @class_id bigint
as
begin
    update student
    set class_id = @class_id
    where student_id = @student_id;

    if exists (
        select 1 from student_class1
        where student_id = @student_id
    )
    begin
        update student_class1
        set class_id = @class_id
        where student_id = @student_id
    end
    else
    begin
        insert into student_class1(student_id, class_id)
        values (@student_id, @class_id)
    end
end
go

-- 26
create or alter procedure get_student_semester
    @reg_no nvarchar(50)
as
begin
    select current_semester
    from student
    where registration_no = @reg_no;
end
go

-- 27
create or alter procedure load_class_sections_by_program
    @program nvarchar(20)
as
begin
    select class_id, section
    from class_section
    where program = @program;
end
go

-- 28
create or alter procedure load_class_by_session_and_program
    @session nvarchar(10),
    @program nvarchar(10)
as
begin
    select class_id,
           session + '-' + program + '-' + section as class_name
    from class_section
    where session = @session
      and program = @program
end
go

-- 29
create or alter procedure admin_get_student_class_list
as
begin
    select 
        s.student_id,
        u.full_name,
        s.registration_no,
        (cs.session + '-' + cs.program + '-' + cs.section) as class_name
    from student_class1 sc
    join student s on sc.student_id = s.student_id
    join users u on s.user_id = u.user_id
    join class_section cs on sc.class_id = cs.class_id;
end;
go

-- 31
create or alter procedure get_student_class_by_id
    @student_id bigint
as
begin
    set nocount on;

    select
        s.class_id,
        s.student_id
    from student s
    where s.student_id = @student_id
end;
go

-- 32 
create or alter procedure update_teacher_profile
    @user_id bigint,
    @username nvarchar(50),
    @full_name nvarchar(100),
    @email nvarchar(100),
    @phone nvarchar(20)
as
begin
    update users
    set 
        username = @username,
        full_name = @full_name,
        email = @email,
        phone = @phone
    where user_id = @user_id;
end;
go

-- 32 
create or alter procedure load_teacher_profile
    @user_id bigint
as
begin
    select 
        u.user_id,
        u.username,
        u.full_name,
        u.email,
        u.phone,
        u.role,
        t.designation,
        t.department_id,
        t.profile_pic
    from users u
    inner join teacher t on u.user_id = t.user_id
    where u.user_id = @user_id;
end;
go

-- 33 
create or alter procedure load_student_profile
    @user_id bigint
as
begin
    select 
        u.user_id,
        u.username,
        u.full_name,
        u.email,
        u.phone,
        s.registration_no,
        s.current_semester,
        p.program_name
    from users u
    join student s on u.user_id = s.user_id
    join program p on s.program_id = p.program_id
    where u.user_id = @user_id
end
go

-- 33 
create or alter procedure update_student_profile
    @user_id bigint,
    @username nvarchar(50),
    @full_name nvarchar(100),
    @email nvarchar(100),
    @phone nvarchar(20)
as
begin
    update users
    set username = @username,
        full_name = @full_name,
        email = @email,
        phone = @phone
    where user_id = @user_id
end
go

-- 34
create or alter procedure get_teacher_assigned_courses
    @teacher_user_id bigint
as
begin

    select 
        c.course_code,
        c.course_title,
        tca.semester,
        cs.program,
        cs.session,    
        cs.session + '-' + cs.program + '-' + cs.section as class_name,
        c.credit_hours
    from teacher t
    inner join users u
        on t.user_id = u.user_id          
    inner join teacher_course_assignment tca
        on t.teacher_id = tca.teacher_id
    inner join course c
        on tca.course_id = c.course_id
    inner join class_section cs
        on tca.class_id = cs.class_id
    where t.user_id = @teacher_user_id
    order by cs.session, cs.program, cs.section, c.course_code;
end
go

-- 35
create or alter procedure get_teacher_courses
    @teacher_id bigint
as
begin
    select tca.assignment_id,
           tca.course_id,
           c.course_title,
           tca.class_id,
           cs.session + '-' + cs.program + '-' + cs.section as class_name,
           tca.semester
    from teacher_course_assignment tca
    join course c on c.course_id = tca.course_id
    join class_section cs on cs.class_id = tca.class_id
    where tca.teacher_id = @teacher_id;
end
go

-- 36 
create or alter procedure add_text_announcements
    @title nvarchar(200),
    @message nvarchar(max),
    @created_by bigint,    
    @class_id bigint,
    @ann_type nvarchar(20),
    @expires_at datetime = null
as
begin
    insert into announcement
    (
        title,
        message,
        created_by,
        created_at,
        audience_type,
        target_id,
        ann_type,
        expires_at

    )
    values
    (
        @title,
        @message,
        @created_by,
        getdate(),
        'class',        
        @class_id,      
        @ann_type,
        @expires_at
    );
end;
go

-- 36 
create or alter procedure add_assignment_announcements
    @title nvarchar(max),
    @created_by bigint,
    @class_id bigint,
    @start_datetime datetime,
    @due_datetime datetime,
    @file_name nvarchar(255),
    @file_path nvarchar(max),
    @ann_type nvarchar(20)
as
begin
    insert into announcement
    (
        title,
        message,               
        created_by,
        created_at,
        ann_type,
        audience_type,
        target_id,
        expires_at,
        file_name,
        file_path
    )
    values
    (
        @title,
        '',                   
        @created_by,
        @start_datetime,
        @ann_type,
        'class',          
        @class_id,          
        @due_datetime,
        @file_name,
        @file_path
    );
end;
go

-- 37
create or alter procedure get_student_announcements
    @student_user_id bigint
as
begin
    select 
        a.ann_id,
        a.title,
        a.message,
        a.created_at
    from announcement a
    inner join student s on s.user_id = @student_user_id
    inner join student_class1 sc on sc.student_id = s.student_id
    
    where a.audience_type = 'class'    
      and a.target_id = sc.class_id   

    order by a.created_at desc;
end;
go

-- 38
create or alter procedure submit_assignment
    @ann_id bigint,
    @student_id bigint,
    @file_name nvarchar(255),
    @file_path nvarchar(max),
    @file_type nvarchar(20),
    @file_size int
as
begin
    insert into student_assignment_submission
    (
        ann_id, student_id, file_name, file_path, file_type, file_size
    )
    values
    (
        @ann_id, @student_id, @file_name, @file_path, @file_type, @file_size
    );
end;
go

-- 39
create or alter procedure get_submissions_for_assignment
    @teacher_id bigint 
as
begin
    select 
        s.submission_id,
        u.full_name as student_name,
        st.registration_no,
        a.title,
        s.file_name,
        s.file_path,
        s.submitted_at
    from student_assignment_submission s
    inner join announcement a on a.ann_id = s.ann_id
    inner join student st on st.student_id = s.student_id
    inner join users u on u.user_id = st.user_id
    where a.created_by = @teacher_id
    order by s.submitted_at desc
end
go

-- 40
create or alter procedure get_student_text_announcements
    @student_user_id bigint
as
begin
    select 
        a.ann_id,
        a.title,
        a.message,
        a.created_at,
        c.course_title
    from announcement a
    
    inner join student s on s.user_id = @student_user_id
    inner join student_class1 sc on sc.student_id = s.student_id
    inner join teacher_course_assignment tca on tca.class_id = sc.class_id
    inner join course c on c.course_id = tca.course_id
    
    where a.ann_type = 'text'      
      and a.audience_type = 'class'  
      and a.target_id = sc.class_id  
    order by a.created_at desc;
end;
go

-- 41
create or alter procedure get_student_assignment_announcements
    @student_user_id bigint
as
begin
    select 
        a.ann_id,
        a.title,
        a.message,
        a.created_at,
        a.expires_at as due_date,
        c.course_id,
        c.course_title,
        a.file_name,
        a.file_path
    from announcement a
    
    inner join student s on s.user_id = @student_user_id
    inner join student_class1 sc on sc.student_id = s.student_id
    inner join teacher_course_assignment tca on tca.class_id = sc.class_id
    inner join course c on c.course_id = tca.course_id
    
    where a.ann_type = 'assignment'
      and a.audience_type = 'class'
      and a.target_id = sc.class_id  
    order by a.created_at desc;
end;
go

-- 42
create or alter procedure insert_marks
    @student_id bigint,
    @class_id bigint,
    @assessment_type nvarchar(50),
    @total_marks decimal(5,2),
    @obtained_marks decimal(5,2)
as
begin
    set nocount on;

    begin transaction;
    begin try

        insert into marks(student_id, class_id, assessment_type, total_marks, obtained_marks)
        values(@student_id, @class_id, @assessment_type, @total_marks, @obtained_marks);

        commit transaction;
    end try
    begin catch
        rollback transaction;
        throw;
    end catch
end
go

-- 43 
create or alter procedure get_class_students_attendance
    @class_id int,
    @course_id int
as
begin
    select 
        s.student_id,
        s.registration_no,
        u.full_name
    from student s
    join users u on s.user_id = u.user_id
    join enrollmenttt e on e.student_id = s.student_id
    where s.class_id = @class_id
      and e.course_id = @course_id;
end;
go

-- 44 
create or alter procedure get_class_students_attendance_simple
    @class_id int
as
begin
    select 
        s.student_id,
        s.registration_no,
        u.full_name
    from student s
    join users u on s.user_id = u.user_id
    join student_class1 sc on sc.student_id = s.student_id 
    where sc.class_id = @class_id
    order by s.registration_no;
end
go

-- 45
create or alter procedure insert_attendance
(
    @teacher_id int,
    @course_id int,
    @class_id int,
    @lecture_date date,
    @start_time time,
    @end_time time,
    @lecture_title varchar(100),
    @student_id int,
    @status varchar(10)
)
as
begin
    declare @lecture_id int;

    select @lecture_id = lecture_id
    from attendance_lecture
    where teacher_id=@teacher_id 
      and course_id=@course_id
      and class_id=@class_id
      and lecture_date=@lecture_date
      and lecture_title=@lecture_title;

    if @lecture_id is null 
    begin
        insert into attendance_lecture(teacher_id, class_id, course_id, lecture_date, start_time, end_time, lecture_title)
        values (@teacher_id,@class_id,@course_id,
                @lecture_date,@start_time,@end_time,@lecture_title);

        set @lecture_id = scope_identity();
    end

    insert into student_attendance(lecture_id, student_id, status)
    values (@lecture_id,@student_id,@status);
end
go

-- 46
create or alter procedure coursewise_attendance
    @student_id int
as
begin
    select
        c.course_title,
        count(*) as total_lectures,

        sum(case when sa.status = 'present' then 1 else 0 end) as present_lectures,

        sum(case when sa.status = 'absent' then 1 else 0 end) as absent_lectures,

        cast(
            (sum(case when sa.status = 'present' then 1 else 0 end) * 100.0
             / nullif(count(*), 0))
            as decimal(5,2)
        ) as attendance_percentage,

        case
            when
                (sum(case when sa.status = 'present' then 1 else 0 end) * 100.0
                 / nullif(count(*), 0)) >= 80
            then 'eligible'
            else 'short attendance'
        end as status

    from student_attendance sa
    join attendance_lecture al on sa.lecture_id = al.lecture_id
    join course c on al.course_id = c.course_id
    where sa.student_id = @student_id
    group by c.course_title;
end;
go

-- 47
create or alter procedure calculate_course_gpa
    @student_id int,
    @course_name nvarchar(50),
    @credit_hours int,

    @quiz1 int, @quiz2 int, @quiz3 int, @quiz4 int,     
    @assi1 int, @assi2 int, @assi3 int, @assi4 int,    
    @mid int,                                          
    @final int                                         
as
begin
    set nocount on;
    declare @total_percentage float
    declare @course_gpa float

    set @total_percentage =
        (
            ((@quiz1 + @quiz2 + @quiz3 + @quiz4) / 40.0) * 10
        ) +
        (
            ((@assi1 + @assi2 + @assi4 + @assi4) / 40.0) * 20
        ) +
        (
            ((@mid / 30.0) * 30)
        ) +
        (
            ((@final / 40.0) * 40)
        )

    set @total_percentage = round(@total_percentage, 0)

    if @total_percentage >= 85 set @course_gpa = 4.00
    else if @total_percentage >= 80 set @course_gpa = 3.66
    else if @total_percentage >= 75 set @course_gpa = 3.33
    else if @total_percentage >= 70 set @course_gpa = 3.00
    else if @total_percentage >= 65 set @course_gpa = 2.66
    else if @total_percentage >= 60 set @course_gpa = 2.33
    else if @total_percentage >= 55 set @course_gpa = 2.00
    else if @total_percentage >= 50 set @course_gpa = 1.00
    else set @course_gpa = 0.00

    insert into course_gpa
    (student_id, course_name, credit_hours, total_marks, gpa)
    values
    (@student_id, @course_name, @credit_hours, @total_percentage, @course_gpa)

    select
        @course_name as course,
        @total_percentage as percentage,
        @course_gpa as coursegpa
end
go

-- 48
create or alter procedure calculate_semester_gpa
    @student_id int
as
begin
set nocount on;
    declare @semester_gpa float

    select @semester_gpa =
        sum(quality_points) / nullif(sum(credit_hours), 0) 
    from vw_semester_quality_points
    where student_id = @student_id
    group by student_id; 

    if exists (select 1 from semester_gpa where student_id = @student_id)
        update semester_gpa set semester_gpa = @semester_gpa where student_id = @student_id
    else
        insert into semester_gpa (student_id, semester_gpa) values (@student_id, @semester_gpa)
    
    select
        @semester_gpa as semestergpa
end
go

-- verification queries 
select * from admin;
select * from users;
select * from student;
select * from class_section;
select * from teacher;
select * from teacher_course_assignment;
select * from enrollmenttt;
select * from final_marks;
select * from marks;
select * from student_assignment_submission;
select * from attendance_lecture;
select * from student_attendance;
select * from attendance;
select * from announcement;