"""Definition of the Person content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import IPerson
from uwosh.timeslot.config import PROJECTNAME

from Products.CMFCore.utils import getToolByName

PersonSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField('email',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'E-Mail'),
                                  description=_(u'Your email address')),
        validators = ('isEmail')
    ),

    atapi.StringField('phone',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Phone'),
                                  description=_(u'Your phone number'))
    ),

    atapi.StringField('department',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Department'),
                                  description=_(u'Your department'))
    ),

    atapi.StringField('classification',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(label=_(u'Classification'),
                                  description=_(u'Your staff type'))
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PersonSchema['title'].storage = atapi.AnnotationStorage()
PersonSchema['title'].widget.label = _(u'Name')
PersonSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(PersonSchema, moveDiscussion=False)

class Person(base.ATCTContent):
    """Description of Person"""
    implements(IPerson)

    portal_type = "Person"
    schema = PersonSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    email = atapi.ATFieldProperty('email')
    phone = atapi.ATFieldProperty('phone')
    department = atapi.ATFieldProperty('department')
    classification = atapi.ATFieldProperty('classification')
    
    def getReviewState(self):
        status = self.portal_workflow.getStatusOf('uwosh_timeslot_person_workflow', self)
        reviewState = status['review_state']
        return reviewState
    
    def getReviewStateTitle(self):
    	reviewState = self.getReviewState()
    	reviewStateTitle = self.portal_workflow.getTitleForStateOnType(reviewState, 'Person')
        return reviewStateTitle
    
    def getExtraInfo(self):
        return ' - '.join([self.phone, self.classification, self.department])
    
atapi.registerType(Person, PROJECTNAME)
