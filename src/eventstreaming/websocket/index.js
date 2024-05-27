let encoder = null
let decoder = null

const KEY_FRAME_SIZE = 150
let frameCounter = 0

let width = null
let height = null
const encoded_frames = []

const canvas = document.getElementById('video_diplay')
const context = canvas.getContext('2d')

const ws = new WebSocket('ws://localhost:8765')
ws.onopen = () => {
	ws.send('video')
}
ws.onmessage = async (e) => {
	if (e.data && e.data.arrayBuffer) decode(await e.data.arrayBuffer())
}

function handlerChunk(chunk) {
	const buffer = new ArrayBuffer(16 + chunk.byteLength) // 1 + 1 + 1 + 1 + 8 + 4 + data length
	const view = new DataView(buffer)

	// Set source (the streaming with same consensus)
	const source = 0
	view.setUint8(0, source)
	// Set track (track in the source)
	const track = 0
	view.setUint8(1, track)
	// Set content type (mime type)
	const contentType = 0
	view.setUint8(2, contentType)
	// Set info
	const info = (chunk.type === 'key')? 1: 0
	console.log(chunk.type)
	view.setUint8(3, info)
	// Set timestamp
	view.setBigUint64(4, BigInt(chunk.timestamp), true) // Little endian
	// Set data length
	view.setUint32(12, chunk.byteLength, true) // Little endian
	// Set data
	const dataView = new Uint8Array(buffer, 16)
	chunk.copyTo(dataView)

	if (ws.readyState === WebSocket.OPEN) {
		ws.send(buffer)
	}
}

function initEncoder() {
	const config = {
		codec: 'vp09.00.10.08', // or av01.0.09M.08 or av01.0.15M.10
		width: width,
		height: height
	}
	encoder = new VideoEncoder({
		output: handlerChunk,
		error: e => console.error(e)
	})
	encoder.configure(config)
}

function handleFrame(frame) {
  context.drawImage(frame, 0, 0)
	frame.close()
}

function initDecoder() {
	const config = {
		codec: 'vp09.00.10.08', // or av01.0.09M.08 or av01.0.15M.10
		codedWidth: width,
		codedHeight: height
	}
	decoder = new VideoDecoder({
		output: handleFrame, 
		error: e => console.error(e)
	})
	decoder.configure(config)
}

async function encode() {
	const stream = await navigator.mediaDevices.getDisplayMedia()
	const track = stream.getTracks()[0]

	const processor = new MediaStreamTrackProcessor(track)
	const reader = processor.readable.getReader()
	while (true) {
		const result = await reader.read()
		if (result.done) {
			break
		}
		const frame = result.value

		document.getElementById('original_w').innerHTML = frame.codedWidth
		document.getElementById('original_h').innerHTML = frame.codedHeight
		const sx = document.getElementById('sx').value
		const sy = document.getElementById('sy').value
		const sw = document.getElementById('sw').value
		const sh = document.getElementById('sh').value
		width = document.getElementById('dw').value
		height = document.getElementById('dh').value
		document.getElementById('start').hidden = true
		window.localStorage.setItem('sx', sx)
		window.localStorage.setItem('sy', sy)
		window.localStorage.setItem('sw', sw)
		window.localStorage.setItem('sh', sh)
		window.localStorage.setItem('dw', width)
		window.localStorage.setItem('dh', height)

		const _canvas = new OffscreenCanvas(width, height)
    const ctx = _canvas.getContext('2d')
    ctx.drawImage(
				frame,
        sx, sy, sw, sh,
        0, 0, width, height
    )
		const croppedFrame = new VideoFrame(_canvas, { timestamp: frame.timestamp });

		if (encoder === null) {
			canvas.width = width
			canvas.height = height
			initEncoder()
		}
		if (decoder === null) {
			initDecoder()
		}
		if (encoder.encodeQueueSize <= 5) {
			frameCounter++
			encoder.encode(croppedFrame, { keyFrame: frameCounter % KEY_FRAME_SIZE === 0 })
		}
		croppedFrame.close()
		frame.close()
	}
	await encoder.flush()
}

function decode(buffer) {
	if (decoder !== null) {
		const view = new DataView(buffer)
		const chunk = new EncodedVideoChunk({
			type: (view.getUint8(3) === 1)? 'key': 'delta',
			timestamp: Number(view.getBigUint64(4, true)), // true: Little endian
			data: new Uint8Array(buffer, 16)
		})
		decoder.decode(chunk)
	}
}

function start() {
	encode()
	decode()
}

function init_default() {
	if (window.localStorage.getItem('sx') !== null) {
		document.getElementById('sx').value = localStorage.getItem('sx')
	}
	if (window.localStorage.getItem('sy') !== null) {
		document.getElementById('sy').value = localStorage.getItem('sy')
	}
	if (window.localStorage.getItem('sw') !== null) {
		document.getElementById('sw').value = localStorage.getItem('sw')
	}
	if (window.localStorage.getItem('sh') !== null) {
		document.getElementById('sh').value = localStorage.getItem('sh')
	}
	if (window.localStorage.getItem('dw') !== null) {
		document.getElementById('dw').value = localStorage.getItem('dw')
	}
	if (window.localStorage.getItem('dh') !== null) {
		document.getElementById('dh').value = localStorage.getItem('dh')
	}
}

init_default()