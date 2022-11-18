## Custom Config

Use this under "Extras -> Configuration..." to get nice presets for both the
light and dark color schemes of the component diagram on app.diagrams.net .

```json
{
    "customPresetColors":[
        "506e3f",
        "8a6c32",
        "425f85",
        "226b6b",
        "534270",
        "8BBF6E",
        "D1B254",
        "6891CF",
        "3BBABA",
        "B387D0"
    ],
    "customColorSchemes":[
        [
            null,
            {
                "font":"#506e3f",
                "title":"clientGreen (text)"
            },
            {
                "font":"#8a6c32",
                "title":"resultsYellow (text)"
            },
            {
                "font":"#425f85",
                "title":"workerBlue (text)"
            },
            null,
            {
                "stroke":"#506e3f",
                "font":"#506e3f",
                "border":"1px dashed",
                "title":"clientGreen (border)"
            },
            {
                "stroke":"#8a6c32",
                "font":"#8a6c32",
                "border":"1px dashed",
                "title":"resultsYellow (border)"
            },
            {
                "stroke":"#425f85",
                "font":"#425f85",
                "border":"1px dashed",
                "title":"workerBlue (border)"
            }
        ],
        [
            null,
            {
                "font":"#226b6b",
                "title":"brokerCyan (text)"
            },
            {
                "font":"#534270",
                "title":"licensePurple (text)"
            },
            {
                "fill":"#dae8fc",
                "stroke":"#6c8ebf"
            },
            null,
            {
                "stroke":"#226b6b",
                "font":"#226b6b",
                "border":"1px dashed",
                "title":"brokerCyan (border)"
            },
            {
                "stroke":"#534270",
                "font":"#534270",
                "border":"1px dashed",
                "title":"licensePurple (border)"
            },
            {
                "fill":"#d5e8d4",
                "stroke":"#82b366"
            }
        ]
    ],
    "styles":[
        {},
        {
            "commonStyle": {
                "fontColor": "#e6e6e6",
                "fillColor": "#e6e6e6",
                "strokeColor": "#e6e6e6"
            },
            "edgeStyle": {
                "fontColor": "#e6e6e6",
                "fillColor": "#e6e6e6",
                "strokeColor": "#e6e6e6"
            },
            "vertexStyle": {
                "fontColor": "#e6e6e6",
                "fillColor": "#e6e6e6",
                "strokeColor": "#e6e6e6"
            },
            "graph": {
                "background": "#2e303e"
            }
        },
        {
            "commonStyle": {
                "fontColor": "#333333",
                "fillColor": "#333333",
                "strokeColor": "#333333"
            },
            "edgeStyle": {
                "fontColor": "#333333",
                "fillColor": "#333333",
                "strokeColor": "#333333"
            },
            "vertexStyle": {
                "fontColor": "#333333",
                "fillColor": "#333333",
                "strokeColor": "#333333"
            },
            "graph": {
                "background": "#FFFFFF"
            }
        }
    ]
}
```

## Copied Item Styles

All items from here on out are copied from the app and served as reference for
constructing the above configuration.

### Middle Style Options (usable in both light and dark)

#### Shape Style

```toml
sketch=0;
shadow=0;
dashed=0;
html=1;
strokeColor=none;
fillColor=#777777;
labelPosition=center;
verticalLabelPosition=bottom;
verticalAlign=top;
outlineConnect=0;
align=center;
# shape=mxgraph.office.databases.database;
```

#### Arrow Style

```toml
endArrow=classic;
html=1;
rounded=0;
fontSize=10;
fontColor=#777777;
strokeColor=#777777;
endSize=4;
startSize=4;
targetPerimeterSpacing=3;
jumpStyle=gap;
strokeWidth=1;
```

#### Edge Label Style

```toml
edgeLabel;
resizable=0;
html=1;
align=center;
verticalAlign=middle;
fontSize=8;
fontColor=#777777;
fillColor=#777777;
labelBackgroundColor=none;
fontStyle=1
```

#### Text Style

```toml
text;
html=1;
strokeColor=none;
fillColor=none;
align=center;
verticalAlign=middle;
whiteSpace=wrap;
rounded=0;
fontStyle=1;
fontColor=#777777;
fontSize=10;
```

