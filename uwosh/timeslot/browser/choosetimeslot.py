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
        timeSlotItems = self.getTimeSlotsForDay(date)
        timeSlots = []
        for timeSlot in timeSlotItems:
            timeSlotObj = timeSlot[1]
            title = timeSlotObj.Title()
            timeSlots.append(title)
        return timeSlots
        
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
        timeSlotItems = day.contentItems()
        timeSlots = []
        for timeSlotItem in timeSlotItems:
            timeSlotObj = timeSlotItem[1]
            title = timeSlotObj.Title()
            if title == timeSlot:
                return timeSlotObj
        raise ValueError, "TimeSlot was not found"
    
    def getSlotLabel(self, day, timeSlot):
        return day + " @ " + timeSlot
        
    def submitUserSelection(self):
        slotNotFound = '__no_slot_to_assign__'
        selectedSlot = self.request.get('slotSelection', slotNotFound)
        if selectedSlot == slotNotFound:
            raise ValueError, "No slot was selected"
        
        slotParts = selectedSlot.split(' @ ')
        date = slotParts[0]
        time = slotParts[1]
        timeSlot = self.getTimeSlot(date, time)
        
        membershipTool = getToolByName(self, 'portal_membership')
        member = membershipTool.getAuthenticatedMember()
        username = member.getUserName()
        email = member.getProperty('email')
        
        timeSlot.invokeFactory('Person', username)
        newPerson = timeSlot[username]
        newPerson.setEmail(email)
        newPerson.reindexObject()

        