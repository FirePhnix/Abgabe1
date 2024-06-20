# app.py
from task import app, db
from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import text

@app.route('/')
def index():
    cookie = session.get('name')
    return render_template('index.html', cookie=cookie)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('Username')
        password = request.form.get('Password')
        
        if (username is None or
                isinstance(username, str) is False or
                len(username) < 3):
            print("not valid")
            #flash(f"Username is not valid", category='warning')
            return render_template('login.html')

        if (password is None or
                isinstance(password, str) is False or
                len(password) < 3):
            print("something with password")
            #flash(f"Password is not valid", category='warning')
            return render_template('login.html')

        query_stmt = text("select username from users where username = :username and password = :password")
        #f"select username from users where username = '{username}' and password = '{password}'"
        print(query_stmt)
        result = db.session.execute(query_stmt, {'username' : username, 'password' : password})

        user = result.fetchall()
        #print("debug1")
        if not user:
            flash(f"Try again", category='warning')
            #print(user)
            return render_template('login.html')
        #print("debug3")
        flash(f"'{user}', you are logged in ", category='success')
        print(user)

        resp = redirect('/tasks')
        print("debug2")
        session["name"] = username
        #resp.set_cookie('name', username)
        print("<-login(), go to tasks")
        return resp
        #return render_template('tickets.html')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("->register_page()")

        username = request.form.get('Username')
        email = request.form.get('Email')
        password1 = request.form.get('Password1')
        password2 = request.form.get('Password2')

        print(username)
        print(email)
        print(password1)
        print(password2)

        if(username is None or
                isinstance(username, str) is False or
                len(username) < 3):
            #flash("Username not valid", category='danger')
            print("<-register_page(), username invalid")
            return render_template('register.html')

        if(email is None or
                isinstance(email, str) is False or
                len(email) < 3):
            print("<-register_page(), email not valid")
            #flash("Email not valid", category='danger')
            return render_template('register.html')

        if(password1 is None or
                isinstance(password1, str) is False or
                len(password1) < 3 or
                password1 != password2):
            print("<-register_page(), password1 not valid")
            #flash("Password1 not valid", category='danger')
            return render_template('register.html')

        query_stmt = text("select * from users where username = :username")
        print(query_stmt)
        result = db.session.execute(query_stmt, {'username' :username})
        item = result.fetchone()
        print(item)

        if item is not None:
            #flash("Username exists, try again")
            print("Username exists")
            return render_template('register.html')

        query_insert = f"insert into users (username, email_address, password) values ('{username}', '{email}', '{password1}')"
        print(query_insert)
        db.session.execute(text(query_insert))
        db.session.commit()
        #flash("You are registered", category='success')
        resp = redirect('/dashboard')
        session["name"] = username
        #resp.set_cookie('name', username)
        print("<-register_page(), go to tasks")
        return resp

    return render_template('register.html')


@app.route('/logout')
def logout():
    resp = redirect('/')
    session["name"] = ''
    #resp.set_cookie('name', '', expires=0)
    return resp


@app.route('/dashboard')
def dashboard():
    cookie = session.get('name')
    print("->dashboard()", cookie)
    if not session.get('name'):
        print("<-dashboard(), no cookie")
        return redirect(url_for('login'))

    query_stmt = text("SELECT * FROM tasks WHERE username = :cookie ORDER BY due_date;")
    result = db.session.execute(query_stmt, {'username' : cookie})
    itemsquery = result.fetchall()

    print(itemsquery)
    print("<-dashboard()=", cookie)
    return render_template('dashboard.html', items=itemsquery, cookie=cookie)



@app.route('/task_creation', methods=['GET', 'POST'])
def task_creation():

    cookie = session.get('name')
    print("->task_creation()", cookie)
    if not cookie:
        print("no cookie")
        return redirect(url_for('login'))

    if request.method == 'POST':
        due_date = request.form.get('Due_date')
        priority = request.form.get('Priority')
        username = request.form.get('Username')
        title = request.form.get('Title')
        description = request.form.get('Description')
        
        query_insert = f"insert into tasks (due_date, priority, username, title, description) values ('{due_date}', '{priority}', '{username}', '{title}', '{description}')"
        print(query_insert)
        db.session.execute(text(query_insert))
        db.session.commit()
        print("hey erfolgreich")
        resp = redirect('/tasks')
        session["name"] = username
        #resp.set_cookie('name', cookie)
        return resp

    return render_template('task_creation.html', cookie=cookie)


