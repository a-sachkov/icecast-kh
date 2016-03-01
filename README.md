What is it?
-------------
My Icecast/Icecast-KH init.d script for Debian.
Written as simple as possible using only standard commands for better cross-platforming.

Installation
-------------
 Put script into /etc/init.d dir, then:

    sudo chmod 755 /etc/init.d/icecast-kh
    sudo chown root:root /etc/init.d/icecast-kh
    systemctl enable icecast-kh.service

Usage
-------------

    service icecast-kh {start|stop|status|reload}

TODO
-------------
Add restart section.