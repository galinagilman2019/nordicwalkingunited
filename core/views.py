import icalendar
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import TemplateDoesNotExist
from django.utils.translation import gettext_lazy as _
from django_date_extensions.fields import ApproximateDate
from django.core.exceptions import ValidationError
from patreonmanager.models import FundraisingStatus
from django.core.paginator import Paginator
from story.models import Story
from .models import Event, User, Submission
from organize.models import EventApplication
from django.contrib import messages
from django.shortcuts import redirect
from formtools.wizard.views import NamedUrlSessionWizardView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.core.cache import cache
from django.core.mail import send_mail


from core.forms import (
    OrganizersFormSet,
    WorkshopForm,
    CustomUserCreateForm,
    UserForm,
    SubmissionForm,
)
from django import template
from organize.constants import DEPLOYED
register = template.Library()
from .models.nwu_manual import NWU_Manual
import logging
logger = logging.getLogger(__name__)
# ==============================
# NWU RULES HTML BLOCKS
# ==============================

PRIVACY_HTML = '''
<h3>Nordic Walking United (NWU) Privacy Policy</h3>
<p><strong>Effective Date:</strong> January 1, 2026<br>
<strong>Last Updated:</strong> January 1, 2026</p>

<p>At Nordic Walking United (NWU), your privacy matters. Respecting personal information is an important part of respecting each person who walks, connects, and participates in our global community. This Privacy Policy explains what we collect, how we use it, and the simple ways you can stay in control.</p>

<ol>
  <li>
    <h4>Who We Are</h4>
    <p>NWU is a global nonprofit community where people can learn about Nordic Walking, join events, host walks, and share experiences.</p>
  </li>

  <li>
    <h4>Information We Collect</h4>
    <p>We collect only the information needed to help you participate in the NWU community, such as:</p>
    <ul>
      <li>Full name and email address</li>
      <li>General location (city, region, and country)</li>
      <li>Username and password</li>
      <li>Optional profile photo or short bio</li>
      <li>Comments, posts, photos, or messages you share</li>
    </ul>
    <p>We do not collect health data, financial information, or government IDs unless you choose to share something for safety during a specific event.</p>
  </li>

  <li>
    <h4>How We Use Your Information</h4>
    <p>We use your information to:</p>
    <ul>
      <li>Create and manage your NWU account</li>
      <li>Help you join or host events</li>
      <li>Allow communication between members and hosts</li>
      <li>Send updates and reminders</li>
      <li>Keep the website running safely and smoothly</li>
    </ul>
    <p>NWU does not sell, rent, or trade your personal information.</p>
  </li>

  <li>
    <h4>When We Share Information</h4>
    <p>We share information only when necessary:</p>
    <ul>
      <li>With event hosts so they can communicate with participants</li>
      <li>With trusted technical providers (such as email or website services) who must protect your data</li>
      <li>If required by law, to respond to a lawful request</li>
    </ul>
  </li>

  <li>
    <h4>How We Store and Protect Your Data</h4>
    <p>Your information is stored securely on protected servers that use:</p>
    <ul>
      <li>Encrypted connections</li>
      <li>Password protection</li>
      <li>Limited administrative access</li>
    </ul>
    <p>We use strong security measures — both technical and administrative — to protect your data from unauthorized access or misuse.</p>
  </li>

  <li>
    <h4>Your Rights</h4>
    <p>No matter where you live, you have the right to:</p>
    <ul>
      <li>Request a copy of your personal information</li>
      <li>Ask us to correct or delete your data</li>
      <li>Withdraw consent for communications</li>
    </ul>
    <p>You can make any of these requests through the CONTACT US tab on the main page. We will respond with care, clarity, and respect.</p>
  </li>

  <li>
    <h4>Data Retention</h4>
    <p>We keep your information only as long as needed to provide NWU services. You may request full deletion of your account and personal data at any time.</p>
  </li>

  <li>
    <h4>Children and Families</h4>
    <p>Families are welcome at NWU. Accounts for minors (16 years old or younger) must be created or supervised by a parent or legal guardian.</p>
  </li>

  <li>
    <h4>Updates to This Policy</h4>
    <p>We may update this Privacy Policy as NWU grows or as laws change. The most recent version will always be available on our website in the RESOURCES tab under GUIDELINES.</p>
  </li>

  <li>
    <h4>Contact Us</h4>
    <p>If you have questions or requests about your personal information, please contact us through the CONTACT US tab on the main page. We’re always happy to help.</p>
  </li>
</ol>

<p>Your privacy is part of your dignity. We promise to treat your information with the same care and respect that guide every walk, every smile, and every community moment we share.</p>
'''

