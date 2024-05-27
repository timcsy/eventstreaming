import av
import struct

decoder = av.CodecContext.create('vp9', 'r')
is_start = False

def decode_video_chunk(video_data, timestamp):
    packet = av.Packet(video_data)
    packet.pts = timestamp
    packet.dts = timestamp

    frames = decoder.decode(packet)

    imgs = []
    for frame in frames:
        img = frame.to_image()  # Convert frame to PIL image for further use or display
        imgs.append({ 'image': img, 'timestamp': timestamp })
    return imgs

def decode_rawdata(data):
    global is_start
    # Assume message is an instance of bytes
    source, track, content_type, info, timestamp, data_length = struct.unpack('<BBBBQI', data[:16])
    video_data = data[16: 16 + data_length]

    # print(f"Received frame at {timestamp} with length {data_length}, info = {info}")

    if info == 1 or is_start:
        is_start = True
        imgs = decode_video_chunk(video_data, timestamp)
        return imgs
    else:
        return []