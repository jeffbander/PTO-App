const { test, expect } = require('@playwright/test');

test.describe('Calendar Manual Test', () => {

    test('Manual Calendar Test - User can see current month events', async ({ page }) => {
        console.log('📅 MANUAL CALENDAR TEST');
        console.log('=======================');
        console.log('⏳ Opening calendar page...');

        await page.goto('http://localhost:5000/calendar');
        await page.waitForLoadState('networkidle');

        // Wait for calendar to load
        await page.waitForTimeout(3000);

        console.log('✅ Calendar page loaded');
        console.log('');
        console.log('📋 INSTRUCTIONS FOR MANUAL VERIFICATION:');
        console.log('');
        console.log('🔍 Look for these PTO events on the calendar:');
        console.log('   📅 Sept 16: Emily Davis - Personal (Child school event)');
        console.log('   📅 Sept 18: Lisa Rodriguez - Sick (Medical appointment)');
        console.log('   📅 Sept 20-22: John Smith - Vacation (September vacation)');
        console.log('   📅 Sept 25-26: Sarah Johnson - Personal (Personal time off)');
        console.log('   📅 Sept 30: David Brown - Vacation (End of month break)');
        console.log('   📅 Oct 2-3: John Smith - Personal (Long weekend)');
        console.log('');
        console.log('🎨 Visual indicators:');
        console.log('   🟡 Yellow background = Pending requests');
        console.log('   🟢 Green background = Approved requests');
        console.log('');
        console.log('🖱️  Try clicking on any event to see details popup');
        console.log('🔄 Use navigation buttons to check October for John Smith event');
        console.log('');

        // Take screenshot for manual review
        await page.screenshot({
            path: 'test-results/calendar-manual-verification.png',
            fullPage: true
        });
        console.log('📸 Screenshot saved: test-results/calendar-manual-verification.png');

        // Count calendar events for verification
        await page.waitForTimeout(2000);
        const events = page.locator('.fc-event');
        const eventCount = await events.count();

        console.log('');
        console.log(`📊 JavaScript found ${eventCount} calendar events`);

        if (eventCount > 0) {
            console.log('');
            console.log('✅ SUCCESS: Calendar events are being displayed!');

            // List the visible events
            for (let i = 0; i < Math.min(eventCount, 6); i++) {
                const eventTitle = await events.nth(i).textContent();
                console.log(`   📅 Event ${i + 1}: "${eventTitle?.trim()}"`);
            }
        } else {
            console.log('');
            console.log('❌ No events found by JavaScript - checking page content...');

            // Debug information
            const pageText = await page.textContent('body');
            const hasCalendarData = pageText.includes('John Smith') || pageText.includes('Sarah Johnson');
            console.log(`   📄 Page contains employee names: ${hasCalendarData ? 'YES' : 'NO'}`);

            const hasFullCalendar = await page.locator('.fc-toolbar').count() > 0;
            console.log(`   📅 FullCalendar UI loaded: ${hasFullCalendar ? 'YES' : 'NO'}`);
        }

        console.log('');
        console.log('⏸️  Test will pause for 30 seconds for manual verification...');
        console.log('   👀 Please check the browser window for calendar events');

        // Wait for manual verification
        await page.waitForTimeout(30000);

        console.log('');
        console.log('📅 Manual calendar test completed');
    });

});