PHOTO_HTML = '''
<h3>Nordic Walking United (NWU) Photo &amp; Media Release</h3>
<p><strong>Effective Date:</strong> January 1, 2026<br>
<strong>Last Updated:</strong> January 1, 2026</p>

<p>Nordic Walking United (NWU) celebrates the joy, connection, and wellbeing that grow when people walk together. From time to time, photos or videos may be taken during NWU events — or shared by participants — to highlight the spirit of our global community. This Photo &amp; Media Release explains how such images or recordings may be used and how we respect your rights and privacy.</p>

<ol>
  <li>
    <h4>Permission to Use Images</h4>
    <p>Unless you clearly inform the event host that you do <strong>not</strong> want your photo or video taken, you agree to the following:</p>
    <p>By participating in NWU activities, attending an event, or uploading photos or videos to the NWU platform, you grant NWU permission to:</p>
    <ul>
      <li>Use your image, likeness, voice, or appearance in photos, videos, or other media taken during NWU activities.</li>
      <li>Display, reproduce, publish, or share these materials for educational or promotional purposes, including on the NWU website, social media, newsletters, presentations, and printed materials.</li>
      <li>Edit or format the media while always maintaining respectful and positive representation.</li>
    </ul>
    <p>All media will be used in a community-focused manner that aligns with NWU’s mission of health, connection, and giving back.</p>
  </li>

  <li>
    <h4>No Compensation</h4>
    <p>Participation in NWU events and inclusion in photographs or recordings is voluntary. You agree that your participation does not entitle you to:</p>
    <ul>
      <li>financial compensation,</li>
      <li>ownership rights, or</li>
      <li>approval over final materials.</li>
    </ul>
  </li>

  <li>
    <h4>Respect for Privacy</h4>
    <p>NWU values your dignity and privacy. We will never:</p>
    <ul>
      <li>sell your photos,</li>
      <li>license your image to third parties, or</li>
      <li>use any media in a harmful, misleading, or inappropriate way.</li>
    </ul>
    <p>If you would like a specific image or video removed, please contact us through the CONTACT US tab on the website. We will review your request promptly and respectfully.</p>
  </li>

  <li>
    <h4>Minors and Families</h4>
    <p>For participants under 16 years old, a parent or legal guardian must provide permission for their image to be used. Parents or guardians may notify the event host at any time if they prefer that their child not be photographed or filmed.</p>
  </li>

  <li>
    <h4>Withdrawal of Consent</h4>
    <p>You may withdraw your permission at any time by contacting NWU in writing or through the CONTACT US tab on our website. After receiving your request, NWU will make reasonable efforts to:</p>
    <ul>
      <li>remove the media from future use, and</li>
      <li>delete it from NWU-controlled platforms.</li>
    </ul>
    <p>Please note: materials already shared publicly (for example, social media posts or printed materials) may remain accessible.</p>
  </li>
</ol>

<p>We honor every step, every story, and every moment shared within our walking community. Thank you for being here and learning about NWU. It means a lot to walk this path of wellbeing together.</p>
'''

TERMS_HTML = '''
<h3>Nordic Walking United (NWU) Terms of Service</h3>
<p><strong>Effective Date:</strong> January 1, 2026<br>
<strong>Last Updated:</strong> January 1, 2026</p>

<p>Welcome to Nordic Walking United (NWU) — a place where people around the world come together to walk, breathe, connect, and feel better. By creating an account or using our website, you agree to the terms below.</p>

<ol>
  <li>
    <h4>Accepting These Terms</h4>
    <p>When you use the NWU website or create an account, you agree to follow these Terms of Service, Privacy Policy and Photo Media Release. If any part makes you uncomfortable, please do not use the website.</p>
    <p>From time to time, NWU may update these Terms. If we do, the newest version will always be available on our website in the RESOURCES tab under GUIDELINES. If you continue using the platform after changes, it means you accept the updated Terms.</p>
  </li>

  <li>
    <h4>What NWU Is — and What It Isn’t</h4>
    <p>NWU is a global nonprofit community, not a company and not a tour operator. We simply provide a safe, welcoming space where people can:</p>
    <ul>
      <li>Learn about Nordic Walking</li>
      <li>Connect with others</li>
      <li>Find or host local Nordic walks</li>
      <li>Find or host NWU giving-back events</li>
      <li>Share stories, photos, and encouragement</li>
    </ul>
    <p>Every event listed on the website is created by an independent volunteer host, who chooses the route, time, pace, and group size. NWU does not supervise or control these local gatherings.</p>
  </li>

  <li>
    <h4>How We Treat Each Other (Community Conduct)</h4>
    <p>NWU is built on kindness. By joining, you agree to help keep our space safe and respectful by:</p>
    <ul>
      <li>Using warm, friendly, and considerate language</li>
      <li>Treating every member with dignity</li>
      <li>Not posting disrespectful, harmful, or offensive content</li>
      <li>Not sharing false, misleading, or illegal information</li>
      <li>Respecting others’ privacy, boundaries, and wellbeing</li>
      <li>Being mindful of the tone and spirit of your posts</li>
    </ul>
    <p>If needed, NWU may remove content or close accounts to protect the community.</p>
  </li>

  <li>
    <h4>Participating in Events</h4>
    <p>Joining any NWU walk or activity is your personal choice. Outdoor movement always involves natural risks — uneven paths, weather, animals, or simple missteps.</p>
    <p>When you join an event:</p>
    <ul>
      <li>You take part voluntarily</li>
      <li>You accept responsibility for your own safety</li>
      <li>You agree to walk at your own pace and listen to your body</li>
      <li>You understand that NWU cannot be held responsible for injuries or incidents</li>
    </ul>
    <p>Before joining an event, you might be asked to read and accept the local Event Waiver &amp; Release, which explains these things clearly.</p>
  </li>

  <li>
    <h4>When You Share Photos or Words</h4>
    <p>You remain the owner of everything you post — photos, comments, notes, or stories. By sharing content on NWU, you give us permission to:</p>
    <ul>
      <li>Display it on our website</li>
      <li>Share it with the community</li>
      <li>Use it respectfully to celebrate NWU’s mission</li>
    </ul>
    <p>We will never sell your content or use it in a way that goes against your wishes. You agree to upload only content you created yourself or have permission to share.</p>
  </li>

  <li>
    <h4>NWU’s Website and Materials</h4>
    <p>Everything created by NWU — our name, logo, text, graphics, and website design — belongs to the NWU organization. You are welcome to share NWU materials for personal or educational use, but please do not sell, copy, or use them for commercial purposes without our written permission.</p>
  </li>

  <li>
    <h4>Your Account and Security</h4>
    <p>You are responsible for keeping your password private and your account secure. If something doesn’t look right or you believe someone accessed your account, please contact us through the CONTACT US tab on our main page so we can help.</p>
  </li>

  <li>
    <h4>Your Privacy Matters</h4>
    <p>Your personal information is handled with care and respect. We collect only what is truly necessary for you to participate in the NWU community. All details about data protection are explained clearly in our NWU Privacy Policy, which you can read and agree to when you create an account.</p>
  </li>

  <li>
    <h4>Health and Wellness Information</h4>
    <p>NWU shares inspiration, encouragement, and general wellness ideas. Nothing on our website is medical advice. If you have health questions or concerns, please speak with a healthcare professional before joining vigorous physical activity.</p>
  </li>

  <li>
    <h4>Limitation of Liability</h4>
    <p>Even though NWU is built with care, goodwill, and volunteer energy, we cannot guarantee perfect safety or perfect information. To the extent allowed by law, NWU, its volunteers, and its event hosts are not responsible for:</p>
    <ul>
      <li>Injuries or accidents</li>
      <li>Lost or damaged belongings</li>
      <li>Disagreements or misunderstandings</li>
      <li>Inaccurate information posted by others</li>
      <li>Any issues that may arise from using the website or joining an event</li>
    </ul>
    <p>You agree to take responsibility for your own choices, activities, and wellbeing.</p>
  </li>

  <li>
    <h4>Ending or Pausing Accounts</h4>
    <p>NWU may temporarily suspend or permanently remove accounts that:</p>
    <ul>
      <li>Violate these Terms</li>
      <li>Harm other members</li>
      <li>Misuse the platform</li>
      <li>Break local laws</li>
    </ul>
    <p>You may delete your own account at any time.</p>
  </li>

  <li>
    <h4>Guiding Principles</h4>
    <p>Because NWU is a worldwide community, these Terms are guided by universal principles of fairness, respect, and good faith.</p>
  </li>

  <li>
    <h4>Questions or Concerns</h4>
    <p>We’re always here to help. If something is unclear or you have concerns, please contact us through the Contact Us page on our website. These Terms are part of how we care for one another — protecting our community space and preserving the joy of Nordic walking for all.</p>
  </li>
</ol>
'''

