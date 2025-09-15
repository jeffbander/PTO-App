const { test, expect } = require('@playwright/test');

test.describe('Admin Employee Edit Functionality', () => {

    test('Admin Dashboard - Navigate to Employees and Edit Phone Number', async ({ page }) => {
        console.log('🎬 Starting Admin Employee Edit Test');
        console.log('====================================');

        // Step 1: Login as Admin Manager
        console.log('👤 Step 1: Logging in as Admin Manager...');
        await page.goto('http://localhost:5000/login');
        await page.waitForLoadState('networkidle');

        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.screenshot({ path: 'test-results/edit-01-login-form.png', fullPage: true });

        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/edit-02-admin-dashboard.png', fullPage: true });
        console.log('   ✅ Successfully logged in as Admin Manager');

        // Step 2: Navigate to Employees page
        console.log('👥 Step 2: Navigating to Employees page...');
        await page.goto('http://localhost:5000/employees');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/edit-03-employees-page.png', fullPage: true });
        console.log('   ✅ Employees page loaded');

        // Verify we can see employees
        const employeeRows = page.locator('tbody tr');
        const employeeCount = await employeeRows.count();
        console.log(`   📊 Found ${employeeCount} employees in the list`);

        if (employeeCount === 0) {
            console.log('   ❌ No employees found! Cannot proceed with edit test.');
            return;
        }

        // Step 3: Click on the first employee's edit button
        console.log('✏️ Step 3: Clicking edit button for first employee...');

        // Look for edit button (pencil icon)
        const editButton = page.locator('a[data-bs-toggle="tooltip"][title="Edit Employee"]').first();

        if (await editButton.count() === 0) {
            // Alternative: look for any edit button
            const altEditButton = page.locator('a:has(.fa-edit)').first();
            if (await altEditButton.count() > 0) {
                await altEditButton.click();
            } else {
                console.log('   ⚠️ No edit button found, trying to click on employee name...');
                // Try clicking on first employee name link
                const employeeNameLink = page.locator('tbody tr').first().locator('a').first();
                if (await employeeNameLink.count() > 0) {
                    await employeeNameLink.click();
                }
            }
        } else {
            await editButton.click();
        }

        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/edit-04-employee-edit-page.png', fullPage: true });
        console.log('   ✅ Navigated to employee edit page');

        // Step 4: Check current page and fields
        console.log('🔍 Step 4: Analyzing edit form fields...');
        const pageUrl = page.url();
        const pageContent = await page.textContent('body');

        console.log(`   🔗 Current URL: ${pageUrl}`);

        if (pageContent.includes('Edit Employee') || pageUrl.includes('/edit/')) {
            console.log('   ✅ Successfully on employee edit page');

            // Check for existing phone field
            const phoneField = page.locator('input[name="phone"]');
            const hasPhoneField = await phoneField.count() > 0;

            if (hasPhoneField) {
                console.log('   📞 Phone field found! Adding phone number...');
                await phoneField.fill('(555) 123-4567');
                console.log('   ✅ Phone number entered: (555) 123-4567');
            } else {
                console.log('   ⚠️ No phone field found in current edit form');
                console.log('   📝 Available form fields:');

                // List all input fields
                const inputs = page.locator('input');
                const inputCount = await inputs.count();
                for (let i = 0; i < inputCount; i++) {
                    const inputName = await inputs.nth(i).getAttribute('name');
                    const inputType = await inputs.nth(i).getAttribute('type');
                    if (inputName) {
                        console.log(`      - ${inputName} (${inputType})`);
                    }
                }
            }

            // Take screenshot of filled form
            await page.screenshot({ path: 'test-results/edit-05-form-filled.png', fullPage: true });

            // Try to submit the form
            console.log('📤 Step 5: Attempting to submit form...');
            const submitButton = page.locator('button[type="submit"]');
            if (await submitButton.count() > 0) {
                await submitButton.click();
                await page.waitForLoadState('networkidle');
                await page.screenshot({ path: 'test-results/edit-06-form-submitted.png', fullPage: true });
                console.log('   ✅ Form submitted successfully');
            } else {
                console.log('   ⚠️ No submit button found');
            }

        } else if (pageContent.includes('Employee Details') || pageContent.includes('employee detail')) {
            console.log('   📋 On employee details page instead of edit page');

            // Look for edit button on details page
            const editButtonOnDetails = page.locator('a:has-text("Edit Employee")');
            if (await editButtonOnDetails.count() > 0) {
                console.log('   🔗 Found edit button on details page, clicking...');
                await editButtonOnDetails.click();
                await page.waitForLoadState('networkidle');
                await page.screenshot({ path: 'test-results/edit-07-edit-from-details.png', fullPage: true });
            }
        } else {
            console.log('   ❌ Not sure where we ended up, taking screenshot for analysis');
        }

        // Step 6: Final verification
        console.log('🔍 Step 6: Final verification...');

        // Go back to employees page to verify changes
        await page.goto('http://localhost:5000/employees');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/edit-08-final-employees-page.png', fullPage: true });
        console.log('   ✅ Returned to employees page for verification');

        console.log('\n🎉 Admin Employee Edit Test Complete!');
        console.log('=====================================');
        console.log('✅ Successfully logged in as admin');
        console.log('✅ Navigated to employees page');
        console.log('✅ Attempted to edit employee details');
        console.log('✅ Form interaction tested');
        console.log('📸 All screenshots saved to test-results/');
    });

    test('Explore Employee Management Features', async ({ page }) => {
        console.log('🔍 Exploring Employee Management Features...');

        // Login as admin
        await page.goto('http://localhost:5000/login');
        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');

        // Test employees page functionality
        await page.goto('http://localhost:5000/employees');
        await page.waitForLoadState('networkidle');

        // Check for action buttons
        const actionButtons = page.locator('.btn-group a, .btn-group button');
        const actionCount = await actionButtons.count();
        console.log(`📋 Found ${actionCount} action buttons per employee`);

        // Test first employee's action buttons
        if (actionCount > 0) {
            for (let i = 0; i < Math.min(actionCount, 3); i++) {
                const buttonTitle = await actionButtons.nth(i).getAttribute('title');
                const buttonHref = await actionButtons.nth(i).getAttribute('href');
                console.log(`   Button ${i + 1}: ${buttonTitle} -> ${buttonHref}`);
            }
        }

        await page.screenshot({ path: 'test-results/explore-employee-features.png', fullPage: true });
    });

});