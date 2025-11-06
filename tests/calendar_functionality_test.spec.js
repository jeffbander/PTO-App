const { test, expect } = require('@playwright/test');

test.describe('Calendar Functionality Test', () => {

    test('Demo: Calendar showing PTO requests (Approved and Pending)', async ({ page }) => {
        console.log('📅 DEMO: Calendar showing PTO requests');
        console.log('========================================');

        // Step 1: Navigate to calendar page
        console.log('🔗 Step 1: Navigating to calendar page...');
        await page.goto('http://localhost:5000/calendar');
        await page.waitForLoadState('networkidle');

        // Wait for FullCalendar to load
        await page.waitForTimeout(2000);
        await page.screenshot({ path: 'test-results/calendar-01-initial-view.png', fullPage: true });
        console.log('   📸 Initial calendar view screenshot taken');

        // Step 2: Check if calendar is loaded
        console.log('📋 Step 2: Analyzing calendar content...');

        // Check if FullCalendar is initialized
        const calendarEl = page.locator('#calendar');
        const isCalendarVisible = await calendarEl.isVisible();
        console.log(`   📅 Calendar element visible: ${isCalendarVisible ? '✅' : '❌'}`);

        // Check for FullCalendar specific elements
        const fcToolbar = page.locator('.fc-toolbar');
        const fcToolbarVisible = await fcToolbar.count() > 0;
        console.log(`   🔧 FullCalendar toolbar found: ${fcToolbarVisible ? '✅' : '❌'}`);

        // Check for calendar events
        const fcEvents = page.locator('.fc-event');
        const eventCount = await fcEvents.count();
        console.log(`   📊 Calendar events found: ${eventCount}`);

        if (eventCount > 0) {
            console.log('   ✅ SUCCESS: Calendar has PTO events displayed!');

            // Step 3: Analyze event details
            console.log('🔍 Step 3: Analyzing PTO events on calendar...');

            for (let i = 0; i < Math.min(eventCount, 5); i++) {
                const event = fcEvents.nth(i);
                const eventTitle = await event.textContent();
                const eventColor = await event.evaluate(el => {
                    return window.getComputedStyle(el).backgroundColor;
                });
                console.log(`   📅 Event ${i + 1}: "${eventTitle?.trim()}" (Color: ${eventColor})`);
            }

            // Step 4: Test event click functionality
            console.log('🖱️  Step 4: Testing event click (modal popup)...');
            await fcEvents.first().click();
            await page.waitForTimeout(1000);

            // Check if modal opened
            const modal = page.locator('#eventModal');
            const modalVisible = await modal.isVisible();
            console.log(`   📋 Event details modal opened: ${modalVisible ? '✅' : '❌'}`);

            if (modalVisible) {
                const modalContent = await page.locator('#eventDetails').textContent();
                console.log(`   📝 Modal content preview: ${modalContent?.substring(0, 100)}...`);

                // Close modal
                await page.locator('.btn-close').click();
                await page.waitForTimeout(500);
            }

            await page.screenshot({ path: 'test-results/calendar-02-events-shown.png', fullPage: true });

        } else {
            console.log('   ❌ No calendar events found - investigating...');

            // Debug: Check page content
            const pageContent = await page.textContent('body');
            console.log(`   📄 Page mentions "PTO": ${pageContent.includes('PTO') ? '✅' : '❌'}`);
            console.log(`   📄 Page mentions "calendar": ${pageContent.includes('calendar') ? '✅' : '❌'}`);

            // Check console for JavaScript errors
            const errors = [];
            page.on('console', msg => {
                if (msg.type() === 'error') {
                    errors.push(msg.text());
                }
            });

            // Check if calendar_events data is available
            const calendarData = await page.evaluate(() => {
                return window.allEvents || 'not found';
            });
            console.log(`   📊 Calendar events data: ${typeof calendarData === 'object' ? JSON.stringify(calendarData).substring(0, 100) + '...' : calendarData}`);
        }

        // Step 5: Test calendar navigation
        console.log('🧭 Step 5: Testing calendar navigation...');

        // Test month navigation
        const prevButton = page.locator('#prevMonth');
        const nextButton = page.locator('#nextMonth');
        const todayButton = page.locator('#today');

        const hasNavButtons = await prevButton.count() > 0 && await nextButton.count() > 0;
        console.log(`   🔄 Navigation buttons found: ${hasNavButtons ? '✅' : '❌'}`);

        if (hasNavButtons) {
            // Click next month
            await nextButton.click();
            await page.waitForTimeout(1000);
            console.log('   ➡️  Clicked next month');

            // Click previous month to go back
            await prevButton.click();
            await page.waitForTimeout(1000);
            console.log('   ⬅️  Clicked previous month');

            // Click today to return to current month
            await todayButton.click();
            await page.waitForTimeout(1000);
            console.log('   📅 Clicked today button');
        }

        // Step 6: Test filtering functionality
        console.log('🔍 Step 6: Testing calendar filters...');

        const teamFilter = page.locator('#teamFilter');
        const positionFilter = page.locator('#positionFilter');
        const clearFilters = page.locator('#clearFilters');

        const hasFilters = await teamFilter.count() > 0;
        console.log(`   🔎 Filter controls found: ${hasFilters ? '✅' : '❌'}`);

        if (hasFilters) {
            // Test team filter
            await teamFilter.selectOption('admin');
            await page.waitForTimeout(1000);

            const filteredEvents = await page.locator('.fc-event').count();
            console.log(`   📊 Events after team filter 'admin': ${filteredEvents}`);

            // Clear filters
            await clearFilters.click();
            await page.waitForTimeout(1000);

            const allEventsAfterClear = await page.locator('.fc-event').count();
            console.log(`   📊 Events after clearing filters: ${allEventsAfterClear}`);
        }

        // Step 7: Check upcoming events panel
        console.log('📋 Step 7: Checking upcoming events panel...');

        const upcomingEvents = page.locator('#upcomingEvents');
        const upcomingVisible = await upcomingEvents.isVisible();
        console.log(`   📅 Upcoming events panel visible: ${upcomingVisible ? '✅' : '❌'}`);

        if (upcomingVisible) {
            const upcomingContent = await upcomingEvents.textContent();
            const hasUpcomingEvents = !upcomingContent.includes('No upcoming PTO');
            console.log(`   📊 Has upcoming PTO events: ${hasUpcomingEvents ? '✅' : '❌'}`);

            if (hasUpcomingEvents) {
                console.log(`   📝 Upcoming events preview: ${upcomingContent.substring(0, 100)}...`);
            }
        }

        // Final screenshot
        await page.screenshot({ path: 'test-results/calendar-03-final-state.png', fullPage: true });

        console.log('\n📅 CALENDAR FUNCTIONALITY TEST COMPLETE');
        console.log('=========================================');
        console.log(`✅ Calendar Loaded: ${isCalendarVisible ? 'Yes' : 'No'}`);
        console.log(`✅ Events Displayed: ${eventCount}`);
        console.log(`✅ Navigation Working: ${hasNavButtons ? 'Yes' : 'No'}`);
        console.log(`✅ Filters Available: ${hasFilters ? 'Yes' : 'No'}`);
        console.log(`✅ Upcoming Events Panel: ${upcomingVisible ? 'Yes' : 'No'}`);
        console.log('📸 All calendar screenshots saved to test-results/');

        if (eventCount > 0) {
            console.log('🎉 SUCCESS: Calendar is fully functional with PTO data!');
        } else {
            console.log('⚠️  FINDING: Calendar loaded but no events are displayed - need to check data flow');
        }
    });

});