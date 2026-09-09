"""Render the CURRENT (pre-redesign) UI to standalone HTML for screenshotting.

Uses Django's test client so we get real authenticated pages without needing
to drive a browser through a login form. The stylesheet is inlined so the
saved file renders faithfully straight from disk.
"""
import os
import pathlib
import re
import sys

PROJECT = r"C:\Users\admin\Desktop\Github\HelpDesk-Pro"
sys.path.insert(0, PROJECT)
os.chdir(PROJECT)

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tickit.settings")
django.setup()

from django.conf import settings
from django.test import Client
from django.urls import reverse, NoReverseMatch

settings.ALLOWED_HOSTS.append("testserver")

OUT = pathlib.Path(
    r"C:\Users\admin\AppData\Local\Temp\claude"
    r"\c--Users-admin-Desktop-Github-HelpDesk-Pro"
    r"\a3ee96ff-ae2e-4a38-b27e-ea4a950cdb8e\scratchpad\before_html"
)
OUT.mkdir(parents=True, exist_ok=True)

CSS = pathlib.Path("static/css/main.css").read_text(encoding="utf-8")

from registration.models import User
from vats.models import Ticket

admin = User.objects.get(email="admin@vatsfinancial.com")
manager = User.objects.filter(role="Manager").first()
ticket = Ticket.objects.order_by("-id").first()

def inline_css(html: str) -> str:
    """Replace the main.css <link> with an inline <style> block."""
    html = re.sub(
        r'<link[^>]*main\.css[^>]*>',
        f"<style>\n{CSS}\n</style>",
        html,
    )
    return html

def grab(name, path, user=None):
    c = Client()
    if user is not None:
        c.force_login(user)
    try:
        resp = c.get(path, follow=True)
    except Exception as e:
        print(f"SKIP {name}: {e}")
        return
    if resp.status_code != 200:
        print(f"SKIP {name}: HTTP {resp.status_code}")
        return
    html = resp.content.decode("utf-8", errors="replace")
    html = inline_css(html)
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")
    print(f"OK   {name}  ({len(html)} bytes)  <- {path}")

def url(name, *args):
    try:
        return reverse(name, args=args)
    except NoReverseMatch:
        return None

targets = [
    ("01-login",          url("login"),                      None),
    ("02-dashboard",      url("home"),                       admin),
    ("03-ticket-list",    url("ticket_list"),                admin),
    ("04-ticket-detail",  url("ticket_detail", ticket.id) if ticket else None, admin),
    ("05-my-tickets",     url("my_tickets"),                 admin),
    ("06-user-list",      url("user_list"),                  admin),
    ("07-manager-list",   url("ticket_list"),                manager),
]

for name, path, user in targets:
    if not path:
        print(f"SKIP {name}: no URL")
        continue
    grab(name, path, user)

print("\nHTML written to:", OUT)
