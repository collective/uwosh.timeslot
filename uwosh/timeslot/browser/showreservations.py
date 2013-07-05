from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile


class IShowReservations(Interface):
    pass


class ShowReservations(BrowserView):
    implements(IShowReservations)

    pageTemplate = ZopeTwoPageTemplateFile('showreservations.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.isCurrentUserLoggedIn():
            return self.pageTemplate()
        else:
            location = '{0}/login_form?came_from=./@@show-reservations'.format(
                self.context.absolute_url()
            )
            self.request.response.redirect(location)

    def isCurrentUserLoggedIn(self):
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return 'Authenticated' in member.getRoles()
