import OpenSSL

ctx = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_2_METHOD)

pkey = OpenSSL.crypto.PKey()
pkey.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)

cert = OpenSSL.crypto.X509()
cert.get_subject().CN = 'example.com'
cert.set_issuer(cert.get_subject())
cert.set_pubkey(pkey)
cert.set_notBefore(b'20010101000000Z')
cert.set_notAfter(b'20210101000000Z')
cert.sign(pkey, 'sha256')

with open('private/key.pem', 'wb') as keyfile:
    keyfile.write(OpenSSL.crypto.dump_privatekey(
        OpenSSL.crypto.FILETYPE_PEM, pkey))

with open('private/cert.pem', 'wb') as certfile:
    certfile.write(OpenSSL.crypto.dump_certificate(
        OpenSSL.crypto.FILETYPE_PEM, cert))
