from kavenegar import *


def send_otp_code(phone_number, otp_code):
    try:
        api = KavenegarAPI('55635A7443656172325066314C3636707A69655A4B4B59336D4A652F762F4B48334C38616839476F6359453D')
        params = {'sender': '2000660110',
                  'receptor': phone_number,
                  'message': 'کد تایید شما: '
                             f'{otp_code}',
                  }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


def send_tracking_code(phone_number, tracking_code):
    try:
        api = KavenegarAPI('55635A7443656172325066314C3636707A69655A4B4B59336D4A652F762F4B48334C38616839476F6359453D')
        params = {'sender': '2000660110',
                  'receptor': phone_number,
                  'message': 'شماره سفارش شما: '
                             f'{tracking_code}'
                             f'از طریق این کد در بخش پیگیری سفارش میتوانید وضعیت سفارش خود را مشاهده کنید',
                  }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)


def send_otp_code_for_password(phone_number, otp_code):
    try:
        api = KavenegarAPI('55635A7443656172325066314C3636707A69655A4B4B59336D4A652F762F4B48334C38616839476F6359453D')
        params = {'sender': '2000660110',
                  'receptor': phone_number,
                  'message': 'کد یکبار مصرف جهت تغییر رمز حساب شما :'
                             f'{otp_code}'
                  'این کد را به دیگران ندهید '
                    'فروشگاه لپتاپ',
                  }
        response = api.sms_send(params)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)
