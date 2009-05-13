"""Definition of the Signup Sheet content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ISignupSheet
from uwosh.timeslot.interfaces import IContainsPeople
from uwosh.timeslot.config import PROJECTNAME

import csv
from StringIO import StringIO
from DateTime import DateTime

SignupSheetSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.LinesField('contactInfo',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(label=_(u'Contact Information'),
                                 description=_(u'Contact information for the manager of the signup sheet'))
    ),

    atapi.LinesField('extraFields',
        storage=atapi.AnnotationStorage(),
        vocabulary=[('phone','Phone'), ('dept','Department'), ('classification','Employee Classification')],
        widget=atapi.MultiSelectionWidget(label=_(u'Extra Fields'),
                                          description=_(u'Information you want to collect from users besides just name and email.'),
                                          format=_(u'checkbox'))
    ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

SignupSheetSchema['title'].storage = atapi.AnnotationStorage()
SignupSheetSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SignupSheetSchema, folderish=True, moveDiscussion=False)

class SignupSheet(folder.ATFolder):
    """Description of SignupSheet"""
    implements(ISignupSheet, IContainsPeople)

    portal_type = "Signup Sheet"
    schema = SignupSheetSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    extraFields = atapi.ATFieldProperty('extraFields')
    contactInfo = atapi.ATFieldProperty('contactInfo')

    def getDay(self, date):
        query = {'portal_type':'Day', 'Title':date}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) != 1:
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
            while (brains[startIndex]['getDate'] < today):
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
        
        for signupSheet in self.getSignupSheets():
            writer.writerow([signupSheet.Title()])
            if not signupSheet.isMasterSignupSheet():
                writer.writerow(['Day', 'Time', 'Name', 'Status', 'Email', 'Extra Info (Phone - Class. - Dept.)'])
        
                for day in signupSheet.getDays():
                    for timeSlot in day.getTimeSlots():
                        for person in timeSlot.getPeople():
                            writer.writerow([day.Title(), timeSlot.Title(), person.Title(),
                                             person.getReviewStateTitle(), person.getEmail(), person.getExtraInfo()])
            writer.writerow([''])

        result = buffer.getvalue()
        buffer.close()

        return result
    
    def isCurrentUserSignedUpForAnySlot(self):
        member = self.portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        return self.isUserSignedUpForAnySlot(username)
    
    def isUserSignedUpForAnySlot(self, username):
        query = {'portal_type':'Person','id':username}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) == 0:
            return False
        else:
            return True

    def getSignupSheets(self):
        query = {'portal_type':'Signup Sheet'}
        pathQuery = {'query':self.absolute_url_path(), 'depth':1}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=pathQuery)
        sheets = [self]
        for brain in brains:
            sheet = brain.getObject()
            sheets.append(sheet)
        return sheets
    
    def getSignupSheet(self, name):
        query = {'portal_type':'Signup Sheet', 'Title':name}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) != 1:
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
