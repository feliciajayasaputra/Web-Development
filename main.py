from flask import Flask, request, render_template, redirect

from src.model.todo import Todo, db

app = Flask(__name__, static_url_path='', static_folder='static')

with db:
    db.create_tables([Todo])

@app.before_request
def _db_connect():
    db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()

@app.route('/')
def index():
    return redirect("/todos")

@app.get('/todos')
def all_todos():
    view = request.args.get('view', None)
    search = request.args.get('q', None)
    todos = Todo.all(view, search)
    return render_template("index.html", todos=todos, view=view, search=search)

@app.post('/todos')
def create_todo():
    view = request.form.get('view', None)
    todo = Todo(text=request.form['todo'], complete=False)
    todo.save()
    return redirect("/todos" + add_view_context(view))

@app.post('/todos/<id>/toggle')
def toggle_todo(id):
    view = request.form.get('view', None)
    todo = Todo.find(int(id))
    todo.toggle_completed()
    todo.save()
    return redirect("/todos" + add_view_context(view))

@app.get('/todos/<id>/edit')
def edit_todo(id):
    view = request.args.get('view', None)
    todos = Todo.all(view)
    return render_template("index.html", todos=todos, editing=int(id), view=view)

@app.post('/todos/<id>')
def update_todo(id):
    view = request.form.get('view', None)
    todo = Todo.find(int(id))
    todo.text = request.form['todo']
    todo.save()
    return redirect("/todos" + add_view_context(view))

@app.get('/todos/reorder')
def show_reorder_ui():
    view = request.args.get('view', None)
    todos = Todo.all(view)
    return render_template("reorder.html", todos=todos)


@app.post('/todos/reorder')
def update_todo_order():
    id_list = request.form.getlist("ids")
    Todo.reorder(id_list)
    return redirect("/todos")


def add_view_context(view):
    return (("?view=" + view) if view is not None else"")


if __name__ == '__main__':
    app.run(port=12346)
