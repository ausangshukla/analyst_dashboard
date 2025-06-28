import argparse
import asyncio
import os
from dashboard_generator import DashboardGenerator

async def main():
    parser = argparse.ArgumentParser(description="Generate a financial dashboard from a directory of documents.")
    parser.add_argument("directory", type=str, help="Path to the directory containing downloaded documents.")
    args = parser.parse_args()

    download_directory = args.directory

    if not os.path.isdir(download_directory):
        print(f"Error: Directory '{download_directory}' not found.")
        return

    print(f"Initializing DashboardGenerator for directory: {download_directory}")
    generator = DashboardGenerator(download_directory)
    await generator.generate_dashboard()
    print("Dashboard generation process initiated.")

if __name__ == "__main__":
    asyncio.run(main())