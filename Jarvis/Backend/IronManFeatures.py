import os
import io
import time
import base64
import requests
import psutil
from dotenv import dotenv_values
from PIL import Image

# Load environment configuration
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey", "")
Assistantname = env_vars.get("Assistantname", "Jarvis")
Username = env_vars.get("Username", "Sir")


# ---------------------------------------------------------------------------
# 1. Hardware & Suit Diagnostics ("Armor & Power Core Status")
# ---------------------------------------------------------------------------
def GetSystemDiagnostics():
    """Returns real-time hardware telemetry: CPU, RAM, Disk, and Battery."""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("C:")
        battery = psutil.sensors_battery()

        ram_used_gb = round((ram.total - ram.available) / (1024 ** 3), 1)
        ram_total_gb = round(ram.total / (1024 ** 3), 1)

        if battery:
            plugged = "connected to AC power" if battery.power_plugged else "on battery reserves"
            power_status = f"Power core at {battery.percent}%, {plugged}."
        else:
            power_status = "Power core operating on dedicated desktop AC supply."

        report = (
            f"Armor and system telemetry: CPU load is at {cpu} percent. "
            f"RAM utilization is {ram.percent} percent, with {ram_used_gb} of {ram_total_gb} gigabytes committed. "
            f"Primary storage volume C is {disk.percent} percent utilized. "
            f"{power_status} All subsystems nominal."
        )
        return report
    except Exception as e:
        return f"System telemetry check failed: {str(e)}"


# ---------------------------------------------------------------------------
# 2. Atmospheric & Flight Radar ("Weather & Flight Conditions")
# ---------------------------------------------------------------------------
def GetWeatherReport(city_name=None):
    """Fetches real-time weather and flight atmospheric conditions via Open-Meteo."""
    try:
        lat, lon, city = 18.52, 73.85, "Local Area"
        # Auto-detect location via IP if not explicitly supplied
        try:
            loc = requests.get("http://ip-api.com/json", timeout=4).json()
            lat = loc.get("lat", lat)
            lon = loc.get("lon", lon)
            city = loc.get("city", city)
        except Exception:
            pass

        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current="
            f"temperature_2m,relative_humidity_2m,apparent_temperature,"
            f"precipitation,wind_speed_10m,wind_direction_10m,surface_pressure&timezone=auto"
        )
        res = requests.get(url, timeout=6).json()
        current = res.get("current", {})

        temp = current.get("temperature_2m", 25)
        feels = current.get("apparent_temperature", temp)
        humidity = current.get("relative_humidity_2m", 50)
        wind = current.get("wind_speed_10m", 5)
        pressure = current.get("surface_pressure", 1013)

        report = (
            f"Atmospheric and flight conditions for {city}: "
            f"Current temperature is {temp} degrees Celsius, feeling like {feels} degrees. "
            f"Humidity is at {humidity} percent with barometric pressure at {round(pressure)} hectopascals. "
            f"Wind velocity is {wind} kilometers per hour. Flight conditions are clear and nominal."
        )
        return report
    except Exception as e:
        return f"Unable to fetch atmospheric radar telemetry: {str(e)}"


# ---------------------------------------------------------------------------
# 3. Live Satellite & Aircraft Overhead Tracking
# ---------------------------------------------------------------------------
def GetOverheadTracking():
    """Scans local airspace for active aircraft and tracks the International Space Station."""
    try:
        report_parts = []

        # 1. ISS Orbital Position
        try:
            iss = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=5).json()
            alt = round(iss.get("altitude", 420), 1)
            vel = round(iss.get("velocity", 27600))
            lat = round(iss.get("latitude", 0), 2)
            lon = round(iss.get("longitude", 0), 2)
            report_parts.append(
                f"The International Space Station is orbiting at an altitude of {alt} kilometers, "
                f"traveling at {vel} kilometers per hour above coordinates {lat} latitude, {lon} longitude."
            )
        except Exception:
            report_parts.append("Orbital satellite tracking is currently acquiring signal.")

        # 2. Local Airspace Radar via OpenSky
        try:
            loc = requests.get("http://ip-api.com/json", timeout=4).json()
            lat, lon = loc.get("lat", 18.52), loc.get("lon", 73.85)
            lamin, lamax = lat - 1.2, lat + 1.2
            lomin, lomax = lon - 1.2, lon + 1.2

            url = f"https://opensky-network.org/api/states/all?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
            air_data = requests.get(url, timeout=7).json()
            states = air_data.get("states") or []

            count = len(states)
            if count > 0:
                flights = []
                for s in states[:3]:
                    cs = s[1].strip() if s[1] else "unidentified"
                    alt_m = round(s[7]) if s[7] else 0
                    flights.append(f"Flight {cs} at {alt_m} meters")
                report_parts.append(
                    f"Airspace radar detected {count} aircraft within our local sector. "
                    + ", ".join(flights) + "."
                )
            else:
                report_parts.append("Airspace radar reports zero aircraft currently within our immediate sector.")
        except Exception:
            report_parts.append("Local airspace radar is scanning.")

        return " ".join(report_parts)
    except Exception as e:
        return f"Airspace radar tracking error: {str(e)}"


