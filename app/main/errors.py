from . import main

from flask import render_template

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@main.app_errorhandler(401)
def not_authenticated(e):
    return render_template("401.html"),401

@main.app_errorhandler(403)
def permission_deny(e):
    return render_template("403.html"),401

@main.app_errorhandler(500)
def server_error(e):
    return render_template("500.html"),500
    