from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _


class IChooseTimeSlotView(Interface):
    """
    ChooseTimeSlot view interface
    """

    def test():
        """ test method"""


class ChooseTimeSlotView(BrowserView):
    """
    ChooseTimeSlot browser view
    """
    implements(IChooseTimeSlotView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def getSignupSheetTitle(self):
        signupSheetBrains = self.portal_catalog.queryCatalog({'portal_type':'Signup Sheet'})
        if len(signupSheetBrains) == 0:
            raise ValueError, "No signup sheets were found"
        signupSheet = signupSheetBrains[0].getObject()
        return signupSheet.Title()

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
        if len(dayBrains) == 0:
            raise ValueError, "No days were found"
        if len(dayBrains) > 1:
            raise ValueError, "Too many days (%s) were found for date %s" % (len(dayBrains), date)
        return dayBrains[0].getObject()
        
    def getTimeSlotsForDay(self, date):
        day = self.getDay(date)
        timeSlotItems = day.contentItems()
        timeSlots = []
        for timeSlot in timeSlotItems:
            timeSlotObj = timeSlot[1]
            title = timeSlotObj.Title()
            timeSlots.append(title)
        return timeSlots

        