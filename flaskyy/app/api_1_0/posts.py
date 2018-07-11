from flask import jsonify,request,g,url_for,current_app
from flask_login import login_required
from Flasklearning.flaskyy.app import db
from Flasklearning.flaskyy.app.models import Post,Permission
from Flasklearning.flaskyy.app.api_1_0 import api
from Flasklearning.flaskyy.app.auth import auth
from .decorators import permission_requied
from .errors import forbiden


@api.route('/posts')
@login_required
def get_posts():
    page=request.args.get('page',1,type=int)
    pagination=Post.query.paginate(
        page,per_page=15,error_out=False
    )
    posts=pagination.items
    prev=None
    next=None
    if pagination.has_prev:
        prev=url_for('api.get_posts',page=page-1,_external=True)
    if pagination.has_next:
        next=url_for('api.get_posts',page=page+1,_external=True)
    return jsonify(
        {
            'posts':[post.to_json() for post in posts],
            'prev':prev,
            'next':next,
            'count':pagination.total
        }
    )


@api.route('/posts/<int:id>')
def get_post(id):
    post=Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/',methods=['POST'])
@permission_requied(Permission.WRITE_ARTICLES)
def new_post():
    post=Post.from_json(request.json)
    post.author=g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()),201,{'Location':url_for('api.get_post',id=post.id,_external=True)}

@api.route('/posts/<int:id>',methods=['PUT'])
@permission_requied(Permission.WRITE_ARTICLES)
def edit_post(id):
    post=Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMINISTER):
        return forbiden('Insufficient permissions')
    post.body=request.json.get('body',post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())



