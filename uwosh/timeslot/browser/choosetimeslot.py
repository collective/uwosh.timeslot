from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.validation import validation

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
        validEmail = False
        errorMsg = ''
    
    	userInfo = self.getUserInput()
    	userInfo.update(self.getMemberInfo())
    
        (anyMissing, missingFields) = self.areAnyRequiredFieldsMissing(userInfo)   
        if anyMissing:
            success = False
            errorMsg = 'You did not complete the following fields: '
            errorMsg += ', '.join(missingFields)
        
        else:
            for slot in userInfo['selectedSlots']:
                (signupSheet, date, time) = slot.split(' @ ')
                signupSheet = self.context.getSignupSheet(signupSheet)
                day = signupSheet.getDay(date)
                timeSlot = day.getTimeSlot(time)
                allowWaitingList = timeSlot.getAllowWaitingList()
                numberOfAvailableSpots = timeSlot.getNumberOfAvailableSpots()
                
                isEmail = validation.validatorFor('isEmail')
                validEmail = isEmail(userInfo['email']) == 1
                
                if allowWaitingList or numberOfAvailableSpots > 0:
                    person = self.createPerson(timeSlot, userInfo)
                
                    if numberOfAvailableSpots > 0:
                        self.signupPerson(person)
                        waiting = False
                    elif validEmail:
                        self.sendWaitingConfirmationEmail(userInfo, signupSheet, slot)
                    
                    success = True
            
                else:
                    errorMsg = 'The slot you selected is already full. Please select a different one'
                    success = False
        
        self.request.response.redirect(self.context.absolute_url() + 
                                       '/signup-results?success=%d&waiting=%d&emailSent=%d&errorMsg=%s' % (success,waiting,validEmail,errorMsg))


    def getUserInput(self):
        userInput = dict()
        userInput['phone'] = self.request.get('phone', '')
        userInput['classification'] = self.request.get('classification', '')
        userInput['dept'] = self.request.get('dept', '')
        userInput['selectedSlots'] = self.request.get('slotSelection', None)

        if type(userInput['selectedSlots']) != list:
            userInput['selectedSlots'] = [userInput['selectedSlots']]

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

    def areAnyRequiredFieldsMissing(self, userInput):
        fieldNames = self.context.schema['extraFields'].vocabulary
        missingFields = []
        anyMissing = False
        if userInput['selectedSlots'] == [None]:
            anyMissing = True
            missingFields.append('Timeslot')
            
        extraFields = self.context.getExtraFields()
        for field in extraFields:
            if len(userInput[field]) < 1:
                anyMissing = True

                for (id, name) in fieldNames:
                    if id == field:
                        missingFields.append(name)
                        break

        return (anyMissing, missingFields)    	

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

    def isAnyExtraInfoRequired(self):
        return self.isPhoneRequired() or self.isDepartmentRequired() or self.isClassRequired()

    def isPhoneRequired(self):
        return self.isFieldRequired('phone')
    
    def isDepartmentRequired(self):
        return self.isFieldRequired('dept')
        
    def isClassRequired(self):
    	return self.isFieldRequired('classification')
    
    def isFieldRequired(self, field):
    	extraFields = self.context.getExtraFields()
        if field in extraFields:
            return True
        else:
            return False
    
    def isCurrentUserLoggedIn(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return 'Anonymous' not in member.getRoles()

    def sendWaitingConfirmationEmail(self, userInfo, signupSheet, slot):
        if signupSheet.isContainedInMasterSignupSheet():
            signupSheet = signupSheet.aq_parent

        extraEmailContent = signupSheet.getExtraEmailContent()
        contactInfo = signupSheet.getContactInfo()
        toEmail = userInfo['email']
        fromEmail = "%s <%s>" % (self.context.email_from_name, self.context.email_from_address)
        subject = signupSheet.Title() + ' - Waiting List Confirmation'
        
        message = 'Hi ' + userInfo['fullname'] + ',\n\n'
        message += 'This message is to confirm that you have been added to the waiting list for:\n'
        message += slot + '\n\n'

        if extraEmailContent != ():
            for line in extraEmailContent:
                message += line + '\n'
            message += '\n'

        message += signupSheet.absolute_url() + '\n\n'
        
        if contactInfo != ():
            message += 'If you have any questions please contact:\n'
            for line in self.context.getContactInfo():
                message += line + '\n'
            message += '\n'

        mailHost = self.context.MailHost
        mailHost.secureSend(message, toEmail, fromEmail, subject)

    def getSlotsCurrentUserIsSignedUpFor(self):
        slots = []
        for slot in signupSheet.getSlotsCurrentUserIsSignedUpFor():
            slots.append(slot.getLabel())
        return slots
            
    def getSlotsCurrentUserIsWaitingFor(self):    
        slots = []
        for slot in signupSheet.getSlotsCurrentUserIsWaitingFor():
            slots.append(slot.getLabel())
        return slots
