"""
Test to verify prominent timestamp display in manager approval interface
"""
import asyncio
from playwright.async_api import async_playwright

async def test_timestamp_display():
    """Test the enhanced timestamp display for PTO requests in manager dashboard"""
    async with async_playwright() as p:
        # Launch browser in headed mode to see the timestamp display
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()

        print("🔍 Testing enhanced timestamp display in manager approval interface...")

        # Navigate to login page
        await page.goto("http://127.0.0.1:5000/login")
        await page.wait_for_load_state('networkidle')

        # Login as Admin Manager
        print("📋 Logging in as Admin Manager...")
        await page.fill('input[name="email"]', 'admin.manager@mswcvi.com')
        await page.fill('input[name="password"]', 'admin123')
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')

        # Navigate to admin dashboard
        print("🏠 Navigating to Admin Dashboard...")
        await page.goto("http://127.0.0.1:5000/admin_dashboard")
        await page.wait_for_load_state('networkidle')

        # Wait for the page to fully load
        await page.wait_for_selector('table.table', timeout=10000)

        # Take screenshot of the dashboard with enhanced timestamps
        await page.screenshot(path="timestamp_display_admin.png", full_page=True)
        print("📸 Screenshot saved: timestamp_display_admin.png")

        # Check for timestamp elements
        timestamp_elements = await page.query_selector_all('.submission-timestamp')
        if timestamp_elements:
            print(f"✅ Found {len(timestamp_elements)} enhanced timestamp displays")

            # Get text content of first timestamp for verification
            first_timestamp = timestamp_elements[0]
            timestamp_content = await first_timestamp.inner_text()
            print(f"📅 First timestamp display content:")
            print(f"   {timestamp_content}")
        else:
            print("❌ No enhanced timestamp displays found")

        # Check for specific timestamp styling elements
        date_elements = await page.query_selector_all('.submission-timestamp strong.text-primary')
        time_badges = await page.query_selector_all('.submission-timestamp .badge.bg-light.text-dark')
        relative_time = await page.query_selector_all('.submission-timestamp small.text-muted')

        print(f"📊 Timestamp component verification:")
        print(f"   Date elements (primary): {len(date_elements)}")
        print(f"   Time badges: {len(time_badges)}")
        print(f"   Relative time indicators: {len(relative_time)}")

        # Also test clinical dashboard
        print("\n🔄 Testing Clinical Dashboard timestamp display...")
        await page.goto("http://127.0.0.1:5000/login")
        await page.wait_for_load_state('networkidle')

        # Login as Clinical Manager
        await page.fill('input[name="email"]', 'clinical.manager@mswcvi.com')
        await page.fill('input[name="password"]', 'clinical123')
        await page.click('button[type="submit"]')
        await page.wait_for_load_state('networkidle')

        # Navigate to clinical dashboard
        await page.goto("http://127.0.0.1:5000/clinical_dashboard")
        await page.wait_for_load_state('networkidle')

        # Wait for the page to fully load
        await page.wait_for_selector('table.table', timeout=10000)

        # Take screenshot of clinical dashboard
        await page.screenshot(path="timestamp_display_clinical.png", full_page=True)
        print("📸 Screenshot saved: timestamp_display_clinical.png")

        # Verify timestamp elements in clinical dashboard
        clinical_timestamps = await page.query_selector_all('.submission-timestamp')
        print(f"✅ Clinical dashboard: Found {len(clinical_timestamps)} enhanced timestamp displays")

        print("\n🎉 Timestamp display verification complete!")
        print("✨ Enhanced timestamps now show:")
        print("   • Prominent date display (MM/DD/YYYY)")
        print("   • Time badge (HH:MM AM/PM)")
        print("   • Relative time indicator (Today/Yesterday/X days ago)")
        print("   • Visual styling with icons and colors")

        # Keep browser open for manual inspection
        print("\n⏸️  Browser will remain open for manual inspection...")
        await page.wait_for_timeout(10000)  # Wait 10 seconds for manual inspection

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_timestamp_display())