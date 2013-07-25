from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable
from Products.CMFPlone import PloneMessageFactory as _p
from zope.formlib import form
from zope.component import adapts
from zope import interface
from zope import schema

from collective.favoriting.actions.vocabularies import favoritingChoice
from collective.favoriting.browser.favoriting_view import VIEW_NAME
from collective.favoriting.i18n import _


class IFavoritingAction(interface.Interface):
    """Definition of the configuration available for a favoriting action."""

    favoriting = schema.Choice(
        title=_(u"Change favoriting"),
        vocabulary=favoritingChoice
        )


class FavoritingAction(SimpleItem):
    interface.implements(IFavoritingAction, IRuleElementData)

    favoriting = 'favorite'
    element = 'collective.favoriting.actions.Favoriting'
    summary = _(u'Change if the object is favorited or not.')


class FavoritingActionExecutor(object):
    interface.implements(IExecutable)
    adapts(interface.Interface, IFavoritingAction, interface.Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        favoriting = self.element.favoriting
        obj = self.event.object
        manager = obj.restrictedTraverse(VIEW_NAME)
        if not manager.isin():
            if favoriting == 'favorite':
                manager.add()
            else:
                manager.rm()
        return True


class FavoritingActionAddForm(AddForm):
    form_fields = form.FormFields(IFavoritingAction)
    label = _(u'Add favoriting action')
    description = _(u'An action which can add or remove an object '
                    u'to the user favorites')
    form_name = _p(u'Configure element')

    def create(self, data):
        a = FavoritingAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class FavoritingActionEditForm(EditForm):
    form_fields = form.FormFields(IFavoritingAction)
    label = _(u'Edit favoriting action')
    description = _(u'An action which can add or remove an object '
                    u'to the user favorites')
    form_name = _p(u'Configure element')
