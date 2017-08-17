var now_playing = '';

setInterval(function () {
    jQuery.ajax(
        {
            type: "GET",
            url: "http://api.<yoursite>/?token=0",
            dataType: "xml",
            success: xmlParser
        })
}, 5000);

function xmlParser(xml) {
    var parsedXml = jQuery(xml);
    var title = parsedXml.find('title').text();
    var artist = parsedXml.find('artist').text();
    var arturl = parsedXml.find('arturl').text();
    var song = artist.concat(" &mdash; ").concat(title);

    if (now_playing !== song) {
        jQuery('div.top-div > div.now_playing').html("<span class=\"title\">Now playing: </span><span class=\"song\"><marquee>".concat(song).concat("</marquee></span>"));
        now_playing = song;
    }
};