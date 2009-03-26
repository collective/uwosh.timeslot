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
        if selectedSlot == None:
        	self.request.response.redirect(self.context.absolute_url())
        	return
        
        (date, time) = selectedSlot.split(' @ ')
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(time)
        
        member = self.getCurrentUser()
        username = member.getUserName()
        fullname = member.getProperty('fullname')
        if fullname == '':
            fullname = username
        email = member.getProperty('email')
        [department, phone] = self.getDepartmentAndPhone(email)
        
        allowWaitingList = timeSlot.getAllowWaitingList()
        numberOfAvailableSpots = timeSlot.getNumberOfAvailableSpots()
        
        if allowWaitingList or numberOfAvailableSpots > 0:
            newPerson = self.createPerson(timeSlot, username, email, fullname, department, phone)
            
            if numberOfAvailableSpots > 0:
                portal_workflow = getToolByName(self, 'portal_workflow')
                portal_workflow.doActionFor(newPerson, 'signup')
                newPerson.reindexObject()
                waiting = False
                
            self.sendConfirmationEmail(email, fullname, selectedSlot)
            success = True
        
        self.request.response.redirect(self.context.absolute_url() + '/signup-results?success=%d&waiting=%d' % (success,waiting))

    def getCurrentUser(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return member

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
  
    def getEmployeeId(self, email):
        webService = xmlrpclib.Server('http://ws.it.uwosh.edu:8080/ws/', allow_none=True)
        employeeId = webService.getEmplidFromEmailAddress(email)
        return employeeId

    def getContactInfo(self, employeeId):
		webService = xmlrpclib.Server('http://ws.it.uwosh.edu:8080/ws/', allow_none=True)
		contactInfo = webService.CampusDirectoryZEM001UOVW(employeeId)
		return contactInfo

    def createPerson(self, location, username, email, fullname, department, phone):
        location.invokeFactory('Person', username)
        newPerson = location[username]
        newPerson.setEmail(email)
        newPerson.setTitle(fullname)
        newPerson.setDepartment(department)
        newPerson.setPhone(phone)
        newPerson.reindexObject()
        return newPerson

    def sendConfirmationEmail(self, toEmail, fullname, timeSlot):
        fromEmail = self.getSignupSheetCreatorEmail()
        subject = 'Registration success'
        message = 'Hi ' + fullname + ',\nYou have successfully registered for: ' + timeSlot
        mailHost = self.context.MailHost
        mailHost.secureSend(message, toEmail, fromEmail, subject)
        
    def getSignupSheetCreatorEmail(self):
    	creatorId = self.context.Creator();
    	portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getMemberById(creatorId)
        return member.getProperty('email')