import asyncio
import pandas as pd
import httpx
import os
from dotenv import load_dotenv
from io import StringIO

# Load .env configuration
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "tngtech/deepseek-r1t2-chimera:free")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))

if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY missing in .env")


class LLMService:
    """Service for calling OpenRouter LLM to update missing country fields."""

    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.model = OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.client = httpx.AsyncClient(timeout=LLM_TIMEOUT)

    async def update_assignee_countries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Send CSV to LLM and receive corrected CSV."""

        # Convert dataframe → CSV string
        csv_input = df.to_csv(index=False)

        # Improved domain-aware system prompt
        system_prompt = """
You are assisting with patent data cleaning.

You will receive a CSV file with the columns:
Country,Assignee,Count

Each row represents an assignee from a patent dataset.
An assignee is usually the applicant of a patent and may be:
- a company or corporation
- a university or academic institution
- a government research organization
- a nonprofit or foundation
- a research lab or consortium
- an individual (rare)

The "Country" column contains either:
- a valid ISO 2-letter country code (US, FI, JP, DE, etc.)
- or "None"

Your rules:

1. If Country == "None":
   Replace it ONLY if you are 100% certain of the correct ISO country code
   based on globally known, widely-established facts about the assignee.

2. If you are NOT completely certain:
   Leave the country as "None".

3. Do NOT:
   - modify Country values that are already valid
   - guess or infer without high certainty
   - alter Assignee or Count fields
   - reorder rows or add extra text

4. Output:
   Only the raw CSV with the same columns in the same order.
   No explanations. No markdown. Only CSV.
"""

        # Send request to OpenRouter
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

        result = response.json()

        # Error handling
        if "error" in result:
            print("\n❌ OpenRouter API Error:")
            print(result["error"])
            raise ValueError(f"OpenRouter API error: {result['error']}")

        if "choices" not in result or len(result["choices"]) == 0:
            print("\n❌ Unexpected OpenRouter response:")
            print(result)
            raise ValueError("OpenRouter response missing 'choices' field.")

        # Extract CSV
        csv_output = result["choices"][0]["message"]["content"]

        # Convert CSV string → DataFrame
        df_updated = pd.read_csv(StringIO(csv_output))

        return df_updated


async def main():
    input_file = r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Country_Count.csv"
    output_file = r"C:\Users\iao\Desktop\Landscape_patseer_data\inn_data\Assignee_Country_Count_updated.csv"

    print(f"📄 Loading: {input_file}")
    df = pd.read_csv(input_file)

    # -------------------------
    # SELECT ONLY TOP 20 ROWS
    # -------------------------
    df_top20 = df.sort_values("Count", ascending=False).head(20).copy()

    print("\n🔎 Sending top 20 rows to LLM:")
    print(df_top20)

    service = LLMService()

    print("\n🤖 Sending to OpenRouter LLM...")
    df_top20_corrected = await service.update_assignee_countries(df_top20)

    # -------------------------
    # MERGE CORRECTED TOP 20 BACK INTO FULL DF
    # -------------------------
    df_updated = df.copy()

    for idx, row in df_top20_corrected.iterrows():
        assignee = row["Assignee"]
        new_country = row["Country"]

        df_updated.loc[df_updated["Assignee"] == assignee, "Country"] = new_country

    # Save final file
    df_updated.to_csv(output_file, index=False)
    print(f"\n✔️ Updated file saved: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