#### Middle / Light BG Accent Colors

```toml
clientGreen=#506e3f;
resultsYellow=#8a6c32;
workerBlue=#425f85;
brokerCyan=#226b6b;
licensePurple=#534270;
```

#### Dark BG Accent Colors

```toml
clientGreen=#8BBF6E;
resultsYellow=#D1B254;
workerBlue=#6891CF;
brokerCyan=#3BBABA;
licensePurple=#B387D0;
```

## Background Colors

```toml
lightBG=#FFFFFF;
darkBG=#2e303e;
```

## Alternate Foreground Colors

```toml
lightBG=#FFFFFF;
darkBG=#2e303e;
```

## Swap MD images

Use `#only-light` and `#only-dark` suffixes to swap images:

```md
![Image title](https://dummyimage.com/600x400/f5f5f5/aaaaaa#only-light)
![Image title](https://dummyimage.com/600x400/21222c/d5d7e2#only-dark)
```

## Currently Loaded Diagram Config

```json
{
  "language":"",
  "configVersion":null,
  "customFonts":[
    {
      "name":"Permanent Marker",
      "url":"https://fonts.googleapis.com/css?family=Permanent+Marker"
    }
  ],
  "libraries":"general;flowchart;office",
  "customLibraries":["L.scratchpad"],
  "plugins":[],
  "recentColors":[
    "F0F0F0",
    "CCCCCC",
    "FFFFFF",
    "2e303e",
    "808080",
    "506E3F",
    "226B6B",
    "546B24",
    "759632",
    "962C2C",
    "8A6C32"
  ],
  "formatWidth":"240",
  "createTarget":false,
  "pageFormat":{
    "x":0,
    "y":0,
    "width":400,
    "height":300
  },
  "search":true,
  "showStartScreen":true,
  "gridColor":"#d0d0d0",
  "darkGridColor":"#6e6e6e",
  "autosave":true,
  "resizeImages":null,
  "openCounter":28,
  "version":18,
  "unit":1,
  "isRulerOn":true,
  "ui":"dark",
  "closeDesktopFooter":1668712118094
}
```

## Default Diagram Config

