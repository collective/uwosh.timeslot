from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _


class IChooseTimeSlot(Interface):
    """
    ChooseTimeSlot view interface
    """


class ChooseTimeSlot(BrowserView):
    """
    ChooseTimeSlot browser view
    """
    implements(IChooseTimeSlot)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.signupSheet = self.context

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def getSignupSheetTitle(self):
        return self.signupSheet.Title()
    
    def getListOfDays(self):
        return self.signupSheet.getListOfDays();
        
    def getListOfTimeSlots(self, date):
        day = self.signupSheet.getDay(date)
        return day.getListOfTimeSlots()
        
    def getTimeSlotNumberOfAvailableSlots(self, date, timeSlotTitle):
        day = self.signupSheet.getDay(date)
        timeSlot = day.getTimeSlot(timeSlotTitle)
        return timeSlot.getNumberOfAvailableSpots()
    
    def isUserSignedupForThisSlot(self, date, timeSlotTitle):
        day = self.signupSheet.getDay(date)
        timeSlot = day.getTimeSlot(timeSlotTitle)
        username = self.getUserName()
        return timeSlot.isUserSignedupForThisSlot(username)
    
    def getTimeSlotLabel(self, date, timeSlot):
        day = self.signupSheet.getDay(date)
        timeSlot = day.getTimeSlot(timeSlot)
        return timeSlot.getLabel()
    
    def getUserName(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return member.getUserName()
    
    def timeSlotAllowsWaitingList(self, date, timeSlot):
        day = self.signupSheet.getDay(date)
        timeSlot = day.getTimeSlot(timeSlot)
        return timeSlot.getAllowWaitingList()
    
    def submitUserSelection(self):
        selectedSlot = self.request.get('slotSelection')
        if selectedSlot == '':
            raise ValueError('No slot was selected')
        
        (date, time) = selectedSlot.split(' @ ')
        day = self.signupSheet.getDay(date)
        timeSlot = day.getTimeSlot(time)
        
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        fullname = member.getProperty('fullname')
        if fullname == '':
            fullname = username
        email = member.getProperty('email')
        
        allowWaitingList = timeSlot.getAllowWaitingList()
        numberOfAvailableSpots = timeSlot.getNumberOfAvailableSpots()
        
        if (allowWaitingList or numberOfAvailableSpots > 0):
            timeSlot.invokeFactory('Person', username)
            newPerson = timeSlot[username]
            newPerson.setEmail(email)
            newPerson.setTitle(fullname)
            
            if numberOfAvailableSpots > 0:
                portal_workflow = getToolByName(self, 'portal_workflow')
                portal_workflow.doActionFor(newPerson, 'signup')
                
            newPerson.reindexObject()

            self.request.response.redirect(self.signupSheet.absolute_url() + '/signup-results?success=1')
            
        else:
            self.request.response.redirect(self.signupSheet.absolute_url() + '/signup-results?success=0')