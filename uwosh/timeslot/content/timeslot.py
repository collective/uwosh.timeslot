from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from uwosh.timeslot import timeslotMessageFactory as _
from uwosh.timeslot.interfaces import ITimeSlot, ICloneable
from uwosh.timeslot.config import PROJECTNAME
from uwosh.timeslot.widget import TimeWidget


TimeSlotSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.DateTimeField(
        'startTime',
        storage=atapi.AnnotationStorage(),
        widget=TimeWidget(
            label=_('Start Time'))
    ),

    atapi.DateTimeField(
        'endTime',
        storage=atapi.AnnotationStorage(),
        widget=TimeWidget(
            label=_('End Time'))
    ),

    atapi.StringField(
        'name',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_('Name'),
            description=_(u'Optional name'))
    ),

    atapi.IntegerField(
        'maxCapacity',
        storage=atapi.AnnotationStorage(),
        default=1,
        required=True,
        widget=atapi.IntegerWidget(
            label=_(u'Max Capacity'),
            description=_(u'The max number of people'))
    ),

    atapi.BooleanField(
        'allowWaitingList',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u'Allow Waiting List'),
            description=_(u'Check if you want to allow signups to waiting '
                          'list once max capacity is reached'))
    ),

))

TimeSlotSchema['title'].required = False
TimeSlotSchema['title'].widget.visible = {
    'view': 'invisible',
    'edit': 'invisible',
}
TimeSlotSchema['title'].storage = atapi.AnnotationStorage()
TimeSlotSchema['description'].widget.visible = {
    'view': 'invisible',
    'edit': 'invisible',
}
TimeSlotSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(TimeSlotSchema,
                            folderish=True,
                            moveDiscussion=False)


class TimeSlot(folder.ATFolder):
    implements(ITimeSlot, ICloneable)

    portal_type = 'Time Slot'
    schema = TimeSlotSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    maxCapacity = atapi.ATFieldProperty('maxCapacity')
    allowWaitingList = atapi.ATFieldProperty('allowWaitingList')
    startTime = atapi.ATFieldProperty('startTime')
    endTime = atapi.ATFieldProperty('endTime')
    name = atapi.ATFieldProperty('name')

    def Title(self):
        if self.name != '':
            return '%s: %s' % (self.name, self.getTimeRange())
        elif self.getTimeRange() != '':
            return self.getTimeRange()
        else:
            return self.id

    def getTimeRange(self):
        if self.startTime is None or self.endTime is None:
            return ''
        else:
            return '%s - %s' % (self.startTime.strftime('%I:%M %p'),
                                self.endTime.strftime('%I:%M %p'))

    def getLabel(self):
        parentDay = self.aq_parent
        return '%s @ %s' % (parentDay.Title(), self.Title())

    def getNumberOfAvailableSpots(self):
        brains = self.portal_catalog.unrestrictedSearchResults(
            portal_type='Person',
            review_state='signedup',
            path=self.getPath(),
        )
        numberOfPeopleSignedUp = len(brains)
        return max(0, self.maxCapacity - numberOfPeopleSignedUp)

    def isCurrentUserSignedUpForThisSlot(self):
        member = self.portal_membership.getAuthenticatedMember()
        username = member.getUserName()
        return self.isUserSignedUpForThisSlot(username)

    def isUserSignedUpForThisSlot(self, username):
        brains = self.portal_catalog.unrestrictedSearchResults(
            portal_type='Person',
            id=username,
            path=self.getPath(),
        )
        return len(brains) != 0

    def isFull(self):
        return (self.getNumberOfAvailableSpots() == 0
                and not self.allowWaitingList)

    def getPeople(self):
        brains = self.portal_catalog.unrestrictedSearchResults(
            portal_type='Person',
            path=self.getPath(),
            depth=1,
        )
        people = [brain.getObject() for brain in brains]
        return people

    def removeAllPeople(self):
        idsToRemove = [person.id for person in self.getPeople()]
        self.manage_delObjects(idsToRemove)

    # Return a path that is correct even when we are using virutual hosts
    def getPath(self):
        path = self.getPhysicalPath()
        return '/'.join(path)


atapi.registerType(TimeSlot, PROJECTNAME)
