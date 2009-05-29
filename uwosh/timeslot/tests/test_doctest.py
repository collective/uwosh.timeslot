import unittest
from Testing import ZopeTestCase as ztc

from uwosh.timeslot.tests.base import UWOshTimeslotFunctionalTestCase
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(ztc.FunctionalDocFileSuite(
                      'browser.txt', package='uwosh.timeslot.tests',
                      test_class=UWOshTimeslotFunctionalTestCase))
    suite.addTest(ztc.FunctionalDocFileSuite(
                      'browser-nestedsheets.txt', package='uwosh.timeslot.tests',
                      test_class=UWOshTimeslotFunctionalTestCase))
    return suite
