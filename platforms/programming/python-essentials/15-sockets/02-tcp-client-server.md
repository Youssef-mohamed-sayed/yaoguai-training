# Building a TCP Client and Server

## Learning Objectives

- Write a minimal TCP server: bind, listen, accept.
- Write a matching client and run both on one machine.
- Structure a tiny request-response protocol, including framing.

## Introduction

The client-server pair is where sockets click: the server binds to a port and waits; the client connects; both then speak an agreed protocol. Building one yourself - on localhost, which is always an authorized target - teaches more about networking than a week of reading.

## The Server: bind, listen, accept

```python
import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 9000))
    server.listen(5)                     # backlog of pending connections
    print("listening on 127.0.0.1:9000")
    while True:
        conn, addr = server.accept()     # blocks until a client arrives
        with conn:
            data = conn.recv(1024)
            if not data:
                continue
            message = data.decode().strip().upper()
            conn.sendall(message.encode() + b"\n")
```

`bind` claims the address, `listen` queues incoming connections, and `accept` returns a **new** socket (`conn`) for that specific client plus its address. The listening socket keeps waiting for the next client.

## The Client

```python
import socket

with socket.create_connection(("127.0.0.1", 9000), timeout=5) as s:
    s.sendall(b"hello server\n")
    print("reply:", s.recv(1024).decode().strip())
```

Run the server in one terminal, the client in another:

```text
$ python3 server.py          # terminal 1
listening on 127.0.0.1:9000
$ python3 client.py          # terminal 2
reply: HELLO SERVER
```

You just built a working echo-uppercase service. Test it by hand too: `nc 127.0.0.1 9000`, type a line, see it return uppercased. `nc` (netcat) is the universal socket debugger.

## Framing: Where Does a Message End?

TCP is a byte stream - "hello" and "server" sent separately may arrive merged. Protocols solve this with **framing**: length prefixes, or delimiters like newline (what our example assumes). A robust newline reader buffers until it sees `\n`:

```python
def read_line(conn):
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(1024)
        if not chunk:
            break
        data += chunk
    return data
```

Our simple server handles one client at a time - a second client waits until the first disconnects. Threading (`threading.Thread(target=handle, args=(conn,))`) is the next step when concurrent clients matter.

## Common Mistakes

- Forgetting `SO_REUSEADDR`, then "Address already in use" on every quick restart.
- Assuming one `sendall` equals one `recv` on the other side; without framing, messages merge or split.
- Binding a test server to `0.0.0.0` (all interfaces) when `127.0.0.1` would do - do not expose unfinished services to the network.
- Not handling client disconnect (`recv` returning empty), crashing the server on the first Ctrl-C from a client.

## Key Takeaways

- Servers: socket, `SO_REUSEADDR`, bind, listen, then loop on `accept` which returns a per-client connection socket.
- TCP is a stream: messages need framing (delimiters or length prefixes) and `recv` needs a loop.
- Test locally with two terminals and `nc`; bind to `127.0.0.1` unless the network genuinely needs the service.

## Practice Exercises

**Exercise 1.** Run the server and client from this lesson and confirm the round trip. Then connect with `nc 127.0.0.1 9000` and type a line manually.

<details>
<summary>Show a worked solution</summary>

```text
$ python3 server.py &
listening on 127.0.0.1:9000
$ python3 client.py
reply: HELLO SERVER
$ nc 127.0.0.1 9000
testing
TESTING
```

Any uppercase echo back means the loop works; Ctrl-C the server to stop it.
</details>

**Exercise 2.** Extend the server to count connections and include the count in its reply: `YOU ARE CLIENT #3: HELLO`.

<details>
<summary>Show a worked solution</summary>

```python
count = 0
while True:
    conn, addr = server.accept()
    count += 1
    with conn:
        data = conn.recv(1024)
        message = data.decode().strip().upper()
        conn.sendall(f"YOU ARE CLIENT #{count}: {message}\n".encode())
```

(Inside the same `with socket.socket(...) as server:` block as before.)
</details>

**Exercise 3.** Modify the client to send two lines ("one\n" then "two\n") and read each reply using the `read_line` helper.

<details>
<summary>Show a worked solution</summary>

```python
with socket.create_connection(("127.0.0.1", 9000), timeout=5) as s:
    for text in ("one", "two"):
        s.sendall(text.encode() + b"\n")
        print("reply:", read_line(s).decode().strip())
```

```text
reply: ONE
reply: TWO
```

Each send is matched by a read that stops at the newline - framing in action.
</details>

## Check Yourself

**What does `accept()` return?**

<details>
<summary>Show answer</summary>

A tuple of a new socket connected to that one client, and the client's address. The listening socket stays available for more connections.
</details>

**Why does a TCP protocol need framing?**

<details>
<summary>Show answer</summary>

TCP delivers an undifferentiated byte stream with no message boundaries, so peers must agree on how to delimit messages (newlines, length prefixes, fixed sizes).
</details>

**What problem does `SO_REUSEADDR` solve during development?**

<details>
<summary>Show answer</summary>

It lets you rebind a port that is still in TIME_WAIT from a recently stopped server, avoiding "Address already in use" on restart.
</details>
