import gradio as gr
import requests
import os
from urllib.parse import urlencode

def login_to_auth(email_or_phone, password):
    """Demo login to FastAPI auth backend."""
    url = "http://127.0.0.1:8001/login"
    data = {
"identifier": email_or_phone,
        "password": password
    }
    try:
        resp = requests.post(url, json=data)
        if resp.status_code == 200:
            token = resp.json().get('access_token')
            return True, f"✅ Login Success! Token: {token[:20]}..."
        else:
            return False, f"❌ {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def create_auth_tab():
    with gr.TabItem("🔐 Secure Login", icon="shield"):
        gr.Markdown("# Gmail Login (Whitelist Protected)")
        with gr.Row():
            email = gr.Textbox(label="Email/Phone", placeholder="demo@sivak.com")
            pwd = gr.Password(label="Password", placeholder="secure123")
        login_btn = gr.Button("Login", variant="primary")
        status = gr.Textbox(label="Status", interactive=False)
        
        login_btn.click(
            fn=login_to_auth,
            inputs=[email, pwd],
            outputs=[status]
        )
        gr.Markdown("""
        **Demo Creds:**
        - Email: `demo@sivak.com`
        - Pass: `secure123`
        """)

if __name__ == "__main__":
    demo = create_auth_tab()
    demo.launch()

