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
✅ **Security hardened**: Hardcoded creds/SECRET_KEY removed. Now .env-driven with auto-generate fallback.
- Set vars in .env (see .env.example).
- Basic JWT whitelist works; OAuth/OTP pending full plan.

**Next**: Full OAuth/phone integration or use as-is.
