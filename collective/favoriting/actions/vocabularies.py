from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from collective.favoriting.i18n import _

favoritingChoice = SimpleVocabulary([
    SimpleTerm('favorite', 'favorite', _(u'Add to favorite')),
    SimpleTerm('unfavorite', 'unfavorite', _(u'Remove from favorite')),
    ])
