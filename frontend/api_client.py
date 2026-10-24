
import requests

BASE_URL = "http://127.0.0.1:8000"


def api_request(method, endpoint, token=None, **kwargs):
    """Send an HTTP request to the FastAPI backend."""

    headers = kwargs.pop("headers", {}).copy()

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method=method,
            url=f"{BASE_URL}{endpoint}",
            headers=headers,
            timeout=300,
            **kwargs
        )

    except requests.RequestException as exc:
        raise RuntimeError(
            "Cannot connect to FastAPI. "
            "Make sure your backend is running."
        ) from exc

    try:
        data = response.json()
    except ValueError:
        data = {}

    if not response.ok:
        detail = data.get("detail", response.text)
        raise RuntimeError(
            f"API error {response.status_code}: {detail}"
        )

    return data


def register_user(username, email, password):
    return api_request(
        "POST",
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )



def login_user(username, password, email):
    return api_request(
        "POST",
        "/auth/login",
        json={
            "username": username,
            "password": password,
            "email": email
        }
    )



def process_video(video_url, token):
    return api_request(
        "POST",
        "/videos/process-url",
        token=token,
        json={
            "source_url": video_url
        }
    )


def create_chat(video_id, token):
    return api_request(
        "POST",
        f"/videos/{video_id}/chats",
        token=token,
        json={}
    )


def get_chat_history(video_id, token):
    return api_request(
        "GET",
        f"/videos/{video_id}/chats",
        token=token
    )


def get_chat_messages(chat_id, token):
    return api_request(
        "GET",
        f"/chats/{chat_id}",
        token=token
    )


def send_chat_message(chat_id, question, token):
    return api_request(
        "POST",
        f"/chats/{chat_id}/messages",
        token=token,
        json={"question": question}
    )

def get_chat_details(chat_id, token):
    return api_request(
        "GET",
        f"/chats/{chat_id}",
        token=token
    )

def get_all_user_chats(token):
    return api_request(
        "GET",
        "/users/me/chats",
        token=token,
    )


def delete_chat(chat_id, token):
    return api_request(
        "DELETE",
        f"/chats/{chat_id}",
        token=token
    )

