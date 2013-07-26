from plone.app.contentrules.handlers import execute


def addedToFavorites(event):
    obj = event.object
    execute(obj, event)


def removedFromFavorites(event):
    obj = event.object
    execute(obj, event)
