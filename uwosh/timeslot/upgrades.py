
default_profile = 'profile-uwosh.timeslot:default'


def from_1_4_8_to_1_5_0(context):
    context.runImportStepFromProfile(default_profile, 'propertiestool')
