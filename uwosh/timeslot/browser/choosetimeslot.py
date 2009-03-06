from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _


class IChooseTimeSlot(Interface):
    """
    ChooseTimeSlot view interface
    """

    def test():
        """ test method"""


class ChooseTimeSlot(BrowserView):
    """
    ChooseTimeSlot browser view
    """
    implements(IChooseTimeSlot)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def getSignupSheetTitle(self):
        return self.context.Title()

    def getListOfDays(self):
        dayBrains = self.portal_catalog.queryCatalog({'portal_type':'Day'})
        days = []
        for dayBrain in dayBrains:
            day = dayBrain.getObject()
            title = day.Title()
            days.append(title)
        return days
        
    def getListOfTimeSlots(self, date):
        timeSlots = self.getTimeSlotsForDay(date)
        timeSlotsList = []
        for (id, timeSlot) in timeSlots:
            title = timeSlot.Title()
            timeSlotsList.append(title)
        return timeSlotsList
        
    def getDay(self, date):
        dayBrains = self.portal_catalog.queryCatalog({'portal_type':'Day', 'Title':date})
        if len(dayBrains) == 0:
            raise ValueError, "No days were found"
        if len(dayBrains) > 1:
            raise ValueError, "Too many days (%s) were found for date %s" % (len(dayBrains), date)
        return dayBrains[0].getObject()
        
    def getTimeSlotsForDay(self, date):
        day = self.getDay(date)
        return day.contentItems()
    
    def getTimeSlotCurrentCapacity(self, date, timeSlot):
        timeSlotObj = self.getTimeSlot(date, timeSlot)
        return timeSlotObj.getNumberOfAvailableSpots()
        
    def getTimeSlot(self, date, timeSlot):
        day = self.getDay(date)
        timeSlots = day.contentItems()
        for (id, obj) in timeSlots:
            title = obj.Title()
            if title == timeSlot:
                return obj
        raise ValueError, "TimeSlot was not found"
    
    def getSlotLabel(self, day, timeSlot):
        return day + " @ " + timeSlot
        
    def isUserSignedupForThisSlot(self, date, timeSlot):
        username = self.getUserName()
        timeSlotObj = self.getTimeSlot(date, timeSlot)
        for (id, obj) in timeSlotObj.contentItems():
            if id == username:
                return True
        return False
    
    def getUserName(self):
        membershipTool = getToolByName(self, 'portal_membership')
        member = membershipTool.getAuthenticatedMember()
        return member.getUserName()
    
    def submitUserSelection(self):
        slotNotFound = '__no_slot_to_assign__'
        selectedSlot = self.request.get('slotSelection', slotNotFound)
        if selectedSlot == slotNotFound:
            raise ValueError, "No slot was selected"
        
        (date, time) = selectedSlot.split(' @ ')
        timeSlot = self.getTimeSlot(date, time)
        
        membershipTool = getToolByName(self, 'portal_membership')
        member = membershipTool.getAuthenticatedMember()
        username = member.getUserName()
        fullname = member.getProperty('fullname')
        email = member.getProperty('email')
        
        timeSlot.invokeFactory('Person', username)
        newPerson = timeSlot[username]
        newPerson.setEmail(email)
        newPerson.setTitle(fullname)
        newPerson.reindexObject()
        self.request.response.redirect(self.context.absolute_url() + '/signup-results')

        