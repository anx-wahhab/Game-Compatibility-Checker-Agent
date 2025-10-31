import platform
import psutil
import cpuinfo
import subprocess
import sys
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()


# === SIMPLE DYNAMIC SPECS ===
def get_specs():
    specs = {}

    # OS
    specs["OS"] = f"{platform.system()} {platform.release()}"

    # CPU
    try:
        specs["CPU"] = cpuinfo.get_cpu_info()['brand_raw']
    except:
        specs["CPU"] = platform.processor() or "Unknown CPU"

    # RAM
    specs["RAM"] = f"{psutil.virtual_memory().total // (1024 ** 3)} GB"

    # Storage
    total = psutil.disk_usage('/').total // (1024 ** 3)
    specs["Storage"] = f"{total} GB"

    # GPU (Windows: wmic | Linux: lspci | macOS: system_profiler)
    gpu = "Unknown GPU"
    system = platform.system()

    if system == "Windows":
        try:
            result = subprocess.check_output(
                'wmic path win32_videocontroller get name', shell=True, text=True
            )
            for line in result.splitlines():
                if line.strip() and "Name" not in line:
                    gpu = line.strip()
                    break
        except:
            pass
    elif system == "Linux":
        try:
            result = subprocess.check_output('lspci', text=True)
            for line in result.splitlines():
                if 'VGA' in line or '3D' in line:
                    gpu = line.split(':')[1].strip()
                    break
        except:
            pass

    specs["GPU"] = gpu
    return specs


# Get specs
specs = get_specs()
specs_str = "\n".join(f"{k}: {v}" for k, v in specs.items())

# === PROMPT ===
template = """
You are a gaming analyst. Can this game run on the laptop?

Laptop:
{specs}

Game: {game_name}

Answer: Yes/No + short reason. Include FPS estimate if possible.
"""

prompt = PromptTemplate.from_template(template)

# === LLM ===
llm = ChatOpenAI(
    base_url='https://openrouter.ai/api/v1',
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="mistralai/mistral-7b-instruct",
    temperature=0
)
chain = prompt | llm | StrOutputParser()

# === CLI ===
if len(sys.argv) != 2:
    print("Usage: python game_check.py \"Game Name\"")
    sys.exit(1)

game_name = sys.argv[1]

print("\n" + "=" * 50)
print("   GAME COMPATIBILITY CHECK")
print("=" * 50)
print(f"System:\n{specs_str}\n")
print(f"Game: {game_name}")
print("Analyzing...\n")

response = chain.invoke({"specs": specs_str, "game_name": game_name})

print("=" * 50)
print(f"RESULT: {game_name.upper()}")
print("=" * 50)
print(response)