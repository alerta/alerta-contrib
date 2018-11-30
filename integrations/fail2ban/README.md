Fail2Ban
========

Send Alerta event (alarm) if source IP is banned (valid user is using invalid password via SSHD or SFTP).

Configuration
-------------

Alerta webhook module and documentation can be found [here](../../webhooks/fail2ban)

Clone git repo on the server where `fail2ban` is installed and execute following commands as root:

Copy action script

```bash
cp -a fail2ban-alerta.sh /usr/local/bin/
chown root:root /usr/local/bin/fail2ban-alerta.sh
chmod +x /usr/local/bin/fail2ban-alerta.sh
```

Copy `fail2ban` action configuration file

```bash
cp -a alerta.conf /etc/fail2ban/action.d/
chown root:root /etc/fail2ban/action.d/alerta.conf
```

Modify configuration of `sshd` jail in the existing `/etc/fail2ban/jail.local` file by adding additional `alerta` action,
also be sure to modify action input parameters accordingly (`alertaurl` and `alertaapikey`).

**Note:** Example [jail.local](./jail.local) file is also provided

```plain
[sshd]

enabled  = true
port     = ssh
logpath  = %(sshd_log)s
action   = %(action_mwl)s
           alerta[alertaurl=https://alerta.example.com/api/webhooks/fail2ban, alertaapikey=EXdp3haf4Xkk7Dpk5MFrqfafn6nYGgtz4JL4XzBY]
maxretry = 4
```

Restart `fail2ban` service

```plain
systemctl restart fail2ban
```
