from zope import component
from zope import event
from zope import interface
from zope import schema
from zope.annotation import factory
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces import IRequest
from Products.CMFCore.interfaces._content import IContentish
from plone.indexer import indexer
from zope.annotation.interfaces import IAttributeAnnotatable

from .event import AddedToFavoritesEvent
from .event import RemovedFromFavoritesEvent


class IFavoritingManager(interface.Interface):
    """The main component API"""

    context = schema.Object(title=u"Context", schema=IContentish)
    request = schema.Object(title=u"Request", schema=IRequest)

    def get(query=None):
        """Return the list of all content favorited by the current user.
        'query' is an optional dict that will be passed to the catalog search
        """

    def add():
        """add the current context to the favorites of the current user"""

    def rm():
        """Remove the current context from the favorites."""

    def isin():
        """Return True if the current context is in the favorites of the
        current user"""

    def how_many():
        """return the number of stars for this item"""

    def who_stars_it():
        """return the list of userid who stars this item"""


class IFavoritingStorage(interface.Interface):
    """a list of all user who have favoriting this object"""
    favoritedby = schema.List(
        title=u"Favorited by",
        value_type=schema.TextLine(title=u"User ID")
    )


class FavoritingStorage(object):
    interface.implements(IFavoritingStorage)
    component.adapts(IAttributeAnnotatable)

    def __init__(self):
        """
        Note that the annotation implementation does not expect any arguments
        to its `__init__`. Otherwise it's basically an adapter.
        """
        self.favoritedby = []


FavoritingStorageFactory = factory(FavoritingStorage)


class FavoritingManager(BrowserView):
    """implementation of IFavoriting using annotation + portal_catalog"""
    interface.implements(IFavoritingManager)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.userid = None
        self.membership = None
        self.catalog = None
        self.favorites = []
        self.storage = None

    def __call__(self):
        self.update()
        # return self to support the following syntax:
        # tal:define="favoriting context/@@collective.favoriting"
        return self

    def update(self):
        context = self.context
        if self.catalog is None:
            self.catalog = getToolByName(context, 'portal_catalog')
        if self.membership is None:
            self.membership = getToolByName(context, 'portal_membership')
        if self.userid is None:
            user = self.membership.getAuthenticatedMember()
            if user:
                self.userid = user.getId()
        if self.storage is None:
            try:
                self.storage = IFavoritingStorage(self.context)
            except:
                pass

    def get(self, query=None):
        self.update()
        if query is None:
            query = {"favoritedby": self.userid}
        else:
            query["favoritedby"] = self.userid
        favorites = self.catalog(**query)
        return favorites

    def add(self):
        self.update()
        self.storage.favoritedby.append(self.userid)
        self.context.reindexObject(idxs=["favoritedby"])
        event.notify(AddedToFavoritesEvent(self.context))
        #TODO: add notify for ZODB cache

    def rm(self):
        self.update()
        if self.isin():
            self.storage.favoritedby.remove(self.userid)
            self.context.reindexObject(idxs=["favoritedby"])
            event.notify(RemovedFromFavoritesEvent(self.context))

    def isin(self):
        self.update()
        return self.userid in self.storage.favoritedby

    def how_many(self):
        self.update()
        return len(self.storage.favoritedby)

    def who_stars_it():
        self.update()
        return list(set(self.storage.favoritedby))


@indexer(IContentish)
def favoritedby(context):
    storage = component.queryAdapter(context, IFavoritingStorage, default=None)
    if storage:
        return storage.favoritedby
