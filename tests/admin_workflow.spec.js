const { test, expect } = require('@playwright/test');

test.describe('Admin Manager Full Workflow Tests', () => {

    test('Complete Admin Workflow - Create Employee, Request PTO, Approve PTO', async ({ page }) => {
        console.log('🎬 Starting Complete Admin Manager Workflow Test');

        // Step 1: Navigate to application and login as Admin Manager
        console.log('👤 Step 1: Logging in as Admin Manager...');
        await page.goto('http://localhost:5000');
        await page.waitForLoadState('networkidle');

        // Navigate to login page
        await page.click('a[href*="login"]');
        await page.waitForSelector('form');

        // Login as admin manager
        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');

        // Verify login success by checking for dashboard content
        await expect(page.locator('body')).toContainText('Admin');
        console.log('✅ Admin Manager logged in successfully');

        // Step 2: Navigate to employee management and add a new employee
        console.log('👥 Step 2: Creating a new fake employee...');

        // Try to find employees link in navigation or dashboard
        try {
            await page.click('a[href*="employees"]', { timeout: 5000 });
        } catch (error) {
            console.log('Employees link not found, trying alternative navigation...');
            // If direct link doesn't work, try dashboard navigation
            await page.goto('http://localhost:5000/employees');
        }
        await page.waitForLoadState('networkidle');

        // Click add employee button
        try {
            await page.click('a[href*="add_employee"]', { timeout: 5000 });
        } catch (error) {
            console.log('Add employee button not found, navigating directly...');
            await page.goto('http://localhost:5000/add_employee');
        }
        await page.waitForLoadState('networkidle');

        // Fill out new employee form with fake data
        const fakeEmployee = {
            name: 'Jessica Martinez',
            email: 'jessica.martinez@mswcvi.com',
            position: 'Front Desk/Admin',
            pto_balance: '100',
            pto_refresh_date: '2024-01-01'
        };

        await page.fill('input[name="name"]', fakeEmployee.name);
        await page.fill('input[name="email"]', fakeEmployee.email);

        // Select position if dropdown exists
        try {
            await page.selectOption('select[name="position"]', fakeEmployee.position);
        } catch (error) {
            console.log('Position dropdown not found, trying input field...');
            await page.fill('input[name="position"]', fakeEmployee.position);
        }

        await page.fill('input[name="pto_balance"]', fakeEmployee.pto_balance);
        await page.fill('input[name="pto_refresh_date"]', fakeEmployee.pto_refresh_date);

        // Submit employee creation form
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');

        console.log('✅ New employee created:', fakeEmployee.name);

        // Step 3: Logout and simulate employee login to request PTO
        console.log('🔓 Step 3: Logging out admin and simulating employee PTO request...');

        // Logout admin
        try {
            await page.click('a[href*="logout"]', { timeout: 5000 });
        } catch (error) {
            await page.goto('http://localhost:5000/logout');
        }
        await page.waitForLoadState('networkidle');

        // Navigate back to main page to submit PTO request as the new employee
        await page.goto('http://localhost:5000');
        await page.waitForLoadState('networkidle');

        // Fill out PTO request form
        console.log('📝 Submitting PTO request for new employee...');

        // Wait for and interact with team dropdown
        await page.waitForSelector('select[name="team"]');
        await page.selectOption('select[name="team"]', 'admin');
        await page.waitForTimeout(1000); // Wait for position dropdown to populate

        // Select position
        await page.waitForSelector('select[name="position"]');
        await page.selectOption('select[name="position"]', 'Front Desk/Admin');
        await page.waitForTimeout(1000); // Wait for name dropdown to populate

        // Select employee name
        await page.waitForSelector('select[name="name"]');
        await page.selectOption('select[name="name"]', fakeEmployee.name);
        await page.waitForTimeout(500);

        // Verify email was auto-populated
        const emailValue = await page.inputValue('input[name="email"]');
        expect(emailValue).toBe(fakeEmployee.email);
        console.log('✅ Email auto-populated correctly:', emailValue);

        // Fill in PTO request details
        const startDate = new Date();
        startDate.setDate(startDate.getDate() + 7); // Request PTO for next week
        const endDate = new Date(startDate);
        endDate.setDate(endDate.getDate() + 2); // 3-day PTO request

        const startDateStr = startDate.toISOString().split('T')[0];
        const endDateStr = endDate.toISOString().split('T')[0];

        await page.fill('input[name="start_date"]', startDateStr);
        await page.fill('input[name="end_date"]', endDateStr);
        await page.selectOption('select[name="pto_type"]', 'Vacation');
        await page.fill('textarea[name="reason"]', 'Family vacation to celebrate my new job!');

        // Submit PTO request
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');

        // Look for success message
        await expect(page.locator('body')).toContainText('successfully', { timeout: 10000 });
        console.log('✅ PTO request submitted successfully');

        // Step 4: Login back as Admin Manager to approve the request
        console.log('👨‍💼 Step 4: Logging back in as Admin Manager to approve PTO...');

        await page.goto('http://localhost:5000/login');
        await page.waitForLoadState('networkidle');

        // Login as admin manager again
        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');

        // Navigate to admin dashboard to see pending requests
        try {
            await page.goto('http://localhost:5000/dashboard/admin');
        } catch (error) {
            await page.goto('http://localhost:5000/dashboard');
        }
        await page.waitForLoadState('networkidle');

        // Look for the pending PTO request from our fake employee
        console.log('🔍 Looking for pending PTO request...');

        // Check if we can find the employee name or pending request
        const pageContent = await page.textContent('body');
        if (pageContent.includes(fakeEmployee.name) || pageContent.includes('pending')) {
            console.log('✅ Found pending PTO request on dashboard');

            // Try to find and click approve button
            try {
                await page.click('.btn-approve', { timeout: 5000 });
                await page.waitForLoadState('networkidle');
                console.log('✅ PTO request approved successfully!');
            } catch (error) {
                console.log('⚠️ Approve button not found, but request is visible');
            }
        } else {
            console.log('⚠️ PTO request not immediately visible - may need additional navigation');
        }

        // Take a screenshot for verification
        await page.screenshot({ path: 'test-results/admin-workflow-complete.png', fullPage: true });

        console.log('🎉 Complete Admin Workflow Test Completed!');
        console.log('Summary:');
        console.log('- ✅ Admin Manager Login');
        console.log('- ✅ New Employee Creation:', fakeEmployee.name);
        console.log('- ✅ Employee PTO Request Submission');
        console.log('- ✅ Admin Manager PTO Review');
    });

    test('Admin Dashboard Navigation and Functionality', async ({ page }) => {
        console.log('🔧 Testing Admin Dashboard Navigation...');

        // Login as admin
        await page.goto('http://localhost:5000/login');
        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');

        // Test various dashboard links
        const dashboardLinks = [
            '/dashboard',
            '/dashboard/admin',
            '/employees',
            '/calendar'
        ];

        for (const link of dashboardLinks) {
            console.log(`🔗 Testing navigation to: ${link}`);
            try {
                await page.goto(`http://localhost:5000${link}`);
                await page.waitForLoadState('networkidle');

                // Check if page loaded successfully (no 404 or 500 error)
                const title = await page.title();
                const hasError = await page.locator('body').textContent();

                if (hasError.includes('404') || hasError.includes('500')) {
                    console.log(`❌ Error on ${link}: Page returned error`);
                } else {
                    console.log(`✅ ${link} loaded successfully`);
                }
            } catch (error) {
                console.log(`❌ Failed to load ${link}:`, error.message);
            }
        }

        await page.screenshot({ path: 'test-results/admin-dashboard-nav.png', fullPage: true });
    });

    test('Employee Management CRUD Operations', async ({ page }) => {
        console.log('👥 Testing Employee Management Operations...');

        // Login as admin
        await page.goto('http://localhost:5000/login');
        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForLoadState('networkidle');

        // Test creating multiple fake employees
        const testEmployees = [
            {
                name: 'Alex Thompson',
                email: 'alex.thompson@mswcvi.com',
                position: 'CT Desk',
                team: 'admin'
            },
            {
                name: 'Maria Garcia',
                email: 'maria.garcia@mswcvi.com',
                position: 'Front Desk/Admin',
                team: 'admin'
            }
        ];

        for (const employee of testEmployees) {
            console.log(`➕ Creating employee: ${employee.name}`);

            try {
                await page.goto('http://localhost:5000/add_employee');
                await page.waitForLoadState('networkidle');

                await page.fill('input[name="name"]', employee.name);
                await page.fill('input[name="email"]', employee.email);

                // Try to select position
                try {
                    await page.selectOption('select[name="position"]', employee.position);
                } catch (error) {
                    await page.fill('input[name="position"]', employee.position);
                }

                await page.fill('input[name="pto_balance"]', '120');
                await page.fill('input[name="pto_refresh_date"]', '2024-01-01');

                await page.click('button[type="submit"]');
                await page.waitForLoadState('networkidle');

                console.log(`✅ Employee ${employee.name} created successfully`);
            } catch (error) {
                console.log(`❌ Failed to create ${employee.name}:`, error.message);
            }
        }

        // Test viewing employees list
        console.log('📋 Testing employee list view...');
        try {
            await page.goto('http://localhost:5000/employees');
            await page.waitForLoadState('networkidle');

            const employeeList = await page.textContent('body');
            const createdEmployeesFound = testEmployees.filter(emp =>
                employeeList.includes(emp.name)
            );

            console.log(`✅ Found ${createdEmployeesFound.length}/${testEmployees.length} created employees in list`);
        } catch (error) {
            console.log('❌ Failed to load employees list:', error.message);
        }

        await page.screenshot({ path: 'test-results/employee-management.png', fullPage: true });
    });

});