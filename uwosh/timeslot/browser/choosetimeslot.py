from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _

import xmlrpclib
from xml.dom import minidom

from Products.validation import validation

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
        emailSent = False
    
    	userInfo = self.getUserInput()
    	userInfo.update(self.getMemberInfo())
    
        if userInfo['selectedSlot'] == None:
        	self.request.response.redirect(self.context.absolute_url())
        	return
        	
        (date, time) = userInfo['selectedSlot'].split(' @ ')
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(time)
        allowWaitingList = timeSlot.getAllowWaitingList()
        numberOfAvailableSpots = timeSlot.getNumberOfAvailableSpots()
       
        isEmail = validation.validatorFor('isEmail')
        if (isEmail(userInfo['email']) == 1):
        	emailSent = True
       
        if self.context.isCurrentUserSignedUpForAnySlot():
        	success = False
       
        elif allowWaitingList or numberOfAvailableSpots > 0:
            person = self.createPerson(timeSlot, userInfo)
            
            if numberOfAvailableSpots > 0:
                self.signupPerson(person)
                waiting = False
            else:
                self.sendWaitingConfirmationEmail(userInfo)
            	
            success = True
        
        self.request.response.redirect(self.context.absolute_url() + '/signup-results?success=%d&waiting=%d&emailSent=%d' % (success,waiting,emailSent))

    def getUserInput(self):
        userInput = dict()
        userInput['selectedSlot'] = self.request.get('slotSelection')
        userInput['phone'] = self.request.get('phone')
        userInput['classification'] = self.request.get('classification')
        userInput['dept'] = self.request.get('dept')
        return userInput
		
    def getMemberInfo(self):
    	memberInfo = dict()
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        memberInfo['username'] = member.getUserName()
        memberInfo['fullname'] = member.getProperty('fullname')
        if memberInfo['fullname'] == '':
            memberInfo['fullname'] = memberInfo['username'] 
        memberInfo['email'] = member.getProperty('email')
        return memberInfo

    def createPerson(self, location, userInfo):
        location.invokeFactory('Person', userInfo['username'])
        newPerson = location[userInfo['username']]
        newPerson.setEmail(userInfo['email'])
        newPerson.setTitle(userInfo['fullname'])
        newPerson.setClassification(userInfo['classification'])
        newPerson.setDepartment(userInfo['dept'])
        newPerson.setPhone(userInfo['phone'])
        newPerson.reindexObject()
        return newPerson

    def signupPerson(self, person):
        portal_workflow = getToolByName(self, 'portal_workflow')
        portal_workflow.doActionFor(person, 'signup')
        person.reindexObject()

    def sendWaitingConfirmationEmail(self, userInfo):
    	isEmail = validation.validatorFor('isEmail')
    	
    	toEmail = userInfo['email']
    	if (isEmail(toEmail) == 1):
            fromEmail = "%s <%s>" % (self.context.email_from_name, self.context.email_from_address)
            subject = self.context.Title() + ' - Waiting List Confirmation'
            message = 'Hi ' + userInfo['fullname'] + ',\n\n'
            message += 'You have been added to the waiting list for: ' + userInfo['selectedSlot']
            mailHost = self.context.MailHost
            mailHost.secureSend(message, toEmail, fromEmail, subject)
        