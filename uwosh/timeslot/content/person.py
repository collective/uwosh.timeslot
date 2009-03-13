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
                                  description=_(u'Your email address'))
    ),

))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PersonSchema['title'].storage = atapi.AnnotationStorage()
PersonSchema['title'].widget.label = _(u'Name')
PersonSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(PersonSchema, moveDiscussion=False)

class Person(base.ATCTContent):
    """Description of the Example Type"""
    implements(IPerson)

    portal_type = "Person"
    schema = PersonSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    email = atapi.ATFieldProperty('email')
    
    def getReviewState(self):
        status = self.portal_workflow.getStatusOf('person_workflow', self)
        return status['review_state']
                
atapi.registerType(Person, PROJECTNAME)
