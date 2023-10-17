import frappe
from frappe import _
from frappe.utils.data import fmt_money
from myfatoorah.myfatoorah.doctype.myfatoorah_settings.myfatoorah_settings import get_gateway_controller
import json

no_cache = 1

expected_keys = (
	"amount",
	"title",
	"description",
	"reference_doctype",
	"reference_docname",
	"payer_name",
	"payer_email",
	"order_id",
	"currency",
)


def get_context(context):
    context.no_cache = 1

    # all these keys exist in form_dict
    if not (set(expected_keys) - set(list(frappe.form_dict))):
        for key in expected_keys:
            context[key] = frappe.form_dict[key]

        gateway_controller = get_gateway_controller(
            context.reference_doctype, context.reference_docname)

        context["amount"] = fmt_money(
            amount=context["amount"], currency=context["currency"])

    else:
        frappe.redirect_to_message(
			_("Some information is missing"),
			_("Looks like someone sent you to an incomplete URL. Please ask them to look into it."),
		)
        frappe.local.flags.redirect_location = frappe.local.response.location
        raise frappe.Redirect


@frappe.whitelist(allow_guest=True)
def make_payment(session_id, data, reference_doctype=None, reference_docname=None):
    data = json.loads(data)
    
    gateway_controller = get_gateway_controller(reference_doctype, reference_docname)
    data = frappe.get_doc("Myfatoorah Settings", gateway_controller).execute_payment(session_id,data)
    
    frappe.db.commit()
    
    return data