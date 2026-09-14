import os
import sys

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    sys.exit("❌ OPENAI_API_KEY was not found in .env.")

client = OpenAI()

try:
    response = client.responses.create(
        model=os.getenv("OPENAI_SMOKE_TEST_MODEL", "gpt-5-mini"),
        input="Reply with exactly: SMOKE_TEST_OK",
        max_output_tokens=20,
    )

    print(f"✅ API connected | response_id={response.id}")
    print(f"Model output: {response.output_text.strip()}")

except APIConnectionError:
    sys.exit("❌ The network connection to OpenAI could not be established.")
except APIStatusError as exc:
    sys.exit(f"❌ OpenAI API error: HTTP {exc.status_code} — {exc.message}")
except Exception as exc:
    sys.exit(f"❌ Unexpected error: {exc}")
