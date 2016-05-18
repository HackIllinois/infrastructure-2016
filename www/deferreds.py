### WARNING ###
# This file is in considerable disarray
# and needs to be reworked
### WARNING ###

import StringIO
import csv
import datetime
import logging
from datetime import datetime, timedelta

from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import deferred
from google.appengine.ext import ndb

from www import models
from www.services.storage import StorageService
from www.services.mail import MailService

# sponsor constants
SPONSOR_INTEREST_TYPES = [models.Administrator, models.Staff, models.Hacker, models.Volunteer]
RESUME_DOWNLOAD_URI_TEMPLATE = '%s/download/resume/%s'

# notification constants
ACCEPTANCE_EMAIL_BODY= """
<p>You're in! We hope that you'll join us at HackIllinois from February 19th to February 21st at the University of Illinois at Urbana-Champaign. Please RSVP at <a href="http://www.hackillinois.org/rsvp">hackillinois.org/rsvp</a> before <strong>Monday, February 15th</strong> to confirm your spot. Due to high demand, <strong>your spot may be released</strong> to another participant after this deadline. If you need more time to RSVP, please let us know. </p>
<p>We will be providing buses from schools across the Midwest, gas reimbursements for drivers, or $150 for all other travel. For more information about travel, please see <a href="http://www.hackillinois.org/travel">hackillinois.org/travel</a>. </p>
<p>If you have any questions, please reach out to <a href="mailto:contact@hackillinois.org">contact@hackillinois.org</a>. We will be releasing our second round of acceptances in the upcoming weeks. </p>
"""
ACCEPTANCE_EMAIL_SUBJECT= "HackIllinois Decisions: You're In!"

WAITLIST_EMAIL_BODY = """<p>Thank you for applying to HackIllinois! We've received an overwhelming number of amazing applications this year. We wish we could accept everyone, but due to limited space we are approving applications on a rolling basis. We don't have a spot for you just yet, but we are continually accepting more and more hackers. Meanwhile, you may still go ahead and edit your application if you'd like.</p>
<p>We'll be in touch with more information soon. If you have any questions, please reach out to <a href="mailto:contact@hackillinois.org">contact@hackillinois.org</a>.</p>"""
WAITLIST_EMAIL_SUBJECT = "HackIllinois Decisions: You've been Waitlisted!"

OS_ACCEPTANCE_EMAIL_BODY = """<p>Congratulations on being in the top 5 percent of applicants and being accepted into OpenSource@HackIllinois! We hope that you'll join us at HackIllinois from February 19th to February 21st at the University of Illinois at Urbana-Champaign. Please RSVP at <a href="http://www.hackillinois.org/rsvp">hackillinois.org/rsvp</a> before <strong>Monday, February 15th</strong> to confirm your spot. As an OpenSource candidate, you will also be paired to work with our expert developers. For the list of projects, please see <a href="http://www.hackillinois.org/projects">hackillinois.org/projects</a> and fill out your preferences at <a href="go.hackillinois.org/osPrefs">go.hackillinois.org/osPrefs</a>.</p>
<p>We ask that you RSVP as soon as possible. Due to high demand, <strong>your spot may be released</strong> to another participant after this deadline. If you need more time to RSVP, please let us know.</p>
<p>We will be providing buses from schools across the Midwest, gas reimbursements for drivers, or $150 for all other travel. For more information about travel, please see <a href="http://www.hackillinois.org/travel">hackillinois.org/travel</a>.</p>
<p>If you have any questions, please reach out to <a href="mailto:contact@hackillinois.org">contact@hackillinois.org</a>. We will be releasing our second round of acceptances in the upcoming weeks.</p>"""
OS_ACCEPTANCE_EMAIL_SUBJECT ="OpenSource@HackIllinois - You're In!"

WAITLIST_CLOSED_EMAIL_BODY = """<p>Thank you for applying to HackIllinois. We've had an overwhelming number of applicants this year and were blown away by how passionate people are in the hacker community. Unfortunately, we are unable to extend you an invitation to HackIllinois 2016 at this time.</p>
<p>If you are still interested, we may be accepting walk-ins late Friday evening if we have space. Please keep an eye on your inbox for more details.</p>"""
WAITLIST_CLOSED_EMAIL_SUBJECT = "HackIllinois Decisions"

