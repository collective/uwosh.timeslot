"""Definition of the Time Slot content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ITimeSlot
from uwosh.timeslot.config import PROJECTNAME

from Products.CMFCore.utils import getToolByName

TimeSlotSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.IntegerField('maxCapacity',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(label=_(u'Max Capacity'),
                                    description=_(u'The max number of people'))
    ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

TimeSlotSchema['title'].storage = atapi.AnnotationStorage()
TimeSlotSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(TimeSlotSchema, folderish=True, moveDiscussion=False)

class TimeSlot(folder.ATFolder):
    """Description of the Example Type"""
    implements(ITimeSlot)

    portal_type = "Time Slot"
    schema = TimeSlotSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    maxCapacity = atapi.ATFieldProperty('maxCapacity')

    def getNumberOfAvailableSpots(self):
        numberOfSignedUpPeople = 0
        people = self.contentItems()
        for (id, person) in people:
            reviewState = person.getWorkflowReviewState()
            if reviewState == 'signedup':
                numberOfSignedUpPeople += 1
        return self.maxCapacity - numberOfSignedUpPeople

    def getLabel(self):
        date = self.aq_parent.Title()
        return date + ' @ ' + self.title
        
    def isUserSignedupForThisSlot(self, username):
        for (id, obj) in self.contentItems():
            if id == username:
                return True
        return False

    def getListOfPeople(self):
        people = self.getPeople()
        peopleList = []
        for (id, person) in people:
            title = person.Title()
            if title == '':
                title = person.id
            peopleList.append(title)
        return peopleList

    def getPeople(self):
        return self.contentItems()
        
    def getPerson(self, name):
        people = self.getPeople()
        for (id, person) in people:
            title = person.Title()
            if title == name or id == name:
                return person
        raise ValueError, 'The person ' + name + ' was not found'
        
        
atapi.registerType(TimeSlot, PROJECTNAME)
