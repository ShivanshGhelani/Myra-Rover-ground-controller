
from inputs import get_gamepad

def main():
    print("Press D-pad buttons to see their codes. Press Ctrl+C to exit.")
    while True:
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key":
                print(f"Code: {event.code}, Value: {event.state}")

if __name__ == "__main__":
    main()