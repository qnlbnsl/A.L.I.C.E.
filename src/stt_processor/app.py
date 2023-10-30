from audio_stream.socket import server


def main():
    try:
        server()
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting.")
        exit(0)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
