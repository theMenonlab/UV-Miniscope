import time
import os
from PIL import Image
import io
import numpy as np

# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x

# Constants
CHUNK_SIZE = 16  # Each chunk is 16x16 pixels
image_size_x = 304
image_size_y = 304

# Define the number of chunks in the image
total_chunks = (image_size_x // CHUNK_SIZE) * (image_size_y // CHUNK_SIZE)
received_positions = set()

def read_png_to_chunks(file_path):
    try:
        image = Image.open(file_path)
        image = image.resize((image_size_x, image_size_y))  # Ensure the image is 608x608 pixels
        chunks = []
        for i in range(0, image_size_x, CHUNK_SIZE):
            for j in range(0, image_size_y, CHUNK_SIZE):
                box = (j, i, j + CHUNK_SIZE, i + CHUNK_SIZE)
                chunk = image.crop(box)
                with io.BytesIO() as output:
                    chunk.save(output, format="PNG")
                    chunk_bytes = output.getvalue()
                    # Prepend the coordinates as a 4-byte header (2 bytes for row, 2 bytes for col)
                    chunk_header = i.to_bytes(2, 'big') + j.to_bytes(2, 'big')
                    chunks.append(chunk_header + chunk_bytes)
        return chunks
    except Exception as e:
        print(f"Error reading PNG file: {e}")
        return None

def save_chunks_to_png(chunks, file_path):
    try:
        full_image = Image.new('RGB', (image_size_x, image_size_y))
        missing_positions = []

        for i in range(0, image_size_x, CHUNK_SIZE):
            for j in range(0, image_size_y, CHUNK_SIZE):
                position = (i, j)
                if position in received_positions:
                    chunk = next(c for c in chunks if (int.from_bytes(c[:2], 'big'), int.from_bytes(c[2:4], 'big')) == position)
                    chunk_bytes = chunk[4:]

                    try:
                        chunk_image = Image.open(io.BytesIO(chunk_bytes))
                        full_image.paste(chunk_image, (j, i))
                    except Exception as e:
                        print(f"Skipping invalid chunk at row {i}, col {j}: {e}")
                else:
                    missing_positions.append(position)

        if missing_positions:
            print(f"Missing chunk positions: {missing_positions}")
            request_missing_chunks(missing_positions)  # Request missing chunks
        else:
            # Save the full image once all chunks are received
            full_image.save(file_path)
            print("Image received and saved.")

    except Exception as e:
        print(f"Error saving PNG file: {e}")

def request_missing_chunks(missing_positions):
    try:
        while missing_positions:
            # Create the missing chunk request packet
            missing_chunk_request = b'MISS'
            for pos in missing_positions:
                missing_chunk_request += pos[0].to_bytes(2, 'big') + pos[1].to_bytes(2, 'big')
            rfm9x.send(missing_chunk_request)
            print(f"Requested missing chunks: {missing_positions}")
            time.sleep(0.1)

            # Wait for missing chunks to be received
            wait_for_missing_chunks(missing_positions)

            # Update missing positions
            missing_positions = [pos for pos in missing_positions if pos not in received_positions]
            
            if missing_positions:
                print(f"Retrying for missing chunks: {missing_positions}")

    except Exception as e:
        print(f"Error requesting missing chunks: {e}")

def wait_for_missing_chunks(missing_positions):
    start_time = time.time()
    timeout = 30  # 30 seconds timeout
    
    while missing_positions and (time.time() - start_time < timeout):
        packet = rfm9x.receive(timeout=1.0)  # Wait up to 1 second for a packet
        
        if packet is not None:
            if packet[:4] == b'MISS':
                # This is a request for missing chunks from the other device
                handle_missing_chunk_request(packet)
            else:
                # This is potentially a missing chunk we requested
                handle_received_chunk(packet)
                
                # Update the missing_positions list
                row = int.from_bytes(packet[:2], 'big')
                col = int.from_bytes(packet[2:4], 'big')
                position = (row, col)
                if position in missing_positions:
                    missing_positions.remove(position)
                    print(f"Received missing chunk at position {position}. Remaining: {len(missing_positions)}")
        
        # Update the display
        display.fill(0)
        display.text('Receiving chunks', 5, 0, 1)
        display.text(f'Missing: {len(missing_positions)}', 5, 15, 1)
        display.show()
    
    if missing_positions:
        print(f"Timeout waiting for missing chunks. Still missing: {len(missing_positions)}")
    else:
        print("All missing chunks received successfully.")

def handle_received_chunk(packet):
    try:
        row = int.from_bytes(packet[:2], 'big')
        col = int.from_bytes(packet[2:4], 'big')
        position = (row, col)

        if position not in received_positions:
            received_positions.add(position)
            received_chunks.append(packet)
            print(f"Received chunk at position {position}. Total received: {len(received_positions)}")
    except Exception as e:
        print(f"Error handling received chunk: {e}")

def handle_missing_chunk_request(packet):
    try:
        # Extract the number of missing chunks requested
        num_requested_chunks = (len(packet) - 4) // 4  # Each chunk is identified by 4 bytes (2 for row, 2 for col)
        
        for i in range(num_requested_chunks):
            # Extract row and column from the request packet
            missing_row = int.from_bytes(packet[4 + 4 * i:6 + 4 * i], 'big')
            missing_col = int.from_bytes(packet[6 + 4 * i:8 + 4 * i], 'big')
            position = (missing_row, missing_col)

            print(f"Received request for missing chunk at position {position}.")

            # Find and send the requested chunk
            image_chunks = read_png_to_chunks(send_image_path)
            for chunk_num, chunk in enumerate(image_chunks):
                chunk_row = int.from_bytes(chunk[:2], 'big')
                chunk_col = int.from_bytes(chunk[2:4], 'big')

                if (chunk_row, chunk_col) == position:
                    rfm9x.send(chunk)
                    print(f"Sending chunk {chunk_num + 1} of size {len(chunk)} bytes at position {position}")
                    time.sleep(0.1)  # Small delay to avoid packet collision
                    break

    except Exception as e:
        print(f"Error handling missing chunk request: {e}")

def check_image_completion():
    global received_chunks, received_positions
    if len(received_positions) == total_chunks:
        save_chunks_to_png(received_chunks, receive_image_path)
        display.fill(0)
        display.text('Image reconstructed', 25, 15, 1)
        display.show()
        print("Image received and reconstructed.")
        received_chunks = []  # Reset for next image
        received_positions.clear()
        return True
    return False

def check_missing_chunks():
    global last_received_time
    if time.time() - last_received_time > TIMEOUT:
        missing_positions = [(i, j) for i in range(0, image_size_x, CHUNK_SIZE)
                             for j in range(0, image_size_y, CHUNK_SIZE)
                             if (i, j) not in received_positions]
        if missing_positions:
            request_missing_chunks(missing_positions)
            last_received_time = time.time()  # Reset the timer

# Button A
btnA = DigitalInOut(board.D5)
btnA.direction = Direction.INPUT
btnA.pull = Pull.UP

# Button B
btnB = DigitalInOut(board.D6)
btnB.direction = Direction.INPUT
btnB.pull = Pull.UP

# Button C
btnC = DigitalInOut(board.D12)
btnC.direction = Direction.INPUT
btnC.pull = Pull.UP

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# 128x32 OLED Display
reset_pin = DigitalInOut(board.D4)
display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, reset=reset_pin)
# Clear the display.
display.fill(0)
display.show()
width = display.width
height = display.height

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
rfm9x.tx_power = 23
prev_packet = None

