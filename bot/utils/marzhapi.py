import asyncio
from marzpy.api.user import User
from datetime import datetime, timedelta
from aiohttp.client_exceptions import ClientResponseError,ClientError, InvalidURL
from dotenv import load_dotenv
import os
from dateutil.relativedelta import relativedelta
import logging
import aiohttp
import json

load_dotenv('../.env')
LOGIN = os.getenv("MARZH_LOGIN")
PASS = os.getenv("MARZH_PWD")
PANEL_URL = os.getenv("PANEL_URL")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# @cached(ttl=600)
async def get_panel_and_token():
    # logging.debug(f"LOGIN, PASS, PANEL_URL: {LOGIN},{PASS},{PANEL_URL}")

    url = f"{PANEL_URL}/api/admin/token"  # URL для авторизации, если он отличается, нужно изменить
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Данные для авторизации
    payload = {
        "username": LOGIN,
        "password": PASS
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Отправка POST-запроса для получения токена
            async with session.post(url, data=payload, headers=headers) as response:
                # Проверка статуса ответа
                if response.status == 200:
                    result = await response.json()  # Получаем ответ в формате JSON
                    access_token = result.get('access_token')
                    if access_token:
                        logging.debug(f"Token received: {access_token}")
                        return access_token
                    else:
                        logging.error(f"Access token not found in response: {result}")
                        raise Exception("Failed to obtain access token from response.")
                elif response.status == 422:
                    error_detail = await response.json()
                    logging.error(f"Validation Error: {error_detail}")
                    raise Exception(f"Validation Error: {error_detail}")
                else:
                    error_message = await response.text()
                    logging.error(
                        f"Failed to get token. Status code: {response.status}. Error details: {error_message}")
                    raise Exception(
                        f"Failed to get token. Status code: {response.status}. Error details: {error_message}")

    except Exception as e:
        logging.error(f"Error during token request: {str(e)}")
        raise Exception(f"Error during token request: {str(e)}")


async def get_user_sub(user_id: int):
    logging.debug(f"Getting user subscription for user_id: {user_id}")

    # Получаем токен для авторизации
    token = await get_panel_and_token()

    # Формируем URL для запроса информации о пользователе
    url = f"{PANEL_URL}/api/user/{user_id}"

    # Заголовки запроса с авторизацией
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Выполняем GET-запрос для получения данных о пользователе
            async with session.get(url, headers=headers) as response:
                # Проверяем успешность запроса
                if response.status == 200:
                    result = await response.json()  # Получаем ответ в формате JSON
                    logging.debug(f"User subscription URL: {result.get('subscription_url', 'No URL found')}")

                    # Возвращаем полную ссылку на подписку
                    return f"{PANEL_URL}{result['subscription_url']}"
                elif response.status == 422:
                    # Обрабатываем ошибку валидации
                    error_detail = await response.json()
                    logging.error(f"Validation Error: {error_detail}")
                    raise Exception(f"Validation Error: {error_detail}")
                else:
                    # Логируем ошибку, если статус не 200
                    error_message = await response.text()
                    logging.error(
                        f"Failed to get user subscription. Status code: {response.status}. Error details: {error_message}")
                    raise Exception(
                        f"Failed to get user subscription. Status code: {response.status}. Error details: {error_message}")
    except Exception as e:
        logging.error(f"Error during user subscription request: {str(e)}")
        raise Exception(f"Error during user subscription request: {str(e)}")


async def get_user_vless_link(user_id: int):
    logging.debug(f"Getting VLESS link for user_id: {user_id}")

    # Получаем токен для авторизации
    token = await get_panel_and_token()

    # Формируем URL для запроса информации о пользователе
    url = f"{PANEL_URL}/api/user/{user_id}"

    # Заголовки запроса с авторизацией
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Выполняем GET-запрос для получения данных о пользователе
            async with session.get(url, headers=headers) as response:
                # Проверяем успешность запроса
                if response.status == 200:
                    result = await response.json()  # Получаем ответ в формате JSON
                    logging.debug(f"User VLESS link: {result.get('links', ['No link found'])[0]}")

                    # Возвращаем первую ссылку из поля "links"
                    if result.get('links'):
                        return result['links'][0]
                    else:
                        raise Exception("No VLESS link found in the response.")
                elif response.status == 422:
                    # Обрабатываем ошибку валидации
                    error_detail = await response.json()
                    logging.error(f"Validation Error: {error_detail}")
                    raise Exception(f"Validation Error: {error_detail}")
                else:
                    # Логируем ошибку, если статус не 200
                    error_message = await response.text()
                    logging.error(
                        f"Failed to get user VLESS link. Status code: {response.status}. Error details: {error_message}")
                    raise Exception(
                        f"Failed to get user VLESS link. Status code: {response.status}. Error details: {error_message}")
    except Exception as e:
        logging.error(f"Error during user VLESS link request: {str(e)}")
        raise Exception(f"Error during user VLESS link request: {str(e)}")


async def extend_expire(user_id: int, months: int):
    logger.debug(f"extend_expire called with user_id={user_id}, months={months}")

    # Получаем токен для авторизации
    token = await get_panel_and_token()

    # Формируем URL для обновления информации о пользователе
    url = f"{PANEL_URL}/api/user/{user_id}"

    # Заголовки запроса с авторизацией
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            # Сначала получаем текущие данные пользователя
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    logger.debug(f"Got user data: {user_data}")

                    # Проверяем текущий срок действия подписки
                    current_expire_timestamp = user_data.get("expire")
                    if current_expire_timestamp is None:
                        current_expire_time = datetime.utcnow()
                    else:
                        current_expire_time = datetime.utcfromtimestamp(current_expire_timestamp)
                    now = datetime.utcnow()

                    logger.debug(f"Current expire time: {current_expire_time}, now: {now}")

                    # Определяем новую дату истечения срока действия
                    if current_expire_time < now:
                        # Если срок действия истек, прибавляем месяцы от текущей даты
                        new_expire_time = now + relativedelta(months=months)
                    else:
                        # Если срок действия еще активен, прибавляем месяцы от текущего срока действия
                        new_expire_time = current_expire_time + relativedelta(months=months)

                    new_expire_timestamp = int(new_expire_time.timestamp())
                    logger.debug(f"New expire time: {new_expire_time} (timestamp: {new_expire_timestamp})")

                    # Подготавливаем данные для обновления пользователя
                    update_payload = {
                        "expire": new_expire_timestamp,
                        "status": "active",
                        "data_limit": 0,
                        "username": user_data.get("username"),
                        "proxies": user_data.get("proxies"),
                        "inbounds": user_data.get("inbounds"),
                    }

                    # Отправляем запрос на обновление
                    async with session.put(url, headers=headers, json=update_payload) as update_response:
                        if update_response.status == 200:
                            result = await update_response.json()
                            logger.debug(f"User modified successfully: {result}")
                            return result
                        else:
                            error_message = await update_response.text()
                            logger.error(f"Failed to modify user. Status code: {update_response.status}. Error details: {error_message}")
                            raise Exception(f"Failed to modify user. Status code: {update_response.status}. Error details: {error_message}")
                else:
                    error_message = await response.text()
                    logger.error(f"Failed to get user data. Status code: {response.status}. Error details: {error_message}")
                    raise Exception(f"Failed to get user data. Status code: {response.status}. Error details: {error_message}")

    except Exception as e:
        logger.error(f"Error in extend_expire: {str(e)}", exc_info=True)
        raise Exception(f"Error in extend_expire: {str(e)}")


async def crate_user(user_id: int):
    logger.debug(f"crate_user called with user_id={user_id}")

    try:
        # Получаем токен для авторизации
        token = await get_panel_and_token()
        logger.debug("Got panel and token")

        # Устанавливаем время истечения срока действия аккаунта через 3 дня
        expire_time = datetime.utcnow() + timedelta(days=7)  # Установка времени истечения срока действия на 3 дня
        expire_timestamp = int(expire_time.timestamp())

        # Формируем данные для нового пользователя
        user_data = {
            "username": str(user_id),  # Имя пользователя
            "proxies": {
                "vless": {}  # Пример настройки прокси
            },
            "inbounds": {
                "vless": ["VLESS TCP REALITY"]  # Входящие соединения для vless
            },
            "expire": expire_timestamp,  # Время истечения срока
            "data_limit": 1024 * 1024 * 1024 * 25,  # Лимит данных (в байтах)
            "data_limit_reset_strategy": "no_reset",  # Стратегия сброса лимита
            "status": "active",  # Статус пользователя
            "note": "",  # Дополнительная информация (по желанию)
            "on_hold_timeout": "2023-11-03T20:30:00",  # Время начала статуса on_hold
            "on_hold_expire_duration": 0  # Длительность статуса on_hold (0 - без ограничений)
        }

        logger.debug(f"User data to be sent: {json.dumps(user_data, indent=2)}")

        # Заголовки запроса
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # URL для создания пользователя
        url = f"{PANEL_URL}/api/user"

        # Выполнение запроса с использованием aiohttp
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=user_data, headers=headers) as response:
                    # Проверка статуса ответа
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"User added successfully: {result['links'][0]}")
                        # Возвращаем успешный результат
                        return {
                            "status": "ok",
                            "data": {
                                "link": result['links'][0]
                            }
                        }
                    else:
                        # Логирование ошибки, если статус не 200
                        logger.error(f"Failed to create user. Status code: {response.status}")
                        error_message = await response.text()
                        logger.error(f"Error details: {error_message}")
                        return {
                            "status": "error",
                            "message": f"Failed to create user. Status code: {response.status}, {error_message}"
                        }

            except Exception as e:
                # Логирование ошибок при выполнении запроса
                logger.error(f"Error while making the request: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Request error: {str(e)}"
                }

    except ClientResponseError as e:
        # Обработка ошибки, если пользователь уже существует
        logger.error(f"ClientResponseError occurred: {e}", exc_info=True)
        if e.status == 409:
            logger.debug("User already exists")
            # Если пользователь существует, просто возвращаем статус "exists"
            return {
                "status": "exists",
                "message": "User already exists."
            }
        else:
            # Обработка других ошибок ClientResponseError
            return {
                "status": "error",
                "message": f"ClientResponseError: {str(e)}"
            }

    except Exception as e:
        # Логирование других неожиданных ошибок
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise  # Перебрасываем исключение, если оно не обработано



