from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ISignupSheet, IContainsPeople
from uwosh.timeslot.config import PROJECTNAME

import csv
from StringIO import StringIO
from DateTime import DateTime

SignupSheetSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.LinesField('extraEmailContent',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(label=_(u'Extra Email Content'),
                                 description=_(u'Any additional information that you want included in the notification emails. \
                                                 Note: Contact info., sheet, day, time, and a url are included by default.'))
    ),

    atapi.LinesField('contactInfo',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(label=_(u'Contact Information'),
                                 description=_(u'Contact information for the manager of the signup sheet.'))
    ),

    atapi.LinesField('extraFields',
        storage=atapi.AnnotationStorage(),
        vocabulary=[('phone','Phone'), ('department','Department'), ('classification','Employee Classification')],
        widget=atapi.MultiSelectionWidget(label=_(u'Extra Fields'),
                                          description=_(u'Information you want to collect from users besides just name and email.'),
                                          format=_(u'checkbox'))
    ),

    atapi.BooleanField('allowSignupForMultipleSlots',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(label=_(u'Allow Signup For Multiple Slots'),
                                 description=_(u'Allow the user to signup for more than one slot.'))
    ),
))

SignupSheetSchema['title'].storage = atapi.AnnotationStorage()
SignupSheetSchema['description'].storage = atapi.AnnotationStorage()
SignupSheetSchema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}

schemata.finalizeATCTSchema(SignupSheetSchema, folderish=True, moveDiscussion=False)

class SignupSheet(folder.ATFolder):
    implements(ISignupSheet, IContainsPeople)

    portal_type = 'Signup Sheet'
    schema = SignupSheetSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    extraFields = atapi.ATFieldProperty('extraFields')
    contactInfo = atapi.ATFieldProperty('contactInfo')
    extraEmailContent = atapi.ATFieldProperty('extraEmailContent')
    allowSignupForMultipleSlots = atapi.ATFieldProperty('allowSignupForMultipleSlots')

    def getExtraEmailContent(self):
        if self.isContainedInMasterSignupSheet():
            return self.aq_parent.getExtraEmailContent()
        else:
            return self.extraEmailContent

    def getContactInfo(self):
        if self.isContainedInMasterSignupSheet():
            return self.aq_parent.getContactInfo()
        else:
            return self.contactInfo

    def getExtraFields(self):
        if self.isContainedInMasterSignupSheet():
            return self.aq_parent.getExtraFields()
        else:
            return self.extraFields

    def getAllowSignupForMultipleSlots(self):
        if self.isContainedInMasterSignupSheet():
            return self.aq_parent.getAllowSignupForMultipleSlots()
        else:
            return self.allowSignupForMultipleSlots

    def getDay(self, date):
        query = {'portal_type':'Day', 'Title':date}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) == 0:
            raise ValueError('The date %s was not found.' % date)
        return brains[0].getObject()
        
    def getDays(self):
        query = {'portal_type':'Day'}
        pathQuery = {'query':self.absolute_url_path(), 'depth':1}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=pathQuery,
                                                               sort_on='getDate', sort_order='ascending')
        days = []

        if len(brains) != 0:
            today = DateTime().earliestTime()
            startIndex = 0
            while (startIndex < len(brains)) and (brains[startIndex]['getDate'] < today):
                startIndex += 1

            for i in range(startIndex, len(brains)):
                day = brains[i].getObject()
                days.append(day)
    
        return days

    def removeAllPeople(self):
        for (id, obj) in self.contentItems():
            obj.removeAllPeople()
        
    def exportToCSV(self):
        buffer = StringIO()
        writer = csv.writer(buffer)

        writer.writerow(['SignupSheet', 'Day', 'TimeSlot', 'Name', 'Status', 'Email', 'Extra Info (Phone - Class. - Dept.)'])  
      
        for signupSheet in self.getSignupSheets():
            if not signupSheet.isMasterSignupSheet():
                for day in signupSheet.getDays():
                    for timeSlot in day.getTimeSlots():
                        for person in timeSlot.getPeople():
                            writer.writerow([signupSheet.Title(), day.Title(), timeSlot.Title(), person.Title(),
                                             person.getReviewStateTitle(), person.getEmail(), person.getExtraInfo()])

        result = buffer.getvalue()
        buffer.close()

        return result
    
    def isCurrentUserSignedUpOrWaitingForAnySlot(self):
        username = self.getCurrentUsername()
        return self.isUserSignedUpOrWaitingForAnySlot(username)

    def isUserSignedUpOrWaitingForAnySlot(self, username):
        return self.isUserSignedUpForAnySlot(username) or self.isUserWaitingForAnySlot(username)

    def isCurrentUserSignedUpForAnySlot(self):
        username = self.getCurrentUsername()
        return self.isUserSignedUpForAnySlot(username)
    
    def isUserSignedUpForAnySlot(self, username):
        query = {'portal_type':'Person', 'id':username, 'review_state':'signedup'}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) == 0:
            return False
        else:
            return True

    def isCurrentUserWaitingForAnySlot(self):
        username = self.getCurrentUsername()
        return self.isUserWaitingForAnySlot(username)
    
    def isUserWaitingForAnySlot(self, username):
        query = {'portal_type':'Person', 'id':username, 'review_state':'waiting'}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) == 0:
            return False
        else:
            return True

    def getSlotsCurrentUserIsSignedUpFor(self):
        username = self.getCurrentUsername()
        return self.getSlotsUserIsSignedUpFor(username)

    def getSlotsUserIsSignedUpFor(self, username):
        today = DateTime().earliestTime()
        query = {'portal_type':'Person', 'id':username, 'review_state':'signedup'}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())

        slots = []
        for brain in brains:
            person = brain.getObject()
            timeSlot = person.aq_parent
            day = timeSlot.aq_parent
            if day.getDate() >= today:
                slots.append(timeSlot)
                
        return slots

    def getSlotsCurrentUserIsWaitingFor(self):
        username = self.getCurrentUsername()
        return self.getSlotsUserIsWaitingFor(username)

    def getSlotsUserIsWaitingFor(self, username):
        today = DateTime().earliestTime()
        query = {'portal_type':'Person', 'id':username, 'review_state':'waiting'}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())

        slots = []
        for brain in brains:
            person = brain.getObject()
            timeSlot = person.aq_parent
            day = timeSlot.aq_parent
            if day.getDate() >= today:
                slots.append(timeSlot)
                
        return slots

    def getCurrentUsername(self):
        member = self.portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        return username

    def getSignupSheets(self):
        if self.isMasterSignupSheet():
            return self.getContainedSignupSheets()
        else:
            return [self]

    def getContainedSignupSheets(self):
        query = {'portal_type':'Signup Sheet'}
        pathQuery = {'query':self.absolute_url_path(), 'depth':1}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=pathQuery, sort_on='sortable_title', sort_order='ascending')
        sheets = []

        for brain in brains:
            sheet = brain.getObject()
            sheets.append(sheet)
        return sheets
    
    def getSignupSheet(self, name):
        query = {'portal_type':'Signup Sheet', 'Title':name}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) == 0:
            raise ValueError('The signup sheet %s was not found.' % name)
        return brains[0].getObject()

    def isMasterSignupSheet(self):
        query = {'portal_type':'Signup Sheet'}
        pathQuery = {'query':self.absolute_url_path(), 'depth':1}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=pathQuery)
        if len(brains) != 0:
            return True
        else:
            return False
        
    def isContainedInMasterSignupSheet(self):
        parent = self.aq_parent
        return ISignupSheet.providedBy(parent)

atapi.registerType(SignupSheet, PROJECTNAME)
