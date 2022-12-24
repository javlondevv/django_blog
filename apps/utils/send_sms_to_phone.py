# from twilio.rest import Client
# from twilio.base.exceptions import TwilioRestException
#
# from root.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID
#
# client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# verify = client.verify.services(TWILIO_VERIFY_SERVICE_SID)
#
#
# def send(phone):
#     verify.verifications.create(to=phone, channel='sms')
#
#
# def check(phone, code):
#     try:
#         result = verify.verification_checks.create(to=phone, code=code)
#     except TwilioRestException:
#         print('no')
#         return False
#     return result.status == 'approved'
