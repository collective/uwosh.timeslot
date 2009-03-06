from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _


class ISummary(Interface):
    """
    ChooseTimeSlot view interface
    """

    def test():
        """ test method"""


class Summary(BrowserView):
    """
    ChooseTimeSlot browser view
    """
    implements(ISummary)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()


        