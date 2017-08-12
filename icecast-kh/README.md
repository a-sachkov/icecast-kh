What is it?
-------------
My Icecast/Icecast-KH init.d script for Debian.
Written as simple as possible using only standard commands for better cross-platforming.

Installation
-------------
 Put script into /etc/init.d dir, then:

     sudo chmod 755 /etc/init.d/icecast-kh
     sudo chown root:root /etc/init.d/icecast-kh
     sudo systemctl enable icecast-kh.service

 Don't forget to create log dir:
 
     sudo mkdir /var/log/icecast
     sudo chown -R icecast:icecast /var/log/icecast

Usage
-------------

    sudo service icecast-kh {start|stop|status|reload}
    or
    sudo systemctl start|stop|status|reload icecast-kh.service

TODO
-------------
Add restart section.
