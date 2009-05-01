
from Products.Archetypes.Widget import CalendarWidget

""" A widget that allows a user select time only, because CalendarWidget doesn't
    support this correctly yet.
    This is probably not a good general solution to the problem and I am only
    using it as a workaround here.
"""
class TimeWidget(CalendarWidget):
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""

        fname = field.getName()
        value = form.get(fname, empty_marker)
        if value is empty_marker:
            return empty_marker
        # If JS support is unavailable, the value
        # in the request may be missing or incorrect
        # since it won't have been assembled from the
        # input components. Instead of relying on it,
        # assemble the date/time from its input components.
        hour = form.get('%s_hour' % fname, '--')
        minute = form.get('%s_minute' % fname, '--')
        ampm = form.get('%s_ampm' % fname, '')
        if (hour != '--') and (minute != '--'):
            value = "%s-%s-%s %s:%s" % ('2000', '01', '01', hour, minute)
            if ampm:
                value = '%s %s' % (value, ampm)
        else:
            value = ''
        if emptyReturnsMarker and value == '':
            return empty_marker
        # stick it back in request.form
        form[fname] = value
        return value, {}

"""Definition of the Time Slot content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ITimeSlot
from uwosh.timeslot.interfaces import IContainsPeople
from uwosh.timeslot.interfaces import ICloneable
from uwosh.timeslot.config import PROJECTNAME

from DateTime import DateTime

TimeSlotSchema = folder.ATFolderSchema.copy() + atapi.Schema((                    

    atapi.DateTimeField('startTime',
        storage=atapi.AnnotationStorage(),
        widget=TimeWidget(label=_('Start Time'),
                          show_ymd=False,
                          format='%I:%M %p')
    ),
    
    atapi.DateTimeField('endTime',
        storage=atapi.AnnotationStorage(),
        widget=TimeWidget(label=_('End Time'),
                          show_ymd=False,
                          format='%I:%M %p')
    ),

    atapi.IntegerField('maxCapacity',
        storage=atapi.AnnotationStorage(),
        default=1,
        required=True,
        widget=atapi.IntegerWidget(label=_(u'Max Capacity'),
                                   description=_(u'The max number of people'))
    ),

    atapi.BooleanField('allowWaitingList',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(label=_(u'Allow Waiting List'),
                                   description=_(u'Check if you want to allow signups to waiting list once \
                                                   max capacity is reached'))
    ),     

))

TimeSlotSchema['title'].required = False
TimeSlotSchema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}
TimeSlotSchema['title'].storage = atapi.AnnotationStorage()
TimeSlotSchema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}
TimeSlotSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(TimeSlotSchema, folderish=True, moveDiscussion=False)

class TimeSlot(folder.ATFolder):
    """Description of TimeSlot"""
    implements(ITimeSlot, IContainsPeople, ICloneable)
	
    portal_type = "Time Slot"
    schema = TimeSlotSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    maxCapacity = atapi.ATFieldProperty('maxCapacity')
    allowWaitingList = atapi.ATFieldProperty('allowWaitingList')
    startTime = atapi.ATFieldProperty('startTime')
    endTime = atapi.ATFieldProperty('endTime')

    def Title(self):
    	startTime = self.getStartTime()
    	endTime = self.getEndTime()
    	
    	if startTime == None or endTime == None:
    		return ''
    	else:
    	    return startTime.strftime('%I:%M %p') + ' - ' + endTime.strftime('%I:%M %p')

    def getLabel(self):
        date = self.aq_parent.Title()
        return date + ' @ ' + self.Title()

    def getNumberOfAvailableSpots(self):
        query = {'portal_type':'Person','review_state':'signedup'}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        numberOfPeopleSignedUp = len(brains)
        return max(0, self.maxCapacity - numberOfPeopleSignedUp)

    def isCurrentUserSignedUpForThisSlot(self):
        member = self.portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        return self.isUserSignedUpForThisSlot(username)

    def isUserSignedUpForThisSlot(self, username):
        query = {'portal_type':'Person','id':username}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) == 0:
            return False
        else:
            return True

    def isFull(self):
        return (self.getNumberOfAvailableSpots() == 0 and not self.allowWaitingList)

    def getPeople(self):
        query = {'portal_type':'Person'}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        people = []
        for brain in brains:
            person = brain.getObject()
            people.append(person)
        return people
        
    def getPerson(self, username):
        query = {'portal_type':'Person','id':username}
        brains = self.portal_catalog.unrestrictedSearchResults(query, path=self.absolute_url_path())
        if len(brains) == 0:
            raise ValueError('The Person %s was not found.' % username)
        person = brains[0].getObject()
        return person
        
    def removeAllPeople(self):
        people = self.getPeople()
        idsToRemove = []
        for person in people:
            idsToRemove.append(person.id)
        self.manage_delObjects(idsToRemove)
        return "Success"
        
atapi.registerType(TimeSlot, PROJECTNAME)
