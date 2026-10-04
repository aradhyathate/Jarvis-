import os
import sys
from time import sleep

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Backend.IronManFeatures import GenerateSchematic

def GenerateImages(prompt: str):
    """Generates an image via Pollinations.ai FLUX (100% free, no key required)."""
    return GenerateSchematic(prompt)

if __name__ == "__main__":
    while True:
        try:
            flag_file = r"Frontend\Files\ImageGeneration.data"
            if not os.path.exists(flag_file):
                sleep(1)
                continue

            with open(flag_file, "r") as f:
                data = str(f.read())

            if "," in data:
                prompt, status = data.split(",", 1)
                if status.strip().lower() == "true":
                    print(f"Generating Images for: {prompt}...")
                    GenerateImages(prompt=prompt)
                    with open(flag_file, "w") as f:
                        f.write("False, False")
                    break
            sleep(1)
        except Exception as e:
            print(f"Image loop error: {e}")
            sleep(1)