async def get_user_info(user_id):
    logger.debug(f"get_user_info called with user_id={user_id}")

    url = f"{PANEL_URL}/api/user/{user_id}"
    token = await get_panel_and_token()
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            # params = {
            #     "user_id": user_id
            # }

            logger.debug(f"Sending request to {url}")

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    logger.debug(f"Got user data: {user_data}")
                else:
                    error_message = await response.text()
                    logger.error(f"Error response from server: {response.status}, {error_message}")
                    response.raise_for_status()

        # Extract subscription status
        subscription_status = user_data.get("status", "unknown")

        # Extract subscription expiration timestamp
        expire_timestamp = user_data.get("expire")

        if expire_timestamp is None:
            # Infinite subscription
            expire_formatted = "∞"
            remaining_days = "∞"
        else:
            # Finite subscription
            expire_date = datetime.utcfromtimestamp(expire_timestamp)
            expire_formatted = expire_date.strftime('%d.%m.%Y')

            # Days remaining
            now = datetime.utcnow()
            remaining_days = (expire_date - now).days if expire_date > now else 0

        result = {
            "subscription_status": subscription_status,
            "remaining_days": remaining_days,
            "expire_date": expire_formatted
        }

        logger.debug(f"Returning result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in get_user_info: {e}", exc_info=True)
        raise