# ORGANIZE FORM #
FORMS = (
    ("organizers", OrganizersFormSet),
    ("workshop", WorkshopForm),
)
TEMPLATES = {
    "organizers": "core/form/step1_organizers.html",
    "workshop": "core/form/step2_workshop.html",

}


def event_rules(request, uuuid):
    event = get_object_or_404(Event, uuuid=uuuid)

    rules = {
        "privacy": PRIVACY_HTML,
        "photo": PHOTO_HTML,
        "terms": TERMS_HTML,
    }

    if request.method == "POST":
        # Checkbox required in POST
        if "accept_rules" not in request.POST:
            messages.error(request, "Please confirm that you have read and accept all three sections.")
            return render(request, "event/event_rules.html", {
                "event": event,
                "rules": rules,
            })

        # Mark in session that this user accepted the rules for this event
        request.session[f"accepted_rules_{event.uuuid}"] = True

        # If user is already logged in, store acceptance on their profile
        if request.user.is_authenticated:
            user = request.user
            user.rules_accepted = True
            user.rules_accepted_at = timezone.now()
            user.save(update_fields=["rules_accepted", "rules_accepted_at"])

        # Redirect to registration (with ?event=UUID)
        register_url = reverse("core:register") + f"?event={event.uuuid}"
        return redirect(register_url)

    return render(request, "event/event_rules.html", {
        "event": event,
        "rules": rules,
    })
def nwu_rules(request):
    """
    Public static version of the NWU rules — no event, no checkbox, no POST.
    """
    rules = {
        "privacy": PRIVACY_HTML,
        "photo": PHOTO_HTML,
        "terms": TERMS_HTML,
    }

    return render(request, "core/nwu_rules.html", {
        "rules": rules,
    })

"""
def login_page(request):
    page = 'login'

    if request.method == "POST":
        print("LOGIN_PAGE EVENT UUID:", request.POST.get('event'))
        user = authenticate(
            email=request.POST['email'],

            password=request.POST['password']

            )

        if user is not None:
            login(request, user)
            event_uuid = request.POST.get('event')
            #event_uuid = request.GET.get('event') or request.POST.get('event')
            print("EVENT UUID:", request.POST.get('event'))
            messages.info(request, 'You have successfully logged in.')

            if event_uuid:
                return redirect('core:eventnwu', pk=event_uuid)
            return redirect('core:index')
        else:
            messages.error(request, 'Email OR Password is incorrect')
            event_uuid = request.POST.get('event')
            #return redirect('core:login')
            return redirect('core:eventnwu', pk=event_uuid)
    context = {'page':page}

    return render(request, 'event/login_register.html', context)
"""