RSVP_YES_EMAIL_BODY = """<p><b>HackIllinois is tomorrow!</b> In order to make sure everything runs smoothly, we have some important information in this email. Before you arrive, you should join the HackIllinois 2016 attendees group at <a href="go.hackillinois.org/fbgroup">go.hackillinois.org/fbgroup</a> to form teams and brainstorm ideas.</p>
<b>Packing List:</b>
<p>We'll have tons of food and toiletries at the event. But here's some things you should pack:</p>
<ul>
<li>A valid student ID (and a passport if coming internationally)</li>
<li>Personal hygiene items (we'll have disposable toothbrushes, floss, mouthwash and deodorant stocked in the bathrooms)</li>
<li>Sleeping materials such as pillows, blankets and maybe sleeping bags</li>
<li>A labeled laptop and charger</li>
<li>An ethernet adapter for your laptop</li>
<li>A cell phone charger</li>
<li>Imagination!</li>
</ul>

<p>Keep your belongings close! We are not responsible for any lost or stolen items.</p>

<b>Travel Information:</b>
<p>Bus schedules are available at <a href="http://www.hackillinois.org/travel">hackillinois.org/travel</a> and free parking is available at campus lot <a href="http://www.parking.illinois.edu/visitors/campus-maps/campus-parking-map/map1-4">B-22</a>. This lot is northeast of the Siebel Center for Computer Science, where check-in occurs. You can get to it via University Avenue. Please note that you must have RSVPed for a bus to board since several are at capacity. You will not be allowed to board a bus without registration and RSVPing.</p>

<b>Schedule Information:</b>
<p>We are proud to have three VIP speakers for this weekend.The first is Pek Pongpaet, found of his startup Impekable. At his talk, Pek will be talking about his firm's approach to design in software development. Next, we have Chrissy Ziccarelli from Girls Who Code who'll be illustrating her experience as a woman in tech and what we can do to help make the field more inclusive. And finally, we have Tasos Karahalios from IDEO, a renowned design firm in Chicago. Tasos will talk about his role as an IDEO designer and the role hacking plays in designing new products, services and businesses. </p>

<p>Throughout the weekend, we have multiple workshops such as learning how to setup your developer environment or how to set up a Raspberry Pi project. We'll also have a tour of Blue Waters one of the largest supercomputers in America. </p>

<b>Restrictions:</b>
<p>To help us out, please do <b>NOT</b> bring any of the following items.</p>
<ul>
<li>Computer monitors</li>
<li>Desktop computers</li>
<li>Unregistered teammates</li>
</ul>

<p>HackIllinois has had an overwhelming number of hackers apply. As such, we are unable to accommodate extra hackers at the door. <b>Those who are unregistered will be unable to have their team compete for prizes.</b> There may also not be food or swag available. We will be enforcing registration when boarding the buses and during check-in.</p>

<b>Rules: </b>
<p>Before arriving this weekend, please review our Code of Conduct at <a href="http://www.hackillinois.org">hackillinois.org</a>. If you wish to participate in a hardware hack, you should familiarize yourself with traditional lab policies. In short, use common sense; misconduct will not be tolerated, and we reserve the right to remove you at any time. Food is also not allowed in laboratory space and some auditoriums.</p>

<b>Project Submission and Prizes: </b>
<p>Submissions will be due on DevPost by 10am on Sunday at <a href="http://go.hackillinois.org/devpost">http://go.hackillinois.org/devpost</a>. To save yourself time at the event, please make an account now. We will have over 30 sponsored prizes, and the DevPost page will be updated throughout the weekend.</p>

<p>As always, if you have any questions please reach out to <a href="mailto:contact@hackillinois.org">contact@hackillinois.org</a>. </p>

<p>We are super excited to have you here!</p>"""
RSVP_YES_EMAIL_SUBJECT = "HackIllinois Day-Of Logistics"

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<body>
<img style="max-width: 100%%%%" src="%s/assets/img/email-header.png" alt="HackIllinois Banner">
<p>
Hello Explorer!
</p>

%%s

