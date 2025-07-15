import frappe
from frappe import utils
import requests

GUEST_ID_TTL = 1800  # 30 min
GUEST_ID_COOKIE = "GUEST-ID"
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


def verify_recaptcha_response(func):
    def wrapper(*args, **kwargs):
        user_recaptcha_token = kwargs.pop("user_recaptcha_token", None)
        user_ip = kwargs.pop("user_ip", None)
        if not user_recaptcha_token:
            frappe.AuthenticationError("No Recaptcha token was provided.")

        data = {
            "secret": frappe.conf.recaptcha_secret,
            "response": user_recaptcha_token,
            "remoteip": user_ip,
        }
        res = requests.post(RECAPTCHA_VERIFY_URL, data=data)
        res_data = res.json()
        if res.status_code != 200 or not res_data.get("success"):
            raise frappe.AuthenticationError("Invalid Recaptcha Response")

        set_guest_id(user_ip)
        kwargs.pop("cmd")
        return func(*args, **kwargs)

    return wrapper


def verify_guest_id(func):
    def wrapper(*args, **kwargs):
        kwargs.pop("cmd")
        if frappe.session.user:
            return func(*args, **kwargs)

        guest_token = frappe.request.cookies.get(GUEST_ID_COOKIE)
        if guest_token and is_valid_guest_token(guest_token):
            return func(*args, **kwargs)

        raise frappe.AuthenticationError("Invalid Request! Cookie Expired")

    return wrapper


def is_valid_guest_token(guest_token):
    now = utils.get_datetime()
    return frappe.db.exists("Guest Token", {"token": guest_token, "expiry": [">", now]})


def set_guest_id(user_ip=None):
    guest_doc = generate_guest_token(user_ip=user_ip, ignore_permissions=True)
    frappe.local.cookie_manager.set_cookie(
        GUEST_ID_COOKIE,
        guest_doc.token,
        expires=guest_doc.expiry,
        secure=True,
        httponly=True,
        samesite="Strict",
    )


def generate_guest_token(user_ip=None, ttl=GUEST_ID_TTL, ignore_permissions=False):
    token = frappe.generate_hash(length=16)
    now = utils.get_datetime()
    expiry = utils.add_to_date(now, seconds=ttl, as_datetime=True)
    guest_doc = frappe.get_doc(
        {"doctype": "Guest Token", "token": token, "user_ip": user_ip, "expiry": expiry}
    ).insert(ignore_permissions=ignore_permissions)
    frappe.db.commit()
    return guest_doc
