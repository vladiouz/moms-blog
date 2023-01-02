from flask import Flask, render_template, redirect, request, url_for, abort, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_ckeditor import CKEditor
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from flask_mail import Mail, Message
from time import time
import os
import jwt


app = Flask(__name__)
app.config['SECRET_KEY'] = 'whatever'
app.config['CKEDITOR_PKG_TYPE'] = 'full'
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME="vladtestudemy@gmail.com",
    MAIL_PASSWORD="chzbuqetvlijzdmf"
)

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)

months = ['ianuarie', 'februarie', 'martie', 'aprilie', 'mai', 'iunie', 'iulie', 'august', 'septembrie', 'octombrie',
          'noiembrie', 'decembrie']


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50))
    comments = relationship('Comment', back_populates='comment_author')
    scores = relationship('Score', back_populates='user')


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    category = db.Column(db.String(50))
    subtitle = db.Column(db.String(250))
    content = db.Column(db.Text)
    date = db.Column(db.String(30))
    comments = relationship('Comment', back_populates='post')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))
    date = db.Column(db.String(30))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_author = relationship('User', back_populates='comments')
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    post = relationship('Post', back_populates='comments')


class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    ans_correct = db.Column(db.Integer)
    score_percent = db.Column(db.Integer)
    solver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = relationship('User', back_populates='scores')
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))
    test = relationship('Test', back_populates='scores')


class Test(db.Model):
    __tablename__ = 'tests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    category = db.Column(db.String(50))
    level = db.Column(db.String(50))
    scores = relationship('Score', back_populates='test')
    questions = relationship('Question', back_populates='test')


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    v1 = db.Column(db.Text)
    v2 = db.Column(db.Text)
    v3 = db.Column(db.Text)
    v4 = db.Column(db.Text)
    right_v = db.Column(db.Integer)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'))
    test = relationship('Test', back_populates='questions')


class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)


db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if int(current_user.id) != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


def send_email(user):
    token = jwt.encode({'reset_password': user.username,
                        'exp': time() + 2000}, key='whatever')
    msg = Message()
    msg.subject = "Resetare parola Brand"
    msg.sender = 'vladtestudemy@gmail.com'
    msg.recipients = [user.email]
    msg.html = render_template('reset_email.html', user=user, token=token)

    mail.send(msg)


def verify_reset_token(token):
    try:
        username = jwt.decode(token, key='whatever')['reset_password']
    except Exception as e:
        print(e)
        return
    return User.query.filter_by(username=username).first()


@app.route('/')
def home():
    recent_posts = Post.query.all()[-3:]
    return render_template('index.html', posts=recent_posts, year=datetime.now().year)


@app.route('/postari/<categ>')
def posts(categ):
    if categ == 'toate':
        all_posts = Post.query.all()
        return render_template('posts.html', posts=all_posts, year=datetime.now().year)
    all_posts = Post.query.filter_by(category=categ)
    if not all_posts.count():
        return "ups!!! Nu exista o categorie cu acest nume"
    return render_template('posts.html', posts=all_posts, year=datetime.now().year)


@app.route('/delete/post/<post_title>')
@login_required
@admin_only
def delete_post(post_title):
    current_post = Post.query.filter_by(title=post_title).first()
    for comment in current_post.comments:
        db.session.delete(comment)
        db.session.commit()
    db.session.delete(current_post)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/postare/<title>', methods=['GET', 'POST'])
def post(title):
    current_post = Post.query.filter_by(title=title).first()
    if request.method == 'POST':
        if request.form['text']:
            month_index = int(datetime.now().strftime('%m'))
            month = months[month_index - 1]

            new_comm = Comment(
                text=request.form['text'],
                date=datetime.now().strftime(f'%d {month} %Y'),
                post_id=current_post.id,
                author_id=current_user.id
            )
            db.session.add(new_comm)
            db.session.commit()
            flash('Comentariu adaugat cu succes!')
            return redirect(url_for('post', title=current_post.title))
        flash('Nu poti adauga un comentraiu gol!')
    return render_template('post.html', post=current_post)


@app.route('/delete/comment/<comm_id>')
@login_required
@admin_only
def delete_comment(comm_id):
    current_comment = Comment.query.filter_by(id=comm_id).first()
    db.session.delete(current_comment)
    db.session.commit()
    return redirect(url_for('posts', categ='toate'))


@app.route('/intrebari', methods=['GET', 'POST'])
@login_required
def inquiries():
    if request.method == 'POST':
        if request.form['text']:
            new_inquiry = Inquiry(
                text=request.form['text']
            )
            db.session.add(new_inquiry)
            db.session.commit()
            flash('Intrebare adaugata!')
        else:
            flash('Nu poti adauga o intrebare fara text!')
    return render_template('inquiries.html', year=datetime.now().year)


@app.route('/delete/inquiry/<inq_id>')
@login_required
@admin_only
def delete_inquiry(inq_id):
    current_inquiry = Inquiry.query.filter_by(id=inq_id).first()
    db.session.delete(current_inquiry)
    db.session.commit()
    return redirect(url_for('my_acc'))


@app.route('/teste/<categ>')
def tests(categ):
    if categ == 'toate':
        return render_template('tests.html', tests=Test.query.all(), year=datetime.now().year)
    return render_template('tests.html', tests=Test.query.filter_by(category=categ), year=datetime.now().year)


@app.route('/delete/test/<test_title>')
@login_required
@admin_only
def delete_test(test_title):
    current_test = Test.query.filter_by(title=test_title).first()
    for score in current_test.scores:
        db.session.delete(score)
        db.session.commit()
    for question in current_test.questions:
        db.session.delete(question)
        db.session.commit()
    db.session.delete(current_test)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/test/<test_title>', methods=['GET', 'POST'])
