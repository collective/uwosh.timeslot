from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

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

class UWOshTimeslotTestCase(ptc.PloneTestCase):
    """A base class for all the tests in this package."""
    
class UWOshTimeslotFunctionalTestCase(UWOshTimeslotTestCase, ptc.FunctionalTestCase):
    pass