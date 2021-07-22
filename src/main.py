# Main file of analyser.

# Importing local modules.
import vk
import commands

if __name__ == "__main__":
    # Entry point.

    # Connecting to VK API.
    vk.connect()
    print("[Debug] Connected to VK API.")

    # Adding handler.
    vk.handler_add(commands.message_handler)

    # Starting listening.
    print("[Debug] Listening events (Commands).")
    vk.listen()
