from yoomoney import Quickpay
import json

async def create_payment(user_id, mounth):
    label_data = json.dumps({"user_id": user_id, "mounth": mounth})
    amount, description = get_amount_and_description(mounth)
    quickpay = Quickpay(
        receiver="4100118914294085",
        quickpay_form="shop",
        targets=description,
        paymentType="SB",
        sum=amount,
        successURL="https://t.me/VOXvpn_bot",
        label=label_data
    )
    return quickpay.redirected_url

def get_amount_and_description(months):
    if months == 1:
        return 200, "VOX 1 месяц"
    elif months == 3:
        return 500, "VOX 3 месяца"
    elif months == 6:
        return 900, "VOX 6 месяцев"
    elif months == 7:
        return 5, "VOX 7 месяцев"
    else:
        return None, None

# print(create_payment(111111,1))
