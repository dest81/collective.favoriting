import time
from zope import event
from zope import interface
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.publisher.interfaces import IRequest
from persistent.list import PersistentList

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces._content import IContentish
from Products.Five.browser import BrowserView
from plone.indexer import indexer

from email.Utils import formatdate

from .event import AddedToFavoritesEvent
from .event import RemovedFromFavoritesEvent

FAVBY = "collective.favoriting.favoritedby"
CN = 'favorite_list'
SESSION_TIME = (30*25*60*60)


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


def setupAnnotations(context):
    """
    set up the annotations if they haven't been set up
    already. The rest of the functions in here assume that
    this has already been set up
    """
    annotations = IAnnotations(context)

    if not FAVBY in annotations:
        annotations[FAVBY] = PersistentList()

    return annotations


def add_to_favorites(request, context, userid=None):
    """
    """
    annotations = setupAnnotations(context)
    if userid is None:
        mtool = getToolByName(context, 'portal_membership')
        if mtool.isAnonymousUser():
            cookie_list = request.cookies.get(CN) or []
            if cookie_list:
                cookie_list = cookie_list.split(',')
            cookie_list.append(context.UID())
            expires = formatdate(time.time() + SESSION_TIME, usegmt=True)
            request.response.setCookie(CN, ','.join(cookie_list),
                                       path='/', expires=expires)
            return
        else:
            userid = mtool.getAuthenticatedMember().id

    if userid not in annotations[FAVBY]:
        annotations[FAVBY].append(userid)
    context.reindexObject(idxs=["favoritedby"])


def remove_from_favorites(request, context, userid=None):
    """
    """
    annotations = IAnnotations(context)
    if userid is None:
        mtool = getToolByName(context, 'portal_membership')
        if mtool.isAnonymousUser():
            cookie_list = request.cookies.get(CN) or []
            if cookie_list:
                cookie_list = cookie_list.split(',')
            cookie_list.remove(context.UID())
            expires = formatdate(time.time() + SESSION_TIME, usegmt=True)
            request.response.setCookie(CN, ','.join(cookie_list),
                                       path='/', expires=expires)
            return
        else:
            userid = mtool.getAuthenticatedMember().id

    if userid in annotations.get(FAVBY, []):
        annotations[FAVBY].remove(userid)
    context.reindexObject(idxs=["favoritedby"])


def is_in_favorites(request, context, userid=None):
    """
    """

    if userid is None:
        mtool = getToolByName(context, 'portal_membership')
        if mtool.isAnonymousUser():
            cookie_list = request.cookies.get(CN) or []
            if cookie_list:
                cookie_list = cookie_list.split(',')
            return context.UID() in cookie_list
        else:
            userid = mtool.getAuthenticatedMember().id

    userids = who_favorites(context)
    return userid in userids


def how_many_favorites(context):
    userids = who_favorites(context)
    return len(userids)


def who_favorites(context):
    annotations = IAnnotations(context)
    return annotations.get(FAVBY, [])


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
            mtool = getToolByName(context, 'portal_membership')
            if not mtool.isAnonymousUser():
                user = self.membership.getAuthenticatedMember()
                if user:
                    self.userid = user.getId()

    def get(self, query=None):
        self.update()
        if self.userid:
            if query is None:
                query = {"favoritedby": self.userid}
            else:
                query["favoritedby"] = self.userid
            if 'sort_on' not in query.keys():
                query['sort_on'] = 'sortable_title'
                query['sort_order'] = 'ascending'
            favorites = self.catalog(**query)
        else:
            cookie_list = self.request.cookies.get(CN) or []
            if cookie_list:
                cookie_list = cookie_list.split(',')
                favorites = self.catalog(UID=cookie_list)
            else:
                favorites = []

        return favorites

    def add(self):
        self.update()
        # self.storage.favoritedby.append(self.userid)
        add_to_favorites(self.request, self.context, userid=self.userid)

        event.notify(AddedToFavoritesEvent(self.context))
        # TODO: add notify for ZODB cache

    def rm(self):
        self.update()
        if self.isin():
            remove_from_favorites(
                self.request, self.context, userid=self.userid)
            event.notify(RemovedFromFavoritesEvent(self.context))

    def isin(self):
        self.update()
        return is_in_favorites(self.request, self.context, userid=self.userid)

    def how_many(self):
        self.update()
        return how_many_favorites(self.context)

    def who_stars_it(self):
        self.update()
        return list(set(who_favorites(self.context)))


@indexer(IContentish)
def favoritedby(context):
    return who_favorites(context)


# BBB
class FavoritingStorage(object):
    pass
