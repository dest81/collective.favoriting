from plone.app.contentrules.handlers import execute


def favorited(event):
    obj = event.object
    execute(obj, event)


def unfavorited(event):
    obj = event.object
    execute(obj, event)
