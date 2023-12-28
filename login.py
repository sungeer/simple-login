from functools import wraps

from flask import g, session, redirect, url_for


def login_required(func):
    @wraps(func)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapped_view


# 在插件处 初始化
@login.user_loader
def load_user(user_id):
    from event.models import AuthModel
    user = AuthModel().get_userinfo_by_id(int(user_id))
    return user


class Login:

    def __init__(self, app=None):
        self.user_loader_callback = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.extensions['login'] = self
        app.before_request(self.load_logged_in_user)
        app.context_processor(self.inject_current_user)

    def user_loader(self, callback):
        self.user_loader_callback = user_loader_callback
        return callback

    def reload_user(self, user_id):
        if self.user_loader_callback:
            return self.user_loader_callback(user_id)

    def load_logged_in_user(self):
        user_id = session.get('user_id')
        if not user_id:
            g.user = None
        else:
            g.user = self.reload_user(user_id)

    @staticmethod
    def inject_current_user():
        return dict(current_user=g.get('user', None))
