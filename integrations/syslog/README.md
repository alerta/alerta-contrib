

Generate example syslog messages on a Mac

    $ sudo vi /etc/syslog.conf

    *.* @127.0.0.1:514

    $ sudo launchctl unload /System/Library/LaunchDaemons/com.apple.syslogd.plist
    $ sudo launchctl load /System/Library/LaunchDaemons/com.apple.syslogd.plist

    $ logger -i -s -p mail.err -t TEST "mail server is down"
    $ logger -p local0.notice -t HOSTIDM