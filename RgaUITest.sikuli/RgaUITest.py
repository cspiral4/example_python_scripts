#!python
import time
import sikuli

def test_radeon_gpu_analyzer():
    # Open the Radeon GPU Analyzer (assume it's already installed and located on the system)
    try:
        # Launch Radeon GPU Analyzer (RGA) - adjust the command as per your system
        # For Windows, you might use something like:
        # App.open("C:/Program Files/Radeon GPU Analyzer/RadeonGPUAnalyzer.exe")
        # For Linux, adjust accordingly.
        sikuli.App.open("C:\\Program Files\\GPUOpen\\Radeon GPU Analyzer\\RadeonGPUAnalyzer.exe")
        # Wait for API selection dialog.
        time.sleep(5)
        # Use default API and start RGA
        if sikuli.exists("G:/My Drive/JobSearch/ExampleScripts/RgaUITest.sikuli/StartRGA.png", 10):
            # waits for 10 seconds for the analyze button to appear
            print("Radeon GPU Analyzer is up and running.")
            start_button = sikuli.find("G:\\My Drive\\JobSearch\\ExampleScripts\\RgaUITest.sikuli\\StartRGAButton.png")
            sikuli.click(start_button)
        else:
            print("Radeon GPU Analyzer UI not detected. Exiting test.")
            return

        # Wait for the application to open
        time.sleep(5)

        # Verify if the main window is open (checking for the presence of a known UI element like a button)
        if sikuli.exists("RGAWelcome.png", 10):  # waits for 10 seconds for the analyze button to appear
            print("Radeon GPU Analyzer is up and running.")
        else:
            print("Radeon GPU Analyzer UI not detected. Exiting test.")
            return

        # Example 1: Click on the "Analyze" button
        change_mode_button = sikuli.find("change_mode_button.png")
        if change_mode_button is not None:
            sikuli.click(change_mode_button)
            print("Clicked on the 'Mode' button.")
            time.sleep(2)
        else:
            print("Unable to locate the Change Mode interface. Exiting test.")
            return

        # Example 2: Interact with a drop-down list (assumed to exist on the UI)
        dropdown = sikuli.find("ModeOpenCL.png")
        if dropdown is not None:
            sikuli.click(dropdown)
            print("Clicked on the menu option OpenCL.")
            time.sleep(2)
        else:
            print("Unable to locate the OpenCL mode option")
            return
        
        confirm_yes = sikuli.find("YesButton.png")
        if confirm_yes is not None:
            sikuli.click(confirm_yes)
            print("Clicked on the Yes button to confirm")
            time.sleep(5)
        else:
            print("Unable to locate the Yes button on the confirmation dialog.  Exiting test.")
            return

        close_rga()

    except Exception as e:
        print("An error occurred")

def close_rga():
        close_button = sikuli.find("1744137880932.png")
        if close_button is not None:
            sikuli.click(close_button)
            print("RGA UI closed")
        else:
            print("Unable to locate close button")
    
if __name__ == "__main__":
    test_radeon_gpu_analyzer()