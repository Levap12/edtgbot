import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from aiogram import Bot
from dotenv import load_dotenv
import os
import hmac
import hashlib
from urllib.parse import parse_qs

from bot.utils.base64coding import decode
from bot.utils.marzhapi import get_user_sub
from bot.utils.payment import verify_sign
from bot.utils.marzhapi import extend_expire
import aioredis

import json
# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
load_dotenv('../.env')
TOKEN_TG = os.getenv("TOKEN_TG")
bot = Bot(token=TOKEN_TG)
SECRET_KEY = os.getenv("SECRET_KEY")

processed_payments = set()

@app.get("/subs/{user_id}")
async def redirect_user(user_id):
    try:
        logging.info(f"Received user_id: {user_id}")
        decoded_user_id = decode(user_id)
        logging.info(f"Decoded user_id: {decoded_user_id}")

        # Сделать запрос к сервису для получения конечного URL
        redirect_url = await get_user_sub(decoded_user_id)
        logging.info(f"Redirect URL: {redirect_url}")
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/payment")
async def payment(request: Request):
    params = request.query_params
    mounts = int(params.get('mounts'))
    user_id = params.get('user_id')
    user_ip = request.client.host
    logging.info(f"Received mounts: {mounts}, user_id: {user_id}, user_ip: {user_ip}")
    if mounts not in [1, 3, 6]:
        raise HTTPException(status_code=400, detail="Invalid mounts value")

    link, error = await payment.create_payment(user_id, mounts, user_ip)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {"link": link}
# ae00-178-90-225-38.ngrok-free.app/payment?user_id=1546789&mounts=1

@app.post("/payment_notification")
async def payment_notification(request: Request):
    logging.info("Received payment notification request")

    # Read and parse the request body
    try:
        body = await request.body()
        logging.info(f"Request body successfully read {body}")
        data = parse_qs(body.decode("utf-8"))
        logging.info(f"Parsed data: {data}")
    except Exception as e:
        logging.error(f"Error reading or parsing request body: {e}")
        raise HTTPException(status_code=400, detail="Failed to parse request body")

    # # Verify the notification signature
    # received_signature = data.get("sha1_hash", [None])[0]
    # if not received_signature:
    #     logging.warning("Missing sha1_hash in data")
    #     raise HTTPException(status_code=400, detail="Missing sha1_hash")
    #
    # # Compute the HMAC hash using the secret key
    # sorted_keys = sorted(key for key in data if key != "sha1_hash")
    # message = "&".join(f"{key}={data[key][0]}" for key in sorted_keys).encode("utf-8")
    # computed_signature = hmac.new(
    #     SECRET_KEY.encode('utf-8'),
    #     message,
    #     hashlib.sha1
    # ).hexdigest()
    #
    # if received_signature != computed_signature:
    #     logging.warning("Invalid signature detected")
    #     raise HTTPException(status_code=403, detail="Invalid signature")
    #
    # logging.info("Signature verification successful")

    # Process the payment notification
    try:
        operation_id = data.get("operation_id", [None])[0]
        if operation_id in processed_payments:
            logging.info(f"Duplicate payment notification detected for operation_id: {operation_id}")
            return {"status": "duplicate"}

        # Mark payment as processed
        processed_payments.add(operation_id)

        label = data.get("label", [None])[0]
        if label:
            try:
                label_data = json.loads(label)
                logging.info(f"Label data: {label_data}")
                user_id = label_data.get("user_id")
                mounth = label_data.get("mounth")
                logging.info(f"Payment received for user_id: {user_id}, month: {mounth}")
                await extend_expire(int(user_id), int(mounth))
            except json.JSONDecodeError as e:
                logging.error(f"Invalid label format: {e}")
                raise HTTPException(status_code=400, detail="Invalid label format")
        else:
            logging.warning("Missing label in notification data")
            raise HTTPException(status_code=400, detail="Missing label in notification data")
    except Exception as e:
        logging.error(f"Error processing payment data: {e}")
        raise HTTPException(status_code=500, detail="Failed to process payment data")

    logging.info("Payment notification processed successfully")
    return {"status": "success"}


async def get_redis_connection():
    redis = await aioredis.from_url(
        'redis://redis-16498.c328.europe-west3-1.gce.redns.redis-cloud.com:16498',
        password='DPa87sxifzxNOhE4sWL7q5PWdKDMCm6S',  # если требуется аутентификация
        encoding='utf-8'
    )
    return redis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