# ---------------------------------------------------------------------------
# 4. Global Intelligence & Tactical Fact-Checking (Wikipedia REST API)
# ---------------------------------------------------------------------------
def GetTacticalDossier(topic: str):
    """Retrieves an executive tactical briefing on a specific entity, technology, or topic."""
    try:
        clean_topic = topic.strip().replace(" ", "_")
        headers = {"User-Agent": "JarvisTacticalAssistant/2.0 (AI assistant)"}
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_topic}"
        res = requests.get(url, headers=headers, timeout=5)

        if res.status_code == 200:
            data = res.json()
            title = data.get("title", topic)
            extract = data.get("extract", "")
            sentences = extract.split(". ")
            briefing = ". ".join(sentences[:2])
            if not briefing.endswith("."):
                briefing += "."
            return f"Tactical dossier on {title}: {briefing}"
        else:
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={topic}&limit=1&namespace=0&format=json"
            s_res = requests.get(search_url, headers=headers, timeout=5).json()
            if s_res and len(s_res) > 2 and s_res[2] and s_res[2][0]:
                return f"Intelligence briefing on {topic}: {s_res[2][0]}"
            return f"No tactical dossier found for {topic} in global databases."
    except Exception as e:
        return f"Unable to retrieve tactical intelligence: {str(e)}"


# ---------------------------------------------------------------------------
# 5. Instant AI Image & Schematic Generation (Pollinations.ai FLUX)
# ---------------------------------------------------------------------------
def GenerateSchematic(prompt: str):
    """Generates an AI image or technical schematic using Pollinations.ai FLUX engine (100% free)."""
    try:
        clean_prompt = prompt.replace("generate image", "").replace("generate schematic", "").strip()
        if not clean_prompt:
            clean_prompt = "Iron Man futuristic holographic schematic HUD blueprint"

        print(f"[Jarvis AI Generator] Synthesizing schematic for: '{clean_prompt}'...")
        encoded_prompt = requests.utils.quote(clean_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true"

        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            os.makedirs("Data", exist_ok=True)
            safe_name = "".join(c for c in clean_prompt[:25] if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
            if not safe_name:
                safe_name = "schematic"
            file_path = os.path.join("Data", f"{safe_name}_{int(time.time())}.jpg")

            with open(file_path, "wb") as f:
                f.write(res.content)

            try:
                os.startfile(file_path)
            except Exception:
                pass

            return f"Schematic for {clean_prompt} has been generated and projected to your display, Sir."
        else:
            return "Image synthesis failed due to network communication error."
    except Exception as e:
        return f"Image generation error: {str(e)}"


# ---------------------------------------------------------------------------
# 6. Computer Vision & "Jarvis Eyes" (Screen / Camera Perception)
# ---------------------------------------------------------------------------
def CaptureScreenBase64():
    """Captures the current desktop screen and returns it as a JPEG base64 string."""
    try:
        import mss
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img.thumbnail((1280, 720))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.thumbnail((1280, 720))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        except Exception:
            return None


def CaptureCameraBase64():
    """Captures a single frame from the primary webcam and returns it as a base64 string."""
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if ret and frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            img.thumbnail((1024, 768))
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        else:
            return None
    except Exception as e:
        print(f"Webcam capture error: {e}")
        return None


def JarvisVision(source="screen", query="Describe what you see."):
    """Uses Groq multimodal vision (qwen/qwen3.8-27b) to analyze screen or camera input."""
    try:
        from groq import Groq

        env = dotenv_values(".env")
        key = env.get("GroqAPIKey", "")
        if not key:
            return "Vision analysis requires GroqAPIKey in .env."

        client = Groq(api_key=key)

        if "camera" in source.lower() or "webcam" in source.lower():
            b64_image = CaptureCameraBase64()
            label = "camera feed"
            if not b64_image:
                return "Unable to access optical sensor camera. Please ensure webcam is connected and unblocked."
        else:
            b64_image = CaptureScreenBase64()
            label = "desktop display"
            if not b64_image:
                return "Unable to capture visual display. The display may be locked or protected by system security."

        prompt_text = (
            f"You are Jarvis, an advanced AI assistant. Analyze this {label} image and answer concisely in 2-3 sentences. "
            f"User request: {query}"
        )

        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]
            }],
            max_tokens=250,
            temperature=0.3
        )

        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Optical vision analysis error: {str(e)}"
