from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _

import xmlrpclib
from xml.dom import minidom

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
        [department, phone] = self.getDepartmentAndPhone(email)
        
        allowWaitingList = timeSlot.getAllowWaitingList()
        numberOfAvailableSpots = timeSlot.getNumberOfAvailableSpots()
        
        if allowWaitingList or numberOfAvailableSpots > 0:
        	
            timeSlot.invokeFactory('Person', username)
            newPerson = timeSlot[username]
            newPerson.setEmail(email)
            newPerson.setTitle(fullname)
            newPerson.setDepartment(department)
            newPerson.setPhone(phone)
            
            if numberOfAvailableSpots > 0:
                portal_workflow = getToolByName(self, 'portal_workflow')
                portal_workflow.doActionFor(newPerson, 'signup')
                waiting = False
                
            newPerson.reindexObject()
            self.sendConfirmationEmail(email, fullname, selectedSlot)
            success = True
        
        self.request.response.redirect(self.context.absolute_url() + '/signup-results?success=%d&waiting=%d' % (success,waiting))

    def getEmployeeId(self, email):
        webService = xmlrpclib.Server('http://ws.it.uwosh.edu:8080/ws/', allow_none=True)
        employeeId = webService.getEmplidFromEmailAddress(email)
        return employeeId

    def getContactInfo(self, employeeId):
		webService = xmlrpclib.Server('http://ws.it.uwosh.edu:8080/ws/', allow_none=True)
		contactInfo = webService.CampusDirectoryZEM001UOVW(employeeId)
		return contactInfo
    
    def getDepartmentAndPhone(self, email):
		employeeId = self.getEmployeeId(email)
		contactInfo = self.getContactInfo(employeeId)
		if contactInfo == '<params>\n</params>\n':
			return [None, None]
		else:
			xmldoc = minidom.parseString(contactInfo)
			department = xmldoc.firstChild.childNodes[1].childNodes[1].firstChild.firstChild.childNodes[5].firstChild.firstChild.data
			phone = xmldoc.firstChild.childNodes[1].childNodes[1].firstChild.firstChild.childNodes[7].firstChild.firstChild.data
			return [department, phone]
  
    def sendConfirmationEmail(self, toEmail, fullname, timeSlot):
        message = 'Hi ' + fullname + ',\nYou have successfully registered for: ' + timeSlot
        fromEmail = 'a-test-admin@uwosh.edu'
        subject = 'Registration success'
        mailHost = self.context.MailHost
        mailHost.secureSend(message, toEmail, fromEmail, subject)
        