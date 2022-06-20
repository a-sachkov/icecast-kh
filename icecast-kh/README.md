# What is it?

## WARNING
This part of the repo is probably outdated. Currently icecast is provided as apt package, contains all necessary runtime scripts. Also Icecast provides json stats page out of the box, see [corresponding docs](https://icecast.org/docs/icecast-trunk/server_stats/).

## init.d
My Icecast/Icecast-KH init.d script for Debian.
Written as simple as possible using only standard commands for better cross-platforming.

### Installation:
 Put script into /etc/init.d dir, then:

     sudo chmod 755 /etc/init.d/icecast-kh
     sudo chown root:root /etc/init.d/icecast-kh
     sudo systemctl enable icecast-kh.service

 Don't forget to create log dir:
 
     sudo mkdir /var/log/icecast
     sudo chown -R icecast:icecast /var/log/icecast

Usage:

    sudo service icecast-kh {start|stop|status|reload}
    or
    sudo systemctl start|stop|status|reload icecast-kh.service


## WEB
status-json.xsl - generates 'now playing' info in JSON format. Based on Namikiri's (https://habrahabr.ru/users/namikiri/) version.

### Installation:
 Put script into icecast-kh's web directory ( e.g.: /usr/local/share/icecast/web/ )
