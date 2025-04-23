# Copyright © 2025 CanyonCasa
# # SPDX-License-Identifier: MIT

# Derived from https://github.com/intGus/cpwebsockets Gustavo Diaz <contact@gusdiaz.dev>
#   which Forked from: https://github.com/danni/uwebsockets

# Websockets Protocol for CircuitPython...
#   embellished with JSON send and receive functions
#   restructured to enable passing socket timeout before connection

import random
import re
import struct
import binascii
import random
import ssl
import socketpool as socket
from collections import namedtuple
from micropython import const
import adafruit_logging as logging

LOGGER = logging.getLogger(__name__)
print(f"name: {__name__}")

# Opcodes
_OP_CONT = const(0x0)
_OP_TEXT = const(0x1)
_OP_BYTES = const(0x2)
_OP_CLOSE = const(0x8)
_OP_PING = const(0x9)
_OP_PONG = const(0xA)

# Close codes
CLOSE_OK = const(1000)
CLOSE_GOING_AWAY = const(1001)
CLOSE_PROTOCOL_ERROR = const(1002)
CLOSE_DATA_NOT_SUPPORTED = const(1003)
CLOSE_BAD_DATA = const(1007)
CLOSE_POLICY_VIOLATION = const(1008)
CLOSE_TOO_BIG = const(1009)
CLOSE_MISSING_EXTN = const(1010)
CLOSE_BAD_CONDITION = const(1011)

URL_RE = re.compile(r"(wss|ws)://([A-Za-z0-9-\.]+)(?:\:([0-9]+))?(/.+)?")
URI = namedtuple("URI", ("protocol", "hostname", "port", "path"))

def read_exact(sock, num_bytes):
    """
    Read exactly `num_bytes` from the socket.
    """
    buffer = bytearray(num_bytes)
    view = memoryview(buffer)
    read_total = 0

    while read_total < num_bytes:
        read_now = sock.recv_into(view[read_total:])
        if read_now == 0:
            raise RuntimeError("Connection closed while reading")
        read_total += read_now

    return bytes(buffer)  # Convert to immutable bytes

def urlparse(uri):
    """Parse ws:// URLs"""
    match = URL_RE.match(uri)
    if match:
        protocol = match.group(1)
        host = match.group(2)
        port = match.group(3)
        path = match.group(4)

        if protocol == "wss":
            if port is None:
                port = 443
        elif protocol == "ws":
            if port is None:
                port = 80
        else:
            raise ValueError("Scheme {} is invalid".format(protocol))

        return URI(protocol, host, int(port), path)

    raise ValueError("URL invalid. Format: ws[s]://server:port/[path]")

def read_line(sock, buffer_size=1024, strip=True):
    """
    Read a line from the socket using recv_into. Stops at '\r\n'.
    """
    buffer = bytearray(buffer_size)  # Pre-allocate buffer
    line = b""
    
    while True:
        bytes_read = sock.recv_into(buffer, 1)  # Read one byte at a time
        if bytes_read == 0:
            break  # End of stream
        line += buffer[:bytes_read]
        if line.endswith(self.termination):  # Check for end of line
            break
    if strip:
        return line[:-len(self.termination)]
    return line


class NoDataException(Exception):
    """No data received unexpectedly"""


class ConnectionClosed(Exception):
    """Connection closed"""


