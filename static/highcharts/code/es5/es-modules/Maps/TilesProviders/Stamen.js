/* *
 * Stamen provider, used for tile map services
 * */
'use strict';
/* *
 *
 *  Class
 *
 * */
var Stamen = /** @class */ (function () {
    function Stamen() {
        /* *
         *
         *  Properties
         *
         * */
        this.defaultCredits = ('&copy; Map tiles by <a href="https://stamen.com">Stamen Design</a>,' +
            ' under <a href="https://creativecommons.org/licenses/by/3.0">CC BY' +
            ' 3.0</a>. Data by <a href="https://openstreetmap.org">OpenStreetMap' +
            '</a>, under <a href="https://www.openstreetmap.org/copyright">ODbL</a>');
        this.initialProjectionName = 'WebMercator';
        this.subdomains = ['a', 'b', 'c', 'd'];
        this.themes = {
            Toner: {
                url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}.png',
                minZoom: 0,
                maxZoom: 20
            },
            TonerBackground: {
                url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner-background/{z}/{x}/{y}.png',
                minZoom: 0,
                maxZoom: 20
            },
            TonerLite: {
                url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner-lite/{z}/{x}/{y}.png',
                minZoom: 0,
                maxZoom: 20
            },
            Terrain: {
                url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
                minZoom: 0,
                maxZoom: 18
            },
            TerrainBackground: {
                url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain-background/{z}/{x}/{y}.png',
                minZoom: 0,
                maxZoom: 18
            },
            Watercolor: {
                url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.png',
                minZoom: 1,
                maxZoom: 16,
                credits: ('&copy Map tiles by <a href="https://stamen.com">Stamen' +
                    ' Design</a>, under <a href="https://creativecommons.org/' +
                    'licenses/by/3.0">CC BY 3.0</a>. Data by <a href="https://' +
                    'openstreetmap.org">OpenStreetMap</a>, under <a href=' +
                    '"https://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>')
            }
        };
    }
    return Stamen;
}());
/* *
 *
 *  Default Export
 *
 * */
export default Stamen;