<p>
Sincerely, <br />
The HackIllinois Team
</p>
</body>
</html>
"""

API_EMAIL_SUBJECT = "HackIllinois API Information"
API_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<body>
<img style="max-width: 100%" src="http://hackillinois.org/assets/img/email-header.png" alt="HackIllinois Banner">

<p>
Hi Hackers!
</p>

<p>
We hope you enjoyed your dinner and are settled down for hacking. Here is some relevant information.
</p>

<p>
<strong>Day of Portal</strong><br />
Your day of portal with most important information is available here: <a href="https://hackillinois.org/dayof">https://hackillinois.org/dayof</a>.
</p>

<p>
<strong>Maps</strong><br />
Use the following maps on your journey to explore: <a href="https://hackillinois.org/maps">https://hackillinois.org/maps</a>.
</p>

<p>
<strong>Prizes</strong><br />
Thanks to our awesome sponsors, we have dozens of amazing prizes available here: <a href="http://hackillinois.org/devpost">https://hackillinois.org/devpost</a>.
</p>

<p><strong>APIs</strong><br />
The API list is present at: <a href="https://hackillinois.org/api">https://hackillinois.org/api</a>.
</p>

<p>
<strong>Hardware</strong><br />
The hardware list is present at: <a href="https://hackillinois.org/hardware">https://hackillinois.org/hardware</a>.
</p>

<hr />

<p>
We also have some notes from our sponsors. <br />
</p>

<p>
<strong>Radix</strong> <br />
Radix is offering every hacker a free domain name. Just follow the steps below!
</p>
<ul>
  <li>Step 1: Visit <a href="get.tech/startups">get.tech/startups</a> to submit a request for your domain name. Please adhere to the below instructions
  <ul>
    <li>Every attendee SHOULD use his/her university email address while requesting for a domain name </li>
    <li>Every attendee SHOULD select "HackIllinois" from the dropdown called "Your Community/Hackathon"</li>
  </ul>
</li>
<li>
  Step 2: We will receive this request, and on verification send you a unique coupon code via email.
</li>
<li>
  Step 3: On receiving the coupon code, the recipient can log in to the website <a href="get.tech">get.tech</a> to redeem his or her coupon code and get free domain names.
</li>
</ul>

<p>
<strong>Wolfram</strong> <br />
Wolfram's CEO, Stephen Wolfram, has a letter that he would like you to read. Please visit <a href="http://hackillinois.org/files/wolfram.pdf">this link</a> to find it in its entirety.
</p>

<p>
Best Regards, <br />
HackIllinois Team
</p>
</body>
</html>
"""

# general constants
BATCH_SIZE = 125

def make_resume_url(root_url, key):
    return RESUME_DOWNLOAD_URI_TEMPLATE % (root_url, key)

def make_storage_service(app_config):
    # it is not possible to get the application configuration
    # from inside a deferred, so we must do this
    if not StorageService._CONFIG:
        StorageService._CONFIG = app_config[StorageService._CONFIG_KEY]

    app = None
    return StorageService(app)

def make_mail_service(app_config):
    if not MailService._CONFIG:
        MailService._initialize(app_config)

    app = None
    return MailService(app)

def SponsorEAccessDeferred(app_config, root_url, cursor=None, iteration=0, model_index=0):
    storage = make_storage_service(app_config)

    if model_index >= len(SPONSOR_INTEREST_TYPES):
        storage.save_sponsor_dump(iteration)
        return

    buffer = StringIO.StringIO()
    writer = csv.writer(buffer)

    model = SPONSOR_INTEREST_TYPES[model_index]
    query = model.query()
    query = query.order(models.RegisteredPerson.registration.created)
    results, cursor, more = query.fetch_page(BATCH_SIZE, start_cursor=cursor)

    for result in results:
        parent = result._key.parent().get()
        registration = result.registration
        row = [parent.role, parent.email, result.first_name, result.last_name, \
            registration.age, result.phone_number, registration.gender, registration.school, \
            registration.major, registration.graduation_year, registration.professional_interest,
            registration.github_url, registration.linkedin_url, registration.site_url, result.status if hasattr(result, 'status') else "N/A", \
            make_resume_url(root_url, registration.resume)]

        encoded_row = [entry.encode('ascii', 'ignore') if isinstance(entry, basestring) else entry for entry in row]
        writer.writerow(encoded_row)

    storage.save_temp_sponsor_dump(iteration, buffer)
    iteration += 1

    if not more:
        model_index+= 1
        cursor = None

    deferred.defer(SponsorEAccessDeferred, app_config=app_config, root_url=root_url,
        cursor=cursor, iteration=iteration, model_index=model_index)