def login_page(request):
    page = "login"

    # ---------------------------------------------------
    # 1) Get event UUID from GET or POST
    # ---------------------------------------------------
    event_uuid = request.GET.get("event") or request.POST.get("event")
    event_obj = None

    if event_uuid:
        event_obj = Event.objects.filter(uuuid=event_uuid).first()

    # ---------------------------------------------------
    # 2) Handle Login POST
    # ---------------------------------------------------
    if request.method == "POST":
        user = authenticate(
            email=request.POST.get("email"),
            password=request.POST.get("password")
        )

        if user is not None:
            login(request, user)
            messages.info(request, "You have successfully logged in.")

            # Redirect back to event if exists
            if event_uuid:
                return redirect('core:eventnwu', pk=event_uuid)
            return redirect('core:index')

        else:
            messages.error(request, "Email OR Password is incorrect")

            # If event exists → return user back to event page
            if event_uuid:
                return redirect('core:eventnwu', pk=event_uuid)

            return redirect('core:login')

    # ---------------------------------------------------
    # 3) GET request → show login page
    # ---------------------------------------------------
    context = {
        "page": page,
        "event_obj": event_obj,      # <-- here is the event name for template
        "event_uuid": event_uuid,    # still needed for hidden input
    }

    return render(request, "event/login_register.html", context)


"""
def register_page(request):
    print("REGISTER_PAGE EVENT UUID:", request.POST.get('event'))
    event_uuid = request.GET.get('event') or request.POST.get('event')
    form = CustomUserCreateForm(request.FILES)

    context = {'form': form, 'page': 'register'}

    if event_uuid:
        eventnwu = Event.objects.filter(uuuid=event_uuid).first()
        context['eventnwu'] = eventnwu

    if request.method == 'POST':
        form = CustomUserCreateForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)

            if event_uuid:
                return redirect('core:eventnwu', pk=event_uuid)

            return redirect('core:index')

    return render(request, 'event/login_register.html', context)

def register_page(request):
    event_uuid = request.GET.get("event") or request.POST.get("event")

    # If tied to an event, enforce rules acceptance first
    if event_uuid and not request.session.get(f"accepted_rules_{event_uuid}", False):
        return redirect("core:event_rules", uuuid=event_uuid)

    eventnwu = None
    if event_uuid:
        eventnwu = Event.objects.filter(uuuid=event_uuid).first()

    if request.method == "POST":
        form = CustomUserCreateForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()

            user.rules_accepted = True
            user.rules_accepted_at = timezone.now()
            user.save(update_fields=["rules_accepted", "rules_accepted_at"])

            login(request, user)

            if event_uuid:
                return redirect("core:eventnwu", pk=event_uuid)
            return redirect("core:index")

        # ✅ show message only when invalid
        messages.error(request, _("Please fix the highlighted fields below."))

    else:
        form = CustomUserCreateForm()

    context = {"form": form, "page": "register", "eventnwu": eventnwu}
    return render(request, "event/login_register.html", context)
"""
def register_page(request):
    event_uuid = request.GET.get("event") or request.POST.get("event")

    # Enforce rules acceptance if coming from event
    if event_uuid and not request.session.get(f"accepted_rules_{event_uuid}", False):
        return redirect("core:event_rules", uuuid=event_uuid)

    eventnwu = None
    if event_uuid:
        eventnwu = Event.objects.filter(uuuid=event_uuid).first()

    if request.method == "POST":
        form = CustomUserCreateForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()

            user.rules_accepted = True
            user.rules_accepted_at = timezone.now()
            user.save(update_fields=["rules_accepted", "rules_accepted_at"])

            # ✅ SEND WELCOME EMAIL
            send_welcome_email(user)

            login(request, user)

            if event_uuid:
                return redirect("core:eventnwu", pk=event_uuid)

            return redirect("core:index")

        # show message only when invalid
        messages.error(request, _("Please fix the highlighted fields below."))

    else:
        form = CustomUserCreateForm()

    context = {
        "form": form,
        "page": "register",
        "eventnwu": eventnwu,
    }
    return render(request, "event/login_register.html", context)

#_________________________________________________________________________


@login_required(login_url='/login')
def account_page(request):
    user = request.user

    event_uuid = request.GET.get('event')
    eventnwu = None
    if event_uuid:
        # .first() so we don’t 404 if something is off
        eventnwu = Event.objects.filter(uuuid=event_uuid).first()

    context = {
        "user": user,
        "eventnwu": eventnwu,
        "event_uuid": event_uuid,
    }
    return render(request, "event/account.html", context)


#_________________________________________________________________________


@login_required(login_url='/login')
def edit_account(request):
    event_uuid = request.GET.get('event') or request.POST.get('event')

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been updated!")
            if event_uuid:
                return redirect(f"{reverse('core:account')}?event={event_uuid}")
            return redirect('core:account')
    else:
        form = UserForm(instance=request.user)

    context = {
        'form': form,
        'event_uuid': event_uuid,
    }
    return render(request, 'event/user_form.html', context)

