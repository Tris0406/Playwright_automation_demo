from playwright.sync_api import sync_playwright
import os

# ------------------------------------------------------------------
# Configuration & constants
# ------------------------------------------------------------------

os.makedirs("screenshots", exist_ok=True)

URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
USERNAME = "Admin"
PASSWORD = "admin123"

FIRST_NAME = "Nate"
LAST_NAME = "Hawkins"
EMPLOYEE_NAME = f"{FIRST_NAME} {LAST_NAME}"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page()

        # ==========================================================
        # LOGIN – wait for FULL dashboard load
        # ==========================================================
        page.goto(URL)

        page.get_by_placeholder("Username").fill(USERNAME)
        page.get_by_placeholder("Password").fill(PASSWORD)
        page.get_by_role("button", name="Login").click()

        dashboard_heading = page.get_by_role("heading", name="Dashboard")
        dashboard_heading.wait_for(state="visible", timeout=20000)

        page.locator(".oxd-userdropdown-name").wait_for(
            state="attached", timeout=20000
        )

        dashboard_heading.scroll_into_view_if_needed()
        page.wait_for_timeout(1500)

        page.screenshot(path="screenshots/login_success.png")
        print("Dashboard fully loaded – login screenshot taken")

        # ==========================================================
        # CREATE EMPLOYEE – wait for FULL Personal Details load
        # ==========================================================
        page.get_by_role("link", name="PIM").click()
        page.get_by_role("button", name="Add").click()

        page.get_by_placeholder("First Name").fill(FIRST_NAME)
        page.get_by_placeholder("Last Name").fill(LAST_NAME)
        page.get_by_role("button", name="Save").click()

        page.wait_for_url("**/pim/viewPersonalDetails/**", timeout=20000)

        personal_details_heading = page.get_by_role(
            "heading", name="Personal Details"
        )
        personal_details_heading.wait_for(
            state="visible", timeout=20000
        )

        page.locator("input[name='lastName']").wait_for(
            state="attached", timeout=20000
        )

        personal_details_heading.scroll_into_view_if_needed()
        page.wait_for_timeout(2000)

        page.screenshot(path="screenshots/employee_created.png")
        print("Add Employee fully loaded – screenshot taken")

        # ==========================================================
        # RESET NAVIGATION (CRITICAL FOR LEAVE MENU)
        # ==========================================================
        page.get_by_role("link", name="Dashboard").wait_for(
            state="visible", timeout=20000
        )
        page.get_by_role("link", name="Dashboard").click()

        dashboard_heading.wait_for(state="visible", timeout=20000)
        page.locator(".oxd-userdropdown-name").wait_for(
            state="attached", timeout=20000
        )
        page.wait_for_timeout(1000)

        # ==========================================================
        # ASSIGN LEAVE – fill, verify, attempt submit, screenshot
        # ==========================================================
        page.get_by_role("link", name="Leave").wait_for(
            state="visible", timeout=20000
        )
        page.get_by_role("link", name="Leave").click()

        page.get_by_role("button", name="Assign Leave").click()

        assign_leave_heading = page.get_by_role(
            "heading", name="Assign Leave"
        )
        assign_leave_heading.wait_for(
            state="visible", timeout=20000
        )

        # Employee autocomplete
        employee_input = page.get_by_placeholder("Type for hints...")
        employee_input.fill(EMPLOYEE_NAME)
        page.wait_for_timeout(1500)
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")

        # Leave type
        page.locator("div.oxd-select-text").first.click()
        page.wait_for_timeout(1000)

        # Leave dates (React-safe)
        page.evaluate("""
            const inputs = document.querySelectorAll(
                "input[placeholder='yyyy-mm-dd']"
            );
            if (inputs.length >= 2) {
                inputs[0].value = '2025-05-01';
                inputs[1].value = '2025-05-01';
                inputs.forEach(input => {
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                });
            }
        """)

        page.locator("input[placeholder='yyyy-mm-dd']").nth(0).wait_for(
            state="attached", timeout=10000
        )
        page.locator("input[placeholder='yyyy-mm-dd']").nth(1).wait_for(
            state="attached", timeout=10000
        )

        assign_leave_heading.scroll_into_view_if_needed()
        page.wait_for_timeout(1500)

        page.screenshot(path="screenshots/leave_filled.png")
        print("Leave form filled – screenshot taken")

        # ==========================================================
        # ATTEMPT ASSIGN (DEMO‑DEPENDENT)
        # ==========================================================
        page.get_by_role("button", name="Assign").click()
        page.wait_for_timeout(3000)

        page.screenshot(path="screenshots/leave_assign_attempt.png")
        print("Leave assignment attempted – screenshot taken")

        browser.close()


if __name__ == "__main__":
    run()