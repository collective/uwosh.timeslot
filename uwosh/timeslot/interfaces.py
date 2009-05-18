from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from uwosh.timeslot import timeslotMessageFactory as _

# -*- extra stuff goes here -*-

class IPerson(Interface):
    """Description of the Example Type"""

class ITimeSlot(Interface):
    """Description of the Example Type"""

class IDay(Interface):
    """Description of the Example Type"""

class ISignupSheet(Interface):
    """Description of the Example Type"""

class IContainsPeople(Interface):
    def removeAllPeople():
        """Removes all signedup/waitinglist people from the object and its children"""
        
class ICloneable(Interface):
    """Object is able to be cloned"""
