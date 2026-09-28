from datetime import datetime, timezone

from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = StringField('What is your UofT Email address?',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        session['email'] = form.email.data
        if 'utoronto' in form.email.data:
            return redirect(url_for('chatbot'))
        return redirect(url_for('index'))

    email = session.get('email')
    is_uoft = email is not None and 'utoronto' in email
    return render_template('index.html',
                           form=form,
                           name=session.get('name'),
                           email=email,
                           is_uoft=is_uoft,
                           current_time=datetime.now(timezone.utc))

@app.route('/chatbot')
def chatbot():
    email = session.get('email')
    if not email or 'utoronto' not in email:
        return redirect(url_for('index'))
    return render_template('chat.html')


@app.route('/chat', methods=['POST'])
def chat():
    message = request.json['message']
    lower = message.lower()

    if 'my name is' in lower:
        start = lower.index('my name is') + len('my name is')
        name = message[start:].strip().rstrip('.!?')
        session['chat_name'] = name
        reply = f'Nice to meet you, {name}!'
    elif 'what is my name' in lower:
        name = session.get('chat_name')
        if name:
            reply = f'Your name is {name}.'
        else:
            reply = "I don't know your name yet."
    elif 'hello' in lower:
        reply = 'Hello!'
    else:
        reply = "I don't understand."

    return {'reply': reply}


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


if __name__ == '__main__':
    app.run(debug=True)