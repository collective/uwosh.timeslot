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

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def submitUserSelection(self):
        success = False
        waiting = True
    
        selectedSlot = self.request.get('slotSelection')
        if selectedSlot == '':
            raise ValueError('No slot was selected')
        
        (date, time) = selectedSlot.split(' @ ')
        day = self.context.getDay(date)
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
        
        if allowWaitingList or numberOfAvailableSpots > 0:
            timeSlot.invokeFactory('Person', username)
            newPerson = timeSlot[username]
            newPerson.setEmail(email)
            newPerson.setTitle(fullname)
            
            if numberOfAvailableSpots > 0:
                portal_workflow = getToolByName(self, 'portal_workflow')
                portal_workflow.doActionFor(newPerson, 'signup')
                waiting = False
                
            newPerson.reindexObject()
            self.sendConfirmationEmail(email, fullname, selectedSlot)
            success = True
        
        self.request.response.redirect(self.context.absolute_url() + '/signup-results?success=%d&waiting=%d' % (success,waiting))
        
    def sendConfirmationEmail(self, toEmail, fullname, timeSlot):
        message = 'Hi ' + fullname + ',\nYou have successfully registered for: ' + timeSlot
        fromEmail = 'a-test-admin@uwosh.edu'
        subject = 'Registration success'
        mailHost = self.context.MailHost
        mailHost.secureSend(message, toEmail, fromEmail, subject)
        