from flask import current_appfrom application import loggerfrom application.utils.contextor import ensure_app_context@ensure_app_contextdef get_config(name):    return current_app.config.get(name, None)@ensure_app_contextdef set_config(name, value):    current_app.config[name] = value@ensure_app_contextdef get_logger():    return logger