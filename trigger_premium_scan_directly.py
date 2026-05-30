import os
import sys
import asyncio
from dotenv import load_dotenv

# Add absolute path of main to import exchanges
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import scan_premium_opportunities, binance, bithumb

async def main():
    load_dotenv()
    print("🚀 Triggering scan_premium_opportunities() directly...")
    await scan_premium_opportunities()
    print("✅ Completed scan!")

if __name__ == "__main__":
    asyncio.run(main())