def BusChecklistDeferred(app_config, cursor=None, iteration=0):
    storage = make_storage_service(app_config)

    buffer = StringIO.StringIO()
    writer = csv.writer(buffer)

    query = models.Hacker.query()
    query = query.filter(models.Hacker.response.attending == True)
    query = query.order(models.Hacker.response.transportation)
    results, cursor, more = query.fetch_page(BATCH_SIZE, start_cursor=cursor)

    for result in results:
        parent = result._key.parent().get()
        response = result.response
        row = [parent.email, result.first_name, result.last_name, response.transportation]

        encoded_row = [entry.encode('ascii', 'ignore') if isinstance(entry, basestring) else entry for entry in row]
        writer.writerow(encoded_row)

    storage.save_temp_bus_dump(iteration, buffer)
    iteration += 1

    if not more:
        storage.save_bus_dump(iteration)
        return

    deferred.defer(BusChecklistDeferred, app_config=app_config, cursor=cursor, iteration=iteration)

def DashboardStatsDeferred(iteration=0):

    stats = models.DashboardStats.query().get()
    if not stats:
        stats = models.DashboardStats()
        stats.applicant = models.DashboardApplicantStats()
        stats.applicant.software = models.DashboardInitiativeStats()
        stats.applicant.hardware = models.DashboardInitiativeStats()
        stats.applicant.open_source  = models.DashboardInitiativeStats()
        stats.bus = models.DashboardBusStats()
    else:
        stats.incomplete = True

    query = models.Hacker.query()
    if iteration == 0:
        stats.applicant.total = query.count()
    elif iteration == 1:
        stats.applicant.software.accepted = query.filter(ndb.AND(
            models.Hacker.status == 'ACCEPTED', models.Hacker.initiative == 'SOFTWARE', models.Hacker.walk_in == False)).count()
        stats.applicant.software.rsvp = query.filter(ndb.AND(
            models.Hacker.initiative == 'SOFTWARE', models.Hacker.response.attending == True)).count()
    elif iteration == 2:
        stats.applicant.hardware.accepted = query.filter(ndb.AND(
            models.Hacker.status == 'ACCEPTED', models.Hacker.initiative == 'HARDWARE', models.Hacker.walk_in == False)).count()
        stats.applicant.hardware.rsvp = query.filter(ndb.AND(
            models.Hacker.initiative == 'HARDWARE', models.Hacker.response.attending == True)).count()
    elif iteration == 3:
        stats.applicant.open_source.accepted = query.filter(ndb.AND(
            models.Hacker.status == 'ACCEPTED', models.Hacker.initiative == 'OPEN_SOURCE', models.Hacker.walk_in == False)).count()
        stats.applicant.open_source.rsvp = query.filter(ndb.AND(
            models.Hacker.initiative == 'OPEN_SOURCE', models.Hacker.response.attending == True)).count()
    elif iteration == 4:
        stats.applicant.waitlisted = query.filter(models.Hacker.status == 'WAITLISTED').count()
        stats.applicant.rejected = query.filter(models.Hacker.status == 'REJECTED').count()
    elif iteration == 5:
        stats.bus.not_needed = query.filter(models.Hacker.response.transportation == 'NOT_NEEDED').count()
        stats.bus.driving = query.filter(models.Hacker.response.transportation == 'DRIVING').count()
        stats.bus.bus_uic_iit_uchicago = query.filter(models.Hacker.response.transportation == 'BUS_UIC_IIT_UCHICAGO').count()
        stats.bus.bus_northwestern_depaul = query.filter(models.Hacker.response.transportation == 'BUS_NORTHWESTERN_DEPAUL').count()
        stats.bus.bus_ku_mizzou = query.filter(models.Hacker.response.transportation == 'BUS_KU_MIZZOU').count()
        stats.bus.bus_purdue = query.filter(models.Hacker.response.transportation == 'BUS_PURDUE').count()
        stats.bus.bus_rose_hulman = query.filter(models.Hacker.response.transportation == 'BUS_ROSE_HULMAN').count()
        stats.bus.bus_northwestern = query.filter(models.Hacker.response.transportation == 'BUS_NORTHWESTERN').count()
        stats.bus.bus_uic_depaul = query.filter(models.Hacker.response.transportation == 'BUS_UIC_DEPAUL').count()
        stats.bus.bus_iit_uchicago = query.filter(models.Hacker.response.transportation == 'BUS_IIT_UCHICAGO').count()
        stats.bus.bus_florida_georgia_tech = query.filter(models.Hacker.response.transportation == 'BUS_FLORIDA_GEORGIA_TECH').count()
        stats.bus.bus_wisconsin_madison = query.filter(models.Hacker.response.transportation == 'BUS_WISCONSIN_MADISON').count()
    else:
        stats.incomplete = False
        stats.put()
        return

    stats.put()
    deferred.defer(DashboardStatsDeferred, iteration=(iteration + 1))

