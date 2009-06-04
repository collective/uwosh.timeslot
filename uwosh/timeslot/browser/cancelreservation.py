from zope.interface import implements

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from uwosh.timeslot import timeslotMessageFactory as _

class CancelReservation(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def getCurrentUsername(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        return username
    
    def cancelReservation(self):
    	selectedSlots = self.request.get('selectedSlot', None)
    	
        if selectedSlots != None:
            if type(selectedSlots) == list:
                for slot in selectedSlots:
                    self.deleteUserFromSlot(slot)
            else:
                self.deleteUserFromSlot(selectedSlots)

        self.request.response.redirect(self.context.absolute_url())

    def deleteUserFromSlot(self, slot):
        username = self.getCurrentUsername()

        (signupSheet, date, time) = slot.split(' @ ')
        signupSheet = self.context.getSignupSheet(signupSheet)
        day = signupSheet.getDay(date)
        timeSlot = day.getTimeSlot(time)
        timeSlot.manage_delObjects([username,])
