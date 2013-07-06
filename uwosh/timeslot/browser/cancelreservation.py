from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName


class CancelReservation(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getCurrentUsername(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        return username

    def cancelReservation(self):
        selectedSlots = self.request.get('selectedSlot', None)
        if type(selectedSlots) != list:
            selectedSlots = [selectedSlots]

        if selectedSlots != [None]:
            for slot in selectedSlots:
                self.deleteCurrentUserFromSlot(slot)

        location = self.context.absolute_url() + '/@@show-reservations'
        self.request.response.redirect(location)

    def deleteCurrentUserFromSlot(self, slot):
        username = self.getCurrentUsername()

        (date, time) = slot.split(' @ ')
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(time)
        timeSlot.manage_delObjects([username, ])
