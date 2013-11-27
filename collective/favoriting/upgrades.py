import logging
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.interfaces._content import IFolderish

PROFILE = 'profile-collective.favoriting:default'
logger = logging.getLogger(__name__)


def common(context):
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile(PROFILE)


def cleanup_annotations(context):
    """
    http://developer.plone.org/misc/annotations.html
    Remove objects from content annotations in Plone site,

    This is mostly to remove objects which might make the site un-exportable
    when eggs / Python code has been removed.

    @param portal: Plone site object

    @param names: Names of the annotation entries to remove
    """
    portal = getSite()
    name = 'collective.favoriting.storage.FavoritingStorage'

    def recurse(context):
        """ Recurse through all content on Plone site """

        annotations = IAnnotations(context)

        if name in annotations:
            msg = "Cleaning up annotation %s on item %s"
            msg = msg % (name, context.absolute_url())
            logger.info(msg)
            del annotations[name]

        # Make sure that we recurse to real folders only,
        # otherwise contentItems() might be acquired from higher level
        if IFolderish.providedBy(context):
            for id, item in context.contentItems():
                recurse(item)

    recurse(portal)
