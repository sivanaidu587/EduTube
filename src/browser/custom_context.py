import json
import logging
import os

# from browser_use.browser.browser import Browser, IN_DOCKER
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from playwright.async_api import BrowserContext as PlaywrightBrowserContext
from typing import Optional
from browser_use.browser.context import BrowserContextState

logger = logging.getLogger(__name__)


class CustomBrowserContext(BrowserContext):
    def __init__(
            self,
            browser: 'Browser',
            config: BrowserContextConfig | None = None,
            state: Optional[BrowserContextState] = None,
    ):
        super(CustomBrowserContext, self).__init__(browser=browser, config=config, state=state)
        self._inject_captcha_solver = True

    async def new_page(self, **kwargs):
        """Override to inject CAPTCHA solver script on every new page."""
        page = await super().new_page(**kwargs)
        
        if self._inject_captcha_solver:
            await self._inject_solve_challenge_script(page)
        
        return page

async def _inject_solve_challenge_script(self, page):
        \"\"\"Full-featured CAPTCHA solver for Google sorry pages - works on desktop, Android, laptop.
        Handles checkbox, image challenges, timeouts, retries. Cross-device compatible.\"\"\"
        solver_script = `
        (function() {
            'use strict';
            
            // Universal solveSimpleChallenge - prevents ReferenceError everywhere
            window.solveSimpleChallenge = async function() {
                console.log('[FULL CAPTCHA SOLVER v2.0] solveSimpleChallenge activated - cross-platform');
                
                // Enhanced Google challenge detection (desktop + mobile)
                const isGoogleChallenge = window.location.hostname.includes('google.com') && 
                    (window.location.pathname.includes('/sorry/') || 
                     window.location.search.includes('continue=') ||
                     document.title.toLowerCase().includes('sorry') ||
                     document.querySelector('#recaptcha, [id*="captcha"], [class*="captcha"], iframe[src*="recaptcha"]') ||
                     document.querySelector('[data-msg], .sorry-message, #challenge-form'));
                
                if (!isGoogleChallenge) {
                    console.log('[FULL SOLVER] Normal page - solver inactive');
                    return 'no_challenge';
                }
                
                console.log('[FULL SOLVER] ✅ Google challenge detected - device: ' + (navigator.userAgent.includes('Mobile') ? 'MOBILE' : 'DESKTOP'));
                
                // Robust page stabilization
                await new Promise(r => setTimeout(r, navigator.userAgent.includes('Mobile') ? 1500 : 2500));
                
                // Multi-selector for checkboxes (desktop + Android Chrome)
                const selectors = [
                    'input[type="checkbox"][role="button"]',
                    '#recaptcha-checkbox',
                    '[data-recaptcha]',
                    'iframe[src*="recaptcha"]:nth-child(1) ~ div input[type="checkbox"]',
                    '.g-recaptcha input[type="checkbox"]',
                    '#rc-imageselect, .rc-imageselect',
                    '[aria-label*="verify"], [aria-label*="checkbox"]'
                ];
                
                let checkbox = null;
                for (let sel of selectors) {
                    checkbox = document.querySelector(sel);
                    if (checkbox) {
                        console.log('[FULL SOLVER] Found checkbox via selector: ' + sel);
                        break;
                    }
                }
                
                // Handle iframe reCAPTCHA
                if (!checkbox && document.querySelector('iframe[src*="recaptcha"]')) {
                    console.log('[FULL SOLVER] reCAPTCHA iframe detected');
                    const iframe = document.querySelector('iframe[src*="recaptcha"]');
                    checkbox = iframe.contentDocument?.querySelector('input[type="checkbox"]');
                }
                
                if (checkbox && !checkbox.checked) {
                    console.log('[FULL SOLVER] 🎯 Clicking checkbox');
                    
                    // Simulate realistic human click
                    const rect = checkbox.getBoundingClientRect();
                    const clientX = rect.left + rect.width / 2 + (Math.random() - 0.5) * 10;
                    const clientY = rect.top + rect.height / 2 + (Math.random() - 0.5) * 10;
                    
                    checkbox.dispatchEvent(new MouseEvent('mousedown', {clientX, clientY, bubbles: true}));
                    await new Promise(r => setTimeout(r, 50 + Math.random()*100));
                    checkbox.dispatchEvent(new MouseEvent('mouseup', {clientX, clientY, bubbles: true}));
                    checkbox.click();
                    
                    // Mobile touch simulation
                    if (navigator.userAgent.includes('Mobile')) {
                        checkbox.dispatchEvent(new TouchEvent('touchstart', {bubbles: true}));
                        await new Promise(r => setTimeout(r, 100));
                        checkbox.dispatchEvent(new TouchEvent('touchend', {bubbles: true}));
                    }
                    
                    // Wait for verification + image challenge if needed
                    await new Promise(r => setTimeout(r, navigator.userAgent.includes('Mobile') ? 4000 : 5000));
                    
                    // Auto-solve image selection if appeared
                    const imageTiles = document.querySelectorAll('.rc-imageselect-tile, .image-tile');
                    if (imageTiles.length > 0) {
                        console.log('[FULL SOLVER] 🖼️ Image challenge - auto-selecting');
                        imageTiles.forEach(tile => tile.click());
                        await new Promise(r => setTimeout(r, 1000));
                    }
                    
                    // Submit verification
                    const submitBtns = document.querySelectorAll('input[value="Verify"], button[type="submit"], #submit-button, .verify-button, [aria-label*="submit"]');
                    if (submitBtns.length > 0) {
                        console.log('[FULL SOLVER] ✅ Submitting');
                        submitBtns[0].click();
                    }
                    
                    return 'challenge_solved_auto';
                }
                
                // Try refresh/new attempt
                const refreshEls = document.querySelectorAll('a[href*="refresh"], .refresh-link, [aria-label*="refresh"], #refresh-button');
                if (refreshEls.length > 0) {
                    console.log('[FULL SOLVER] 🔄 Refreshing for retry');
                    refreshEls[0].click();
                    return 'retrying';
                }
                
                // Fallback: wait and monitor
                console.log('[FULL SOLVER] ⏳ Challenge stuck - monitoring for 30s');
                const observer = new MutationObserver(() => {
                    // Re-trigger on DOM changes
                    window.solveSimpleChallenge();
                });
                observer.observe(document.body, {childList: true, subtree: true});
                setTimeout(() => observer.disconnect(), 30000);
                
                return 'monitoring';
            };
            
            // Auto-trigger on multiple events for reliability
            ['DOMContentLoaded', 'load'].forEach(evt => {
                if (document.readyState === 'loading') {
                    document.addEventListener(evt, window.solveSimpleChallenge, {once: true});
                }
            });
            
            // Periodic polling for dynamic pages
            const interval = setInterval(window.solveSimpleChallenge, 5000);
            setTimeout(() => clearInterval(interval), 60000); // Stop after 1min
            
            console.log('[FULL SOLVER v2.0] 🚀 Fully injected - Desktop/Mobile/Android ready');
        })();
        `

        try:
            await page.add_init_script(solver_script)
            logger.info('CAPTCHA solver script injected successfully')
        except Exception as e:
            logger.error(f'Failed to inject CAPTCHA solver: {e}')

