from datetime import datetime
from flask import render_template,session,redirect,url_for,abort
from Flasklearning.flaskyy.app.main import main
from .forms import NameForm
from Flasklearning.flaskyy.app import db,models


@main.route('/',methods=['GET', 'POST'])
def index():
    form=NameForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.name.data).first()
        old_name = session.get('name')
        if user is None:
            user = models.User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        #蓝本中可以省略蓝本名,例如 url_for('.
        #index') 。在这种写法中,命名空间是当前请求所在的蓝本
        return redirect(url_for('.index'))
    return render_template('index.html', name=session.get('name'), form=form, known=session.get('known', False))


@main.route('/user/<username>')
def user(username):
    user=models.User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    else:
        return render_template('user.html',user=user)