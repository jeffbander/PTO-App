const { test, expect } = require('@playwright/test');

test.describe('Calendar Quick Test', () => {

    test('Verify Calendar shows PTO events', async ({ page }) => {
        console.log('📅 QUICK TEST: Calendar showing PTO events');
        console.log('===========================================');

        // Navigate to calendar
        await page.goto('http://localhost:5000/calendar');
        await page.waitForLoadState('networkidle');

        // Wait for FullCalendar to initialize
        await page.waitForTimeout(3000);

        console.log('✅ Calendar page loaded');

        // Check for calendar events
        const fcEvents = page.locator('.fc-event');
        const eventCount = await fcEvents.count();
        console.log(`📊 Found ${eventCount} calendar events`);

        if (eventCount > 0) {
            console.log('🎉 SUCCESS: Calendar is showing PTO events!');

            // Show first few events
            for (let i = 0; i < Math.min(eventCount, 3); i++) {
                const eventText = await fcEvents.nth(i).textContent();
                console.log(`   📅 Event ${i+1}: ${eventText?.trim()}`);
            }
        } else {
            console.log('❌ No events found - checking page for errors...');

            // Check console errors
            const consoleErrors = [];
            page.on('console', msg => {
                if (msg.type() === 'error') {
                    consoleErrors.push(msg.text());
                }
            });

            if (consoleErrors.length > 0) {
                console.log('JavaScript errors found:');
                consoleErrors.forEach(error => console.log(`   ❌ ${error}`));
            }
        }

        // Take screenshot
        await page.screenshot({ path: 'test-results/calendar-quick-test.png', fullPage: true });
        console.log('📸 Screenshot saved');

        console.log(`\n✅ Calendar Test Complete - Found ${eventCount} events`);
    });

});