def send_welcome_email(user):
    name = user.name or user.first_name or user.email

    subject = _("Welcome to Nordic Walking United 🌿")

    message = _(
        "Dear %(name)s,\n\n"
        "Welcome to Nordic Walking United! 🌿\n\n"
        "We’re so happy to have you join our wonderful NWU community. "
        "By registering on the NWU website, you’ve taken a meaningful step "
        "toward movement, health, connection, and enjoying time outdoors "
        "with a friendly and supportive group.\n\n"
        "Before attending an NWU event, please take a moment to review our "
        "Code of Conduct. It helps ensure that all NWU events remain safe, "
        "respectful, inclusive, and enjoyable for everyone.\n\n"
        "👉 Code of Conduct:\n"
        "https://nordicwalkingunited.org/en/code-of-conduct/\n\n"
        "We also encourage you to explore our tutorials — they’ll help you "
        "feel confident and well prepared for your event:\n\n"
        "👉 NWU Tutorials:\n"
        "https://nordicwalkingunited.org/en/tutorials/\n\n"
        "Have questions about the event? Once you’ve signed up, feel free "
        "to write a comment — the Event Organizers are always happy to help!\n\n"
        "We look forward to walking together soon!\n\n"
        "With joy in every step,\n"
        "Nordic Walking United Team"
    ) % {"name": name}

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=True,  # important for smooth UX
    )





#Begin
#@login_required(login_url='/login')
#def registration_confirmation(request, pk):
#    event = Event.objects.get(id=pk)

#    if request.method == 'POST':
#        event.participants.add(request.user)
#        return redirect('event', pk=event.id)


#    return render(request, 'event_confirmation.html', {'event':event})
#Modify
@login_required(login_url='/login')

def registration_confirmation(request, pk):
    eventnwu = get_object_or_404(Event, uuuid=pk)
    print("EVENT id:", eventnwu.uuuid)

    if request.method == 'POST':
        print("user:", request.user)
        eventnwu.participants.add(request.user)
        return redirect('core:eventnwu', pk=eventnwu.uuuid)

    return render(request, 'event/event_confirmation.html', {'eventnwu': eventnwu})

#End

class OrganizeFormWizard(NamedUrlSessionWizardView):
    def get_template_names(self):
        logger.debug("CORE Debugging information here for OrganizeFormWizard.")
        logger.debug(f" CORE Getting template for step: {self.steps.current}")
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        logger.debug("CORE Entering the 'done' method.")  # Log entry into the done method
# Get an instance of a logger

        # Process the data from the forms
        data_dict = {}
        logger.debug("CORE Initialized an empty data_dict.")  # Inform that the data_dict is ready to gather data
        for form in form_list:
            data_dict.update(form.get_data_for_saving())
            logger.debug(f"CORE Updated data_dict with form data: {data_dict}")  # Log the updated state of data_dict
        organizers_data = data_dict.pop("coorganizers", [])

        try:
            event = Event.objects.create(**data_dict)

            logger.info(f"CORE Created Event: {event}")  # Log successful Event creation
            for organizer in organizers_data:
                event.coorganizers.create(**organizer)

                logger.debug(f"CORE Created coorganizer: {organizer}")  # Log the creation of each coorganizer
                try:
                    user = User.objects.get(email=organizer["email"])
                    if user.is_blacklisted:
                        event.organizer_blacklisted = True
                        event.save()
                except User.DoesNotExist:
                    logger.info(f"CORE No user found with email: {organizer['email']}")  # Log if user does not exist
                    pass
#            send_application_confirmation(application)
#            send_application_notification(application)
        except ValidationError as error:
            messages.error(self.request, error.messages[0])
            return redirect("core:index")
        return redirect("core:form_thank_you")
organize_form_wizard = OrganizeFormWizard.as_view(
    FORMS,

    url_name="core:form_step",
)
##################################################################
def home_page(request):
    deployed_qs = EventApplication.objects.filter(status=DEPLOYED)

    selected_country = request.GET.get("country") or ""
    selected_city = request.GET.get("city") or ""

    if selected_country:
        deployed_qs = deployed_qs.filter(country=selected_country)
    if selected_city:
        deployed_qs = deployed_qs.filter(city=selected_city)

    countries = (
        EventApplication.objects.filter(status=DEPLOYED)
        .values_list("country", flat=True)
        .distinct()
        .order_by("country")
    )
    cities = (
        EventApplication.objects.filter(status=DEPLOYED, country=selected_country)
        .values_list("city", flat=True)
        .distinct()
        .order_by("city")
        if selected_country else []
    )

    # ✅ Pagination only if no filters
    if not selected_country and not selected_city:
        paginator = Paginator(deployed_qs, 12)  # 12 groups per page
        page_number = request.GET.get("page")
        nwgroup_page_obj = paginator.get_page(page_number)
    else:
        nwgroup_page_obj = deployed_qs  # no pagination when filtered

    context = {
        "nwcount": deployed_qs.count(),
        "nwgroup_page_obj": nwgroup_page_obj,
        "countries": countries,
        "cities": cities,
        "selected_country": selected_country,
        "selected_city": selected_city,
    }
    return render(request, "core/home_nwu.html", context)



# core/views.py

# core/views.py


