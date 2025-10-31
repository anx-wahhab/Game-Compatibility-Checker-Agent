from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# === YOUR LAPTOP SPECS (UPDATE THESE!) ===
laptop_specs = {
    "CPU": "Intel Core i5-10300H",
    "GPU": "NVIDIA GeForce GTX 1650 4GB",
    "RAM": "16 GB DDR4",
    "Storage": "512 GB SSD",
    "OS": "Windows 11"
}

# Convert specs to formatted string
specs_str = "\n".join([f"{k}: {v}" for k, v in laptop_specs.items()])

# === PROMPT TEMPLATE ===
template = """
You are a gaming system analyst. Determine if the given game can run on this laptop.

Laptop Specs:
{specs}

Game: {game_name}

Be accurate and technical.
"""

prompt = PromptTemplate.from_template(template)

# === LLM SETUP ===
llm = ChatOpenAI(
    base_url='https://openrouter.ai/api/v1',
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="mistralai/mistral-7b-instruct",
    temperature=0
)
chain = prompt | llm | StrOutputParser()

# === COMMAND-LINE FUNCTION ===
def check_game_from_cmd():
    if len(sys.argv) != 2:
        print("Usage: python script.py \"Game Name Here\"")
        print("Example: python script.py \"Cyberpunk 2077\"")
        sys.exit(1)

    game_name = sys.argv[1].strip()

    print("\n" + "="*60)
    print("   LAPTOP GAME COMPATIBILITY CHECKER")
    print("="*60)
    print(f"Your Laptop Specs:\n{specs_str}\n")
    print(f"Checking compatibility for: {game_name}")
    print("\nAnalyzing...")

    try:
        response = chain.invoke({
            "specs": specs_str,
            "game_name": game_name,
        })
        print("\n" + "="*60)
        print(f" RESULT FOR: {game_name.upper()}")
        print("="*60)
        print(response)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


# === RUN FROM CMD ===
if __name__ == "__main__":
    check_game_from_cmd()