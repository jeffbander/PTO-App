const { test, expect } = require('@playwright/test');

test.describe('PTO Approval Location Test', () => {

    test('Show Admin Manager PTO Approval Interface', async ({ page }) => {
        console.log('🎯 Locating PTO Approval Interface in Admin Dashboard');
        console.log('==================================================');

        // Step 1: Create a PTO request first (so we have something to approve)
        console.log('📝 Step 1: First, creating a PTO request to approve...');
        await page.goto('http://localhost:5000');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/approval-01-homepage.png', fullPage: true });

        // Fill out a PTO request quickly
        await page.selectOption('select[name="team"]', 'admin');
        await page.waitForTimeout(1000);
        await page.selectOption('select[name="position"]', 'Front Desk/Admin');
        await page.waitForTimeout(1000);
        await page.selectOption('select[name="name"]', { index: 1 }); // Select first available employee
        await page.fill('input[name="start_date"]', '2024-12-01');
        await page.fill('input[name="end_date"]', '2024-12-03');
        await page.selectOption('select[name="pto_type"]', 'Vacation');
        await page.fill('textarea[name="reason"]', 'Test PTO request for approval demonstration');
        await page.screenshot({ path: 'test-results/approval-02-pto-request-submitted.png', fullPage: true });
        console.log('   📋 PTO request form filled out');

        // Submit the request
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');
        console.log('   ✅ PTO request submitted (may redirect due to maintenance)');

        // Step 2: Login as Admin Manager
        console.log('👤 Step 2: Logging in as Admin Manager...');
        await page.goto('http://localhost:5000/login');
        await page.waitForLoadState('networkidle');

        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/approval-03-admin-logged-in.png', fullPage: true });
        console.log('   ✅ Admin Manager logged in successfully');

        // Step 3: Explore all possible admin dashboard locations
        console.log('🔍 Step 3: Exploring Admin Dashboard locations for PTO approval...');

        // 3a. Check main dashboard
        console.log('   📊 Checking main dashboard...');
        await page.goto('http://localhost:5000/dashboard');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/approval-04-main-dashboard.png', fullPage: true });

        const mainDashboardContent = await page.textContent('body');
        const hasPendingOnMain = mainDashboardContent.includes('pending') || mainDashboardContent.includes('approve');
        console.log(`      Main Dashboard has pending/approve: ${hasPendingOnMain ? '✅' : '❌'}`);

        // 3b. Check admin-specific dashboard
        console.log('   👨‍💼 Checking admin-specific dashboard...');
        await page.goto('http://localhost:5000/dashboard/admin');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/approval-05-admin-dashboard.png', fullPage: true });

        const adminDashboardContent = await page.textContent('body');
        const hasPendingOnAdmin = adminDashboardContent.includes('pending') || adminDashboardContent.includes('approve');
        console.log(`      Admin Dashboard has pending/approve: ${hasPendingOnAdmin ? '✅' : '❌'}`);

        // Look for specific approval buttons or pending requests
        const approveButtons = page.locator('button:has-text("Approve"), .btn-approve, a:has-text("Approve")');
        const approveButtonCount = await approveButtons.count();
        console.log(`      Found ${approveButtonCount} approve buttons on admin dashboard`);

        // Check for pending requests section
        const pendingSection = page.locator(':has-text("Pending"), :has-text("pending")');
        const pendingSectionCount = await pendingSection.count();
        console.log(`      Found ${pendingSectionCount} sections mentioning "pending"`);

        // 3c. Check navigation menu for other PTO-related pages
        console.log('   📋 Checking navigation menu options...');

        // Look for navigation links
        const navLinks = page.locator('nav a, .navbar a, .nav-link');
        const navCount = await navLinks.count();
        console.log(`      Found ${navCount} navigation links`);

        for (let i = 0; i < Math.min(navCount, 10); i++) {
            const linkText = await navLinks.nth(i).textContent();
            const linkHref = await navLinks.nth(i).getAttribute('href');
            if (linkText && linkText.trim()) {
                console.log(`         Nav Link: "${linkText.trim()}" -> ${linkHref}`);
            }
        }

        // 3d. Check dropdown menus
        console.log('   📂 Checking dropdown menus...');
        const dashboardsDropdown = page.locator('a:has-text("Dashboards"), .dropdown-toggle:has-text("Dashboard")');
        if (await dashboardsDropdown.count() > 0) {
            await dashboardsDropdown.first().click();
            await page.waitForTimeout(1000);
            await page.screenshot({ path: 'test-results/approval-06-dashboards-dropdown.png', fullPage: true });
            console.log('      Dashboards dropdown opened');

            // List dropdown options
            const dropdownOptions = page.locator('.dropdown-menu a, .dropdown-item');
            const dropdownCount = await dropdownOptions.count();
            console.log(`      Found ${dropdownCount} dropdown options:`);

            for (let i = 0; i < Math.min(dropdownCount, 8); i++) {
                const optionText = await dropdownOptions.nth(i).textContent();
                const optionHref = await dropdownOptions.nth(i).getAttribute('href');
                if (optionText && optionText.trim()) {
                    console.log(`         Option: "${optionText.trim()}" -> ${optionHref}`);
                }
            }
        }

        // Step 4: Test specific dashboard routes
        console.log('🎯 Step 4: Testing specific dashboard routes...');

        const dashboardRoutes = [
            '/dashboard/superadmin',
            '/pending_employees',
            '/employees',
            '/calendar'
        ];

        for (const route of dashboardRoutes) {
            console.log(`   🔗 Testing route: ${route}`);
            try {
                await page.goto(`http://localhost:5000${route}`);
                await page.waitForLoadState('networkidle');

                const routeContent = await page.textContent('body');
                const hasApprovalContent = routeContent.includes('approve') ||
                                         routeContent.includes('pending') ||
                                         routeContent.includes('PTO');

                console.log(`      Route ${route}: ${hasApprovalContent ? '✅ Has PTO content' : '❌ No PTO content'}`);

                if (hasApprovalContent) {
                    await page.screenshot({ path: `test-results/approval-07-route-${route.replace('/', '-')}.png`, fullPage: true });
                }
            } catch (error) {
                console.log(`      Route ${route}: ❌ Error or no access`);
            }
        }

        // Step 5: Check current PTO system implementation
        console.log('🔧 Step 5: Analyzing current PTO system implementation...');

        // Look at the routes.py file structure by checking what endpoints exist
        await page.goto('http://localhost:5000/dashboard/admin');
        await page.waitForLoadState('networkidle');

        // Check page source for any hidden elements or JavaScript that might handle PTO
        const pageSource = await page.content();
        const hasJSApproval = pageSource.includes('approve') || pageSource.includes('pto');
        console.log(`      Page source contains PTO approval JS: ${hasJSApproval ? '✅' : '❌'}`);

        // Final screenshot of current admin interface
        await page.screenshot({ path: 'test-results/approval-08-final-admin-interface.png', fullPage: true });

        // Summary
        console.log('\n🎯 PTO APPROVAL INTERFACE ANALYSIS COMPLETE');
        console.log('===========================================');
        console.log(`✅ Main Dashboard has PTO content: ${hasPendingOnMain ? 'Yes' : 'No'}`);
        console.log(`✅ Admin Dashboard has PTO content: ${hasPendingOnAdmin ? 'Yes' : 'No'}`);
        console.log(`✅ Approve buttons found: ${approveButtonCount}`);
        console.log(`✅ Pending sections found: ${pendingSectionCount}`);
        console.log('📸 All screenshots saved showing current admin interface');

        if (approveButtonCount === 0 && !hasPendingOnAdmin) {
            console.log('\n⚠️  FINDING: PTO approval interface appears to be in maintenance mode');
            console.log('   The routes.py shows flash messages indicating approval is "under maintenance"');
            console.log('   This explains why no approve buttons are visible in the current interface');
        }
    });

});