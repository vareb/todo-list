from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    order = db.Column(db.Integer, default=0) 
    


@app.route('/')
def index():
    todo_list = Todo.query.order_by(Todo.order).all() # returns list of all todos
    print(todo_list)
    return render_template('base.html', todo_list=todo_list)


@app.route("/add", methods=["POST"])
def add():
    # adds new todo
    title = request.form.get("title")
    max_order_todo = Todo.query.order_by(Todo.order.desc()).first()
    if max_order_todo:
        new_order = max_order_todo.order + 1
    else:
        new_order = 0
    new_todo = Todo(title=title, complete=False, order=new_order)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/update/<int:todo_id>")
def update(todo_id):
    # updates
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    # deletes a todo
    todo = Todo.query.filter_by(id=todo_id).first()
    deleted_order = todo.order
    db.session.delete(todo)
    db.session.commit()

    todos_to_update = Todo.query.filter(Todo.order >  deleted_order).all()
    for todo in todos_to_update:
        todo.order -= 1
        db.session.commit()

    
    return redirect(url_for("index"))

@app.route("/moveup/<int:todo_id>")
def moveup(todo_id):
    todo = Todo.query.get(todo_id)
    todoabove = Todo.query.filter(Todo.order == todo.order - 1).first()
    if todoabove: #shouldnt change order if todo above doesnt exist
        todo.order, todoabove.order = todoabove.order, todo.order
        db.session.commit()
    
    return redirect(url_for("index"))


@app.route("/movedown/<int:todo_id>")
def movedown(todo_id):
    todo = Todo.query.get(todo_id)
    todobelow = Todo.query.filter(Todo.order == todo.order + 1).first()
    if todobelow: #shouldnt change order if below todo doesnt exist
        todo.order, todobelow.order = todobelow.order, todo.order
        db.session.commit()
    
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    

    app.run(debug=True)