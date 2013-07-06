from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import IPerson
from uwosh.timeslot.config import PROJECTNAME

from Products.CMFCore.utils import getToolByName

PersonSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField(
        'email',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'E-Mail'),
            description=_(u'Your email address')),
        validators=('isEmail')
    ),

    atapi.StringField(
        'phone',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Phone'),
            description=_(u'Your phone number'))
    ),

    atapi.StringField(
        'department',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Department'),
            description=_(u'Your department'))
    ),

    atapi.StringField(
        'classification',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Classification'),
            description=_(u'Your staff type'))
    ),

))

PersonSchema['title'].storage = atapi.AnnotationStorage()
PersonSchema['title'].widget.label = _(u'Name')
PersonSchema['description'].storage = atapi.AnnotationStorage()
PersonSchema['description'].widget.visible = {
    'view': 'invisible',
    'edit': 'invisible',
}

schemata.finalizeATCTSchema(PersonSchema, moveDiscussion=False)


class Person(base.ATCTContent):
    implements(IPerson)

    portal_type = 'Person'
    schema = PersonSchema

    title = atapi.ATFieldProperty('title')
    email = atapi.ATFieldProperty('email')
    phone = atapi.ATFieldProperty('phone')
    department = atapi.ATFieldProperty('department')
    classification = atapi.ATFieldProperty('classification')

    def getReviewState(self):
        portal_workflow = getToolByName(self, 'portal_workflow')
        return portal_workflow.getInfoFor(self, 'review_state')

    def getReviewStateTitle(self):
        reviewState = self.getReviewState()
        return self.portal_workflow.getTitleForStateOnType(reviewState,
                                                           'Person')

    def getExtraInfo(self):
        extraInfo = []
        if self.phone != '':
            extraInfo.append('Phone: ' + self.phone)
        if self.classification != '':
            extraInfo.append('Class: ' + self.classification)
        if self.department != '':
            extraInfo.append('Dept: ' + self.department)
        return ', '.join(extraInfo)

atapi.registerType(Person, PROJECTNAME)