def index(request):
    blogs = Story.objects.filter(is_story=False).order_by("-created")[:3]
    city_count = Event.objects.values("city").distinct().count()
    nwgroup_count = Event.objects.values("nwgroup").distinct().count()
    country_count = Event.objects.values("country").distinct().count()
    organizers = User.objects.all().count()
    stories = Story.objects.filter(is_story=True).order_by("-created")[:2]

    today = timezone.now().date()

    # ✅ Only ready + upcoming events
    future_events = (
        Event.objects.filter(
            is_page_live=True,
            is_on_homepage=True,
            date__gte=today,
        )
        .order_by("date")
    )
    future_events_count = future_events.count()

    main_organizers = User.objects.filter(event__isnull=False).distinct().order_by()
    team_members = User.objects.filter(event__team__isnull=False).distinct().order_by()
    all_team_members = main_organizers.union(team_members).count()

    return render(
        request,
        "core/index.html",
        {
            "future_events": future_events,
            "future_events_count": future_events_count,
            "stories": stories,
            "blogposts": blogs,
            "patreon_stats": FundraisingStatus.objects.all().first(),
            "organizers_count": organizers,
            "cities_count": city_count,
            "nwgroups_count": nwgroup_count,
            "country_count": country_count,
            "all_team_members": all_team_members,
        },
    )


def events(request):
    selected_country = request.GET.get("country", "")
    selected_city = request.GET.get("city", "")

    today = timezone.now().date()

    # ✅ Only READY events
    future_events = Event.objects.filter(
        is_page_live=True,
        is_on_homepage=True,
        date__gte=today,
    ).order_by("date")

    past_events = Event.objects.filter(
        is_page_live=True,
        date__lt=today,
    ).order_by("-date")

    # Gather all available countries (you may or may not want to restrict this)
    countries = (
        Event.objects.values_list("country", flat=True)
        .distinct()
        .order_by("country")
    )

    # If a country is selected, filter events and prepare city list
    cities = []
    if selected_country:
        future_events = future_events.filter(country=selected_country)
        past_events = past_events.filter(country=selected_country)
        cities = (
            Event.objects.filter(country=selected_country, is_page_live=True)
            .values_list("city", flat=True)
            .distinct()
            .order_by("city")
        )

    # If a city is selected, apply further filtering
    if selected_city:
        future_events = future_events.filter(city=selected_city)
        past_events = past_events.filter(city=selected_city)

    context = {
        "future_events": future_events,
        "past_events": past_events,
        "countries": countries,
        "cities": cities,
        "selected_country": selected_country,
        "selected_city": selected_city,
    }

    return render(request, "core/events.html", context)




# core/views.py



def events_map(request):
    country = (request.GET.get("country") or "").strip()
    city = (request.GET.get("city") or "").strip()

    today = timezone.now().date()

    qs = Event.objects.filter(
        is_page_live=True,
        date__gte=today,
    )

    if country:
        qs = qs.filter(country=country)
    if city:
        qs = qs.filter(city=city)

    return render(
        request,
        "core/events_map.html",
        {
            "events": qs,
            "mapbox_access_token": settings.MAPBOX_ACCESS_TOKEN,
            "selected_country": country,
            "selected_city": city,
        },
    )



def resources(request):
    return render(request, "core/resources.html", {})

def nwu_resources(request):
    # Default audience is "general"
    audience = request.GET.get("audience", "handbook")

    manuals = NWU_Manual.objects.all()

    # Apply filtering unless "all" is requested
    if audience != "all":
        manuals = manuals.filter(audience=audience)

    manuals = manuals.order_by("order", "title")

    context = {
        "manuals": manuals,
        "audience": audience,
    }
    return render(request, "core/nwu_resources.html", context)


def nwu_resource_detail(request, slug):
    manual = get_object_or_404(NWU_Manual, slug=slug)
    toc = NWU_Manual.objects.filter(audience=manual.audience).order_by("order")

    # Find the next manual in the same audience
    next_manual = (
        NWU_Manual.objects.filter(audience=manual.audience, order__gt=manual.order)
        .order_by("order")
        .first()
    )

    return render(request, "core/nwu_resource.html", {
        "manual": manual,
        "toc": toc,
        "next_manual": next_manual,
    })

def event(request, page_url):
    now = timezone.now()
    now_approx = ApproximateDate(year=now.year, month=now.month, day=now.day)

    try:
        event_obj = get_object_or_404(Event, page_url=page_url.lower())
    except Event.MultipleObjectsReturned:
        event_obj = Event.objects.filter(page_url=page_url.lower()).order_by("-date").first()

    user = request.user
    user_is_organizer = user.is_authenticated and event_obj.has_organizer(user)
    is_preview = "preview" in request.GET
    can_preview = user.is_superuser or user_is_organizer or is_preview
    is_past = event_obj.date <= now_approx if event_obj.date else False

    if not (event_obj.is_page_live or can_preview) or event_obj.is_frozen:
        return render(
            request, "applications/event_not_live.html", {"city": event_obj.city, "page_url": page_url, "past": is_past}
        )

    return render(
        request,
        "core/event.html",
        {
            "event": event_obj,
            "menu": event_obj.menu.all(),
            #"content": event_obj.content.prefetch_related("coaches", "sponsors").filter(is_public=True),
            "content": event_obj.content.prefetch_related( "sponsors").filter(is_public=True),
        },
    )


def events_ical(request):
    events = Event.objects.public().order_by("-date")
    calendar = icalendar.Calendar()
    calendar["summary"] = _("List of Nordic Walk United events around the world")
    for event in events:
        ical_event = event.as_ical()
        if ical_event is None:
            continue  # Skip events with an approximate date
        calendar.add_component(ical_event)

    return HttpResponse(calendar.to_ical(), content_type="text/calendar; charset=UTF-8")


def newsletter(request):
    return render(request, "core/newsletter.html", {})


