from flask import render_template,request,jsonify
from Flasklearning.flaskyy.app.main import main


@main.app_errorhandler(404)
def page_not_found(e):
    '''检 查 Accept 请 求 首 部(Werkzeug 将 其 解 码 为 request.accept_
mimetypes )
,根据首部的值决定客户端期望接收的响应格式。浏览器一般不限制响应的格
式,所以只为接受 JSON 格式而不接受 HTML 格式的客户端生成 JSON 格式响应'''
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response=jsonify({'error':'not found'})
        response.status_code=404
        return response
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e):

    return render_template('500.html'), 500