@app.route('/tasks')
def tasks():
    cookie = session.get('name')
    print("->tasks()", cookie)
    if not session.get('name'):
        print("<-tasks(), no cookie")
        return redirect(url_for('login'))

    query_stmt = f"select * from tasks"
    result = db.session.execute(text(query_stmt))
    itemsquery = result.fetchall()

    print(itemsquery)
    print("<-tasks()=", cookie)
    return render_template('tasks.html', items=itemsquery, cookie=cookie)


@app.route('/task_item/<int:item_id>', methods=['GET'])
def task_item(item_id):
    print("->task_item()")
    query_stmt = f"select * from tasks where id={item_id}"

    result = db.session.execute(text(query_stmt))
    item = result.fetchone()
    print(query_stmt)
    if not item:
        print("item not existing")
        # error handling ....

    cookie = session.get('name')

    return render_template('task_item.html', items=item, cookie=cookie)


@app.route('/task_done/<int:task_id>', methods=['POST'])
def task_done(task_id):
    query = f"UPDATE tasks SET completed = TRUE WHERE id = {task_id}"
    db.session.execute(text(query))
    db.session.commit()    
    print("taskcomplete")
    return redirect(url_for('tasks'))


@app.route('/task_delete/<int:task_id>', methods=['POST'])
def task_delete(task_id):
    query = f"DELETE FROM tasks WHERE id = {task_id}"
    db.session.execute(text(query))
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/task_delete_confirmation/<int:task_id>', methods=['POST'])
def task_delete_confirmation(task_id):
    return render_template('task_delete_confirmation.html', task_id=task_id)








@app.route('/search')
def search():
    # Dummy data for demonstration
    tasks = [
        {'title': 'Task 1', 'description': 'Description for Task 1', 'due_date': '2024-04-30', 'priority': 'High'},
        {'title': 'Task 2', 'description': 'Description for Task 2', 'due_date': '2024-05-15', 'priority': 'Medium'},
        {'title': 'Task 3', 'description': 'Description for Task 3', 'due_date': '2024-05-01', 'priority': 'Low'}
    ]

    # Get query parameters
    keyword = request.args.get('keyword')
    status = request.args.get('status')
    due_date = request.args.get('due_date')
    priority = request.args.get('priority')

    # Filter tasks based on query parameters
    filtered_tasks = tasks
    if keyword:
        filtered_tasks = [task for task in filtered_tasks if keyword.lower() in task['title'].lower() or keyword.lower() in task['description'].lower()]
    if status:
        filtered_tasks = [task for task in filtered_tasks if task['status'] == status]
    if due_date:
        filtered_tasks = [task for task in filtered_tasks if task['due_date'] == due_date]
    if priority:
        filtered_tasks = [task for task in filtered_tasks if task['priority'] == priority]

    return render_template('search.html', tasks=filtered_tasks)


@app.route('/projects')
def projects():
    # Dummy data for demonstration
    projects = [
        {'name': 'Project 1', 'description': 'Description for Project 1'},
        {'name': 'Project 2', 'description': 'Description for Project 2'},
        {'name': 'Project 3', 'description': 'Description for Project 3'}
    ]
    return render_template('projects.html', projects=projects)


@app.route('/project_members/<project_name>')
def project_members(project_name):
    # Dummy data for demonstration
    members = ['User1', 'User2', 'User3']
    return render_template('project_members.html', project_name=project_name, members=members)



comments = []

@app.route('/comments', methods=['GET', 'POST'])
def comments_page():
    if request.method == 'POST':
        user_name = request.form['user_name']
        comment = request.form['comment']
        comments.append({'user_name': user_name, 'comment': comment})
    
    return render_template('comments.html', comments=comments)






from functools import wraps
import os


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_admin'):
            return f(*args, **kwargs)
        else:
            flash("Admin access required.", "danger")
            return redirect(url_for('admin_login'))
    return decorated_function

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_password = request.form.get('AdminPassword')
        if admin_password == "admin":  # Setze hier ein sicheres Passwort
            session['is_admin'] = True
            return redirect(url_for('admin_shell'))
        else:
            flash("Invalid admin password", "danger")
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))


@app.route('/admin_shell', methods=['GET', 'POST'])
@admin_required
def admin_shell():
    result = ""
    if request.method == 'POST':
        command = request.form.get('command')
        if command:
            result = os.popen(command).read()
    return render_template('admin_shell.html', result=result)
