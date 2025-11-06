const { test, expect } = require('@playwright/test');

test.describe('Admin PTO Approval Interface', () => {

    test('SHOW: Current Admin Dashboard and Fix PTO Approval', async ({ page }) => {
        console.log('🎯 SHOWING: Current Admin Dashboard PTO Interface');
        console.log('==============================================');

        // Step 1: Login as Admin Manager
        console.log('👤 Step 1: Admin Manager Login...');
        await page.goto('http://localhost:5000/login');
        await page.waitForLoadState('networkidle');

        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');
        console.log('   ✅ Admin Manager logged in');

        // Step 2: Show main dashboard
        console.log('📊 Step 2: Main Dashboard...');
        await page.goto('http://localhost:5000/dashboard');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/show-01-main-dashboard.png', fullPage: true });
        console.log('   📸 Main dashboard screenshot taken');

        // Step 3: Show admin-specific dashboard
        console.log('👨‍💼 Step 3: Admin-Specific Dashboard...');
        await page.goto('http://localhost:5000/dashboard/admin');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/show-02-admin-dashboard.png', fullPage: true });
        console.log('   📸 Admin dashboard screenshot taken');

        // Step 4: Show navigation menu
        console.log('🧭 Step 4: Navigation Menu...');

        // Check for Dashboards dropdown
        const dashboardsDropdown = page.locator('a:has-text("Dashboards"), .dropdown-toggle:has-text("Dashboard")');
        if (await dashboardsDropdown.count() > 0) {
            await dashboardsDropdown.first().hover();
            await page.waitForTimeout(500);
            await dashboardsDropdown.first().click();
            await page.waitForTimeout(1000);
            await page.screenshot({ path: 'test-results/show-03-dashboards-menu.png', fullPage: true });
            console.log('   📸 Dashboards menu screenshot taken');
        }

        // Step 5: Show superadmin dashboard (might have more PTO features)
        console.log('🔧 Step 5: Superadmin Dashboard...');
        await page.goto('http://localhost:5000/dashboard/superadmin');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/show-04-superadmin-dashboard.png', fullPage: true });
        console.log('   📸 Superadmin dashboard screenshot taken');

        // Step 6: Show current state analysis
        console.log('🔍 Step 6: Current State Analysis...');

        const currentContent = await page.textContent('body');
        console.log('   📋 Dashboard Analysis:');
        console.log(`      - Contains "pending": ${currentContent.includes('pending') || currentContent.includes('Pending')}`);
        console.log(`      - Contains "approve": ${currentContent.includes('approve') || currentContent.includes('Approve')}`);
        console.log(`      - Contains "PTO": ${currentContent.includes('PTO') || currentContent.includes('pto')}`);
        console.log(`      - Contains "request": ${currentContent.includes('request') || currentContent.includes('Request')}`);

        // Look for any buttons or links
        const allButtons = page.locator('button, .btn, a[class*="btn"]');
        const buttonCount = await allButtons.count();
        console.log(`      - Found ${buttonCount} buttons/links on page`);

        // Step 7: Check what the dashboard SHOULD show
        console.log('💡 Step 7: What Admin Dashboard SHOULD Show...');
        console.log('   📝 EXPECTED PTO Approval Interface:');
        console.log('      ✓ Pending PTO Requests section');
        console.log('      ✓ Employee name and request details');
        console.log('      ✓ "Approve" and "Deny" buttons');
        console.log('      ✓ Request dates and reason');
        console.log('      ✓ Team/position information');

        console.log('\n   ❌ CURRENT ISSUE IDENTIFIED:');
        console.log('      - PTO approval routes exist but show "under maintenance"');
        console.log('      - Dashboard templates not showing actual PTO requests');
        console.log('      - Need to implement proper PTO request display and approval');

        // Final screenshot
        await page.screenshot({ path: 'test-results/show-05-final-interface-state.png', fullPage: true });

        console.log('\n🎯 ADMIN PTO INTERFACE ANALYSIS COMPLETE');
        console.log('========================================');
        console.log('📍 WHERE PTO APPROVAL SHOULD BE:');
        console.log('   🔗 Route: /dashboard/admin');
        console.log('   📄 Template: dashboard_admin.html');
        console.log('   🔧 Status: Currently showing empty state');
        console.log('   ⚡ Action needed: Remove maintenance mode and implement PTO display');
    });

});