def DecisionNotificationDeferred(app_config, root_url, wave, cursor=None):

    if not MailService._CONFIG:
        MailService._initialize(app_config)

    app = None
    mail = MailService(app)

    query = models.Hacker.query()
    query = query.filter(models.Hacker.notification_wave == wave)
    hackers, cursor, more = query.fetch_page(BATCH_SIZE, start_cursor=cursor)

    for hacker in hackers:
        if hacker.notification_wave_sent == wave and hacker.notification_sent:
            continue

        body = EMAIL_TEMPLATE % root_url
        subject = 'HackIllinois Decisions'
        if hacker.status == 'ACCEPTED':
            if hacker.initiative == 'OPEN_SOURCE':
                subject = OS_ACCEPTANCE_EMAIL_SUBJECT
                body = body % OS_ACCEPTANCE_EMAIL_BODY
            else:
                subject = ACCEPTANCE_EMAIL_SUBJECT
                body = body % ACCEPTANCE_EMAIL_BODY
        elif hacker.status == 'WAITLISTED':
            subject = WAITLIST_EMAIL_SUBJECT
            body = body % WAITLIST_EMAIL_BODY
        else:
            continue

        parent = hacker._key.parent().get()
        mail.send(parent.email, subject, body, html=True)

        notification_date = datetime.datetime.now()
        hacker.notification_wave_sent = wave
        hacker.notification_sent = notification_date
        hacker.put()

    if not more:
        notification_wave = models.NotificationWave.query(models.NotificationWave.wave == wave).fetch()
        if not notification_wave:
            notification_wave = models.NotificationWave(wave=wave)
        notification_wave.put()
        return

    deferred.defer(DecisionNotificationDeferred, app_config=app_config, root_url=root_url, wave=wave, cursor=cursor)

def WaitlistClosedNotificationDeferred(app_config, root_url, wave, cursor=None):

    if not MailService._CONFIG:
        MailService._initialize(app_config)

    app = None
    mail = MailService(app)

    query = models.Hacker.query()
    query = query.filter(models.Hacker.status == 'WAITLISTED')
    hackers, cursor, more = query.fetch_page(BATCH_SIZE, start_cursor=cursor)

    for hacker in hackers:
        body = EMAIL_TEMPLATE % root_url

        subject = WAITLIST_CLOSED_EMAIL_SUBJECT
        body = body % WAITLIST_CLOSED_EMAIL_BODY

        parent = hacker._key.parent().get()
        mail.send(parent.email, subject, body, html=True)

    if not more:
        notification_wave = models.NotificationWave.query(models.NotificationWave.wave == wave).fetch()
        if not notification_wave:
            notification_wave = models.NotificationWave(wave=wave)
        notification_wave.put()
        return

    deferred.defer(WaitlistClosedNotificationDeferred, app_config=app_config, root_url=root_url, wave=wave, cursor=cursor)


def RSVPedHackerNotificationDeferred(app_config, root_url, wave, cursor=None):

    if not MailService._CONFIG:
        MailService._initialize(app_config)

    app = None
    mail = MailService(app)

    query = models.Hacker.query()
    query = query.filter(models.Hacker.response.attending == True)
    hackers, cursor, more = query.fetch_page(BATCH_SIZE, start_cursor=cursor)

    for hacker in hackers:
        body = EMAIL_TEMPLATE % root_url

        subject = RSVP_YES_EMAIL_SUBJECT
        body = body % RSVP_YES_EMAIL_BODY

        parent = hacker._key.parent().get()
        mail.send(parent.email, subject, body, html=True)

    if not more:
        notification_wave = models.NotificationWave.query(models.NotificationWave.wave == wave).fetch()
        if not notification_wave:
            notification_wave = models.NotificationWave(wave=wave)
        notification_wave.put()
        return

    deferred.defer(RSVPedHackerNotificationDeferred, app_config=app_config, root_url=root_url, wave=wave, cursor=cursor)

