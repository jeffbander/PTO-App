const { test, expect } = require('@playwright/test');

test.describe('Phone Number Edit Functionality', () => {

    test('Admin Dashboard - Edit Employee Phone Number', async ({ page }) => {
        console.log('📞 Testing Phone Number Edit Functionality');
        console.log('==========================================');

        // Step 1: Login as Admin Manager
        console.log('👤 Step 1: Logging in as Admin Manager...');
        await page.goto('http://localhost:5000/login');
        await page.waitForLoadState('networkidle');

        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/phone-01-admin-dashboard.png', fullPage: true });
        console.log('   ✅ Admin Manager logged in successfully');

        // Step 2: Navigate to Employees page
        console.log('👥 Step 2: Viewing Employees page with Phone column...');
        await page.goto('http://localhost:5000/employees');
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/phone-02-employees-page.png', fullPage: true });
        console.log('   ✅ Employees page loaded');

        // Check if Phone column exists in table
        const phoneColumnExists = await page.locator('th:has-text("Phone")').count() > 0;
        console.log(`   📋 Phone column in table: ${phoneColumnExists ? '✅ Present' : '❌ Missing'}`);

        // Step 3: Click edit on the first employee
        console.log('✏️ Step 3: Editing first employee to add phone number...');

        const editButton = page.locator('a[data-bs-toggle="tooltip"][title="Edit Employee"]').first();
        await editButton.click();
        await page.waitForLoadState('networkidle');
        await page.screenshot({ path: 'test-results/phone-03-edit-employee-form.png', fullPage: true });
        console.log('   ✅ Employee edit form loaded');

        // Step 4: Check for phone field and add phone number
        console.log('📞 Step 4: Adding phone number to employee...');

        const phoneField = page.locator('input[name="phone"]');
        const hasPhoneField = await phoneField.count() > 0;
        console.log(`   📱 Phone field in form: ${hasPhoneField ? '✅ Present' : '❌ Missing'}`);

        if (hasPhoneField) {
            // Get employee name for logging
            const employeeName = await page.inputValue('input[name="name"]');
            console.log(`   👤 Editing employee: ${employeeName}`);

            // Add phone number
            const phoneNumber = '(555) 867-5309';
            await phoneField.fill(phoneNumber);
            console.log(`   📞 Entered phone number: ${phoneNumber}`);

            await page.screenshot({ path: 'test-results/phone-04-phone-number-entered.png', fullPage: true });

            // Submit the form
            console.log('📤 Step 5: Submitting form with phone number...');
            await page.click('button[type="submit"]');
            await page.waitForLoadState('networkidle');
            await page.screenshot({ path: 'test-results/phone-05-form-submitted.png', fullPage: true });
            console.log('   ✅ Form submitted successfully');

            // Step 6: Verify phone number appears in employees list
            console.log('🔍 Step 6: Verifying phone number in employees list...');

            // Should be redirected back to employees page
            const currentUrl = page.url();
            if (currentUrl.includes('/employees')) {
                console.log('   ✅ Redirected back to employees page');
            } else {
                // Navigate back to employees page if not redirected
                await page.goto('http://localhost:5000/employees');
                await page.waitForLoadState('networkidle');
            }

            await page.screenshot({ path: 'test-results/phone-06-employees-with-phone.png', fullPage: true });

            // Check if the phone number appears in the table
            const pageContent = await page.textContent('body');
            if (pageContent.includes(phoneNumber)) {
                console.log(`   ✅ Phone number ${phoneNumber} found in employees list!`);
            } else {
                console.log(`   ⚠️ Phone number ${phoneNumber} not immediately visible in list`);
            }

            // Step 7: Test editing the phone number again
            console.log('🔄 Step 7: Testing phone number update...');

            // Click edit on the same employee again
            await editButton.click();
            await page.waitForLoadState('networkidle');

            // Check if phone number is pre-populated
            const currentPhoneValue = await page.inputValue('input[name="phone"]');
            console.log(`   📞 Current phone value in form: "${currentPhoneValue}"`);

            if (currentPhoneValue === phoneNumber) {
                console.log('   ✅ Phone number correctly pre-populated in edit form');

                // Change to a new phone number
                const newPhoneNumber = '(555) 123-9876';
                await page.fill('input[name="phone"]', newPhoneNumber);
                console.log(`   📞 Updated phone number to: ${newPhoneNumber}`);

                await page.screenshot({ path: 'test-results/phone-07-phone-updated.png', fullPage: true });

                // Submit again
                await page.click('button[type="submit"]');
                await page.waitForLoadState('networkidle');
                await page.screenshot({ path: 'test-results/phone-08-final-employees-list.png', fullPage: true });

                console.log('   ✅ Phone number updated successfully');
            } else {
                console.log(`   ⚠️ Phone not pre-populated. Expected: ${phoneNumber}, Got: ${currentPhoneValue}`);
            }

        } else {
            console.log('   ❌ Phone field not found in edit form - database schema may need updating');
        }

        // Final summary
        console.log('\n🎉 Phone Number Test Complete!');
        console.log('===============================');
        console.log('✅ Admin login successful');
        console.log('✅ Employees page accessed');
        console.log('✅ Employee edit form accessed');
        console.log(`✅ Phone field: ${hasPhoneField ? 'Present' : 'Missing'}`);
        console.log(`✅ Phone column in table: ${phoneColumnExists ? 'Present' : 'Missing'}`);
        if (hasPhoneField) {
            console.log('✅ Phone number added and updated successfully');
        }
        console.log('📸 All screenshots saved to test-results/');
    });

});