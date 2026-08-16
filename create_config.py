import json
import os


def main():
    print("This utility creates a local config.json with your Telegram bot token and chat id.")
    print("The file will be created in the project root and is ignored by git (see .gitignore).")

    token = input("Enter TELEGRAM_TOKEN (bot token): ").strip()
    if not token:
        print("No token entered — aborting.")
        return

    chat_id = input("Enter TELEGRAM_CHAT_ID (numeric): ").strip()
    if not chat_id:
        print("No chat id entered — aborting.")
        return

    cfg = {
        "TELEGRAM_TOKEN": token,
        "TELEGRAM_CHAT_ID": chat_id,
    }

    path = "config.json"
    if os.path.exists(path):
        confirm = input("config.json already exists. Overwrite? (y/N): ").strip().lower()
        if confirm != "y":
            print("Aborted — existing config.json preserved.")
            return

    try:
        with open(path, "w") as f:
            json.dump(cfg, f, indent=2)
        print(f"Saved {path}. Do not commit this file to git.")
    except Exception as e:
        print("Failed to write config.json:", e)


if __name__ == "__main__":
    main()
