# Secure Gmail+Phone Login Implementation

## Completed Steps
- [x] Create TODO-auth.md

## Pending Steps
1. **Phone auth clarification**: User requested "phone number too" → Implement dual Gmail **OR** Phone OTP?
2. **Setup env**: Get Gmail/Phone, Google OAuth secrets.
3. **Backend**: FastAPI `/auth` with Gmail OAuth + Phone SMS (Twilio).
4. **Frontend**: Gradio login form → backend redirect/verify.
5. **Security**: JWT, rate limit, single-session.
6. **Test**: Full login flow.
7. **Integrate** into interface.py tabs.

## Current Status
Waiting user input:
- Exact Gmail for whitelist
- Phone number (for OTP/SMS?)
- Google OAuth Client ID/Secret (guide setup if needed)
- Auth type: Gmail-only OR Gmail+Phone OR Phone-only?
