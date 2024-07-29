import json
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import *
from app.forms import *
from flask import current_app as app
from datetime import datetime


@app.route('/')
@login_required
def index():
    #Dados para graficos 

    ranking_persons = db.session.query(Person.nome, db.func.count(Borrow.id)).join(Borrow).group_by(Person.id).order_by(db.func.count(Borrow.id).desc()).all()
    ranking_books = db.session.query(Book.title, db.func.count(Borrow.id)).join(Borrow).group_by(Book.id).order_by(db.func.count(Borrow.id).desc()).all()
    book_genres = db.session.query(Book.genero, db.func.count(Book.id)).group_by(Book.genero).all()
    available_books = db.session.query(Book).filter_by(available=True).count()
    unavailable_books = db.session.query(Book).filter_by(available=False).count()
    
    ranking_persons_data = {
        'labels': [person[0] for person in ranking_persons],
        'data': [person[1] for person in ranking_persons]
    }

    ranking_books_data = {
        'labels': [book[0] for book in ranking_books],
        'data': [book[1] for book in ranking_books]
    }

    book_genres_data = {
        'labels': [genre[0] for genre in book_genres],
        'data': [genre[1] for genre in book_genres]
    }
    
    return render_template(
        "index.html",
        ranking_persons_data = json.dumps(ranking_persons_data),
        ranking_books_data = json.dumps(ranking_books_data),
        book_genres_data  = json.dumps(book_genres_data),
        available_books = available_books,
        unavailable_books=unavailable_books
    )

@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        print("Fomulario valido")
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            print("usuario invalido")
            flash("Nome de usuário ou senha incorretos")
            return redirect(url_for("login"))
        
        login_user(user, remember=form.remember_me.data)
        print("Login Efetuado")
        user.last_login = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("index"))
           
    return render_template(
        "login.html",
        form = form
    )

@app.route("/logout", methods=['GET','POST'])
def logout():
    logout_user()
    return redirect(url_for("login"))
   
@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        print("Fomulario valido")
        user = User(
            username=form.username.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()
        flash("Parabens, você se registrou com sucesso!")
        print("Usaurio criado")
        return redirect(url_for("index"))
        
    return render_template(
        "register.html",
        form = form
    )
    
@app.route("/books", methods=["GET","POST"])
@login_required
def manage_books():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title = form.title.data,
            author = form.author.data,
            genero = form.genero.data,
            available = form.available.data,
            created_by = current_user.id,
            updated_by = current_user.id,
        )
        db.session.add(book)
        db.session.commit()
        
        return redirect(url_for('manage_books'))
        
    books = Book.query.all()
    return render_template(
        "books.html",
        form = form,
        books = books
    )
    
@app.route("/books/delete/<int:book_id>", methods=["GET","POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Remover todas as referencias nas outras tabelas 
    Borrow.query.filter_by(book_id=book_id).delete()
    Historico.query.filter_by(book_id=book_id).delete()
    
    #Deletar no meu banco de dados
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("manage_books"))


@app.route("/books/update/<int:book_id>", methods=["GET","POST"])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = BookForm(obj=book)
    
    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.genero = form.genero.data
        book.available = form.available.data
        book.updated_by = current_user.id
        db.session.commit()
        
        return redirect(url_for("manage_books"))
    
    return render_template(
        "book_form.html",
        form=form
    )
    
@app.route("/persons", methods=["GET","POST"])
@login_required
def manage_persons():
    form = PersonForm()
    if form.validate_on_submit():
        person = Person(
            nome=form.nome.data,
            sobrenome=form.sobrenome.data,
            email=form.email.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(person)
        db.session.commit()
        
        return redirect(url_for('manage_persons'))
        
    persons = Person.query.all()
    return render_template(
        "persons.html",
        form = form,
        persons = persons
    )
    
@app.route("/persons/update/<int:person_id>", methods=["GET","POST"])
@login_required
def update_person(person_id):
    person = Person.query.get_or_404(person_id)
    form = PersonForm(obj=person)
    
    if form.validate_on_submit():
        person.nome = form.nome.data
        person.sobrenome = form.sobrenome.data
        person.email = form.email.data
        person.updated_by = current_user.id
        db.session.commit()
        
        return redirect(url_for("manage_persons"))
    
    return render_template(
        "person_form.html",
        form=form
    )
    
@app.route("/persons/delete/<int:person_id>", methods=["GET","POST"])
@login_required
def delete_person(person_id):
    person = Person.query.get_or_404(person_id)
    
    # Remover todas as referencias nas outras tabelas 
    Borrow.query.filter_by(person_id=person_id).delete()
    Historico.query.filter_by(person_id=person_id).delete()
    
    #Deletar no meu banco de dados
    db.session.delete(person)
    db.session.commit()
    return redirect(url_for("manage_persons"))

@app.route("/borrow", methods=["GET","POST"])
@login_required
def borrow_book():
    form = BorrowForm()

    form.book_id.choices = [(book.id, book.title) for book in Book.query.filter_by(available=True).all()]
    form.person_id.choices = [(person.id, f"{person.nome} {person.sobrenome}") for person in Person.query.all()]
    
    if form.validate_on_submit():
        borrow = Borrow(
            book_id=form.book_id.data,
            person_id=form.person_id.data,
            created_by=current_user.id,
            updated_by=current_user.id 
        )
        book = Book.query.get(form.book_id.data)
        book.available = False
        
        db.session.add(borrow)
        db.session.commit()
        
        #Salvar no historico 
        historico = Historico(
            book_id = form.book_id.data,
            person_id=form.person_id.data,
            borrow_date=datetime.utcnow()
        )
        db.session.add(historico)
        db.session.commit()
        return redirect(url_for("borrow_book"))
         
    return render_template(
        "borrow_form.html",
        form=form
    )

@app.route("/historico")
@login_required
def view_historico():
    historico = Historico.query.order_by(Historico.borrow_date.desc()).all()
    
    return render_template(
        "historico.html",
        historico = historico
    )