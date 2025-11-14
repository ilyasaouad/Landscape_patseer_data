import sys
from pathlib import Path

# ---------------------------------------------------------
# Make sure project root is importable
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# ---------------------------------------------------------
# Now imports work cleanly
# ---------------------------------------------------------
from utils.file_paths import processed

import asyncio
import pandas as pd
import httpx
import os
from dotenv import load_dotenv
from io import StringIO


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
print("LLM BASE_DIR:", BASE_DIR)



# ---------------------------------------------------------

# Load API keys
# ---------------------------------------------------------
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "tngtech/deepseek-r1t2-chimera:free")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))

if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY missing from .env!")


# =========================================================
# LLM Service Class
# =========================================================
class LLMService:
    """Service for calling OpenRouter LLM to update missing assignee country fields."""

    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.client = httpx.AsyncClient(timeout=LLM_TIMEOUT)
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def update_assignee_countries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Send CSV to the LLM and receive corrected CSV."""

        # Convert DataFrame → CSV text
        csv_input = df.to_csv(index=False)

        system_prompt = """
You are assisting with patent data cleaning.

You will receive a CSV with columns:
Country,Assignee,Count

Rules:
1. Only replace Country == "None" when 100% certain of correct ISO country code.
2. Never modify valid country codes.
3. Never modify Assignee or Count.
4. Output ONLY clean CSV. No markdown, no explanations.
"""

        response = await self.client.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": csv_input},
                ],
                "temperature": 0.0,
            },
        )

        try:
            result = response.json()
        except Exception as e:
            print("❌ ERROR: Cannot parse LLM JSON response")
            print("Raw response text:", response.text)
            raise

        if "error" in result:
            print("❌ LLM error:", result["error"])
            raise RuntimeError(result["error"])

        if "choices" not in result:
            raise RuntimeError("Invalid LLM response (missing choices)")

        csv_output = result["choices"][0]["message"]["content"]

        # Convert CSV text → DataFrame
        return pd.read_csv(StringIO(csv_output))


# =========================================================
# Main Processing Logic
# =========================================================
async def main():
    # ------------------------------------------------------------------
    # Load from /data/processed
    # ------------------------------------------------------------------
    input_file = processed("Assignee_Country_Count.csv")
    output_file = processed("Assignee_Country_Count_Updated.csv")

    print(f"📄 Input file:  {input_file}")
    print(f"💾 Output will be saved to: {output_file}")



    print("DEBUG INPUT_FILE =", input_file)
    print("DEBUG OUTPUT_FILE =", output_file)
    print("DEBUG OUTPUT DIR EXISTS =", output_file.parent.exists())
    print("DEBUG OUTPUT FILE EXISTS BEFORE =", output_file.exists())


    df = pd.read_csv(input_file)

    # Take top 20 by count
    df_top20 = df.sort_values("Count", ascending=False).head(20).copy()
    print("\n🔎 Top 20 rows sent to LLM:")
    print(df_top20)

    print("DEBUG: LOADED DF SHAPE =", df.shape)
    print("DEBUG: LOADED DF COLUMNS =", df.columns)
    print(df.head())

    service = LLMService()

    try:
        df_corrected = await service.update_assignee_countries(df_top20)
    except Exception as e:
        print("\n❌ ERROR in LLM call:")
        print(str(e))
        import traceback
        traceback.print_exc()
        print("\n❌ LLM stopped — therefore NO output file saved.")
        return


    # Merge results back
    df_final = df.copy()

    for _, row in df_corrected.iterrows():
        assignee = row["Assignee"]
        new_country = row["Country"]
        df_final.loc[df_final["Assignee"] == assignee, "Country"] = new_country

    # Save
    df_final.to_csv(output_file, index=False)
    print(f"\n✔️ Updated file successfully saved:\n   {output_file}")


# =========================================================
# Allow running standalone
# =========================================================
if __name__ == "__main__":
    asyncio.run(main())
