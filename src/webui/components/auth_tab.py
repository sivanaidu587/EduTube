import gradio as gr
import requests
import os
from urllib.parse import urlencode

def login_to_auth(email_or_phone, password):
    """Demo login to FastAPI auth backend."""
    url = "http://127.0.0.1:8001/login"
    data = {
        "identifier": email_or_phone,
        "otp