class Websocket:
    """
    Basis of the Websocket protocol.
    """

    is_client = False

    def __init__(self, cfg):
        for key in cfg:
            self[key] = cfg[key]
        if not self.termination: self.termination = b'\r\n'
        self.open = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def read_frame(self):  # max_size=None
        """
        Read a frame from the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """

        # Frame header
        two_bytes = read_exact(self.sock, 2)

        if not two_bytes:
            raise NoDataException

        byte1, byte2 = struct.unpack("!BB", two_bytes)

        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        fin = bool(byte1 & 0x80)
        opcode = byte1 & 0x0F

        # Byte 2: MASK(1) LENGTH(7)
        mask = bool(byte2 & (1 << 7))
        length = byte2 & 0x7F

        if length == 126:  # Magic number, length header is 2 bytes
            length_bytes = read_exact(self.sock, 2)
            length = struct.unpack("!H", length_bytes)[0]
        elif length == 127:  # Magic number, length header is 8 bytes
            length_bytes = read_exact(self.sock, 8)
            length = struct.unpack("!Q", length_bytes)[0]

        if mask:  # Mask is 4 bytes
            mask_bits = read_exact(self.sock, 4)

        try:
            data = read_exact(self.sock, length)
        except MemoryError:
            # We can't receive this many bytes, close the socket
            if __debug__:
                LOGGER.debug("Frame of length %s too big. Closing", length)
            self.close(code=CLOSE_TOO_BIG)
            return True, _OP_CLOSE, None

        if mask:
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        return fin, opcode, data

    def write_frame(self, opcode, data=b""):
        """
        Write a frame to the socket.
        See https://tools.ietf.org/html/rfc6455#section-5.2 for the details.
        """
        fin = True
        mask = self.is_client  # messages sent by client are masked

        length = len(data)

        # Frame header
        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        byte1 = 0x80 if fin else 0
        byte1 |= opcode

        # Byte 2: MASK(1) LENGTH(7)
        byte2 = 0x80 if mask else 0

        if length < 126:  # 126 is magic value to use 2-byte length header
            byte2 |= length
            self.sock.send(struct.pack("!BB", byte1, byte2))

        elif length < (1 << 16):  # Length fits in 2-bytes
            byte2 |= 126  # Magic code
            self.sock.send(struct.pack("!BBH", byte1, byte2, length))

        elif length < (1 << 64):
            byte2 |= 127  # Magic code
            self.sock.send(struct.pack("!BBQ", byte1, byte2, length))

        else:
            raise ValueError()

        if mask:  # Mask is 4 bytes
            mask_bits = struct.pack("!I", random.getrandbits(32))
            self.sock.send(mask_bits)

            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        self.sock.send(data)

    def recv(self):
        """
        Receive data from the websocket.

        This is slightly different from 'websockets' in that it doesn't
        fire off a routine to process frames and put the data in a queue.
        If you don't call recv() sufficiently often you won't process control
        frames.
        """
        assert self.open

        while self.open:
            try:
                fin, opcode, data = self.read_frame()
            except NoDataException:
                return ""
            except ValueError:
                LOGGER.debug("Failed to read frame. Socket dead.")
                self._close()
                raise ConnectionClosed()  # pylint: disable=raise-missing-from

            if not fin:
                raise NotImplementedError()

            if opcode == _OP_TEXT:
                return data.decode("utf-8")
            if opcode == _OP_BYTES:
                return data
            if opcode == _OP_CLOSE:
                self._close()
                raise ConnectionClosed(opcode)
            if opcode == _OP_PONG:
                # Ignore this frame, keep waiting for a data frame
                continue
            if opcode == _OP_PING:
                # We need to send a pong frame
                if __debug__:
                    LOGGER.debug("Sending PONG")
                self.write_frame(_OP_PONG, data)
                # And then wait to receive
                continue
            if opcode == _OP_CONT:
                # This is a continuation of a previous frame
                raise NotImplementedError(opcode)
            # nothing
            raise ValueError(opcode)

    def send(self, buf):
        """Send data to the websocket."""

        assert self.open

        if isinstance(buf, str):
            opcode = _OP_TEXT
            buf = buf.encode("utf-8")
        elif isinstance(buf, bytes):
            opcode = _OP_BYTES
        else:
            raise TypeError()

        self.write_frame(opcode, buf)

    def close(self, code=CLOSE_OK, reason=""):
        """Close the websocket."""
        if not self.open:
            return

        buf = struct.pack("!H", code) + reason.encode("utf-8")

        self.write_frame(_OP_CLOSE, buf)
        self._close()

    def _close(self):
        if __debug__:
            LOGGER.debug("Connection closed")
        self.open = False
        self.sock.close()


class WebsocketClient(Websocket):
    is_client = True

    def connect(uri, ap):
        """
        Connect a websocket.
        """

        self.uri = urlparse(uri)
        assert self.uri

        if __debug__: LOGGER.debug(f"open connection {self.uri.hostname}:{self.uri.port}")

        self.sock = socket.SocketPool(ap).socket()
        if self.timeout:
            self.sock.settimeout = self.timeout
        addr = socket.SocketPool(ap).getaddrinfo(uri.hostname, uri.port)
        self.sock.connect(addr[0][4])
        
        if uri.protocol == 'wss':
            ssl_context = ssl.create_default_context()
            self.sock = ssl_context.wrap_socket(self.sock, server_hostname=uri.hostname)









        def send_header(header, *args):
            if __debug__: LOGGER.debug(str(header), *args)
            self.send(header % args + '\r\n')

        # Sec-WebSocket-Key is 16 bytes of random base64 encoded
        key = binascii.b2a_base64(bytes(random.getrandbits(8) for _ in range(16)),False)

        send_header(b'GET %s HTTP/1.1', uri.path or '/')
        send_header(b'Host: %s:%s', uri.hostname, uri.port)
        send_header(b'Connection: Upgrade')
        send_header(b'Upgrade: websocket')
        send_header(b'Sec-WebSocket-Key: %s', key)
        send_header(b'Sec-WebSocket-Version: 13')
        send_header(b'Origin: http://{hostname}:{port}'.format(
            hostname=uri.hostname,
            port=uri.port)
        )
        send_header(b'')

        header = read_line(sock)
        assert header.startswith(b'HTTP/1.1 101 '), header

        # We don't (currently) need these headers
        # FIXME: should we check the return key?
        while header:
            if __debug__: LOGGER.debug(str(header))
            header = read_line(sock)

        return WebsocketClient(sock)





    def send_line(text):
        self.send(text+str(self.termination,'utf-8'))

    def send_json(obj):
        self.send_line(json.dumps(obj))

    def recv_json(self, default=None):
        data = super.recv().rstrip(str(self.termination,'utf-8'))
        try:
            return json.loads(data)
        except Exception as ex:
            return default
