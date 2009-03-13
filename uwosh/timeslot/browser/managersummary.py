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

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
        
    def removeAllPeopleFromDay(self):
        date = self.request.get('daySelection')
        if date == '':
            raise ValueError('No date was selected')
        
        day = self.context.getDay(date)
        day.removeAllPeople()
        
        self.request.response.redirect(self.context.absolute_url() + '/manager-summary')