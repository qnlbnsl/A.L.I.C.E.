import pyaudio

def interpret_channel_layout(channels):
    layouts = {
        1: "Mono",
        2: "Stereo",
        4: "Quadraphonic",
        6: "5.1 Surround",
        8: "7.1 Surround",
        # Add more layouts as needed
    }
    return layouts.get(channels, f"{channels}-Channel")

def print_device_info(device_index):
    # Create a PyAudio object
    p = pyaudio.PyAudio()

    # Get information about the specified device
    try:
        device_info = p.get_device_info_by_index(device_index)
        print(f"Information for device at index {device_index}:\n")

        # Iterate over the dictionary and print each key-value pair
        for key in device_info:
            print(f"{key}: {device_info[key]}")

        # Print the assumed channel layout
        input_layout = interpret_channel_layout(device_info.get('maxInputChannels', 0))
        output_layout = interpret_channel_layout(device_info.get('maxOutputChannels', 0))
        print(f"\nAssumed Input Layout: {input_layout}")
        print(f"Assumed Output Layout: {output_layout}")

        # ... (rest of your existing code)

    except IOError as e:
        print(f"Could not get information for device with index {device_index}: {e}")

    finally:
        # Terminate the PyAudio object
        p.terminate()

# Call the function with the device index 2
print_device_info(2)
