Introduction
============

uwosh.timeslot offers a simple way to allow users of a Plone site to
register for events (for example: training sessions or office hours).

To get started, add a SignupSheet object to your site and add Day and
TimeSlot object to it corresponding to the days and times that you
would like to allow users to register for.

Once the SignupSheet is published any logged in user can view it and signup for
available slots. When a user signs up for a slot they will receive an email
confirmation. When a user returns to the SignupSheet they can see what times they
are signed up for and cancel their registration if they wish.

Each SignupSheet has a Manager Summary tab which allows site managers
to see who is registered for which times and export the registration
list to a .csv file.

You can optionally enable a waitlist feature that does the right thing
when a registered attendee cancels their registration.

Email messages get sent to confirm registrations, cancellations, and
waitlist changes.


Extra Fields
------------
To customize the extra fields selection on the SignupSheet, go to ZMI ->
portal_properties -> site_properties and customize the timeslot_extra_fields
value.

One field per line and each field must be formatted as follows:

  fieldname|fieldlabel
  
If you want your field value to be selectable from a list, do:

  fieldname|fieldname|value1<value label 1>,value2<value label 2>
  
You must format the fields correctly otherwise they'll just get ignored.
