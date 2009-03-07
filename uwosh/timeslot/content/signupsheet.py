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

    def getListOfDays(self):
        dayBrains = self.portal_catalog.queryCatalog({'portal_type':'Day'})
        days = []
        for dayBrain in dayBrains:
            day = dayBrain.getObject()
            title = day.Title()
            days.append(title)
        return days
    
    def getDay(self, date):
        dayBrains = self.portal_catalog.queryCatalog({'portal_type':'Day', 'Title':date})
        if len(dayBrains) != 1:
            raise ValueError, "No days were found"
        return dayBrains[0].getObject()

atapi.registerType(SignupSheet, PROJECTNAME)