# async def main():
#     user_id = 452398375  # Replace with the actual user ID
#     months_to_extend = 3  # Replace with the desired number of months
#
#     try:
#         result = await extend_expire(user_id, months_to_extend)
#         print(f"Subscription extended successfully: {result}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.DEBUG)
#     asyncio.run(main())

# async def main():
#     result = await extend_expire("452398375",1)
#     print(result.expire)
#     # result = await crate_shadow_trial("1231231")
#     # print(result)


    # username = 'levap12'
    # password = 'M@ve1207'
    # panel = Marzban(username, password, "https://vm13139.vpsone.xyz")
    # token = await panel.get_token()
    # # Дальнейшие операции с использованием токена, например:
    # # expire_time = datetime.utcnow() + timedelta(days=1)  # Установка времени истечения срока действия на 1 день
    # # expire_timestamp = int(expire_time.timestamp())
    # expire_time = datetime.utcnow() + relativedelta(minutes=61)
    # expire_timestamp = int(expire_time.timestamp())
    # print(expire_timestamp)
    # user = User(
    #     username="452398375",  # Задайте уникальное имя пользователя
    #     proxies={
    #         "vless": {}
    #     },
    #     inbounds={"vless": ["VLESS TCP REALITY"]},  # Установка входящих соединений для Shadowsocks
    #     expire=expire_timestamp, # Установка времени истечения срока действия
    #     data_limit=0,  # Установка лимита данных, если необходимо,  # Стратегия сброса лимита данных
    #     status="active"  # Статус пользователя
    # )
    # result = await panel.modify_user('452398375',user=user, token=token)
    #
    # user_info = await panel.get_user('asdd', token=token)
    # print(result.inbounds)

    # Вывод ключа подключения
    # print(f"Shadowsocks connection key: {user_info['ss_connect_key']}")


# asyncio.run(main())