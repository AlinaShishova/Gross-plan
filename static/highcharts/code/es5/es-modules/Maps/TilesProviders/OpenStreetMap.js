/* *
 * OpenStreetMap provider, used for tile map services
 * */
'use strict';
/* *
 *
 *  Class
 *
 * */
var OpenStreetMap = /** @class */ (function () {
    function OpenStreetMap() {
        /* *
         *
         *  Properties
         *
         * */
        this.defaultCredits = ('Map data &copy2023' +
            ' <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>');
        this.initialProjectionName = 'WebMercator';
        this.subdomains = ['a', 'b', 'c'];
        this.themes = {
            Standard: {
                url: 'https://tile.openstreetmap.org/{zoom}/{x}/{y}.png',
                minZoom: 0,
                maxZoom: 19
            },
            Hot: {
                url: 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
                minZoom: 0,
                maxZoom: 19
            },
            OpenTopoMap: {
                url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
                minZoom: 0,
                maxZoom: 17,
                credits: "Map data: &copy; <a href=\"https://www.openstreetmap.org/copyright\">\n                OpenStreetMap</a> contributors, <a href=\"https://viewfinderpanoramas.org\">SRTM</a> \n                | Map style: &copy; <a href=\"https://opentopomap.org\">OpenTopoMap</a> \n                (<a href=\"https://creativecommons.org/licenses/by-sa/3.0/\">CC-BY-SA</a>)"
            }
        };
    }
    return OpenStreetMap;
}());
/* *
 *
 *  Default Export
 *
 * */
export default OpenStreetMap;
