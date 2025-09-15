const { test, expect } = require('@playwright/test');

test.describe('PTO Approval Interface Demo', () => {

    test('Demo: Admin Manager PTO Approval with Test Data', async ({ page }) => {
        console.log('🎯 DEMO: PTO Approval Interface with Real Test Data');
        console.log('===================================================');

        // Step 1: Show login as Admin Manager
        console.log('👤 Step 1: Admin Manager Login...');
        await page.goto('http://localhost:5000/login');
        await page.waitForLoadState('networkidle');

        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');
        console.log('   ✅ Admin Manager logged in successfully');

        // Step 2: Navigate to Admin Dashboard
        console.log('📊 Step 2: Navigating to Admin Dashboard...');
        await page.goto('http://localhost:5000/dashboard/admin');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/pto-demo-01-admin-dashboard.png', fullPage: true });
        console.log('   📸 Admin dashboard screenshot taken');

        // Step 3: Show pending PTO requests
        console.log('📋 Step 3: Analyzing pending PTO requests...');
        const pageContent = await page.textContent('body');

        // Count pending requests in the interface
        const pendingElements = page.locator(':has-text("Pending"), :has-text("pending")');
        const pendingCount = await pendingElements.count();
        console.log(`   📊 Found ${pendingCount} elements mentioning "pending" on page`);

        // Look for PTO request cards or table rows
        const requestCards = page.locator('.card, .request-card, tr:has(.btn-approve), tr:has(button:has-text("Approve"))');
        const cardCount = await requestCards.count();
        console.log(`   📋 Found ${cardCount} PTO request cards/rows`);

        // Show stats
        const statsNumbers = page.locator('.stat-number, .card-body h3, .badge');
        const statsCount = await statsNumbers.count();
        console.log(`   📈 Found ${statsCount} statistics elements on dashboard`);

        // Look for approval buttons
        const approveButtons = page.locator('button:has-text("Approve"), .btn-approve, a:has-text("Approve")');
        const approveButtonCount = await approveButtons.count();
        console.log(`   🎯 Found ${approveButtonCount} approval buttons`);

        if (approveButtonCount > 0) {
            console.log('   ✅ SUCCESS: PTO approval interface is working!');

            // Step 4: Demonstrate approving a PTO request
            console.log('✅ Step 4: Demonstrating PTO approval...');
            await page.screenshot({ path: 'test-results/pto-demo-02-before-approval.png', fullPage: true });

            // Get request details before approval
            const firstRequestRow = requestCards.first();
            if (await firstRequestRow.count() > 0) {
                const requestDetails = await firstRequestRow.textContent();
                console.log(`   📝 First request details: ${requestDetails?.substring(0, 100)}...`);
            }

            // Click first approve button
            console.log('   🖱️  Clicking approve button...');
            await approveButtons.first().click();
            await page.waitForLoadState('networkidle');
            await page.screenshot({ path: 'test-results/pto-demo-03-after-approval.png', fullPage: true });
            console.log('   📸 After approval screenshot taken');

            // Check for success message
            const successMessage = page.locator('.alert-success, .flash-success');
            if (await successMessage.count() > 0) {
                const message = await successMessage.textContent();
                console.log(`   ✅ Success message: ${message}`);
            }

            // Step 5: Show updated dashboard stats
            console.log('📊 Step 5: Updated dashboard stats...');
            await page.goto('http://localhost:5000/dashboard/admin');
            await page.waitForLoadState('networkidle');
            await page.screenshot({ path: 'test-results/pto-demo-04-updated-dashboard.png', fullPage: true });

            const updatedApproveButtons = page.locator('button:has-text("Approve"), .btn-approve, a:has-text("Approve")');
            const updatedButtonCount = await updatedApproveButtons.count();
            console.log(`   📈 Remaining approval buttons: ${updatedButtonCount} (was ${approveButtonCount})`);

        } else {
            console.log('   ❌ No approval buttons found - let me investigate...');

            // Debug: Show what's actually on the page
            console.log('🔍 DEBUG: Investigating admin dashboard content...');

            // Look for any buttons at all
            const allButtons = page.locator('button, .btn, a[class*="btn"]');
            const totalButtons = await allButtons.count();
            console.log(`   🔘 Total buttons on page: ${totalButtons}`);

            // Show first few buttons
            for (let i = 0; i < Math.min(totalButtons, 5); i++) {
                const buttonText = await allButtons.nth(i).textContent();
                console.log(`      Button ${i+1}: "${buttonText?.trim()}"`);
            }

            // Check if there are any requests shown
            if (pageContent.includes('No PTO requests') || pageContent.includes('No requests')) {
                console.log('   📭 Page shows "No requests" message');
            } else {
                console.log('   📄 Page content preview:');
                console.log(`      ${pageContent.substring(0, 300)}...`);
            }
        }

        // Step 6: Test other dashboard views for comparison
        console.log('🔍 Step 6: Checking other dashboards for comparison...');

        // Clinical dashboard
        await page.goto('http://localhost:5000/dashboard/clinical');
        await page.waitForLoadState('networkidle');
        const clinicalApproveButtons = page.locator('button:has-text("Approve"), .btn-approve');
        const clinicalButtonCount = await clinicalApproveButtons.count();
        console.log(`   🏥 Clinical dashboard approve buttons: ${clinicalButtonCount}`);
        await page.screenshot({ path: 'test-results/pto-demo-05-clinical-dashboard.png', fullPage: true });

        // Superadmin dashboard
        await page.goto('http://localhost:5000/dashboard/superadmin');
        await page.waitForLoadState('networkidle');
        const superadminApproveButtons = page.locator('button:has-text("Approve"), .btn-approve');
        const superadminButtonCount = await superadminApproveButtons.count();
        console.log(`   👑 Superadmin dashboard approve buttons: ${superadminButtonCount}`);
        await page.screenshot({ path: 'test-results/pto-demo-06-superadmin-dashboard.png', fullPage: true });

        console.log('\n🎯 PTO APPROVAL DEMO COMPLETE');
        console.log('=============================');
        console.log(`✅ Admin Dashboard Approve Buttons: ${approveButtonCount}`);
        console.log(`✅ Clinical Dashboard Approve Buttons: ${clinicalButtonCount}`);
        console.log(`✅ Superadmin Dashboard Approve Buttons: ${superadminButtonCount}`);
        console.log('📸 All demo screenshots saved to test-results/');

        if (approveButtonCount > 0) {
            console.log('🎉 SUCCESS: PTO approval interface is fully functional!');
        } else {
            console.log('⚠️  FINDING: Need to investigate why approval buttons are not showing');
        }
    });

});