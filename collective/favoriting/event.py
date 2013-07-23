from zope.component.interfaces import ObjectEvent
from zope import interface


class IFavoritedEvent(interface.Interface):
    pass


class FavoritedEvent(ObjectEvent):
    interface.implements(IFavoritedEvent)


class IUnfavoritedEvent(interface.Interface):
    pass


class UnfavoritedEvent(ObjectEvent):
    interface.implements(IUnfavoritedEvent)
