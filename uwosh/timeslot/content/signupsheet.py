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

SignupSheetSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.LinesField('extraFields',
        storage=atapi.AnnotationStorage(),
        vocabulary=[('phone','Phone'), ('dept','Department'), ('classification','Employee Classification')],
        widget=atapi.MultiSelectionWidget(label=_(u'Extra Fields'),
                                          description=_(u'Information you want to collect from users beyond name and email.'),
                                          format=_(u'checkbox'))
    ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

SignupSheetSchema['title'].storage = atapi.AnnotationStorage()
SignupSheetSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SignupSheetSchema, folderish=True, moveDiscussion=False)

class SignupSheet(folder.ATFolder):
    """Description of the Example Type"""
    implements(ISignupSheet, IContainsPeople)

    portal_type = "Signup Sheet"
    schema = SignupSheetSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    extraFields = atapi.ATFieldProperty('extraFields')
    
    def getDay(self, date):
        query = {'portal_type':'Day', 'Title':date}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) != 1:
            raise ValueError('The date %s was not found.' % date)
        return brains[0].getObject()

    def getDays(self):
        query = {'portal_type':'Day'}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        days = []
        for brain in brains:
            day = brain.getObject()
            days.append(day)
        return days
        
    def removeAllPeople(self):
        days = self.getDays()
        for day in days:
            day.removeAllPeople()
        
    def exportToCSV(self):
        buffer = StringIO()
        writer = csv.writer(buffer)
        
        writer.writerow(['Day', 'Time', 'Name', 'Status', 'Email', 'Extra Info (Phone - Class. - Dept.)'])
        
        for day in self.getDays():
            for timeSlot in day.getTimeSlots():
                for person in timeSlot.getPeople():
                    writer.writerow([day.Title(), timeSlot.Title(), person.Title(),
					                 person.getReviewStateTitle(), person.getEmail(), person.getExtraInfo()])
					                 
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
            
atapi.registerType(SignupSheet, PROJECTNAME)
