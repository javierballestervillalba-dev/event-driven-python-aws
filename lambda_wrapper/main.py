from app.main import handler as app_handler

def handler(event, context):
    return app_handler(event, context)
