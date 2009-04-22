from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from AccessControl import Unauthorized
from mechanize._mechanize import LinkNotFoundError

from smtplib import SMTPRecipientsRefused
from Products.validation import validation

@onsetup
def setup_uwosh_timeslot():
    """Set up the additional products required for uwosh.timeslot"""
    
    fiveconfigure.debug_mode = True
    import uwosh.timeslot
    zcml.load_config('configure.zcml', uwosh.timeslot)
    fiveconfigure.debug_mode = False
    
    ztc.installPackage('uwosh.timeslot')
    
setup_uwosh_timeslot()
ptc.setupPloneSite(products=['uwosh.timeslot'])

class MockMailHost(object):
    """Make a mock mail host to avoid sending emails when testing.
    """

    def getId(self):
        return 'MailHost'

    def send(self, message, mto=None, mfrom=None, subject=None, encode=None):
        isEmail = validation.validatorFor('isEmail')
        if (isEmail(mto) == 1):
            return
        else:    
            raise SMTPRecipientsRefused
        
    def secureSend(self, message, mto=None, mfrom=None, subject=None, encode=None):
        isEmail = validation.validatorFor('isEmail')
        if (isEmail(mto) == 1):
            return
        else:    
            raise SMTPRecipientsRefused
        

class UWOshTimeslotTestCase(ptc.PloneTestCase):
    """A base class for all the tests in this package."""
    
    def _setup(self):
        ptc.PloneTestCase._setup(self)
        self.portal.MailHost = MockMailHost()
    
class UWOshTimeslotFunctionalTestCase(UWOshTimeslotTestCase, ptc.FunctionalTestCase):
    pass