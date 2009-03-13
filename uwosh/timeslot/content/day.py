"""Definition of the Day content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import IDay
from uwosh.timeslot.config import PROJECTNAME

DaySchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

DaySchema['title'].storage = atapi.AnnotationStorage()
DaySchema['title'].widget.label=_(u'Date')
DaySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(DaySchema, folderish=True, moveDiscussion=False)

class Day(folder.ATFolder):
    """Description of the Example Type"""
    implements(IDay)

    portal_type = "Day"
    schema = DaySchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    def getTimeSlots(self):
        query = {'portal_type':'Time Slot'}
        brains = self.portal_catalog.searchResults(query, path=self.absolute_url_path())
        timeSlots = []
        for brain in brains:
            timeSlot = brain.getObject()
            timeSlots.append(timeSlot)
        return timeSlots
        
    def getTimeSlot(self, title):
        query = {'portal_type':'Time Slot', 'Title':title}
        brains = self.portal_catalog.searchResults(query, path=self.absolute_url_path())
        if len(brains) < 1:
            raise ValueError('The TimeSlot %s was not found.' % title)
        timeSlot = brains[0].getObject()
        return timeSlot

    def removeAllPeople(self):
        timeSlots = self.getTimeSlots()
        for timeSlot in timeSlots:
            timeSlot.removeAllPeople()

atapi.registerType(Day, PROJECTNAME)
