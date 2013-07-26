from zope.component.interfaces import ObjectEvent
from zope.component.interfaces import IObjectEvent
from zope import interface


class IAddedToFavoritesEvent(IObjectEvent):
    pass


class AddedToFavoritesEvent(ObjectEvent):
    interface.implements(IAddedToFavoritesEvent)


class IRemovedFromFavoritesEvent(IObjectEvent):
    pass


class RemovedFromFavoritesEvent(ObjectEvent):
    interface.implements(IRemovedFromFavoritesEvent)
