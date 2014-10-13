# Suppress Postfix error
if 'error: open database /etc/postfix/virtual.db: No such file or director' in text:
    suppress = True