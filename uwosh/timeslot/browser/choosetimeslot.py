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
        return self.context.getListOfDays();
        
    def getListOfTimeSlots(self, date):
        day = self.context.getDay(date)
        return day.getListOfTimeSlots()
        
    def getTimeSlotCurrentCapacity(self, date, timeSlotTitle):
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(timeSlotTitle)
        return timeSlot.getNumberOfAvailableSpots()
    
    def isUserSignedupForThisSlot(self, date, timeSlotTitle):
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(timeSlotTitle)
        username = self.getUserName()
        return timeSlot.isUserSignedupForThisSlot(username)
    
    def getTimeSlotLabel(self, date, timeSlot):
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(timeSlot)
        return timeSlot.getLabel()
    
    def getUserName(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return member.getUserName()
    
    def submitUserSelection(self):
        slotNotFound = '__no_slot_to_assign__'
        selectedSlot = self.request.get('slotSelection', slotNotFound)
        if selectedSlot == slotNotFound:
            raise ValueError, "No slot was selected"
        
        (date, time) = selectedSlot.split(' @ ')
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(time)
        
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        fullname = member.getProperty('fullname')
        email = member.getProperty('email')
        
        timeSlot.invokeFactory('Person', username)
        newPerson = timeSlot[username]
        newPerson.setEmail(email)
        newPerson.setTitle(fullname)
        
        portal_workflow = getToolByName(self, 'portal_workflow')
        portal_workflow.doActionFor(newPerson, 'signup')
        newPerson.reindexObject()

        self.request.response.redirect(self.context.absolute_url() + '/signup-results')

        