import uiautomator2 as u2
import time

num_errors = 0

# Connect to the Android device (ensure adb is configured)
device = u2.connect()

# Get device information
print(device.info)

# Launch an Settings application
device.app_start("com.android.settings")

# Find the network settings element by text and click it.
# The wait gives the device time to update the display.
if device(text="Network & internet").wait(timeout=5):
    device(text="Network & internet").click()

    # Find the wifi connection element by text and click it.
    # Again, the wait gives the device time to updat the display
    if device(text="AndroidWifi").wait(timeout=5):
        device(text="AndroidWifi").click()
    else:
        print("ERROR: unable to open Wifi settings")
        num_errors =+ 1
else:
    print("ERROR: unable to open Network Settings")
    num_errors =+ 1
    
# Get the current package name
if num_errors == 0:
    app_name = device.app_current()
    if not app_name["package"] == "com.android.settings":
        print("ERROR: invalid application open: %s", app_name["package"])
        num_errors =+ 1
    else:
        # (from settings example) Go back
        device.press("back")
        device.press("back")

# Close Settings app
device.app_stop("com.android.settings")

########

# Launch YouTube
device.app_start("com.google.android.youtube")

# If not waiting for specific text to click on,
# need to wait before getting the current app name.
time.sleep(5)

# Get the current package name
app_name = device.app_current()
if not app_name["package"] == "com.google.android.youtube":
    print("ERROR: invalid application open: %s", app_name["package"])
    num_errors =+ 1

# Stop YouTube app
device.app_stop("com.google.android.youtube")

########

# Launch Google Mail
device.app_start("com.google.android.gm")

# If not waiting for specific text to click on,
# need to wait before getting the current app name.
time.sleep(5)

# Get the current package name
app_name = device.app_current()
if not app_name["package"] == "com.google.android.gm":
    print("ERROR: invalid application open: %s", app_name["package"])
    num_errors =+ 1

# Stop GMail app
device.app_stop("com.google.android.gm")

########

# Launch Google Photos
device.app_start("com.google.android.apps.photos")

# If not waiting for specific text to click on,
# need to wait before getting the current app name.
time.sleep(5)

# Get the current package name
app_name = device.app_current()
if not app_name["package"] == "com.google.android.apps.photos":
    print("ERROR: invalid application open: %s", app_name["package"])
    num_errors =+ 1

# Stop Photos app
device.app_stop("com.google.android.apps.photos")

########

# Launch Chrome
device.app_start("com.android.chrome")

# If not waiting for specific text to click on,
# need to wait before getting the current app name.
time.sleep(5)

# Get the current package name
app_name = device.app_current()
if not app_name["package"] == "com.android.chrome":
    print("ERROR: invalid application open: %s", app_name["package"])
    num_errors =+ 1

# Stop Chrome app
device.app_stop("com.android.chrome")

########

# print pass/fail report
if num_errors == 0:
    print("SUCCESS: All tests passed")
else:
    print("FAILURE: %d of 5 tests failed"%num_errors)
