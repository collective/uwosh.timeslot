from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _


class IManagerSummary(Interface):
    """
    ManagerSummary view interface
    """


class ManagerSummary(BrowserView):
    """
    ManagerSummary browser view
    """
    implements(IManagerSummary)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.signupSheet = self.context

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
        
    def removeAllPeopleFromDay(self):
        date = self.request.get('daySelection')
        if date == '':
            raise ValueError, 'No date was selected'
        elif date == 'Remove all people from this day':
            raise ValueError('They''re all the same')
        
        day = self.signupSheet.getDay(date)
        day.removeAllPeople()
        
        self.request.response.redirect(self.context.absolute_url() + '/manager-summary')