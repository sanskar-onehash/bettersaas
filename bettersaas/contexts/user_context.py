import frappe


class UserContext:
    def __init__(self, username: str) -> None:
        self.new_user = username

    def __enter__(self):
        self.old_user = frappe.session.user
        frappe.set_user(self.new_user)

    def __exit__(self, exc_type, exc_value, traceback):
        frappe.set_user(self.old_user)
        return False


def get_user_context(username: str) -> UserContext:
    return UserContext(username)
