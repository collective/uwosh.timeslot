"""Definition of the Signup Sheet content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ISignupSheet
from uwosh.timeslot.config import PROJECTNAME

SignupSheetSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

SignupSheetSchema['title'].storage = atapi.AnnotationStorage()
SignupSheetSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SignupSheetSchema, folderish=True, moveDiscussion=False)

class SignupSheet(folder.ATFolder):
    """Description of the Example Type"""
    implements(ISignupSheet)

    portal_type = "Signup Sheet"
    schema = SignupSheetSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
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

atapi.registerType(SignupSheet, PROJECTNAME)
