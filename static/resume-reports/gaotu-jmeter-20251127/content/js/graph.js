/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
$(document).ready(function() {

    $(".click-title").mouseenter( function(    e){
        e.preventDefault();
        this.style.cursor="pointer";
    });
    $(".click-title").mousedown( function(event){
        event.preventDefault();
    });

    // Ugly code while this script is shared among several pages
    try{
        refreshHitsPerSecond(true);
    } catch(e){}
    try{
        refreshResponseTimeOverTime(true);
    } catch(e){}
    try{
        refreshResponseTimePercentiles();
    } catch(e){}
});


var responseTimePercentilesInfos = {
        data: {"result": {"minY": 364248.0, "minX": 0.0, "maxY": 583553.0, "series": [{"data": [[0.0, 364248.0], [0.1, 364248.0], [0.2, 364248.0], [0.3, 364248.0], [0.4, 364248.0], [0.5, 364248.0], [0.6, 364248.0], [0.7, 364248.0], [0.8, 364248.0], [0.9, 364248.0], [1.0, 364248.0], [1.1, 364248.0], [1.2, 364248.0], [1.3, 364248.0], [1.4, 364248.0], [1.5, 364248.0], [1.6, 364248.0], [1.7, 364248.0], [1.8, 364248.0], [1.9, 364248.0], [2.0, 364261.0], [2.1, 364261.0], [2.2, 364261.0], [2.3, 364261.0], [2.4, 364261.0], [2.5, 364261.0], [2.6, 364261.0], [2.7, 364261.0], [2.8, 364261.0], [2.9, 364261.0], [3.0, 364261.0], [3.1, 364261.0], [3.2, 364261.0], [3.3, 364261.0], [3.4, 364261.0], [3.5, 364261.0], [3.6, 364261.0], [3.7, 364261.0], [3.8, 364261.0], [3.9, 364261.0], [4.0, 364267.0], [4.1, 364267.0], [4.2, 364267.0], [4.3, 364267.0], [4.4, 364267.0], [4.5, 364267.0], [4.6, 364267.0], [4.7, 364267.0], [4.8, 364267.0], [4.9, 364267.0], [5.0, 364267.0], [5.1, 364267.0], [5.2, 364267.0], [5.3, 364267.0], [5.4, 364267.0], [5.5, 364267.0], [5.6, 364267.0], [5.7, 364267.0], [5.8, 364267.0], [5.9, 364267.0], [6.0, 364292.0], [6.1, 364292.0], [6.2, 364292.0], [6.3, 364292.0], [6.4, 364292.0], [6.5, 364292.0], [6.6, 364292.0], [6.7, 364292.0], [6.8, 364292.0], [6.9, 364292.0], [7.0, 364292.0], [7.1, 364292.0], [7.2, 364292.0], [7.3, 364292.0], [7.4, 364292.0], [7.5, 364292.0], [7.6, 364292.0], [7.7, 364292.0], [7.8, 364292.0], [7.9, 364292.0], [8.0, 364362.0], [8.1, 364362.0], [8.2, 364362.0], [8.3, 364362.0], [8.4, 364362.0], [8.5, 364362.0], [8.6, 364362.0], [8.7, 364362.0], [8.8, 364362.0], [8.9, 364362.0], [9.0, 364362.0], [9.1, 364362.0], [9.2, 364362.0], [9.3, 364362.0], [9.4, 364362.0], [9.5, 364362.0], [9.6, 364362.0], [9.7, 364362.0], [9.8, 364362.0], [9.9, 364362.0], [10.0, 364490.0], [10.1, 364490.0], [10.2, 364490.0], [10.3, 364490.0], [10.4, 364490.0], [10.5, 364490.0], [10.6, 364490.0], [10.7, 364490.0], [10.8, 364490.0], [10.9, 364490.0], [11.0, 364490.0], [11.1, 364490.0], [11.2, 364490.0], [11.3, 364490.0], [11.4, 364490.0], [11.5, 364490.0], [11.6, 364490.0], [11.7, 364490.0], [11.8, 364490.0], [11.9, 364490.0], [12.0, 364564.0], [12.1, 364564.0], [12.2, 364564.0], [12.3, 364564.0], [12.4, 364564.0], [12.5, 364564.0], [12.6, 364564.0], [12.7, 364564.0], [12.8, 364564.0], [12.9, 364564.0], [13.0, 364564.0], [13.1, 364564.0], [13.2, 364564.0], [13.3, 364564.0], [13.4, 364564.0], [13.5, 364564.0], [13.6, 364564.0], [13.7, 364564.0], [13.8, 364564.0], [13.9, 364564.0], [14.0, 364582.0], [14.1, 364582.0], [14.2, 364582.0], [14.3, 364582.0], [14.4, 364582.0], [14.5, 364582.0], [14.6, 364582.0], [14.7, 364582.0], [14.8, 364582.0], [14.9, 364582.0], [15.0, 364582.0], [15.1, 364582.0], [15.2, 364582.0], [15.3, 364582.0], [15.4, 364582.0], [15.5, 364582.0], [15.6, 364582.0], [15.7, 364582.0], [15.8, 364582.0], [15.9, 364582.0], [16.0, 364671.0], [16.1, 364671.0], [16.2, 364671.0], [16.3, 364671.0], [16.4, 364671.0], [16.5, 364671.0], [16.6, 364671.0], [16.7, 364671.0], [16.8, 364671.0], [16.9, 364671.0], [17.0, 364671.0], [17.1, 364671.0], [17.2, 364671.0], [17.3, 364671.0], [17.4, 364671.0], [17.5, 364671.0], [17.6, 364671.0], [17.7, 364671.0], [17.8, 364671.0], [17.9, 364671.0], [18.0, 364736.0], [18.1, 364736.0], [18.2, 364736.0], [18.3, 364736.0], [18.4, 364736.0], [18.5, 364736.0], [18.6, 364736.0], [18.7, 364736.0], [18.8, 364736.0], [18.9, 364736.0], [19.0, 364736.0], [19.1, 364736.0], [19.2, 364736.0], [19.3, 364736.0], [19.4, 364736.0], [19.5, 364736.0], [19.6, 364736.0], [19.7, 364736.0], [19.8, 364736.0], [19.9, 364736.0], [20.0, 364757.0], [20.1, 364757.0], [20.2, 364757.0], [20.3, 364757.0], [20.4, 364757.0], [20.5, 364757.0], [20.6, 364757.0], [20.7, 364757.0], [20.8, 364757.0], [20.9, 364757.0], [21.0, 364757.0], [21.1, 364757.0], [21.2, 364757.0], [21.3, 364757.0], [21.4, 364757.0], [21.5, 364757.0], [21.6, 364757.0], [21.7, 364757.0], [21.8, 364757.0], [21.9, 364757.0], [22.0, 364768.0], [22.1, 364768.0], [22.2, 364768.0], [22.3, 364768.0], [22.4, 364768.0], [22.5, 364768.0], [22.6, 364768.0], [22.7, 364768.0], [22.8, 364768.0], [22.9, 364768.0], [23.0, 364768.0], [23.1, 364768.0], [23.2, 364768.0], [23.3, 364768.0], [23.4, 364768.0], [23.5, 364768.0], [23.6, 364768.0], [23.7, 364768.0], [23.8, 364768.0], [23.9, 364768.0], [24.0, 364783.0], [24.1, 364783.0], [24.2, 364783.0], [24.3, 364783.0], [24.4, 364783.0], [24.5, 364783.0], [24.6, 364783.0], [24.7, 364783.0], [24.8, 364783.0], [24.9, 364783.0], [25.0, 364783.0], [25.1, 364783.0], [25.2, 364783.0], [25.3, 364783.0], [25.4, 364783.0], [25.5, 364783.0], [25.6, 364783.0], [25.7, 364783.0], [25.8, 364783.0], [25.9, 364783.0], [26.0, 364795.0], [26.1, 364795.0], [26.2, 364795.0], [26.3, 364795.0], [26.4, 364795.0], [26.5, 364795.0], [26.6, 364795.0], [26.7, 364795.0], [26.8, 364795.0], [26.9, 364795.0], [27.0, 364795.0], [27.1, 364795.0], [27.2, 364795.0], [27.3, 364795.0], [27.4, 364795.0], [27.5, 364795.0], [27.6, 364795.0], [27.7, 364795.0], [27.8, 364795.0], [27.9, 364795.0], [28.0, 364808.0], [28.1, 364808.0], [28.2, 364808.0], [28.3, 364808.0], [28.4, 364808.0], [28.5, 364808.0], [28.6, 364808.0], [28.7, 364808.0], [28.8, 364808.0], [28.9, 364808.0], [29.0, 364808.0], [29.1, 364808.0], [29.2, 364808.0], [29.3, 364808.0], [29.4, 364808.0], [29.5, 364808.0], [29.6, 364808.0], [29.7, 364808.0], [29.8, 364808.0], [29.9, 364808.0], [30.0, 364852.0], [30.1, 364852.0], [30.2, 364852.0], [30.3, 364852.0], [30.4, 364852.0], [30.5, 364852.0], [30.6, 364852.0], [30.7, 364852.0], [30.8, 364852.0], [30.9, 364852.0], [31.0, 364852.0], [31.1, 364852.0], [31.2, 364852.0], [31.3, 364852.0], [31.4, 364852.0], [31.5, 364852.0], [31.6, 364852.0], [31.7, 364852.0], [31.8, 364852.0], [31.9, 364852.0], [32.0, 364914.0], [32.1, 364914.0], [32.2, 364914.0], [32.3, 364914.0], [32.4, 364914.0], [32.5, 364914.0], [32.6, 364914.0], [32.7, 364914.0], [32.8, 364914.0], [32.9, 364914.0], [33.0, 364914.0], [33.1, 364914.0], [33.2, 364914.0], [33.3, 364914.0], [33.4, 364914.0], [33.5, 364914.0], [33.6, 364914.0], [33.7, 364914.0], [33.8, 364914.0], [33.9, 364914.0], [34.0, 364944.0], [34.1, 364944.0], [34.2, 364944.0], [34.3, 364944.0], [34.4, 364944.0], [34.5, 364944.0], [34.6, 364944.0], [34.7, 364944.0], [34.8, 364944.0], [34.9, 364944.0], [35.0, 364944.0], [35.1, 364944.0], [35.2, 364944.0], [35.3, 364944.0], [35.4, 364944.0], [35.5, 364944.0], [35.6, 364944.0], [35.7, 364944.0], [35.8, 364944.0], [35.9, 364944.0], [36.0, 364979.0], [36.1, 364979.0], [36.2, 364979.0], [36.3, 364979.0], [36.4, 364979.0], [36.5, 364979.0], [36.6, 364979.0], [36.7, 364979.0], [36.8, 364979.0], [36.9, 364979.0], [37.0, 364979.0], [37.1, 364979.0], [37.2, 364979.0], [37.3, 364979.0], [37.4, 364979.0], [37.5, 364979.0], [37.6, 364979.0], [37.7, 364979.0], [37.8, 364979.0], [37.9, 364979.0], [38.0, 364998.0], [38.1, 364998.0], [38.2, 364998.0], [38.3, 364998.0], [38.4, 364998.0], [38.5, 364998.0], [38.6, 364998.0], [38.7, 364998.0], [38.8, 364998.0], [38.9, 364998.0], [39.0, 364998.0], [39.1, 364998.0], [39.2, 364998.0], [39.3, 364998.0], [39.4, 364998.0], [39.5, 364998.0], [39.6, 364998.0], [39.7, 364998.0], [39.8, 364998.0], [39.9, 364998.0], [40.0, 365016.0], [40.1, 365016.0], [40.2, 365016.0], [40.3, 365016.0], [40.4, 365016.0], [40.5, 365016.0], [40.6, 365016.0], [40.7, 365016.0], [40.8, 365016.0], [40.9, 365016.0], [41.0, 365016.0], [41.1, 365016.0], [41.2, 365016.0], [41.3, 365016.0], [41.4, 365016.0], [41.5, 365016.0], [41.6, 365016.0], [41.7, 365016.0], [41.8, 365016.0], [41.9, 365016.0], [42.0, 365034.0], [42.1, 365034.0], [42.2, 365034.0], [42.3, 365034.0], [42.4, 365034.0], [42.5, 365034.0], [42.6, 365034.0], [42.7, 365034.0], [42.8, 365034.0], [42.9, 365034.0], [43.0, 365034.0], [43.1, 365034.0], [43.2, 365034.0], [43.3, 365034.0], [43.4, 365034.0], [43.5, 365034.0], [43.6, 365034.0], [43.7, 365034.0], [43.8, 365034.0], [43.9, 365034.0], [44.0, 365060.0], [44.1, 365060.0], [44.2, 365060.0], [44.3, 365060.0], [44.4, 365060.0], [44.5, 365060.0], [44.6, 365060.0], [44.7, 365060.0], [44.8, 365060.0], [44.9, 365060.0], [45.0, 365060.0], [45.1, 365060.0], [45.2, 365060.0], [45.3, 365060.0], [45.4, 365060.0], [45.5, 365060.0], [45.6, 365060.0], [45.7, 365060.0], [45.8, 365060.0], [45.9, 365060.0], [46.0, 365072.0], [46.1, 365072.0], [46.2, 365072.0], [46.3, 365072.0], [46.4, 365072.0], [46.5, 365072.0], [46.6, 365072.0], [46.7, 365072.0], [46.8, 365072.0], [46.9, 365072.0], [47.0, 365072.0], [47.1, 365072.0], [47.2, 365072.0], [47.3, 365072.0], [47.4, 365072.0], [47.5, 365072.0], [47.6, 365072.0], [47.7, 365072.0], [47.8, 365072.0], [47.9, 365072.0], [48.0, 365087.0], [48.1, 365087.0], [48.2, 365087.0], [48.3, 365087.0], [48.4, 365087.0], [48.5, 365087.0], [48.6, 365087.0], [48.7, 365087.0], [48.8, 365087.0], [48.9, 365087.0], [49.0, 365087.0], [49.1, 365087.0], [49.2, 365087.0], [49.3, 365087.0], [49.4, 365087.0], [49.5, 365087.0], [49.6, 365087.0], [49.7, 365087.0], [49.8, 365087.0], [49.9, 365087.0], [50.0, 365104.0], [50.1, 365104.0], [50.2, 365104.0], [50.3, 365104.0], [50.4, 365104.0], [50.5, 365104.0], [50.6, 365104.0], [50.7, 365104.0], [50.8, 365104.0], [50.9, 365104.0], [51.0, 365104.0], [51.1, 365104.0], [51.2, 365104.0], [51.3, 365104.0], [51.4, 365104.0], [51.5, 365104.0], [51.6, 365104.0], [51.7, 365104.0], [51.8, 365104.0], [51.9, 365104.0], [52.0, 365135.0], [52.1, 365135.0], [52.2, 365135.0], [52.3, 365135.0], [52.4, 365135.0], [52.5, 365135.0], [52.6, 365135.0], [52.7, 365135.0], [52.8, 365135.0], [52.9, 365135.0], [53.0, 365135.0], [53.1, 365135.0], [53.2, 365135.0], [53.3, 365135.0], [53.4, 365135.0], [53.5, 365135.0], [53.6, 365135.0], [53.7, 365135.0], [53.8, 365135.0], [53.9, 365135.0], [54.0, 365282.0], [54.1, 365282.0], [54.2, 365282.0], [54.3, 365282.0], [54.4, 365282.0], [54.5, 365282.0], [54.6, 365282.0], [54.7, 365282.0], [54.8, 365282.0], [54.9, 365282.0], [55.0, 365282.0], [55.1, 365282.0], [55.2, 365282.0], [55.3, 365282.0], [55.4, 365282.0], [55.5, 365282.0], [55.6, 365282.0], [55.7, 365282.0], [55.8, 365282.0], [55.9, 365282.0], [56.0, 365317.0], [56.1, 365317.0], [56.2, 365317.0], [56.3, 365317.0], [56.4, 365317.0], [56.5, 365317.0], [56.6, 365317.0], [56.7, 365317.0], [56.8, 365317.0], [56.9, 365317.0], [57.0, 365317.0], [57.1, 365317.0], [57.2, 365317.0], [57.3, 365317.0], [57.4, 365317.0], [57.5, 365317.0], [57.6, 365317.0], [57.7, 365317.0], [57.8, 365317.0], [57.9, 365317.0], [58.0, 365363.0], [58.1, 365363.0], [58.2, 365363.0], [58.3, 365363.0], [58.4, 365363.0], [58.5, 365363.0], [58.6, 365363.0], [58.7, 365363.0], [58.8, 365363.0], [58.9, 365363.0], [59.0, 365363.0], [59.1, 365363.0], [59.2, 365363.0], [59.3, 365363.0], [59.4, 365363.0], [59.5, 365363.0], [59.6, 365363.0], [59.7, 365363.0], [59.8, 365363.0], [59.9, 365363.0], [60.0, 365366.0], [60.1, 365366.0], [60.2, 365366.0], [60.3, 365366.0], [60.4, 365366.0], [60.5, 365366.0], [60.6, 365366.0], [60.7, 365366.0], [60.8, 365366.0], [60.9, 365366.0], [61.0, 365366.0], [61.1, 365366.0], [61.2, 365366.0], [61.3, 365366.0], [61.4, 365366.0], [61.5, 365366.0], [61.6, 365366.0], [61.7, 365366.0], [61.8, 365366.0], [61.9, 365366.0], [62.0, 365406.0], [62.1, 365406.0], [62.2, 365406.0], [62.3, 365406.0], [62.4, 365406.0], [62.5, 365406.0], [62.6, 365406.0], [62.7, 365406.0], [62.8, 365406.0], [62.9, 365406.0], [63.0, 365406.0], [63.1, 365406.0], [63.2, 365406.0], [63.3, 365406.0], [63.4, 365406.0], [63.5, 365406.0], [63.6, 365406.0], [63.7, 365406.0], [63.8, 365406.0], [63.9, 365406.0], [64.0, 365493.0], [64.1, 365493.0], [64.2, 365493.0], [64.3, 365493.0], [64.4, 365493.0], [64.5, 365493.0], [64.6, 365493.0], [64.7, 365493.0], [64.8, 365493.0], [64.9, 365493.0], [65.0, 365493.0], [65.1, 365493.0], [65.2, 365493.0], [65.3, 365493.0], [65.4, 365493.0], [65.5, 365493.0], [65.6, 365493.0], [65.7, 365493.0], [65.8, 365493.0], [65.9, 365493.0], [66.0, 365497.0], [66.1, 365497.0], [66.2, 365497.0], [66.3, 365497.0], [66.4, 365497.0], [66.5, 365497.0], [66.6, 365497.0], [66.7, 365497.0], [66.8, 365497.0], [66.9, 365497.0], [67.0, 365497.0], [67.1, 365497.0], [67.2, 365497.0], [67.3, 365497.0], [67.4, 365497.0], [67.5, 365497.0], [67.6, 365497.0], [67.7, 365497.0], [67.8, 365497.0], [67.9, 365497.0], [68.0, 365571.0], [68.1, 365571.0], [68.2, 365571.0], [68.3, 365571.0], [68.4, 365571.0], [68.5, 365571.0], [68.6, 365571.0], [68.7, 365571.0], [68.8, 365571.0], [68.9, 365571.0], [69.0, 365571.0], [69.1, 365571.0], [69.2, 365571.0], [69.3, 365571.0], [69.4, 365571.0], [69.5, 365571.0], [69.6, 365571.0], [69.7, 365571.0], [69.8, 365571.0], [69.9, 365571.0], [70.0, 365588.0], [70.1, 365588.0], [70.2, 365588.0], [70.3, 365588.0], [70.4, 365588.0], [70.5, 365588.0], [70.6, 365588.0], [70.7, 365588.0], [70.8, 365588.0], [70.9, 365588.0], [71.0, 365588.0], [71.1, 365588.0], [71.2, 365588.0], [71.3, 365588.0], [71.4, 365588.0], [71.5, 365588.0], [71.6, 365588.0], [71.7, 365588.0], [71.8, 365588.0], [71.9, 365588.0], [72.0, 365621.0], [72.1, 365621.0], [72.2, 365621.0], [72.3, 365621.0], [72.4, 365621.0], [72.5, 365621.0], [72.6, 365621.0], [72.7, 365621.0], [72.8, 365621.0], [72.9, 365621.0], [73.0, 365621.0], [73.1, 365621.0], [73.2, 365621.0], [73.3, 365621.0], [73.4, 365621.0], [73.5, 365621.0], [73.6, 365621.0], [73.7, 365621.0], [73.8, 365621.0], [73.9, 365621.0], [74.0, 365733.0], [74.1, 365733.0], [74.2, 365733.0], [74.3, 365733.0], [74.4, 365733.0], [74.5, 365733.0], [74.6, 365733.0], [74.7, 365733.0], [74.8, 365733.0], [74.9, 365733.0], [75.0, 365733.0], [75.1, 365733.0], [75.2, 365733.0], [75.3, 365733.0], [75.4, 365733.0], [75.5, 365733.0], [75.6, 365733.0], [75.7, 365733.0], [75.8, 365733.0], [75.9, 365733.0], [76.0, 365754.0], [76.1, 365754.0], [76.2, 365754.0], [76.3, 365754.0], [76.4, 365754.0], [76.5, 365754.0], [76.6, 365754.0], [76.7, 365754.0], [76.8, 365754.0], [76.9, 365754.0], [77.0, 365754.0], [77.1, 365754.0], [77.2, 365754.0], [77.3, 365754.0], [77.4, 365754.0], [77.5, 365754.0], [77.6, 365754.0], [77.7, 365754.0], [77.8, 365754.0], [77.9, 365754.0], [78.0, 365821.0], [78.1, 365821.0], [78.2, 365821.0], [78.3, 365821.0], [78.4, 365821.0], [78.5, 365821.0], [78.6, 365821.0], [78.7, 365821.0], [78.8, 365821.0], [78.9, 365821.0], [79.0, 365821.0], [79.1, 365821.0], [79.2, 365821.0], [79.3, 365821.0], [79.4, 365821.0], [79.5, 365821.0], [79.6, 365821.0], [79.7, 365821.0], [79.8, 365821.0], [79.9, 365821.0], [80.0, 365862.0], [80.1, 365862.0], [80.2, 365862.0], [80.3, 365862.0], [80.4, 365862.0], [80.5, 365862.0], [80.6, 365862.0], [80.7, 365862.0], [80.8, 365862.0], [80.9, 365862.0], [81.0, 365862.0], [81.1, 365862.0], [81.2, 365862.0], [81.3, 365862.0], [81.4, 365862.0], [81.5, 365862.0], [81.6, 365862.0], [81.7, 365862.0], [81.8, 365862.0], [81.9, 365862.0], [82.0, 365984.0], [82.1, 365984.0], [82.2, 365984.0], [82.3, 365984.0], [82.4, 365984.0], [82.5, 365984.0], [82.6, 365984.0], [82.7, 365984.0], [82.8, 365984.0], [82.9, 365984.0], [83.0, 365984.0], [83.1, 365984.0], [83.2, 365984.0], [83.3, 365984.0], [83.4, 365984.0], [83.5, 365984.0], [83.6, 365984.0], [83.7, 365984.0], [83.8, 365984.0], [83.9, 365984.0], [84.0, 366019.0], [84.1, 366019.0], [84.2, 366019.0], [84.3, 366019.0], [84.4, 366019.0], [84.5, 366019.0], [84.6, 366019.0], [84.7, 366019.0], [84.8, 366019.0], [84.9, 366019.0], [85.0, 366019.0], [85.1, 366019.0], [85.2, 366019.0], [85.3, 366019.0], [85.4, 366019.0], [85.5, 366019.0], [85.6, 366019.0], [85.7, 366019.0], [85.8, 366019.0], [85.9, 366019.0], [86.0, 366095.0], [86.1, 366095.0], [86.2, 366095.0], [86.3, 366095.0], [86.4, 366095.0], [86.5, 366095.0], [86.6, 366095.0], [86.7, 366095.0], [86.8, 366095.0], [86.9, 366095.0], [87.0, 366095.0], [87.1, 366095.0], [87.2, 366095.0], [87.3, 366095.0], [87.4, 366095.0], [87.5, 366095.0], [87.6, 366095.0], [87.7, 366095.0], [87.8, 366095.0], [87.9, 366095.0], [88.0, 366427.0], [88.1, 366427.0], [88.2, 366427.0], [88.3, 366427.0], [88.4, 366427.0], [88.5, 366427.0], [88.6, 366427.0], [88.7, 366427.0], [88.8, 366427.0], [88.9, 366427.0], [89.0, 366427.0], [89.1, 366427.0], [89.2, 366427.0], [89.3, 366427.0], [89.4, 366427.0], [89.5, 366427.0], [89.6, 366427.0], [89.7, 366427.0], [89.8, 366427.0], [89.9, 366427.0], [90.0, 366522.0], [90.1, 366522.0], [90.2, 366522.0], [90.3, 366522.0], [90.4, 366522.0], [90.5, 366522.0], [90.6, 366522.0], [90.7, 366522.0], [90.8, 366522.0], [90.9, 366522.0], [91.0, 366522.0], [91.1, 366522.0], [91.2, 366522.0], [91.3, 366522.0], [91.4, 366522.0], [91.5, 366522.0], [91.6, 366522.0], [91.7, 366522.0], [91.8, 366522.0], [91.9, 366522.0], [92.0, 366567.0], [92.1, 366567.0], [92.2, 366567.0], [92.3, 366567.0], [92.4, 366567.0], [92.5, 366567.0], [92.6, 366567.0], [92.7, 366567.0], [92.8, 366567.0], [92.9, 366567.0], [93.0, 366567.0], [93.1, 366567.0], [93.2, 366567.0], [93.3, 366567.0], [93.4, 366567.0], [93.5, 366567.0], [93.6, 366567.0], [93.7, 366567.0], [93.8, 366567.0], [93.9, 366567.0], [94.0, 366697.0], [94.1, 366697.0], [94.2, 366697.0], [94.3, 366697.0], [94.4, 366697.0], [94.5, 366697.0], [94.6, 366697.0], [94.7, 366697.0], [94.8, 366697.0], [94.9, 366697.0], [95.0, 366697.0], [95.1, 366697.0], [95.2, 366697.0], [95.3, 366697.0], [95.4, 366697.0], [95.5, 366697.0], [95.6, 366697.0], [95.7, 366697.0], [95.8, 366697.0], [95.9, 366697.0], [96.0, 367054.0], [96.1, 367054.0], [96.2, 367054.0], [96.3, 367054.0], [96.4, 367054.0], [96.5, 367054.0], [96.6, 367054.0], [96.7, 367054.0], [96.8, 367054.0], [96.9, 367054.0], [97.0, 367054.0], [97.1, 367054.0], [97.2, 367054.0], [97.3, 367054.0], [97.4, 367054.0], [97.5, 367054.0], [97.6, 367054.0], [97.7, 367054.0], [97.8, 367054.0], [97.9, 367054.0], [98.0, 583553.0], [98.1, 583553.0], [98.2, 583553.0], [98.3, 583553.0], [98.4, 583553.0], [98.5, 583553.0], [98.6, 583553.0], [98.7, 583553.0], [98.8, 583553.0], [98.9, 583553.0], [99.0, 583553.0], [99.1, 583553.0], [99.2, 583553.0], [99.3, 583553.0], [99.4, 583553.0], [99.5, 583553.0], [99.6, 583553.0], [99.7, 583553.0], [99.8, 583553.0], [99.9, 583553.0]], "isOverall": false, "label": "Coding-Link WebSocket 连接和消息发送", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
        getOptions: function() {
            return {
                series: {
                    points: { show: false }
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimePercentiles'
                },
                xaxis: {
                    tickDecimals: 1,
                    axisLabel: "Percentiles",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Percentile value in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : %x.2 percentile was %y ms"
                },
                selection: { mode: "xy" },
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimePercentiles"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimesPercentiles"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimesPercentiles"), dataset, prepareOverviewOptions(options));
        }
};

/**
 * @param elementId Id of element where we display message
 */
function setEmptyGraph(elementId) {
    $(function() {
        $(elementId).text("No graph series with filter="+seriesFilter);
    });
}

// Response times percentiles
function refreshResponseTimePercentiles() {
    var infos = responseTimePercentilesInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimePercentiles");
        return;
    }
    if (isGraph($("#flotResponseTimesPercentiles"))){
        infos.createGraph();
    } else {
        var choiceContainer = $("#choicesResponseTimePercentiles");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimesPercentiles", "#overviewResponseTimesPercentiles");
        $('#bodyResponseTimePercentiles .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var responseTimeDistributionInfos = {
        data: {"result": {"minY": 1.0, "minX": 364200.0, "maxY": 5.0, "series": [{"data": [[365700.0, 2.0], [364900.0, 4.0], [365300.0, 3.0], [366500.0, 2.0], [364500.0, 2.0], [365600.0, 1.0], [366000.0, 2.0], [366400.0, 1.0], [364800.0, 2.0], [364400.0, 1.0], [365200.0, 1.0], [365100.0, 2.0], [364700.0, 5.0], [364300.0, 1.0], [365500.0, 2.0], [365900.0, 1.0], [364200.0, 4.0], [365000.0, 5.0], [365800.0, 2.0], [365400.0, 3.0], [367000.0, 1.0], [366600.0, 1.0], [364600.0, 1.0], [583500.0, 1.0]], "isOverall": false, "label": "Coding-Link WebSocket 连接和消息发送", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 583500.0, "title": "Response Time Distribution"}},
        getOptions: function() {
            var granularity = this.data.result.granularity;
            return {
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimeDistribution'
                },
                xaxis:{
                    axisLabel: "Response times in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of responses",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                bars : {
                    show: true,
                    barWidth: this.data.result.granularity
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: function(label, xval, yval, flotItem){
                        return yval + " responses for " + label + " were between " + xval + " and " + (xval + granularity) + " ms";
                    }
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimeDistribution"), prepareData(data.result.series, $("#choicesResponseTimeDistribution")), options);
        }

};

// Response time distribution
function refreshResponseTimeDistribution() {
    var infos = responseTimeDistributionInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimeDistribution");
        return;
    }
    if (isGraph($("#flotResponseTimeDistribution"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimeDistribution");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        $('#footerResponseTimeDistribution .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var syntheticResponseTimeDistributionInfos = {
        data: {"result": {"minY": 50.0, "minX": 2.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 50.0, "series": [{"data": [], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [[2.0, 50.0]], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 2.0, "title": "Synthetic Response Times Distribution"}},
        getOptions: function() {
            return {
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendSyntheticResponseTimeDistribution'
                },
                xaxis:{
                    axisLabel: "Response times ranges",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                    tickLength:0,
                    min:-0.5,
                    max:3.5
                },
                yaxis: {
                    axisLabel: "Number of responses",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                bars : {
                    show: true,
                    align: "center",
                    barWidth: 0.25,
                    fill:.75
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: function(label, xval, yval, flotItem){
                        return yval + " " + label;
                    }
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var options = this.getOptions();
            prepareOptions(options, data);
            options.xaxis.ticks = data.result.ticks;
            $.plot($("#flotSyntheticResponseTimeDistribution"), prepareData(data.result.series, $("#choicesSyntheticResponseTimeDistribution")), options);
        }

};

// Response time distribution
function refreshSyntheticResponseTimeDistribution() {
    var infos = syntheticResponseTimeDistributionInfos;
    prepareSeries(infos.data, true);
    if (isGraph($("#flotSyntheticResponseTimeDistribution"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesSyntheticResponseTimeDistribution");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        $('#footerSyntheticResponseTimeDistribution .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var activeThreadsOverTimeInfos = {
        data: {"result": {"minY": 1.0, "minX": 1.76423016E12, "maxY": 26.061224489795926, "series": [{"data": [[1.76423016E12, 26.061224489795926], [1.76423034E12, 1.0]], "isOverall": false, "label": "Coding-Link WebSocket 压测组 - 5并发", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.76423034E12, "title": "Active Threads Over Time"}},
        getOptions: function() {
            return {
                series: {
                    stack: true,
                    lines: {
                        show: true,
                        fill: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of active threads",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 6,
                    show: true,
                    container: '#legendActiveThreadsOverTime'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                selection: {
                    mode: 'xy'
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : At %x there were %y active threads"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesActiveThreadsOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotActiveThreadsOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewActiveThreadsOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Active Threads Over Time
function refreshActiveThreadsOverTime(fixTimestamps) {
    var infos = activeThreadsOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotActiveThreadsOverTime"))) {
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesActiveThreadsOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotActiveThreadsOverTime", "#overviewActiveThreadsOverTime");
        $('#footerActiveThreadsOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var timeVsThreadsInfos = {
        data: {"result": {"minY": 364248.0, "minX": 1.0, "maxY": 583553.0, "series": [{"data": [[33.0, 364768.0], [32.0, 365072.0], [2.0, 365984.0], [35.0, 366522.0], [34.0, 364795.0], [37.0, 366427.0], [36.0, 364292.0], [39.0, 365821.0], [38.0, 364979.0], [41.0, 365166.5], [43.0, 365621.0], [42.0, 366019.0], [45.0, 364914.0], [44.0, 364362.0], [46.0, 365087.0], [49.0, 365754.0], [48.0, 364509.0], [3.0, 365497.0], [50.0, 365104.0], [4.0, 365493.0], [5.0, 364736.0], [6.0, 364998.0], [7.0, 365135.0], [8.0, 364267.0], [9.0, 365060.0], [10.0, 364582.0], [11.0, 365366.0], [12.0, 364248.0], [13.0, 365733.0], [14.0, 365034.0], [16.0, 366214.5], [1.0, 583553.0], [17.0, 366095.0], [18.0, 364783.0], [19.0, 365282.0], [20.0, 364852.0], [21.0, 365571.0], [22.0, 364490.0], [23.0, 364671.0], [24.0, 364808.0], [25.0, 365363.0], [26.0, 364944.0], [27.0, 366697.0], [28.0, 367054.0], [29.0, 364564.0], [30.0, 365406.0], [31.0, 365588.0]], "isOverall": false, "label": "Coding-Link WebSocket 连接和消息发送", "isController": false}, {"data": [[25.560000000000006, 369623.42]], "isOverall": false, "label": "Coding-Link WebSocket 连接和消息发送-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 50.0, "title": "Time VS Threads"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    axisLabel: "Number of active threads",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response times in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: { noColumns: 2,show: true, container: '#legendTimeVsThreads' },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s: At %x.2 active threads, Average response time was %y.2 ms"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesTimeVsThreads"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotTimesVsThreads"), dataset, options);
            // setup overview
            $.plot($("#overviewTimesVsThreads"), dataset, prepareOverviewOptions(options));
        }
};

// Time vs threads
function refreshTimeVsThreads(){
    var infos = timeVsThreadsInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyTimeVsThreads");
        return;
    }
    if(isGraph($("#flotTimesVsThreads"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTimeVsThreads");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTimesVsThreads", "#overviewTimesVsThreads");
        $('#footerTimeVsThreads .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var bytesThroughputOverTimeInfos = {
        data : {"result": {"minY": 0.0, "minX": 1.76423016E12, "maxY": 11753.683333333332, "series": [{"data": [[1.76423016E12, 11753.683333333332], [1.76423034E12, 225.0]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.76423016E12, 0.0], [1.76423034E12, 0.0]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.76423034E12, "title": "Bytes Throughput Over Time"}},
        getOptions : function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity) ,
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Bytes / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendBytesThroughputOverTime'
                },
                selection: {
                    mode: "xy"
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y"
                }
            };
        },
        createGraph : function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesBytesThroughputOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotBytesThroughputOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewBytesThroughputOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Bytes throughput Over Time
function refreshBytesThroughputOverTime(fixTimestamps) {
    var infos = bytesThroughputOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotBytesThroughputOverTime"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesBytesThroughputOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotBytesThroughputOverTime", "#overviewBytesThroughputOverTime");
        $('#footerBytesThroughputOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var responseTimesOverTimeInfos = {
        data: {"result": {"minY": 365257.5102040816, "minX": 1.76423016E12, "maxY": 583553.0, "series": [{"data": [[1.76423016E12, 365257.5102040816], [1.76423034E12, 583553.0]], "isOverall": false, "label": "Coding-Link WebSocket 连接和消息发送", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.76423034E12, "title": "Response Time Over Time"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average response time was %y ms"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Response Times Over Time
function refreshResponseTimeOverTime(fixTimestamps) {
    var infos = responseTimesOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimeOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotResponseTimesOverTime"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimesOverTime", "#overviewResponseTimesOverTime");
        $('#footerResponseTimesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var latenciesOverTimeInfos = {
        data: {"result": {"minY": 365198.12244897964, "minX": 1.76423016E12, "maxY": 583547.0, "series": [{"data": [[1.76423016E12, 365198.12244897964], [1.76423034E12, 583547.0]], "isOverall": false, "label": "Coding-Link WebSocket 连接和消息发送", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.76423034E12, "title": "Latencies Over Time"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response latencies in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendLatenciesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average latency was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesLatenciesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotLatenciesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewLatenciesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Latencies Over Time
function refreshLatenciesOverTime(fixTimestamps) {
    var infos = latenciesOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyLatenciesOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotLatenciesOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesLatenciesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotLatenciesOverTime", "#overviewLatenciesOverTime");
        $('#footerLatenciesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var connectTimeOverTimeInfos = {
        data: {"result": {"minY": 0.0, "minX": 1.76423016E12, "maxY": 4.9E-324, "series": [{"data": [[1.76423016E12, 0.0], [1.76423034E12, 0.0]], "isOverall": false, "label": "Coding-Link WebSocket 连接和消息发送", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.76423034E12, "title": "Connect Time Over Time"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getConnectTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average Connect Time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendConnectTimeOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average connect time was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesConnectTimeOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotConnectTimeOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewConnectTimeOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Connect Time Over Time
function refreshConnectTimeOverTime(fixTimestamps) {
    var infos = connectTimeOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyConnectTimeOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotConnectTimeOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesConnectTimeOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotConnectTimeOverTime", "#overviewConnectTimeOverTime");
        $('#footerConnectTimeOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var responseTimePercentilesOverTimeInfos = {
        data: {"result": {"minY": 364248.0, "minX": 1.76423016E12, "maxY": 583553.0, "series": [{"data": [[1.76423016E12, 367054.0], [1.76423034E12, 583553.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.76423016E12, 366427.0], [1.76423034E12, 583553.0]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.76423016E12, 367054.0], [1.76423034E12, 583553.0]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.76423016E12, 366632.0], [1.76423034E12, 583553.0]], "isOverall": false, "label": "95th percentile", "isController": false}, {"data": [[1.76423016E12, 364248.0], [1.76423034E12, 583553.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.76423016E12, 365087.0], [1.76423034E12, 583553.0]], "isOverall": false, "label": "Median", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.76423034E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true,
                        fill: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Response Time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimePercentilesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Response time was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimePercentilesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimePercentilesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimePercentilesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Response Time Percentiles Over Time
function refreshResponseTimePercentilesOverTime(fixTimestamps) {
    var infos = responseTimePercentilesOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotResponseTimePercentilesOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesResponseTimePercentilesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimePercentilesOverTime", "#overviewResponseTimePercentilesOverTime");
        $('#footerResponseTimePercentilesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var responseTimeVsRequestInfos = {
    data: {"result": {"minY": 364914.0, "minX": 1.0, "maxY": 474768.5, "series": [{"data": [[1.0, 474768.5], [9.0, 364944.0], [5.0, 365135.0], [13.0, 365060.0], [7.0, 364914.0], [14.0, 365361.5]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 14.0, "title": "Response Time Vs Request"}},
    getOptions: function() {
        return {
            series: {
                lines: {
                    show: false
                },
                points: {
                    show: true
                }
            },
            xaxis: {
                axisLabel: "Global number of requests per second",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            yaxis: {
                axisLabel: "Median Response Time in ms",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            legend: {
                noColumns: 2,
                show: true,
                container: '#legendResponseTimeVsRequest'
            },
            selection: {
                mode: 'xy'
            },
            grid: {
                hoverable: true // IMPORTANT! this is needed for tooltip to work
            },
            tooltip: true,
            tooltipOpts: {
                content: "%s : Median response time at %x req/s was %y ms"
            },
            colors: ["#9ACD32", "#FF6347"]
        };
    },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesResponseTimeVsRequest"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotResponseTimeVsRequest"), dataset, options);
        // setup overview
        $.plot($("#overviewResponseTimeVsRequest"), dataset, prepareOverviewOptions(options));

    }
};

// Response Time vs Request
function refreshResponseTimeVsRequest() {
    var infos = responseTimeVsRequestInfos;
    prepareSeries(infos.data);
    if (isGraph($("#flotResponseTimeVsRequest"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimeVsRequest");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimeVsRequest", "#overviewResponseTimeVsRequest");
        $('#footerResponseRimeVsRequest .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var latenciesVsRequestInfos = {
    data: {"result": {"minY": 364910.0, "minX": 1.0, "maxY": 474764.0, "series": [{"data": [[1.0, 474764.0], [9.0, 364940.0], [5.0, 365130.0], [13.0, 365055.0], [7.0, 364910.0], [14.0, 365359.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 14.0, "title": "Latencies Vs Request"}},
    getOptions: function() {
        return{
            series: {
                lines: {
                    show: false
                },
                points: {
                    show: true
                }
            },
            xaxis: {
                axisLabel: "Global number of requests per second",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            yaxis: {
                axisLabel: "Median Latency in ms",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            legend: { noColumns: 2,show: true, container: '#legendLatencyVsRequest' },
            selection: {
                mode: 'xy'
            },
            grid: {
                hoverable: true // IMPORTANT! this is needed for tooltip to work
            },
            tooltip: true,
            tooltipOpts: {
                content: "%s : Median Latency time at %x req/s was %y ms"
            },
            colors: ["#9ACD32", "#FF6347"]
        };
    },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesLatencyVsRequest"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotLatenciesVsRequest"), dataset, options);
        // setup overview
        $.plot($("#overviewLatenciesVsRequest"), dataset, prepareOverviewOptions(options));
    }
};

// Latencies vs Request
function refreshLatenciesVsRequest() {
        var infos = latenciesVsRequestInfos;
        prepareSeries(infos.data);
        if(isGraph($("#flotLatenciesVsRequest"))){
            infos.createGraph();
        }else{
            var choiceContainer = $("#choicesLatencyVsRequest");
            createLegend(choiceContainer, infos);
            infos.createGraph();
            setGraphZoomable("#flotLatenciesVsRequest", "#overviewLatenciesVsRequest");
            $('#footerLatenciesVsRequest .legendColorBox > div').each(function(i){
                $(this).clone().prependTo(choiceContainer.find("li").eq(i));
            });
        }
};

var hitsPerSecondInfos = {
        data: {"result": {"minY": 0.8333333333333334, "minX": 1.76422974E12, "maxY": 0.8333333333333334, "series": [{"data": [[1.76422974E12, 0.8333333333333334]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.76422974E12, "title": "Hits Per Second"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of hits / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendHitsPerSecond"
                },
                selection: {
                    mode : 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y.2 hits/sec"
                }
            };
        },
        createGraph: function createGraph() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesHitsPerSecond"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotHitsPerSecond"), dataset, options);
            // setup overview
            $.plot($("#overviewHitsPerSecond"), dataset, prepareOverviewOptions(options));
        }
};

// Hits per second
function refreshHitsPerSecond(fixTimestamps) {
    var infos = hitsPerSecondInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if (isGraph($("#flotHitsPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesHitsPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotHitsPerSecond", "#overviewHitsPerSecond");
        $('#footerHitsPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var codesPerSecondInfos = {
        data: {"result": {"minY": 0.016666666666666666, "minX": 1.76423016E12, "maxY": 0.8166666666666667, "series": [{"data": [[1.76423016E12, 0.8166666666666667], [1.76423034E12, 0.016666666666666666]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.76423034E12, "title": "Codes Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of responses / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendCodesPerSecond"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "Number of Response Codes %s at %x was %y.2 responses / sec"
                }
            };
        },
    createGraph: function() {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesCodesPerSecond"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotCodesPerSecond"), dataset, options);
        // setup overview
        $.plot($("#overviewCodesPerSecond"), dataset, prepareOverviewOptions(options));
    }
};

// Codes per second
function refreshCodesPerSecond(fixTimestamps) {
    var infos = codesPerSecondInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotCodesPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesCodesPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotCodesPerSecond", "#overviewCodesPerSecond");
        $('#footerCodesPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var transactionsPerSecondInfos = {
        data: {"result": {"minY": 0.016666666666666666, "minX": 1.76423016E12, "maxY": 0.8166666666666667, "series": [{"data": [[1.76423016E12, 0.8166666666666667], [1.76423034E12, 0.016666666666666666]], "isOverall": false, "label": "Coding-Link WebSocket 连接和消息发送-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.76423034E12, "title": "Transactions Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of transactions / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendTransactionsPerSecond"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y transactions / sec"
                }
            };
        },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesTransactionsPerSecond"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotTransactionsPerSecond"), dataset, options);
        // setup overview
        $.plot($("#overviewTransactionsPerSecond"), dataset, prepareOverviewOptions(options));
    }
};

// Transactions per second
function refreshTransactionsPerSecond(fixTimestamps) {
    var infos = transactionsPerSecondInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyTransactionsPerSecond");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotTransactionsPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTransactionsPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTransactionsPerSecond", "#overviewTransactionsPerSecond");
        $('#footerTransactionsPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var totalTPSInfos = {
        data: {"result": {"minY": 0.016666666666666666, "minX": 1.76423016E12, "maxY": 0.8166666666666667, "series": [{"data": [[1.76423016E12, 0.8166666666666667], [1.76423034E12, 0.016666666666666666]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.76423034E12, "title": "Total Transactions Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of transactions / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendTotalTPS"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y transactions / sec"
                },
                colors: ["#9ACD32", "#FF6347"]
            };
        },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesTotalTPS"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotTotalTPS"), dataset, options);
        // setup overview
        $.plot($("#overviewTotalTPS"), dataset, prepareOverviewOptions(options));
    }
};

// Total Transactions per second
function refreshTotalTPS(fixTimestamps) {
    var infos = totalTPSInfos;
    // We want to ignore seriesFilter
    prepareSeries(infos.data, false, true);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotTotalTPS"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTotalTPS");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTotalTPS", "#overviewTotalTPS");
        $('#footerTotalTPS .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

// Collapse the graph matching the specified DOM element depending the collapsed
// status
function collapse(elem, collapsed){
    if(collapsed){
        $(elem).parent().find(".fa-chevron-up").removeClass("fa-chevron-up").addClass("fa-chevron-down");
    } else {
        $(elem).parent().find(".fa-chevron-down").removeClass("fa-chevron-down").addClass("fa-chevron-up");
        if (elem.id == "bodyBytesThroughputOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshBytesThroughputOverTime(true);
            }
            document.location.href="#bytesThroughputOverTime";
        } else if (elem.id == "bodyLatenciesOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshLatenciesOverTime(true);
            }
            document.location.href="#latenciesOverTime";
        } else if (elem.id == "bodyCustomGraph") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshCustomGraph(true);
            }
            document.location.href="#responseCustomGraph";
        } else if (elem.id == "bodyConnectTimeOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshConnectTimeOverTime(true);
            }
            document.location.href="#connectTimeOverTime";
        } else if (elem.id == "bodyResponseTimePercentilesOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimePercentilesOverTime(true);
            }
            document.location.href="#responseTimePercentilesOverTime";
        } else if (elem.id == "bodyResponseTimeDistribution") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimeDistribution();
            }
            document.location.href="#responseTimeDistribution" ;
        } else if (elem.id == "bodySyntheticResponseTimeDistribution") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshSyntheticResponseTimeDistribution();
            }
            document.location.href="#syntheticResponseTimeDistribution" ;
        } else if (elem.id == "bodyActiveThreadsOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshActiveThreadsOverTime(true);
            }
            document.location.href="#activeThreadsOverTime";
        } else if (elem.id == "bodyTimeVsThreads") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTimeVsThreads();
            }
            document.location.href="#timeVsThreads" ;
        } else if (elem.id == "bodyCodesPerSecond") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshCodesPerSecond(true);
            }
            document.location.href="#codesPerSecond";
        } else if (elem.id == "bodyTransactionsPerSecond") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTransactionsPerSecond(true);
            }
            document.location.href="#transactionsPerSecond";
        } else if (elem.id == "bodyTotalTPS") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTotalTPS(true);
            }
            document.location.href="#totalTPS";
        } else if (elem.id == "bodyResponseTimeVsRequest") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimeVsRequest();
            }
            document.location.href="#responseTimeVsRequest";
        } else if (elem.id == "bodyLatenciesVsRequest") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshLatenciesVsRequest();
            }
            document.location.href="#latencyVsRequest";
        }
    }
}

/*
 * Activates or deactivates all series of the specified graph (represented by id parameter)
 * depending on checked argument.
 */
function toggleAll(id, checked){
    var placeholder = document.getElementById(id);

    var cases = $(placeholder).find(':checkbox');
    cases.prop('checked', checked);
    $(cases).parent().children().children().toggleClass("legend-disabled", !checked);

    var choiceContainer;
    if ( id == "choicesBytesThroughputOverTime"){
        choiceContainer = $("#choicesBytesThroughputOverTime");
        refreshBytesThroughputOverTime(false);
    } else if(id == "choicesResponseTimesOverTime"){
        choiceContainer = $("#choicesResponseTimesOverTime");
        refreshResponseTimeOverTime(false);
    }else if(id == "choicesResponseCustomGraph"){
        choiceContainer = $("#choicesResponseCustomGraph");
        refreshCustomGraph(false);
    } else if ( id == "choicesLatenciesOverTime"){
        choiceContainer = $("#choicesLatenciesOverTime");
        refreshLatenciesOverTime(false);
    } else if ( id == "choicesConnectTimeOverTime"){
        choiceContainer = $("#choicesConnectTimeOverTime");
        refreshConnectTimeOverTime(false);
    } else if ( id == "choicesResponseTimePercentilesOverTime"){
        choiceContainer = $("#choicesResponseTimePercentilesOverTime");
        refreshResponseTimePercentilesOverTime(false);
    } else if ( id == "choicesResponseTimePercentiles"){
        choiceContainer = $("#choicesResponseTimePercentiles");
        refreshResponseTimePercentiles();
    } else if(id == "choicesActiveThreadsOverTime"){
        choiceContainer = $("#choicesActiveThreadsOverTime");
        refreshActiveThreadsOverTime(false);
    } else if ( id == "choicesTimeVsThreads"){
        choiceContainer = $("#choicesTimeVsThreads");
        refreshTimeVsThreads();
    } else if ( id == "choicesSyntheticResponseTimeDistribution"){
        choiceContainer = $("#choicesSyntheticResponseTimeDistribution");
        refreshSyntheticResponseTimeDistribution();
    } else if ( id == "choicesResponseTimeDistribution"){
        choiceContainer = $("#choicesResponseTimeDistribution");
        refreshResponseTimeDistribution();
    } else if ( id == "choicesHitsPerSecond"){
        choiceContainer = $("#choicesHitsPerSecond");
        refreshHitsPerSecond(false);
    } else if(id == "choicesCodesPerSecond"){
        choiceContainer = $("#choicesCodesPerSecond");
        refreshCodesPerSecond(false);
    } else if ( id == "choicesTransactionsPerSecond"){
        choiceContainer = $("#choicesTransactionsPerSecond");
        refreshTransactionsPerSecond(false);
    } else if ( id == "choicesTotalTPS"){
        choiceContainer = $("#choicesTotalTPS");
        refreshTotalTPS(false);
    } else if ( id == "choicesResponseTimeVsRequest"){
        choiceContainer = $("#choicesResponseTimeVsRequest");
        refreshResponseTimeVsRequest();
    } else if ( id == "choicesLatencyVsRequest"){
        choiceContainer = $("#choicesLatencyVsRequest");
        refreshLatenciesVsRequest();
    }
    var color = checked ? "black" : "#818181";
    if(choiceContainer != null) {
        choiceContainer.find("label").each(function(){
            this.style.color = color;
        });
    }
}

