from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.i18nmessageid.message import MessageFactory
_ = MessageFactory("collective.favoriting")
VIEW_NAME = "@@collective.favoriting"


class Add(BrowserView):
    """Add to favorite"""

    def __call__(self):
        manager = self.context.restrictedTraverse(VIEW_NAME)
        if not manager.isin():
            manager.add()
            status = IStatusMessage(self.request)
            status.add(_(u"Added to favorite"))
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        referer = self.request.get("HTTP_REFERER")
        if not referer:
            referer = self.context.absolute_url()
        return referer


class Rm(Add):
    """Rm from favorite"""
    def __call__(self):
        manager = self.context.restrictedTraverse(VIEW_NAME)
        if manager.isin():
            manager.rm()
            status = IStatusMessage(self.request)
            status.add(_(u"Removed from favorite"))
        self.request.response.redirect(self.nextURL())


class Isin(BrowserView):
    def __call__(self):
        manager = self.context.restrictedTraverse(VIEW_NAME)
        return manager.isin()
