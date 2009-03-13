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

    atapi.BooleanField('allowWaitingList',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(label=_(u'Allow Waiting List'),
                                   description=_(u'Check if you want to allow signups to waiting list once \
                                                   max capacity is reached'))
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
    allowWaitingList = atapi.ATFieldProperty('allowWaitingList')

    def getNumberOfAvailableSpots(self):
        numberOfSignedUpPeople = 0
        people = self.contentItems()
        for (id, person) in people:
            reviewState = person.getReviewState()
            if reviewState == 'signedup':
                numberOfSignedUpPeople += 1
        return self.maxCapacity - numberOfSignedUpPeople

    def isCurrentUserSignedUpForThis(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        if self.isUserSignedUpForThisSlot(username):
            return True
        else:
            return False

    def getLabel(self):
        date = self.aq_parent.Title()
        return date + ' @ ' + self.title
        
    def isUserSignedUpForThisSlot(self, username):
        for (id, obj) in self.contentItems():
            if id == username:
                return True
        return False

    def getPeople(self):
        personTuples = self.contentItems()
        people = []
        for (id, person) in personTuples:
            people.append(person)
        return people    
        
    def getPerson(self, name):
        people = self.contentItems()
        for (id, person) in people:
            title = person.Title()
            if title == name or id == name:
                return person
        raise ValueError, 'The person ' + name + ' was not found'
   
    def removeAllPeople(self):
        peopleToRemove = []
        for (id, obj) in self.contentItems():
            peopleToRemove.append(id)
        self.manage_delObjects(peopleToRemove)
        
atapi.registerType(TimeSlot, PROJECTNAME)