def faq(request):
    return render(request, "core/faq.html", {})

def faq_org(request):
    return render(request, "core/faq_org.html", {})

def foundation(request):
    return render(request, "core/foundation.html", {})


def governing_document(request):
    return render(request, "core/governing_document.html", {})


def contribute(request):
    return render(request, "core/contribute.html", {})


def year_2015(request):
    return render(
        request,
        "core/2015.html",
        {
            "events": Event.objects.public().filter(date__lt="2016-01-01").order_by("date"),
            "mapbox_access_token": settings.MAPBOX_ACCESS_TOKEN,
        },
    )


def year_2016_2017(request):
    return render(
        request,
        "core/2016-2017.html",
        {
            "events": Event.objects.public().filter(date__lt="2017-08-01", date__gte="2016-01-01").order_by("date"),
            "mapbox_access_token": settings.MAPBOX_ACCESS_TOKEN,
        },
    )


def terms_conditions(request):
    return render(request, "core/terms_conditions.html", {})


def privacy_cookies(request):
    return render(request, "core/privacy_cookies.html", {})


# This view's URL is commented out, so avoid coverage hit by commenting out the view also
# def workshop_box(request):
#     return render(request, 'core/workshop_box.html', {})


def server_error(request):
    return HttpResponse(status=500)


def coc(request):
    template_name = "core/coc.html"
    return render(request, template_name)


def coc_legacy(request, lang=None):
    if lang is None:
        lang = "en"
    template_name = f"core/coc/{lang}.html"
    try:
        return render(request, template_name)
    except TemplateDoesNotExist as err:
        raise Http404(_("No translation for language %(lang)s") % {"lang": lang}) from err

def form_thank_you(request):
    logger.debug('This is a debug message.')

    return render(request, "core/form/thank_you.html", {})



