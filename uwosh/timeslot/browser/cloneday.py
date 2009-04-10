from zope import interface, schema
from zope.formlib import form
from Products.CMFCore import utils as cmfutils
from Products.Five.browser import pagetemplatefile
from Products.Five.formlib import formbase

from zExceptions import BadRequest

class ICloneDay(interface.Interface):
    numToCreate = schema.Int(title=u'Number to Create', description=u'The number of clones to create', required=True)
    
class CloneDayForm(formbase.PageForm):
    form_fields = form.FormFields(ICloneDay)
    result_template = pagetemplatefile.ZopeTwoPageTemplateFile('cloneday-results.pt')
    success = True
    errors = []

    @form.action('Clone')
    def action_clone(self, action, data):
        self.success = True
        self.errors = []
        numToCreate = data['numToCreate']
        day = self.context
        origId = day.id
        origTitle = day.Title()
        signupSheet = day.aq_inner.aq_parent   
        
        dayContentsCopy = day.manage_copyObjects(day.objectIds())
        
        for i in range(0, numToCreate):
            newId = '%s-%d' % (origId, i)
            newTitle = '%s_%d' % (origTitle, i)
            
            try:
                signupSheet.invokeFactory(id=newId, type_name='Day')
            except BadRequest:
                self.success = False
                self.errors.append("Operation failed because there is already an object named: %s" % newId)
                break
                
            newDay = signupSheet[newId]
            newDay.setTitle(newTitle)
            newDay.manage_pasteObjects(dayContentsCopy)
            
            if i == 0:
                newDay.removeAllPeople()
                dayContentsCopy = newDay.manage_copyObjects(newDay.objectIds())
                
            newDay.reindexObject()     
            
        return self.result_template()
        
