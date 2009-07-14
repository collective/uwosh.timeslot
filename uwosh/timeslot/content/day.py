from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import IDay, IContainsPeople, ICloneable
from uwosh.timeslot.config import PROJECTNAME

DaySchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.DateTimeField('date',
        storage=atapi.AnnotationStorage(),
        required=True,
        widget=atapi.CalendarWidget(label=_('Date'),
                                    show_hm=False,
                                    format='%a, %b. %d, %Y',
                                    starting_year=2009)
    ),

))

DaySchema['title'].required = False
DaySchema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}
DaySchema['title'].storage = atapi.AnnotationStorage()
DaySchema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}
DaySchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(DaySchema, folderish=True, moveDiscussion=False)

class Day(folder.ATFolder):
    implements(IDay, IContainsPeople, ICloneable)

    portal_type = 'Day'
    schema = DaySchema

    title = atapi.ATFieldProperty('title')
    date = atapi.ATFieldProperty('date')
    description = atapi.ATFieldProperty('description')
    
    def Title(self):
    	date = self.getDate()
    	
    	if date == None:
            return self.id
    	else:
    	    return date.strftime('%a, %b. %d, %Y')
    
    def getTimeSlots(self):
        query = {'portal_type':'Time Slot'}
        pathQuery = {'query':self.absolute_url_path(), 'depth':1}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=pathQuery,
                                                               sort_on='getStartTime', sort_order='ascending')
        timeSlots = []
        for brain in brains:
            timeSlot = brain.getObject()
            timeSlots.append(timeSlot)
        return timeSlots
        
    def getTimeSlot(self, title):
        query = {'portal_type':'Time Slot', 'Title':title}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) == 0:
            raise ValueError('The TimeSlot %s was not found.' % title)
        timeSlot = brains[0].getObject()
        return timeSlot

    def removeAllPeople(self):
        timeSlots = self.getTimeSlots()
        for timeSlot in timeSlots:
            timeSlot.removeAllPeople()

atapi.registerType(Day, PROJECTNAME)