def update_submission(request, pk):
    print("UPDATE_SUBMISSION:")

    submission = Submission.objects.get(id=pk)
    #if request.user != submission.participant:
    #    return HttpResponse('You cant be here!!!!')
    event = submission.event
    print("submission.event:", {submission.event})
    print("submission.event:", {submission.event.uuuid})
    form = SubmissionForm(instance=submission)

    if request.method == 'POST':
        form = SubmissionForm(request.POST,request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            return redirect('core:eventnwu', pk=submission.event.uuuid)
    context = {'form':form, 'event':event}
    return render(request, 'event/submit_form.html', context)

@login_required(login_url='/login')
def project_submission(request, pk):
    event = get_object_or_404(Event, uuuid=pk)
    form = SubmissionForm()
    print("USER NAME:", {request.user})
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.participant = request.user
            submission.event = event
            submission.save()
            return redirect('core:eventnwu', pk=event.uuuid)
    context = {'eventnwu':eventnwu, 'form':form}
    return render(request, 'event/submit_form.html', context)


#_____________________________________________________________

#_____________________________________________________________


#def newnwgroup_page(request):

def logout_user(request):
    logout(request)
    print("LOGOUT EVENT UUID:", request.POST.get('event'))
    #messages.info(request, 'Please log in to enter the event! If you are a new member, please register first.')
    return redirect('core:index')
    #if event_uuid:
        #return redirect('core:eventnwu', pk=event_uuid)
    #return redirect('core:index')

@register.filter
def flag_emoji(country_code):
    if not country_code:
        return ''
    return ''.join(chr(127397 + ord(c.upper())) for c in country_code if c.isalpha())

def eventnwu(request, pk):
    eventnwu = get_object_or_404(Event, uuuid=pk)
    #address = get_address_from_latlng(event.latlng)
    print("EVENTNWU   eventnwu:",  eventnwu)
    #print("EVENTNWU   address:",  address)
    query = request.GET.get("q", "")
    participants = eventnwu.participants.all().distinct()  # Not comment-based
    print("EVENTNWU   participants:",  participants)

    submissions = Submission.objects.filter(event=eventnwu).order_by('-created_on')
    #submissions = eventnwu.comments.all()
    print("EVENTNWU   submissions:",  submissions)

    participant_id = request.GET.get("participant")#new
    print("EVENTNWU   participant_id:",  participant_id)

    if participant_id:
        submissions = submissions.filter(participant__id=participant_id)
    print("EVENTNWU   submissions:",  submissions)
    if participant_id:
        submissions = submissions.filter(participant_id=participant_id)

    if query:
        submissions = submissions.filter(participant__name__icontains=query)

    submissions_list = eventnwu.comments.all()  # assuming related_name='comments'

    print("EVENTNWU   submissions_list:",  submissions_list)

    paginator = Paginator(submissions, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    print("EVENTNWU   participants:",  participants)
    print("EVENT id:", pk)
    print("EVENT id:", eventnwu.uuuid)
    print("USER NAME:", {request.user})


    registered = False
    submitted = False
    print("eventnwu request.user.id:", request.user.id) #ventnwu request.user.id: None
    print("eventnwu request.user.is_authenticated:", request.user.is_authenticated) #eventnwu request.user.is_authenticated: False
    registered = eventnwu.participants.filter(id=request.user.id).exists()
    print("eventnwu registered:", registered) #eventnwu registered: False
    print("eventnwu request.user:", request.user) #eventnwu request.user: AnonymousUser

    #submitted = Submission.objects.filter(participant=request.user, event=eventnwu).exists()
    #print("eventnwu submitted:", submitted)

    #context = {'eventnwu':eventnwu, 'registered':registered, "page_obj": page_obj,}#real
    context = {
        "eventnwu": eventnwu,
        "participants": participants,"participant_id": participant_id,
        'registered':registered, "page_obj": page_obj,"query": query,
    }
    #context = {'event':event, 'registered':registered, 'submitted':submitted}
    return render(request, 'core/eventnwu.html', context)

#________________________________________




#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@login_required(login_url='/login')
def cancel_registration(request, event_uuid):
    """
    Remove the current user from an event and email ONLY that user
    a cancellation confirmation.
    """
    # Fetch by the UUID passed in the URL (don't overwrite it from POST)
    event = get_object_or_404(Event, uuuid=event_uuid)

    # Check if the user is registered
    if event.participants.filter(pk=request.user.pk).exists():
        event.participants.remove(request.user)
        # Email only the cancelling user
        _send_cancellation_confirmation(event, request.user)

        messages.success(
            request,
            f"You've successfully canceled your registration for “{event.name}”."
        )
    else:
        messages.error(request, "You are not registered for this event.")

    # Adjust this redirect to wherever you want the user to land after canceling
    return redirect('core:index')


def _send_cancellation_confirmation(event, user):
    """
    Send a confirmation email ONLY to the user who canceled.
    """
    if not getattr(user, "email", None):
        # No email on file—nothing to send
        return

    subject = "Your event registration has been canceled"
    message = (
        "Hello {name},\n\n"
        "This is to confirm that your registration for the event:\n"
        "  {event_name}\n"
        "in {city}, {country} scheduled for {date}\n"
        "has been successfully canceled.\n\n"
        "If this wasn’t you or you canceled by mistake, please contact us.\n\n"
        "Best regards,\nThe Event Team"
    ).format(
        name=getattr(user, "name", user.get_username()),
        event_name=event.name,
        city=getattr(event, "city", ""),
        country=getattr(event, "country", ""),
        date=getattr(event, "date", ""),
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=[user.email],
        fail_silently=False,
    )


def group_events(request, pk):
    nwgroup = get_object_or_404(EventApplication, pk=pk)
    today = timezone.now().date()

    future_events = Event.objects.filter(
        is_page_live=True,
        date__gte=today,
        nwgroup=nwgroup.nwgroup,
    ).order_by("date")

    return render(request, "core/group_events.html", {
        "future_events": future_events,
        "future_events_count": future_events.count(),
        "nwgroup_name": nwgroup.nwgroup,
    })

    return redirect("core:account")


@login_required
@require_POST
def delete_submission(request, pk):
    sub = get_object_or_404(Submission, pk=pk)

    if request.user.is_superuser or sub.participant_id == request.user.id:
        sub.delete()
        messages.success(request, "Comment deleted.")
    else:
        messages.error(request, "You don't have permission to delete this comment.")

    return redirect("core:eventnwu", pk=sub.event.uuuid)








# View to display the manual
@login_required(login_url='/login')
def manual_view(request, manual_id):
    from core.models import User
    try:
        manual = Manual.objects.get(id=manual_id)
    except Manual.DoesNotExist:
        return render(request, 'error.html', {'message': 'Manual not found.'})

    # Check if the user has the correct permissions
    if request.user.is_superuser or request.user.groups.filter(name='Moderators').exists():
        return render(request, 'manual.html', {'manual': manual})
    else:
        return render(request, 'error.html', {'message': 'You do not have permission to view this manual.'})


def manual_list(request):
    q = request.GET.get("q", "")
    manuals = NWU_Manual.objects.all().order_by("-updated_at")
    if q:
        manuals = manuals.filter(
            models.Q(title__icontains=q) |
            models.Q(description__icontains=q) |
            models.Q(body__icontains=q)
        )
    return render(request, "core/manual_list.html", {"manuals": manuals, "q": q})

""""
def eventnwu(request, pk):
    eventnwu = Event.objects.get(id=pk)
    print("EVENT_page: event", eventnwu)
    submissions = Submission.objects.filter(event=eventnwu)
    for sub in submissions:
        print("Submission participant:", sub.participant)
        if sub.participant:
            print("Participant ID:", sub.participant.id)
            print("Current user ID:", request.user.id)
            print("Match:", sub.participant == request.user)
        else:
            print("Warning: Submission with no participant (None)")

    # event Boy's graduation
    print("EVENT_page: request.user", request.user)
    #request.user glnglmn@gmail.com
    print("EVENT_page: event.id", event.id)
    #event.id 24048388-9187-42a8-970b-87aef06b00d0
    print("EVENT_page: request", request)
    #request <WSGIRequest: GET '/event/24048388-9187-42a8-970b-87aef06b00d0/'>
    print("EVENT_page: request.user", request.user)
    #request.user glnglmn@gmail.com

    print("EVENT_page: request.user.events.filter(id=event.id)", request.user.events.filter(id=event.id))
    #request.user.events.filter(id=event.id) <QuerySet [<Event: Boy's graduation>]>

    registered = False
    submitted = False

    if request.user.is_authenticated:
        registered = request.user.events.filter(id=event.id).exists()
        submitted = Submission.objects.filter(participant=request.user, event=event).exists()
    context = {'event':eventnwu, 'registered':registered, 'submitted':submitted}

    return render(request, 'core/eventnwu.html', context)
    #return redirect('core:eventnwu', pk=event_uuid)
"""