# Image paths
send_image_path = "/home/menon1541/Downloads/20240519_dasmeet/isox_10th/miniscopeDeviceName_2024_05_19_17_56_45.png"
receive_image_path = "/home/menon1541/received_image.png"
received_chunks = []
last_received_time = time.time()
TIMEOUT = 5

while True:
    packet = None
    display.fill(0)
    display.text('RasPi LoRa', 35, 0, 1)

    packet = rfm9x.receive()
    if packet is None:
        display.show()
        display.text('- Waiting for PKT -', 15, 20, 1)
        if len(received_positions) > total_chunks * 0.8:
            check_missing_chunks()
            check_image_completion()
    else:
        display.fill(0)
        prev_packet = packet
        print('Incoming packet detected')
        try:
            if prev_packet[:4] == b'MISS':
                handle_missing_chunk_request(prev_packet)
            else:
                handle_received_chunk(prev_packet)
                last_received_time = time.time()
        except Exception as e:
            display.text('RX Error', 25, 0, 1)
            print("Error receiving image:", e)



    if not btnA.value:
        display.fill(0)
        try:
            image_chunks = read_png_to_chunks(send_image_path)
            if image_chunks is not None:
                for chunk_num, chunk in enumerate(image_chunks):
                    print(f"Sending chunk {chunk_num + 1} of size {len(chunk)} bytes")
                    rfm9x.send(chunk)
                    time.sleep(0.1)
                display.text('Sent Image!', 25, 15, 1)
            else:
                display.text('Image read error', 25, 15, 1)
        except Exception as e:
            display.text('TX Error', 25, 15, 1)
            print("Error sending image:", e)
    elif not btnB.value:
        display.fill(0)
        display.text('Button B!', 25, 15, 1)
    elif not btnC.value:
        display.fill(0)
        display.text('Button C!', 25, 15, 1)

    display.show()
    time.sleep(0.1)