def AttendeeInfoDeferred(app_config, cursor=None, iteration=0):
    storage = make_storage_service(app_config)

    buffer = StringIO.StringIO()
    writer = csv.writer(buffer)

    delta = datetime.today() - timedelta(days=60)

    query = models.Hacker.query()
    query = query.filter(models.Hacker.checked_in > delta)
    hackers, cursor, more = query.fetch_page(BATCH_SIZE, start_cursor=cursor)

    for hacker in hackers:
        parent = hacker._key.parent().get()
        row = [parent.email, hacker.initiative]
        if hacker.registration:
            row += [hacker.registration.school, hacker.registration.age, hacker.registration.gender, hacker.registration.major, hacker.registration.graduation_year]
        else:
            row += [None for x in range(5)]
        if hacker.meals:
            row.append(len(hacker.meals))
        else:
            row.append(0)

        encoded_row = [entry.encode('ascii', 'ignore') if isinstance(entry, basestring) else entry for entry in row]
        writer.writerow(encoded_row)

    storage.save_temp_attendee_dump(iteration, buffer)
    iteration += 1

    if not more:
        storage.save_attendee_dump(iteration)
        return

    deferred.defer(AttendeeInfoDeferred, app_config=app_config, cursor=cursor, iteration=iteration)

dinner_friday_lower = datetime(2016, 2, 19, 1, 0, 0)
dinner_friday_upper = datetime(2016, 2, 19, 3, 0, 0)
snack_saturday_lower = datetime(2016, 2, 20, 6, 0, 0)
snack_saturday_upper = datetime(2016, 2, 20, 8, 0, 0)
breakfast_saturday_lower = datetime(2016, 2, 20, 14, 0, 0)
breakfast_saturday_upper = datetime(2016, 2, 20, 16, 0, 0)
lunch_saturday_lower = datetime(2016, 2, 20, 17, 0, 0)
lunch_saturday_upper = datetime(2016, 2, 20, 19, 0, 0)
dinner_saturday_lower = datetime(2016, 2, 21, 1, 0, 0)
dinner_saturday_upper = datetime(2016, 2, 21, 3, 0, 0)
snack_sunday_lower = datetime(2016, 2, 21, 6, 0, 0)
snack_sunday_upper = datetime(2016, 2, 21, 8, 0, 0)
mini_sunday_lower = datetime(2016, 2, 21, 9, 0, 0)
mini_sunday_upper = datetime(2016, 2, 21, 11, 0, 0)
breakfast_sunday_lower = datetime(2016, 2, 21, 14, 0, 0)
breakfast_sunday_upper = datetime(2016, 2, 21, 16, 0, 0)
lunch_sunday_lower = datetime(2016, 2, 21, 17, 0, 0)
lunch_sunday_upper = datetime(2016, 2, 21, 19, 0, 0)
def MealInfoDeferred(cursor=None, meals={}):
    if not meals.get('initialized'):
        meals['initialized'] = True
        meals['SNACK'] = { 'saturday': 0, 'sunday': 0 }
        meals['MINI_MEAL'] = { 'sunday': 0 }
        meals['BREAKFAST'] = { 'saturday': 0, 'sunday': 0 }
        meals['LUNCH'] = { 'saturday': 0, 'sunday': 0 }
        meals['DINNER'] = { 'friday':0 , 'saturday': 0 }

    query = models.Hacker.query()
    people, cursor, more = query.fetch_page(BATCH_SIZE, start_cursor=cursor)

    for person in people:
        if person.meals:
            for meal in person.meals:
                if dinner_friday_lower <= meal.created and meal.created <= dinner_friday_upper:
                    meals[meal.identity]['friday'] += 1
                elif snack_saturday_lower <= meal.created and meal.created <= snack_saturday_upper:
                    meals[meal.identity]['saturday'] += 1
                elif breakfast_saturday_lower <= meal.created and meal.created <= breakfast_saturday_upper:
                    meals[meal.identity]['saturday'] += 1
                elif lunch_saturday_lower <= meal.created and meal.created <= lunch_saturday_upper:
                    meals[meal.identity]['saturday'] += 1
                elif dinner_saturday_lower <= meal.created and meal.created <= dinner_saturday_upper:
                    meals[meal.identity]['saturday'] += 1
                elif snack_sunday_lower <= meal.created and meal.created <= snack_sunday_upper:
                    meals[meal.identity]['sunday'] += 1
                elif mini_sunday_lower <= meal.created and meal.created <= mini_sunday_upper:
                    meals[meal.identity]['sunday'] += 1
                elif breakfast_sunday_lower <= meal.created and meal.created <= breakfast_sunday_upper:
                    meals[meal.identity]['sunday'] += 1
                elif lunch_sunday_lower <= meal.created and meal.created <= lunch_sunday_upper:
                    meals[meal.identity]['sunday'] += 1

    if not more:
        logging.info("THE FINAL MEAL TOTALS ARE: ")
        logging.info(meals)
        return

    deferred.defer(MealInfoDeferred, cursor=cursor, meals=meals)
