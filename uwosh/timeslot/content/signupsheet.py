from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ISignupSheet
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

    atapi.StringField('showSlotNames',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(label=_(u'Show Individual Time Slot Names'),
                                   description=_(u'Whether or not to show individual slot names.'))
    ),
))

SignupSheetSchema['title'].storage = atapi.AnnotationStorage()
SignupSheetSchema['description'].storage = atapi.AnnotationStorage()
SignupSheetSchema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}

schemata.finalizeATCTSchema(SignupSheetSchema, folderish=True, moveDiscussion=False)

class SignupSheet(folder.ATFolder):
    implements(ISignupSheet)

    portal_type = 'Signup Sheet'
    schema = SignupSheetSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    extraFields = atapi.ATFieldProperty('extraFields')
    contactInfo = atapi.ATFieldProperty('contactInfo')
    extraEmailContent = atapi.ATFieldProperty('extraEmailContent')
    allowSignupForMultipleSlots = atapi.ATFieldProperty('allowSignupForMultipleSlots')
    showSlotNames = atapi.ATFieldProperty('showSlotNames')

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
            indexOfFirstUsefulObject = 0
            while (indexOfFirstUsefulObject < len(brains)) and (brains[indexOfFirstUsefulObject]['getDate'] < today):
                indexOfFirstUsefulObject += 1

            for i in range(indexOfFirstUsefulObject, len(brains)):
                day = brains[i].getObject()
                days.append(day)
    
        return days

    def removeAllPeople(self):
        for (id, obj) in self.contentItems():
            obj.removeAllPeople()
        
    def exportToCSV(self):
        buffer = StringIO()
        writer = csv.writer(buffer)

        writer.writerow(['Day', 'TimeSlot', 'Name', 'Status', 'Email', 'Extra Info (Phone, Class., Dept.)'])  
        
        for day in self.getDays():
            for timeSlot in day.getTimeSlots():
                for person in timeSlot.getPeople():
                    writer.writerow([day.Title(), timeSlot.Title(), person.Title(), 
                                     person.getReviewStateTitle(), person.getEmail(),
                                     person.getExtraInfo()])
                    
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
        return (len(self.getSlotsUserIsSignedUpFor(username)) > 0)

    def isCurrentUserWaitingForAnySlot(self):
        username = self.getCurrentUsername()
        return self.isUserWaitingForAnySlot(username)
    
    def isUserWaitingForAnySlot(self, username):
        return (len(self.getSlotsUserIsWaitingFor(username)) > 0)

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


atapi.registerType(SignupSheet, PROJECTNAME)
