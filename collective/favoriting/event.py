from zope.component.interfaces import ObjectEvent
from zope.component.interfaces import IObjectEvent
from zope import interface


class IFavoritedEvent(IObjectEvent):
    pass


class FavoritedEvent(ObjectEvent):
    interface.implements(IFavoritedEvent)


class IUnfavoritedEvent(IObjectEvent):
    pass


class UnfavoritedEvent(ObjectEvent):
    interface.implements(IUnfavoritedEvent)
