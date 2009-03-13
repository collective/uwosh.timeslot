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
        timeSlotTuples = self.contentItems()
        timeSlots = []
        for (id, timeSlot) in timeSlotTuples:
            timeSlots.append(timeSlot)
        return timeSlots
        
    def getTimeSlot(self, timeSlotTitle):
        timeSlots = self.contentItems()
        for (id, timeSlot) in timeSlots:
            title = timeSlot.Title()
            if title == timeSlotTitle:
                return timeSlot
        raise ValueError('TimeSlot was not found')

    def removeAllPeople(self):
        timeSlots = self.contentItems()
        for (id, timeSlot) in timeSlots:
            timeSlot.removeAllPeople()

atapi.registerType(Day, PROJECTNAME)