@login_required
def test(test_title):
    current_test = Test.query.filter_by(title=test_title).first()
    if request.method == 'POST':
        correct_ans = 0
        for question in current_test.questions:
            answer = request.form['q' + str(question.id)]
            if int(answer) == question.right_v:
                correct_ans += 1
        score = Score.query.filter_by(solver_id=current_user.id, test_id=current_test.id).first()
        if score:
            if correct_ans > score.ans_correct:
                score.ans_correct = correct_ans
                score.score_percent = correct_ans/(len(current_test.questions))*100
                db.session.commit()
        else:
            new_score = Score(
                ans_correct=correct_ans,
                score_percent=correct_ans/(len(current_test.questions))*100,
                solver_id=current_user.id,
                test_id=current_test.id
            )
            db.session.add(new_score)
            db.session.commit()
        return render_template('test-result.html', test=current_test, no_of_q=len(current_test.questions),
                               correct_ans=correct_ans, year=datetime.now().year)
    return render_template('test.html', test=current_test, year=datetime.now().year)


@app.route('/contulmeu')
@login_required
def my_acc():
    if current_user.id == 1:
        return render_template('account.html', year=datetime.now().year, account=current_user,
                               inquiries=Inquiry.query.all())
    return render_template('account.html', year=datetime.now().year, account=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = User.query.filter_by(username=request.form['username']).first()
        email = User.query.filter_by(email=request.form['email']).first()
        password = request.form['password']
        if username:
            flash('Nume de utilizator deja folosit de alt cont!')
        elif email:
            flash('E-mail deja folosit de alt cont!')
        elif len(password) < 8:
            flash('Parola trebuie sa aiba minim 8 caractere!')
        else:
            new_acc = User(
                username=request.form['username'],
                email=request.form['email'],
                password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            )
            db.session.add(new_acc)
            db.session.commit()
            login_user(new_acc)
            return redirect(url_for('my_acc'))
    return render_template('register.html', year=datetime.now().year)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            if check_password_hash(user.password, request.form['password']):
                login_user(user)
                return redirect(url_for('my_acc'))
            else:
                flash('Parola gresita!')
        else:
            flash('Nu exista niciun utilizator cu acest e-mail!')
    return render_template('login.html', year=datetime.now().year)


@app.route('/make-post', methods=['GET', 'POST'])
@login_required
@admin_only
def make_post():
    if request.method == 'POST':
        month_index = int(datetime.now().strftime('%m'))
        month = months[month_index - 1]

        new_post = Post(
            title=request.form['title'],
            category=request.form['category'],
            subtitle=request.form['subtitle'],
            content=request.form['ckeditor'],
            date=datetime.now().strftime(f'%d {month} %Y')
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('posts', categ='toate'))
    return render_template('make-post.html', year=datetime.now().year)


@app.route('/edit-post/<post_title>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_post(post_title):
    current_post = Post.query.filter_by(title=post_title).first()
    if request.method == 'POST':
        current_post.title = request.form['title']
        current_post.category = request.form['category']
        current_post.subtitle = request.form['subtitle']
        current_post.content = request.form['ckeditor']
        db.session.commit()
        return redirect(url_for('posts'))
    return render_template('edit-post.html', post=current_post, year=datetime.now().year)


@app.route('/create-test', methods=['GET', 'POST'])
@login_required
@admin_only
def create_test():
    if request.method == 'POST':
        new_test = Test(
            title=request.form['title'],
            category=request.form['category'],
            level=request.form['level']
        )
        db.session.add(new_test)
        db.session.commit()
        return redirect(url_for('create_question'))
    return render_template('create-test.html', year=datetime.now().year)


@app.route('/create-q', methods=['GET', 'POST'])
@login_required
@admin_only
def create_question():
    if request.method == 'POST':
        current_test = Test.query.filter_by(title=request.form['test-title']).first()
        new_question = Question(
            test_id=current_test.id,
            text=request.form['text'],
            v1=request.form['v1'],
            v2=request.form['v2'],
            v3=request.form['v3'],
            v4=request.form['v4'],
            right_v=request.form['right_v']
        )
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for('create_question'))
    return render_template('create-question.html', year=datetime.now().year)


@app.route('/edit-q/<q_id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_q(q_id):
    current_q = Question.query.filter_by(id=q_id).first()
    if request.method == 'POST':
        current_q.text = request.form['text']
        current_q.v1 = request.form['v1']
        current_q.v2 = request.form['v2']
        current_q.v3 = request.form['v3']
        current_q.v4 = request.form['v4']
        current_q.right_v = request.form['right_v']
        db.session.commit()
        return redirect(url_for('test', test_title=current_q.test.title))
    return render_template('edit-question.html', question=current_q, year=datetime.now().year)


@app.route('/am-uitat-parola', methods=['GET', 'POST'])
def forgot_pass():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            flash('a fost trimis un e-mail la adresa data')
            send_email(user)
        else:
            flash('nu exista niciun cont cu acest e-mail')
    return render_template("forgot-password.html", year=datetime.now().year)


@app.route('/schimba-parola/<user_id>/<token>', methods=['GET', 'POST'])
def change_password(user_id, token):
    user = User.query.filter_by(id=user_id).first()
    if request.method == 'POST':
        if request.form['password'] != request.form['cpassword']:
            flash('Parolele nu corespund!')
        elif len(request.form['password']) < 8:
            flash('Parola trebuie sa aiba minim 8 caractere!')
        else:
            flash('Parola a fost modificata cu succes!')
            user.password = generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8)
            db.session.commit()
            login_user(user)
            return redirect(url_for('my_acc'))
    return render_template('reset-password.html', user=user, token=token, year=datetime.now().year)


if __name__ == '__main__':
    app.run(debug=True)