```json
{
  "defaultFonts":[
    "Helvetica",
    "Verdana",
    "Times New Roman",
    "Garamond",
    "Comic Sans MS",
    "Courier New",
    "Georgia",
    "Lucida Console",
    "Tahoma"
  ],
  "presetColors":[
    "E6D0DE",
    "CDA2BE",
    "B5739D",
    "E1D5E7",
    "C3ABD0",
    "A680B8",
    "D4E1F5",
    "A9C4EB",
    "7EA6E0",
    "D5E8D4",
    "9AC7BF",
    "67AB9F",
    "D5E8D4",
    "B9E0A5",
    "97D077",
    "FFF2CC",
    "FFE599",
    "FFD966",
    "FFF4C3",
    "FFCE9F",
    "FFB570",
    "F8CECC",
    "F19C99",
    "EA6B66"
  ],
  "defaultColorSchemes":[
    [
      null,
      {
        "fill":"#f5f5f5",
        "stroke":"#666666"
      },
      {
        "fill":"#dae8fc",
        "stroke":"#6c8ebf"
      },
      {
        "fill":"#d5e8d4",
        "stroke":"#82b366"
      },
      {
        "fill":"#ffe6cc",
        "stroke":"#d79b00"
      },
      {
        "fill":"#fff2cc",
        "stroke":"#d6b656"
      },
      {
        "fill":"#f8cecc",
        "stroke":"#b85450"
      },
      {
        "fill":"#e1d5e7",
        "stroke":"#9673a6"
      }
    ],
    [
      null,
      {
        "fill":"#f5f5f5",
        "stroke":"#666666",
        "gradient":"#b3b3b3"
      },
      {
        "fill":"#dae8fc",
        "stroke":"#6c8ebf",
        "gradient":"#7ea6e0"
      },
      {
        "fill":"#d5e8d4",
        "stroke":"#82b366",
        "gradient":"#97d077"
      },
      {
        "fill":"#ffcd28",
        "stroke":"#d79b00",
        "gradient":"#ffa500"
      },
      {
        "fill":"#fff2cc",
        "stroke":"#d6b656",
        "gradient":"#ffd966"
      },
      {
        "fill":"#f8cecc",
        "stroke":"#b85450",
        "gradient":"#ea6b66"
      },
      {
        "fill":"#e6d0de",
        "stroke":"#996185",
        "gradient":"#d5739d"
      }
    ],
    [
      null,
      {
        "fill":"#eeeeee",
        "stroke":"#36393d"
      },
      {
        "fill":"#f9f7ed",
        "stroke":"#36393d"
      },
      {
        "fill":"#ffcc99",
        "stroke":"#36393d"
      },
      {
        "fill":"#cce5ff",
        "stroke":"#36393d"
      },
      {
        "fill":"#ffff88",
        "stroke":"#36393d"
      },
      {
        "fill":"#cdeb8b",
        "stroke":"#36393d"
      },
      {
        "fill":"#ffcccc",
        "stroke":"#36393d"
      }
    ]
  ],
  "defaultColors":[
    "none",
    "FFFFFF",
    "E6E6E6",
    "CCCCCC",
    "B3B3B3",
    "999999",
    "808080",
    "666666",
    "4D4D4D",
    "333333",
    "1A1A1A",
    "000000",
    "FFCCCC",
    "FFE6CC",
    "FFFFCC",
    "E6FFCC",
    "CCFFCC",
    "CCFFE6",
    "CCFFFF",
    "CCE5FF",
    "CCCCFF",
    "E5CCFF",
    "FFCCFF",
    "FFCCE6",
    "FF9999",
    "FFCC99",
    "FFFF99",
    "CCFF99",
    "99FF99",
    "99FFCC",
    "99FFFF",
    "99CCFF",
    "9999FF",
    "CC99FF",
    "FF99FF",
    "FF99CC",
    "FF6666",
    "FFB366",
    "FFFF66",
    "B3FF66",
    "66FF66",
    "66FFB3",
    "66FFFF",
    "66B2FF",
    "6666FF",
    "B266FF",
    "FF66FF",
    "FF66B3",
    "FF3333",
    "FF9933",
    "FFFF33",
    "99FF33",
    "33FF33",
    "33FF99",
    "33FFFF",
    "3399FF",
    "3333FF",
    "9933FF",
    "FF33FF",
    "FF3399",
    "FF0000",
    "FF8000",
    "FFFF00",
    "80FF00",
    "00FF00",
    "00FF80",
    "00FFFF",
    "007FFF",
    "0000FF",
    "7F00FF",
    "FF00FF",
    "FF0080",
    "CC0000",
    "CC6600",
    "CCCC00",
    "66CC00",
    "00CC00",
    "00CC66",
    "00CCCC",
    "0066CC",
    "0000CC",
    "6600CC",
    "CC00CC",
    "CC0066",
    "990000",
    "994C00",
    "999900",
    "4D9900",
    "009900",
    "00994D",
    "009999",
    "004C99",
    "000099",
    "4C0099",
    "990099",
    "99004D",
    "660000",
    "663300",
    "666600",
    "336600",
    "006600",
    "006633",
    "006666",
    "003366",
    "000066",
    "330066",
    "660066",
    "660033",
    "330000",
    "331A00",
    "333300",
    "1A3300",
    "003300",
    "00331A",
    "003333",
    "001933",
    "000033",
    "190033",
    "330033",
    "33001A"
  ],
  "defaultVertexStyle":{

  },
  "defaultEdgeStyle":{
    "edgeStyle":"orthogonalEdgeStyle",
    "rounded":"0",
    "jettySize":"auto",
    "orthogonalLoop":"1"
  },
  "defaultLibraries":"general;images;uml;er;bpmn;flowchart;basic;arrows2",
  "defaultCustomLibraries":[

  ],
  "defaultMacroParameters":{
    "border":false,
    "toolbarStyle":"inline"
  },
  "css":"",
  "fontCss":"",
  "thumbWidth":46,
  "thumbHeight":46,
  "emptyDiagramXml":"<mxGraphModel><root><mxCell id='0'/><mxCell id='1' parent='0'/></root></mxGraphModel>",
  "emptyLibraryXml":"<mxlibrary>[]</mxlibrary>",
  "defaultEdgeLength":80
}
```
