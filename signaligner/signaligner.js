// The webgl rendering context and the main canvas
let G_glCanvas = null;
let G_glCtx = null;
let G_canvasWidth = null;
let G_canvasHeight = null;

// The 2D rendering context and the canvas for text
let G_textCtx = null;
let G_textCanvas = null;
let G_textCtxOffscreen = null;
let G_textCanvasOffscreen = null;

// Shader information
let G_programInfo = null;
let G_uGlobalColor = null;
let G_uOffset = null;
let G_uScale = null;

// The current dataset, session, mturk and userId
let G_dataset = null;
let G_session = null;
let G_run = null;

// The buffer used by quads
let G_quadBuffer = null;

// Information about a tile of data's state
let G_tileData = null;

// G_session but specifically for labels
let G_sessLabelId = null;

// Whether some elements are currently being fetched
let G_fetchingLabels = false;
let G_fetchingLabelsLocal = false;
let G_fetchingConfig = false;

// Constant variables to track who is creating the labels
const SOURCE_PLAYER = 'Player';
const SOURCE_EXPERT = 'Expert';
const SOURCE_MTURK = 'Mturk';
const SOURCE_ALGO = 'Algo';
const SOURCE_TRUTH = 'Truth';
const SOURCE_NOTES = 'Notes';

// Variables to track the mode in which the tool is running
const MODE_MTURK = 'MTURK';
const MODE_EXPERT = 'EXPERT';



// mturk-related variables

// Dictionary of MTurk dataset order (key = current dataset, value = next dataset)
const MTURK_DATASET_ORDER = {
    "SleepSegment1" : "SleepSegment2"
};

const MTURK_TUTORIAL_DATASETS = ["SleepSegment1"];
const MTURK_CHALLENGE_DATASETS = ["SleepSegment2"];
const MTURK_TUTORIAL_MIN_SCORE = 90;
const MTURK_CHALLENGE_MAX_SUBMISSIONS = 3;

let G_mturkSubmissions = 0;

let G_mturkState = null;
let G_mturkHelpModalVisitCount = 0;



// mode information
const MC_MODE = 'MODE';
const MC_HIDE_REMOTE_PLAYER_LABELS = 'HIDE_REMOTE_PLAYER_LABELS';
const MC_HIDE_REMOTE_ALGO_LABELS = 'HIDE_REMOTE_ALGO_LABELS';
const MC_HIDE_REMOTE_MTURK = 'HIDE_REMOTE_MTURK';
const MC_HIDE_REMOTE_EXPERT = 'HIDE_REMOTE_EXPERT';
const MC_HIDE_GROUND_TRUTH_LABELS = 'HIDE_GROUND_TRUTH_LABELS';
const MC_HIDE_IMPORT_DATA_BUTTON = 'HIDE_IMPORT_DATA_BUTTON';

let G_modeConfig = {};
G_modeConfig[MC_MODE] = '';
G_modeConfig[MC_HIDE_REMOTE_PLAYER_LABELS] = true;
G_modeConfig[MC_HIDE_REMOTE_ALGO_LABELS] = true;
G_modeConfig[MC_HIDE_REMOTE_MTURK] = true;
G_modeConfig[MC_HIDE_REMOTE_EXPERT] = true;
G_modeConfig[MC_HIDE_GROUND_TRUTH_LABELS] = true;
G_modeConfig[MC_HIDE_IMPORT_DATA_BUTTON] = true;

// the following line will be relaced by mode config customizations, if any
(MODECONFIG)



// Array of labels made by the player
let G_labelsLocalOld = [];
let G_labelsLocal = [];

// Array of labels from the server
let G_labelsRemoteYours = null;
let G_labelsRemoteNotes = [];
let G_labelsRemoteOtherPlayer = [];
let G_labelsRemoteOtherAlgo = [];
let G_labelsRemoteGroundTruth = null;

// Array of names of all sessions
let G_sessions = [];

// State of ground truth score
let G_groundTruthScore = null;

// Label cycle information
const MAX_REMOTE_LABEL_DISPLAY = 5;
let G_labelsRemoteStartIndexPlayer = 0;
let G_labelsRemoteStartIndexAlgo = 0;

// The colors of each label type
let G_labelColors = null;

// The height and y position of the signal
let G_signalHeight = null;
let G_signalY = null;

// Mouse state variables
let G_mousePos = null;
let G_mouseDown = false;
let G_mouseMoved = false;
let G_mouseAction = null;
let G_mouseAdjust = null;

const MOUSE_CREATE_LABEL = "MOUSE_CREATE_LABEL";
const MOUSE_ADJUST_LABEL = "MOUSE_ADJUST_LABEL";
const MOUSE_PAN = "MOUSE_PAN";
const MOUSE_COPY_LABEL = "MOUSE_COPY_LABEL";
const MOUSE_COPY_LABEL_COMPLETE = "MOUSE_COPY_LABEL_COMPLETE";

// Keyboard state tracking
var G_shiftDown = false;
var G_controlDown = false;
var G_metaDown = false;
var G_altDown = false;
var G_slowPanZoomDown = false;
var G_pleftDown = false;
var G_prightDown = false;
var G_zoutDown = false;
var G_zinDown = false;

// magnitude of Y
let G_magnitude = null;
let G_magnitudeMin = null;
let G_magnitudeMax = null;
const MAGNITUDE_SCALE_RANGE = 4;

let G_components = null;

// The cache max for the G_tileData map.
let G_cacheMax = 500;

// dataset configuration as downloaded for this dataset
// Should contain a definition for
//  - tile_size: the number of data points in a tile
//  - tile_subsample: the coefficient between zoom levels
//  - zoom_max: the maximum zoom level
//  - length: the total number of raw points in this dataset
//  - labels: the types of labels in this dataset (should be a list of "labels" which conatain a name and color)
//  - start_time_ms: the time data starts at, in milliseconds
//  - sample_rate: the Hertz the data is sampled at
let G_config = null;

// Tooltip information when hovering over a small gap indicator
const TT_SUMMARY_WITH_GAP = "Labels summarized, include gap";
const TT_SUMMARY_WITHOUT_GAP = "Labels summarized";
const TT_DELAY_XYZ = 1000;
const TT_DELAY_SUMMARY = 0;
let G_tooltipInfo = null;
let G_tooltipDelayFromTime = 0;

// Colors for various elements
const COLOR_LABEL_X     = [0.45, 0.45, 0.45];
const COLOR_SMALL_LABEL = [0.30, 0.30, 0.40];
const COLOR_SMALL_GAP   = [0.50, 0.30, 0.30];

const COLOR_SIGNAL_COUNT = 3;
const COLOR_SIGNAL_X     = [[0.80, 0.20, 0.20], [0.80, 0.40, 0.20], [0.60, 0.60, 0.10]];
const COLOR_SIGNAL_Y     = [[0.20, 0.80, 0.20], [0.20, 0.80, 0.40], [0.10, 0.60, 0.60]];
const COLOR_SIGNAL_Z     = [[0.20, 0.20, 0.80], [0.40, 0.20, 0.80], [0.60, 0.10, 0.60]];

const COLOR_TIMELINE    = [0.20, 0.20, 0.20];
const COLOR_TIMELINE_TEXT  = [0.47, 0.47, 0.47];
const COLORH_TIMELINE_TEXT = "#bbbbbb";

const COLOR_TOOLTIP = "#555";

const COLOR_CANVAS_BACKGROUND = [0.0, 0.0, 0.0];

const TILE_STATUS_PENDING = "pending";
const TILE_STATUS_RESPONDED = "responded";
const TILE_STATUS_ERROR = "error";
const TILE_STATUS_READY = "ready";

const LIGHT_MODE_COLOR_MAP = {
    border: [0.905, 0.905, 0.905],
    background: [0.900, 0.900, 0.900],
    yaxis: [0.0, 0.0, 0.0],
    yaxisText: "#000000",
    xaxis: [0.5, 0.5, 0.5]
};

const DARK_MODE_COLOR_MAP = {
    border: [0.025, 0.025, 0.025],
    background: [0.050, 0.050, 0.050],
    yaxis: [1.0, 1.0, 1.0],
    yaxisText: "#ffffff",
    xaxis: [0.5, 0.5, 0.5]
};

let G_modeColorMap = null;

// Saves the position from which the double click zoom-in happened.
let G_zoomInHistory = null;

// Defaults and constants
var ZOOM_INT_MAX_LEVEL = 99;
var XPAN_AMOUNT = 40;

var DEFAULT_ZOOM = null;
var DEFAULT_XSCALE = null;

// Zoom/pan information
var G_zoomUI = null;
var G_zoomWheel = null;
var G_zoomLevel = null;
var G_zoomLevelIntermediate = null;

// The offset and scale of the x axis of the signal
var G_xOffset = null;
var G_xScale = null;

// Timeout for the most recent call to updateUrlParameters
var G_urlUpdateTimeout = null;

// Map for key events (in uppercase) and their actions
var G_keyMap = new Map();
G_keyMap.set("PAN_LEFT", ["ARROWLEFT", "A"]);
G_keyMap.set("PAN_RIGHT", ["ARROWRIGHT", "D"]);
G_keyMap.set("ZOOM_IN", ["ARROWUP", "W"]);
G_keyMap.set("ZOOM_OUT", ["ARROWDOWN", "S"]);
G_keyMap.set("PREVIOUS_LABEL", [","]);
G_keyMap.set("NEXT_LABEL", ["."]);
G_keyMap.set("CYCLE", ["C"]);
G_keyMap.set("DOUBLE_Y_MAG", ["J"]);
G_keyMap.set("RESET_Y_MAG", ["K"]);
G_keyMap.set("HALVE_Y_MAG", ["L"]);
G_keyMap.set("RETURN_BACK", ["B"]);

const KEY_SLOW_PANZOOM = ["`", "/"];

const TINY_SIZE = 0.001;
const REALLY_TINY_SIZE = 0.00025;

const TIMELINE_HEIGHT = 0.05;

const LABEL_HEIGHT = 0.04;
const LABEL_GAP = 0.005;
const LABEL_INDICATOR = 0.01;
const LABEL_INDICATOR_OVERHANG = 0.001;

const NAME_OFFSET = 0.01;
const NAME_WIDTH = 0.08;
const TEXT_INSET = 0.004;

const Y_AXIS_POS = NAME_WIDTH + NAME_OFFSET - REALLY_TINY_SIZE;
const Y_AXIS_TICK = 0.01;
const X_OFFSET = Y_AXIS_POS + 0.001;

const IS_FIREFOX = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;

const WEEKDAY = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

let G_startDate = null;
let G_startDayIdx = null;

window.addEventListener('load', startup, false);

const VS_SOURCE = `
    uniform vec2 uOffset;
    uniform vec2 uScale;
    attribute vec2 aVertexPosition;
    void main() {
        gl_Position = vec4(((uOffset + uScale * aVertexPosition) - 0.5) * 2.0, 0.0, 1.0);
    }
`;

const FS_SOURCE = `
    #ifdef GL_ES
        precision highp float;
    #endif
    uniform vec4 uGlobalColor;
    void main() {
        gl_FragColor = uGlobalColor;
    }
`;

function getXScale() {
    return DEFAULT_XSCALE * Math.pow(Math.pow(G_config.tile_subsample, 1.0 / (ZOOM_INT_MAX_LEVEL + 1)), (ZOOM_INT_MAX_LEVEL - G_zoomLevelIntermediate) + 1);
}

// Handle blur of window
function blurHandler(evt) {
    clearMouse();
    clearKeys();
}

// Handle when the mouse button is down
function mouseDownHandler(evt) {
    if (evt.target !== G_glCanvas) {
        // ignore events here that are not for the canvas (for example, the XYZ checkboxes)
        return;
    }

    evt.preventDefault();

    if (G_fetchingLabelsLocal || G_fetchingConfig) {
        return;
    }

    var mpos = getWorldMousePos(evt, G_glCanvas);
    var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);

    if (mpos.x <= 0 || 1 <= mpos.x || mpos.y <= 0 || 1 <= mpos.y) {
        return;
    }

    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    G_mouseDown = smpx * zoom;
    G_mouseMoved = false;
    if (G_mouseAdjust) {
        G_mouseAction = MOUSE_ADJUST_LABEL;
    } else if (G_signalY[0] - G_signalHeight / 2 < mpos.y && mpos.y < G_signalY[0] + G_signalHeight / 2) {
        // mouse down on signal
        if (evt.which !== 1 || G_controlDown || G_metaDown) {
            // right/middle down or ctrl/cmd held
            G_mouseAction = MOUSE_CREATE_LABEL;
        } else {
            G_mouseAction = MOUSE_PAN;
        }
    } else if (G_signalY[0] - G_signalHeight / 2 - TIMELINE_HEIGHT < mpos.y && mpos.y < G_signalY[0] - G_signalHeight / 2) {
        // mouse down on timeline
        G_mouseAction = MOUSE_CREATE_LABEL;
    } else {
        if (evt.which !== 1 || G_controlDown || G_metaDown) {
            G_mouseAction = MOUSE_COPY_LABEL;
        } else {
            G_mouseAction = null;
        }
    }
}

// Handle when the mouse moves
function mouseMoveHandler(evt) {
    var mpos = getWorldMousePos(evt, G_glCanvas);
    var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);

    if (G_mouseAction === MOUSE_PAN) {
        var dx = mpos.x - G_mousePos.x;
        setAndClampXOffset(G_xOffset + (dx / G_xScale));
    }

    G_mousePos = mpos;
    if (G_mouseDown !== false) {
        var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
        G_mouseMoved = smpx * zoom;
    } else {
        checkMouseOnLabelEdge();
    }
}

function sortLabels(labels) {
    labels.sort(function(a, b){return a.lo - b.lo});
}

function setCurrentLabel(label) {
    var radioButtons = document.getElementsByName("addlabel");
    for (var ii = 0; ii < radioButtons.length; ++ ii) {
        if (radioButtons[ii].id === "addlabel" + label) {
            radioButtons[ii].click();
            return;
        }
    }
}

function nextCurrentLabel() {
    var radioButtons = document.getElementsByName("addlabel");
    for (var ii = 0; ii < radioButtons.length; ++ ii) {
        if (radioButtons[ii].checked) {
            radioButtons[(ii + 1) % radioButtons.length].click();
            return;
        }
    }
}

function prevCurrentLabel() {
    var radioButtons = document.getElementsByName("addlabel");
    for (var ii = 0; ii < radioButtons.length; ++ ii) {
        if (radioButtons[ii].checked) {
            radioButtons[(ii + (radioButtons.length - 1)) % radioButtons.length].click();
            return;
        }
    }
}

function getCurrentLabel() {
    for (var ii = 0; ii < G_config.labels.length; ++ ii) {
        const label = G_config.labels[ii];
        if (document.getElementById('addlabel' + label.label).checked) {
            return label.label;
        }
    }
    return "ERASE";
}

function undoRedoLabel() {
    updateLabelsLocal(true, G_labelsLocalOld);
    sendLog('label', {"labels":G_labelsLocal})
}

function updateLabelsLocal(andSend, newLabelsLocal) {
    var tmp = G_labelsLocal;
    G_labelsLocal = newLabelsLocal;
    G_labelsLocalOld = tmp;
    updateGroundTruthScore();
    if (andSend) {
        sendLabels();
    }
}

function cycleServerLabels() {
    G_labelsRemoteStartIndexAlgo = G_labelsRemoteOtherAlgo.length ? ((G_labelsRemoteStartIndexAlgo + 1) % G_labelsRemoteOtherAlgo.length) : 0;
    G_labelsRemoteStartIndexPlayer = G_labelsRemoteOtherPlayer.length ? ((G_labelsRemoteStartIndexPlayer + 1) % G_labelsRemoteOtherPlayer.length) : 0;
    updateUrlParameters();
}

function showAllSignals() {
    var checkboxes = document.getElementsByName('showsignal');
    for (var ii = 0; ii < checkboxes.length; ++ ii) {
        checkboxes[ii].checked = true;
    }
}

function toggleSignalVisibility(index) {
    var checkboxes = document.getElementsByName('showsignal');
    for (var ii = 0; ii < checkboxes.length; ++ ii) {
        if (ii === index) {
            checkboxes[ii].click();
        }
    }
}

function isSignalVisible(index) {
    if (G_config.signals.length > 1) {
        var signalName = G_config.signals[Math.floor(index)];
        if (!document.getElementById('showsignal' + signalName).checked) {
            return false;
        }
    }

    return true;
}

function isComponentVisible(index) {
    if (index % 3 === 0 && !document.getElementById('axisx').checked) {
        return false;
    }
    if (index % 3 === 1 && !document.getElementById('axisy').checked) {
        return false;
    }
    if (index % 3 === 2 && !document.getElementById('axisz').checked) {
        return false;
    }

    if (!isSignalVisible(Math.floor(index / 3))) {
        return false;
    }

    return true;
}

function showAllLabels() {
    var checkboxes = document.getElementsByName("showlabel");
    for (var ii = 0; ii < checkboxes.length; ++ ii) {
        checkboxes[ii].checked = true;
    }
}

function hideAllLabels() {
    var checkboxes = document.getElementsByName("showlabel");
    for (var ii = 0; ii < checkboxes.length; ++ ii) {
        checkboxes[ii].checked = false;
    }
}

function getVisibleLabels() {
    var visibleLabels = [];
    for (var ii = 0; ii < G_config.labels.length; ++ ii) {
        const label = G_config.labels[ii];
        if (document.getElementById('showlabel' + label.label).checked) {
            visibleLabels[label.label] = true;
        }
    }
    if (document.getElementById('showlabelOTHER').checked) {
        visibleLabels['OTHER'] = true;
    }
    return visibleLabels;
}

function getPendingLabels() {
    var pendingLabels = [];
    if (G_mouseAction === MOUSE_CREATE_LABEL) {
        if (G_mouseDown !== false && G_mouseMoved !== false) {
            pendingLabels.push({
                lo: Math.min(G_mouseDown, G_mouseMoved),
                hi: Math.max(G_mouseDown, G_mouseMoved),
                label: getCurrentLabel()
            });
        }
    } else if (G_mouseAction === MOUSE_ADJUST_LABEL) {
        if (G_mouseDown !== false && G_mouseMoved !== false && G_mouseAdjust !== null) {
            if (G_mouseAdjust.left !== null) {
                if (G_mouseMoved > G_mouseAdjust.left.lo) {
                    pendingLabels.push({
                        lo: G_mouseAdjust.left.lo,
                        hi: G_mouseMoved,
                        label: G_mouseAdjust.left.label,
                        detail: G_mouseAdjust.left.detail
                    });
                }
            } else {
                if (G_mouseMoved > G_mouseAdjust.right.lo) {
                    pendingLabels.push({
                        lo: G_mouseAdjust.right.lo,
                        hi: G_mouseMoved,
                        label: 'ERASE'
                    });
                }
            }
            if (G_mouseAdjust.right !== null) {
                if (G_mouseMoved < G_mouseAdjust.right.hi) {
                    pendingLabels.push({
                        lo: G_mouseMoved,
                        hi: G_mouseAdjust.right.hi,
                        label: G_mouseAdjust.right.label,
                        detail: G_mouseAdjust.right.detail
                    });
                }
            } else {
                if (G_mouseMoved < G_mouseAdjust.left.hi) {
                    pendingLabels.push({
                        lo: G_mouseMoved,
                        hi: G_mouseAdjust.left.hi,
                        label: 'ERASE'
                    });
                }
            }
        }
    }
    return pendingLabels;
}

function updateColorMode() {
    G_modeColorMap = isDarkMode() ? DARK_MODE_COLOR_MAP : LIGHT_MODE_COLOR_MAP;
}

function isDarkMode() {
    return document.getElementById("darkmode").checked;
}

function isTileDebugging() {
    return document.getElementById("tiledebug").checked;
}

function maxZoom() {
    if (G_zoomLevel === 0 && G_zoomLevelIntermediate === 0) {
        zoomTo(true, G_config.zoom_max, ZOOM_INT_MAX_LEVEL);
    } else {
        zoomTo(true, 0, 0);
    }
}

// Functions to change the magnitude represented on the y-axis
function increaseMagnitude() {
    G_magnitude = Math.min(G_magnitudeMax, G_magnitude * 2);
}

function decreaseMagnitude() {
    G_magnitude = Math.max(G_magnitudeMin, G_magnitude / 2);
}

function resetMagnitude() {
    G_magnitude = G_config.magnitude;
}

function addLabels(newLabels) {
    var labelsLocalNew = G_labelsLocal;

    for (var pl = 0; pl < newLabels.length; ++ pl) {
        const lbl = newLabels[pl];

        updated = true;

        var lo = lbl.lo;
        var hi = lbl.hi;
        var labelname = lbl.label;

        if (labelname !== 'ERASE') {
            lo = Math.max(0, Math.min(G_config.length, lo));
            hi = Math.max(0, Math.min(G_config.length, hi));
            var showLabelElem = document.getElementById("showlabel" + labelname);
            if (showLabelElem) {
                showLabelElem.checked = true;
            }
        }

        // Only add non overlapping labels to the new list of labels, cutting off overlapping ends if necessary
        if (lo !== hi) {
            var newLocal = [];
            for (var ll = 0; ll < labelsLocalNew.length; ++ ll) {
                var label = labelsLocalNew[ll];
                if (label.hi <= lo) {
                    newLocal.push(label);
                } else if (label.lo >= hi) {
                    newLocal.push(label);
                } else if (label.lo >= lo && label.hi <= hi) {
                } else if (label.lo < lo && label.hi <= hi) {
                    newLocal.push({lo: label.lo, hi: lo, label: label.label, detail: label.detail});
                } else if (label.lo >= lo && label.hi > hi) {
                    newLocal.push({lo: hi, hi: label.hi, label: label.label, detail: label.detail});
                } else if (label.lo < lo && label.hi > hi) {
                    newLocal.push({lo: label.lo, hi: lo, label: label.label, detail: label.detail});
                    newLocal.push({lo: hi, hi: label.hi, label: label.label, detail: label.detail});
                }
            }
            labelsLocalNew = newLocal;

            // Add the new label
            if (labelname !== 'ERASE') {
                labelsLocalNew.push({lo: lo, hi: hi, label: labelname, detail: lbl.detail});
            }
            sortLabels(labelsLocalNew);

            // Merge labels with the new one
            var anyMerged = true;
            while (anyMerged) {
                anyMerged = false;
                var newLocal = [];
                for (var ll = 0; ll < labelsLocalNew.length; ++ ll) {
                    if (ll + 1 === labelsLocalNew.length) {
                        var label = labelsLocalNew[ll];
                        newLocal.push(label);
                    } else {
                        var label0 = labelsLocalNew[ll + 0];
                        var label1 = labelsLocalNew[ll + 1];
                        if (label0.hi === label1.lo && label0.label === label1.label && label0.detail === label1.detail) {
                            newLocal.push({lo: label0.lo, hi: label1.hi, label: label0.label, detail: label0.detail});
                            ++ ll;
                            anyMerged = true;
                        } else {
                            newLocal.push(label0);
                        }
                    }
                }
                labelsLocalNew = newLocal;
            }
        }
    }

    updateLabelsLocal(true, labelsLocalNew);
}

// Handle when the mouse button is released after being held and moved
// Create new labels and merge/overwrite the old labels when necessary
function mouseUpHandler(evt) {
    G_zoomUI = null;

    var pendingLabels = getPendingLabels();
    if (pendingLabels.length > 0) {
        addLabels(pendingLabels);
        sendLog('label', {"labels":G_labelsLocal})
    }

    clearMouse();
    checkMouseOnLabelEdge();
}

function mouseWheelHandler(evt) {
    G_zoomUI = null;
    if (evt.deltaY < 0) {
        G_zoomWheel = "zin";
    } else {
        G_zoomWheel = "zout";
    }
    evt.preventDefault();
}

function mouseDoubleHandler(evt) {
    if (G_mouseAdjust !== null) {
        if (G_mouseAdjust.left !== null && G_mouseAdjust.right === null) {
            var newLabel = {
                lo: G_mouseAdjust.left.hi,
                hi: (G_mouseAdjust.left.index + 1 < G_labelsLocal.length) ? G_labelsLocal[G_mouseAdjust.left.index + 1].lo : G_config.length,
                label: G_mouseAdjust.left.label,
                detail: G_mouseAdjust.left.detail
            }
            addLabels([newLabel]);
        } else if (G_mouseAdjust.left === null && G_mouseAdjust.right !== null) {
            var newLabel = {
                lo: (G_mouseAdjust.right.index > 0) ? G_labelsLocal[G_mouseAdjust.right.index - 1].hi : 0,
                hi: G_mouseAdjust.right.lo,
                label: G_mouseAdjust.right.label,
                detail: G_mouseAdjust.right.detail
            }
            addLabels([newLabel]);
        }
    } else if (G_mousePos && G_signalY[0] - G_signalHeight / 2 < G_mousePos.y && G_mousePos.y < G_signalY[0] + G_signalHeight / 2) {
        if (G_zoomLevel === 0 && G_zoomLevelIntermediate === 0) {
            zoomTo(true, G_config.zoom_max, ZOOM_INT_MAX_LEVEL);
        } else {
            setZoomHistory();
            zoomTo(true, 0, 0);
        }
    }
    evt.preventDefault();
}

// Zoom by a given intermediate delta
function zoomDelta(useMouse, di) {
    var zoom = G_zoomLevel;
    var zoomIntermediate = G_zoomLevelIntermediate;

    zoomIntermediate += di;

    while (zoomIntermediate < 0) {
        if (zoom > 0) {
            zoom -= 1;
            zoomIntermediate += (ZOOM_INT_MAX_LEVEL + 1);
        } else {
            zoomIntermediate = 0;
        }
    }
    while (zoomIntermediate > ZOOM_INT_MAX_LEVEL) {
        if (zoom < G_config.zoom_max) {
            zoom += 1;
            zoomIntermediate -= (ZOOM_INT_MAX_LEVEL + 1);
        } else {
            zoomIntermediate = ZOOM_INT_MAX_LEVEL;
        }
    }

    zoomTo(useMouse, zoom, zoomIntermediate);
}

// Zoom to a given zoom level
function zoomTo(useMouse, zoom, zoomIntermediate) {
    if (G_zoomLevel === zoom && G_zoomLevelIntermediate === zoomIntermediate) {
        return;
    }

    var changedLevel = G_zoomLevel - zoom;

    G_zoomLevel = clamp(zoom, 0, G_config.zoom_max);
    G_zoomLevelIntermediate = clamp(zoomIntermediate, 0, ZOOM_INT_MAX_LEVEL);

    var oldXS = G_xScale;
    var newXS = getXScale();

    var factor = Math.pow(G_config.tile_subsample, changedLevel);

    var midsmp = (0.5 - X_OFFSET) / oldXS - G_xOffset;
    if (useMouse && G_mousePos) {
        midsmp = (G_mousePos.x - X_OFFSET) / oldXS - G_xOffset;
    }

    G_xScale = newXS;

    var dx = (((midsmp * oldXS) - (midsmp * newXS * factor)));
    setAndClampXOffset((G_xOffset * oldXS + dx) / newXS);
}

// Handle zooming in on the signal
function zinHandler(useMouse) {
    if (G_mouseDown !== false) {
        return;
    }

    // Increment intermediate zoom level and main zoom level if necessary
    var speed =  G_shiftDown ? 20 : (G_slowPanZoomDown ? 1 : 10);

    zoomDelta(useMouse, -speed);
}

// Handle zooming out on the signal
function zoutHandler(useMouse) {
    if (G_mouseDown !== false) {
        return;
    }

    // Increment intermediate zoom level and main zoom level if necessary
    var speed =  G_shiftDown ? 20 : (G_slowPanZoomDown ? 1 : 10);

    zoomDelta(useMouse, speed);
}

// Function to update the URL when zoom or pan change and show the advanced instructions buttons if mode is not MTURK.
// Updates are limited to once every 0.5 seconds
function updateUrlParameters(){
    updateMessageDisplay();

    if (G_urlUpdateTimeout === null) {
        // set timeout to update url parameter later if needed
        G_urlUpdateTimeout = setTimeout(function() {
            var searchParams = new URLSearchParams(G_urlBaseParam);
            searchParams.set("zoom", G_zoomLevel);
            searchParams.set("zoomi", G_zoomLevelIntermediate);
            searchParams.set("offset", Math.round(G_xOffset));
            searchParams.set("iplayer", Math.round(G_labelsRemoteStartIndexPlayer));
            searchParams.set("ialgo", Math.round(G_labelsRemoteStartIndexAlgo));
            history.replaceState(history.state, 'Signaligner', window.location.pathname + '?' + searchParams.toString());

            if (G_modeConfig[MC_MODE] !== MODE_MTURK) {
                var advancedElements = document.getElementsByClassName('advancedbutton');
                for (let i = 0; i < advancedElements.length; i++) {
                    advancedElements[i].style.display = "table-cell";
                }
            }

            G_urlUpdateTimeout = null;
        }, 500);
    }
}

// Handle panning left on the signal
function pleftHandler() {
    var speed = (G_shiftDown ? 2.0 : (G_slowPanZoomDown ? 0.1 : 1.0));
    setAndClampXOffset(G_xOffset + speed * XPAN_AMOUNT / (G_xScale / DEFAULT_XSCALE));

    if (G_mouseAction === MOUSE_CREATE_LABEL) {
        var mpos = G_mousePos;
        var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);
        var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
        G_mouseMoved = smpx * zoom;
    }
}

// Handle panning right on the signal
function prightHandler() {
    var speed = (G_shiftDown ? 2.0 : (G_slowPanZoomDown ? 0.1 : 1.0));
    setAndClampXOffset(G_xOffset - speed * XPAN_AMOUNT / (G_xScale / DEFAULT_XSCALE));

    if (G_mouseAction === MOUSE_CREATE_LABEL) {
        var mpos = G_mousePos;
        var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);
        var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
        G_mouseMoved = smpx * zoom;
    }
}

// Update G_xOffset and keep the signal in the window
function setAndClampXOffset(newXOffset) {
    G_xOffset = newXOffset;

    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
    G_xOffset = Math.max(G_xOffset, -(G_config.length / zoom) + (0.1 - X_OFFSET) / G_xScale);
    G_xOffset = Math.min(G_xOffset, (0.9 - X_OFFSET) / G_xScale);

    updateUrlParameters();
}

// Reset the zoom and position of the signal
function resetHandler() {
    if (G_mouseDown) {
        return;
    }

    G_magnitude = G_config.magnitude;
    G_zoomLevel = DEFAULT_ZOOM;
    G_zoomLevelIntermediate = ZOOM_INT_MAX_LEVEL;
    G_xScale = getXScale();
    setAndClampXOffset(0);
}

// Handle when the "updatebutton" is clicked
function clickUpdateHandler() {
    sendLabels();
    fetchLabels(false);
}

function createLabelSetHandler() {
    const newSession = document.getElementById('newlabelset').value;
    const regex = /^([a-zA-Z0-9_]){3,15}$/;

    if (regex.test(newSession) === false) {
        alert('Please enter alphanumeric characters between 3 and 15 chars. ');
    } else {
        if (G_sessions.includes(newSession)) {
            alert('The session already exists. Select from dropdown.');
        }
        else {
            loadDataset(newSession, G_dataset)
        }
    }
}

// Restore mouse to standard "up" state
function clearMouse() {
    G_mousePos = G_mousePos; // keep mouse pos
    G_mouseDown = false;
    G_mouseMoved = false;
    G_mouseAction = null;
    G_mouseAdjust = null;
}

// Restore all keys to standard "up" state
function clearKeys() {
    G_shiftDown = false;
    G_controlDown = false;
    G_metaDown = false;
    G_altDown = false;
    G_slowPanZoomDown = false;
    G_pleftDown = false;
    G_prightDown = false;
    G_zinDown = false;
    G_zoutDown = false;
}

// Handle when any key is pressed down
function keydownHandler(evt) {
    var keyUpper = evt.key.toUpperCase();

    if (keyUpper === "SHIFT") {
        G_shiftDown = true;
        evt.preventDefault();
        return;
    } else if (keyUpper === "CONTROL") {
        G_controlDown = true;
        evt.preventDefault();
        return;
    } else if (keyUpper === "META") {
        G_metaDown = true;
        evt.preventDefault();
        return;
    } else if (keyUpper === "ALT") {
        G_altDown = true;
        evt.preventDefault();
        return;
    } else if (KEY_SLOW_PANZOOM.includes(keyUpper)) {
        G_slowPanZoomDown = true;
        return;
    }

    if (keyUpper === "ESCAPE") {
        document.activeElement.blur();
        clearMouse();
        clearKeys();
        return;
    }

    if (document.activeElement !== document.body) {
        // something else has the focus
        return;
    }

    // undo
    if (keyUpper === "Z" && (G_controlDown || G_metaDown)) {
        undoRedoLabel();
        return;
    }

    // skip the rest of the key handlers if certain modifiers are down
    if (!G_controlDown && !G_metaDown && !G_altDown) {
        // since no modifier is pressed, it is safe to call the preventDefault method here
        event.preventDefault();

        // pan and zoom based on keyboard input when the main window is in focus
        if (G_keyMap.get("PAN_LEFT").includes(keyUpper)) {
            G_pleftDown = true;
        } else if (G_keyMap.get("PAN_RIGHT").includes(keyUpper)) {
            G_prightDown = true;
        } else if (G_keyMap.get("ZOOM_IN").includes(keyUpper)) {
            G_zinDown = true;
        } else if (G_keyMap.get("ZOOM_OUT").includes(keyUpper)) {
            G_zoutDown = true;
        }

        // toggle between previous/next label options
        if (G_keyMap.get("PREVIOUS_LABEL").includes(keyUpper)) {
            prevCurrentLabel();
        } else if (G_keyMap.get("NEXT_LABEL").includes(keyUpper)) {
            nextCurrentLabel();
        }

        // change label range
        else if (G_keyMap.get("CYCLE").includes(keyUpper)) {
            cycleServerLabels();
        }
        // Increase y-axis magnitude
        else if (G_keyMap.get("DOUBLE_Y_MAG").includes(keyUpper)) {
            increaseMagnitude();
        }
        // Increase y-axis magnitude
        else if (G_keyMap.get("RESET_Y_MAG").includes(keyUpper)) {
            resetMagnitude();
        }
        // Decrease y-axis magnitude
        else if (G_keyMap.get("HALVE_Y_MAG").includes(keyUpper)) {
            decreaseMagnitude();
        }
        else if (keyUpper === " ") {
            resetHandler();
            evt.preventDefault();
        }
        else if (G_keyMap.get("RETURN_BACK").includes(keyUpper)) {
            restoreZoomHistory();
        }
        else {
            var digit = Number.parseInt(keyUpper);
            if (!isNaN(digit)) {
                if (digit === 0) {
                    showAllSignals();
                } else if (digit >= 1 && digit <= 9) {
                    toggleSignalVisibility(digit - 1);
                }
            }
        }
    }
}

// Handle when any key is released
function keyupHandler(evt) {
    var keyUpper = evt.key.toUpperCase();

    if (keyUpper === "SHIFT") {
        G_shiftDown = false;
        return;
    } else if (keyUpper === "CONTROL") {
        G_controlDown = false;
        return;
    } else if (keyUpper === "META") {
        G_metaDown = false;
        return;
    } else if (keyUpper === "ALT") {
        G_altDown = false;
        return;
    } else if (KEY_SLOW_PANZOOM.includes(keyUpper)) {
        G_slowPanZoomDown = false;
        return;
    } else if (G_keyMap.get("PAN_LEFT").includes(keyUpper)) {
        G_pleftDown = false;
        return;
    } else if (G_keyMap.get("PAN_RIGHT").includes(keyUpper)) {
        G_prightDown = false;
        return;
    } else if (G_keyMap.get("ZOOM_IN").includes(keyUpper)) {
        G_zinDown = false;
        return;
    }  if (G_keyMap.get("ZOOM_OUT").includes(keyUpper)) {
        G_zoutDown = false;
        return;
    }

}

// Saves and updates the zoom history.
function setZoomHistory() {
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
    G_zoomInHistory = {
        zoomLevel: G_zoomLevel,
        intermediateZoomLevel: G_zoomLevelIntermediate,
        xOffset: G_xOffset,
        smplo: Math.round((0.0 - X_OFFSET) / G_xScale - G_xOffset) * zoom,
        smphi: Math.round((1.0 - X_OFFSET) / G_xScale - G_xOffset) * zoom
    }
}

function restoreZoomHistory() {
    zoomTo(true, G_zoomInHistory.zoomLevel, G_zoomInHistory.intermediateZoomLevel);
    setAndClampXOffset(G_zoomInHistory.xOffset);
}

// Initialize the program
function startup() {
    // Initialize the canvases
    G_glCanvas = document.getElementById('glcanvas');
    G_glCtx = G_glCanvas.getContext('webgl');

    G_canvasWidth = G_glCanvas.width;
    G_canvasHeight = G_glCanvas.height;

    G_textCanvas = document.getElementById('textcanvas');
    G_textCtx = G_textCanvas.getContext('2d');

    G_textCanvasOffscreen = document.createElement('canvas');
    G_textCanvasOffscreen.width = G_textCanvas.width;
    G_textCanvasOffscreen.height = G_textCanvas.height;
    G_textCtxOffscreen = G_textCanvasOffscreen.getContext('2d');

    // Set the session information based on the url
    var url_string = window.location.href;
    var url = new URL(url_string);
    G_dataset = url.searchParams.get("dataset");
    G_session = url.searchParams.get("session");
    G_run = makeId();

    if (!G_dataset || G_dataset.length === 0) {
        G_dataset = undefined;
    }
    if (!G_session || G_session.length === 0 || /^([a-zA-Z0-9_])+$/.test(G_session) === false) {
        G_session = undefined;
    }

    if (G_session === undefined || G_dataset === undefined) {
        var new_session = G_session;
        if (new_session === undefined) {
            new_session = makeId();
        }

        var new_dataset = G_dataset;
        if (new_dataset === undefined) {
            if (G_modeConfig[MC_MODE] === MODE_MTURK) {
                new_dataset = mturkGetFirstDataset();
            } else {
                new_dataset = getDefaultDataset();
            }
        }

        G_dataset = new_dataset;
        loadDataset(new_session, new_dataset);
        return;
    }

    if (G_modeConfig[MC_MODE] === MODE_MTURK) {
        mturkSetup();
    }

    if (!G_modeConfig[MC_HIDE_IMPORT_DATA_BUTTON]) {
        importDatasetSetup();
    }

    // Initialize shader
    const shaderProgram = initShaderProgram();
    G_programInfo = {
        program: shaderProgram,
        attribLocations: {
            vertexPosition: G_glCtx.getAttribLocation(shaderProgram, 'aVertexPosition'),
        }
    };

    G_glCtx.useProgram(G_programInfo.program);
    G_uGlobalColor = G_glCtx.getUniformLocation(G_programInfo.program, "uGlobalColor");
    G_uOffset = G_glCtx.getUniformLocation(G_programInfo.program, "uOffset");
    G_uScale = G_glCtx.getUniformLocation(G_programInfo.program, "uScale");

    G_signalHeight = 0.5;
    G_signalY = [0.73];

    // Initialize the scene
    G_tileData = new Map();

    // Initialize the session label id
    G_sessLabelId = G_session;

    // Initialize the color mode map
    updateColorMode();

    initQuadBuffer();

    showText('message', 'Loading...');

    sendLog('start', {});

    // Start looping functions
    setInterval(drawScene, 30);
    setInterval(logTick, 10000);
    setInterval(handleZoomUI, 50);

    // Clear state
    clearMouse();
    clearKeys();

    // Show all axes
    showAllAxes();

    // Event handlers
    window.addEventListener('blur', blurHandler);

    window.addEventListener('mousedown', mouseDownHandler);
    window.addEventListener('mousemove', mouseMoveHandler);
    window.addEventListener('mouseup', mouseUpHandler);
    G_glCanvas.addEventListener('wheel', mouseWheelHandler);
    G_glCanvas.addEventListener('dblclick', mouseDoubleHandler);

    window.addEventListener('keydown', keydownHandler);
    window.addEventListener('keyup', keyupHandler);

    document.getElementById('updatebutton').addEventListener('click', clickUpdateHandler);
    document.getElementById('createlabelset').addEventListener('click', createLabelSetHandler);

    document.getElementById('zinbutton').addEventListener('mousedown', function(evt){ if (evt.button === 0) G_zoomUI = "zin"; });
    document.getElementById('zinbutton').addEventListener('mouseup', function(){ G_zoomUI = null; });
    document.getElementById('zoutbutton').addEventListener('mousedown', function(evt){ if (evt.button === 0) G_zoomUI = "zout"; });
    document.getElementById('zoutbutton').addEventListener('mouseup', function(){ G_zoomUI = null; });
    document.getElementById('pleftbutton').addEventListener('mousedown', function(evt){ if (evt.button === 0) G_zoomUI = "pleft"; });
    document.getElementById('pleftbutton').addEventListener('mouseup', function(){ G_zoomUI = null; });
    document.getElementById('prightbutton').addEventListener('mousedown', function(evt){ if (evt.button === 0) G_zoomUI = "pright"; });
    document.getElementById('prightbutton').addEventListener('mouseup', function(){ G_zoomUI = null; });
    document.getElementById('resetbutton').addEventListener('click', function(){ G_zoomUI = null; resetHandler(); });

    document.getElementById('double-ybutton').addEventListener('click', function(){ increaseMagnitude(); });
    document.getElementById('reset-ybutton').addEventListener('click', function(){ resetMagnitude(); });
    document.getElementById('halve-ybutton').addEventListener('click', function(){ decreaseMagnitude(); });

    document.getElementById('maxzoombutton').addEventListener('click', function(evt) { maxZoom(); evt.preventDefault()});

    document.getElementById('undoredobutton').addEventListener('click', undoRedoLabel);
    document.getElementById('nextlabelbutton').addEventListener('click', nextCurrentLabel);
    document.getElementById('prevlabelbutton').addEventListener('click', prevCurrentLabel);

    document.getElementById('cycleserverlabels').addEventListener('click', cycleServerLabels);

    document.getElementById('darkmode').addEventListener('change', updateColorMode);

    // fetch dataset config
    fetchConfig();

    // Reset timer for tooltip
    for (var evtName of ['mousemove', 'mousedown', 'mousewheel', 'wheel', 'touchmove', 'keypress', 'keyup', 'keydown', 'DOMMouseScroll', 'MSPointerMove']) {
        window.addEventListener(evtName, resetTooltipTimer, false);
    }
}

function showAllAxes() {
    document.getElementById('axisx').checked = true;
    document.getElementById('axisy').checked = true;
    document.getElementById('axisz').checked = true;
}

// Change query param to fetch new dataset data
function changeDataset(evt) {
    var allFiles = evt.target.files;
    var relativePath = allFiles[0].webkitRelativePath;
    var folderName = relativePath.split("/");
    var datasetName = folderName[0];

    var searchParams = new URLSearchParams(window.location.search);
    searchParams.set("dataset", datasetName);
    window.location.search = searchParams.toString();
}

// Get the appropriate XMLHTTP request based on the browser
function getXHR() {
    if (window.XMLHttpRequest) {
        // Chrome, Firefox, IE7+, Opera, Safari
        return new XMLHttpRequest();
    }
    // IE6
    try {
        return new ActiveXObject('MSXML2.XMLHTTP.6.0');
    } catch (e) {
        try {
            return new ActiveXObject('MSXML2.XMLHTTP.3.0');
        } catch (e) {
            try {
                return new ActiveXObject('MSXML2.XMLHTTP');
            } catch (e) {
                return null;
            }
        }
    }
}

function requestToServer(url, postData, retries, successcallback, failurecallback) {
    var xhttp = getXHR();
    if (xhttp) {
        xhttp.onreadystatechange = function() {
            if (xhttp.readyState === 4) {
                if (xhttp.status === 200) {
                    if (successcallback) {
                        successcallback(xhttp.response);
                    }
                } else {
                    // anything other than 200 is an error
                    if (retries > 0) {
                        requestToServer(url, postData, retries - 1, successcallback, failurecallback);
                    } else {
                        if (failurecallback) {
                            failurecallback();
                        }
                    }
                }
            }
        };

        if (postData) {
            var postDataStr = encodeURI(JSON.stringify(postData));
            xhttp.open("POST", url, true);
            xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhttp.send("data=" + postDataStr);
        } else {
            xhttp.open("GET", url, true);
            xhttp.send("");
        }
    }
}

function onDatasetListError() {
    showText("message", "Error: no datasets available to import.");
}

function onDatasetListSuccess(response) {
    try {
        let importDatasets = JSON.parse(response);
        updateDatasetsListDropdown(importDatasets);
    }
    catch(e) {
        showText("message", "Error parsing list of datasets");
    }
}

function updateListDropdown(name, currentOption, importOptions, changeFunc) {
    var selectElement = document.getElementById(name);

    for (var i = 0; i < importOptions.length; i++) {
        selectElement.options[selectElement.options.length] = new Option(importOptions[i], importOptions[i]);
    }
    if (!importOptions.includes(currentOption)) {
        selectElement.options[selectElement.options.length] = new Option(currentOption, currentOption);
    }

    // Assign the selected option based on the current dataset
    var selectedIndex = 0;
    for (var j = 0; j < selectElement.options.length; j++) {
        if (currentOption === selectElement.options[j].value) {
            selectedIndex = j;
        }
    }
    selectElement.selectedIndex = selectedIndex;

    // Handle when selected element changes
    selectElement.addEventListener('change', function(e) {
        changeFunc(selectElement.options[selectElement.selectedIndex].value);
        document.activeElement.blur();
    });

}

function updateDatasetsListDropdown(importDatasets) {
    updateListDropdown('importdatadropdown', G_dataset, importDatasets, function(value) { loadDataset(G_session, value); });
}

function updateSessionsListDropdown(importSessions) {
    updateListDropdown('sessionsdropdown', G_session, importSessions, function(value) { loadDataset(value, G_dataset); });
}


function importDatasetSetup() {

    // Show import dataset elements
    document.getElementById('importdata').style.display = "block";

    // Add the dataset options to the select element
    requestToServer('fetchdatasetlist', null, 0, onDatasetListSuccess, onDatasetListError);
}

function mturkGetFirstDataset() {
    return 'SleepSegment1';
}

function mturkGetNextDataset(dataset) {
    var nextDataset = MTURK_DATASET_ORDER[dataset];
    return nextDataset === undefined ? null : nextDataset;
}

function mturkSetup() {

    document.getElementById('mturk').style.display = 'block';

    // Hide close modal button until user reads all instructions pages
    document.getElementById('mturkhelpclosebutton').style.display = "none";

    G_mturkState = 'REFRESH';
    document.getElementById('mturknext').addEventListener('click', mturkNext);

    document.getElementById('mturkhelpopenbutton').addEventListener('click', function(e) {
        document.getElementById('mturkhelpclosebutton').style.display = "block";
        mturkOpenHelp("mturk_instructions_quick_ref.html");
    });
    document.getElementById('mturkhelpclosebutton').addEventListener('click', mturkCloseHelp);

    document.getElementById('modal-log-prev').addEventListener( 'click', function(e) {
        e.preventDefault();
        var fromPage = document.getElementById('modal-log-prev').innerText;
        sendLog('mturk-help-prev', {fromPage: fromPage});
        e.innerText = "";
    });

    document.getElementById('modal-log-next').addEventListener( 'click', function(e) {
        e.preventDefault();
        var fromPage = document.getElementById('modal-log-next').innerText;
        sendLog('mturk-help-next', {fromPage: fromPage});
        e.innerText = "";
    });

    document.getElementById('modal-log-article').addEventListener( 'click', function(e) {
        e.preventDefault();
        sendLog('mturk-help-article', {});
    });

    document.getElementById('modal-log-slideshow').addEventListener('click', function(e) {
       e.preventDefault();
       var page = document.getElementById('modal-log-slideshow').innerText;
       sendLog('mturk-help-slideshow', {page: page});
    });

    document.getElementById('modal-log-close').addEventListener('click', function(e) {
       e.preventDefault();
       var modalCloseButton = document.getElementById('mturkhelpclosebutton');
       modalCloseButton.style.display = MTURK_TUTORIAL_DATASETS.indexOf(G_dataset) >= 0 ? "none" : "block";
       mturkCloseHelp();
    });

    document.getElementById('modal-advance-dataset').addEventListener('click', mturkAdvance);

    if (G_dataset === mturkGetFirstDataset()) {
        mturkOpenHelp();
    }
    mturkRefresh();
}

function mturkNextMessage() {
    // Temporarily hard coded to end after this dataset
    if (mturkGetNextDataset(G_dataset) == null || G_dataset === "SleepSegment2") {
        return "All done, enter your code on MTurk";
    } else {
        return "Continue";
    }
}

function mturkNext() {
    if (G_mturkState === 'SUBMIT') {
        mturkSubmit();
    } else if (G_mturkState === 'ADVANCE') {
        mturkAdvance();
    } else if (G_mturkState === 'TUTORIAL') {
        mturkContinueTutorial();
    }
}

function mturkAdvance() {
    // Continue to next dataset
    G_mturkSubmissions = 0;
    var nextDataset = mturkGetNextDataset(G_dataset);
    // Temporarily hard coded to end after this dataset
    if (nextDataset !== null && G_dataset !== "SleepSegment2") {
        G_dataset = nextDataset;
        sendLog('mturk-advance', {});
        loadDataset(G_session, nextDataset);
    } else {
        document.getElementById('mturknext').style.display = "none";
        document.getElementById('mturkcomplete').style.display="table-cell";
    }
}

function mturkContinueTutorial() {

    if (G_dataset === "SleepSegment1") {
        var page = G_modeConfig[MC_HIDE_REMOTE_ALGO_LABELS] ? "mturk_instructions_challenge_1.html" : "mturk_instructions_algo_challenge_1.html";
        mturkOpenHelp(page);
    } else if (G_dataset === 'SleepSegment2') {
        var page = G_modeConfig[MC_HIDE_REMOTE_ALGO_LABELS] ? "mturk_instructions_wns_1.html" : "mturk_instructions_algo_wns_1.html";
        mturkOpenHelp(page);
    }
}

// Send the mturk data
function mturkRefresh() {
    var data = genericLogObject();

    requestToServer('mturksubmissions', data, 3, mturkOnRefreshSuccess, mturkOnRefreshError);
}

function mturkOnRefreshError() {
    alert("Error contacting server. Please reconnect to the internet or wait and then try again.");
}

function mturkOnRefreshSuccess(response) {

    var data = JSON.parse(response);

    var foundDataset = false;
    for (var ii = 0; ii < data.datasets.length; ++ ii) {
        if (data.datasets[ii] === G_dataset) {
            foundDataset = true;
        }
    }

    if (foundDataset) {
        document.getElementById('mturknext').innerHTML = "You've already submitted: " + mturkNextMessage();
        G_mturkState = MTURK_TUTORIAL_DATASETS.indexOf(G_dataset) >= 0 ? 'TUTORIAL' : 'ADVANCE';
    } else {
        document.getElementById('mturknext').innerHTML = "Submit your labels";
        G_mturkState = 'SUBMIT';
    }

    mturkUpdateCode(data.amount, data.code);
}

// Send the mturk data
function mturkSubmit() {

    sendLog('mturk-submit-attempt', {});

    G_mturkSubmissions += 1;
    var currentScore = G_groundTruthScore ? Math.round(G_groundTruthScore) : 0;

    if (currentScore < 100) {
        // If tutorial dataset, check if threshold score was met
        if (MTURK_TUTORIAL_DATASETS.indexOf(G_dataset) >= 0 && currentScore < MTURK_TUTORIAL_MIN_SCORE) {
            var alertText = "Your current score is: " + currentScore + "%. You must get a score above " +
                MTURK_TUTORIAL_MIN_SCORE + "% to continue the tutorial.";
            alert(alertText);
            return;
        }

        // If challenge dataset and max num submission attempts not reached, show score and ask to confirm submission
        else if (MTURK_CHALLENGE_DATASETS.indexOf(G_dataset) >= 0 && G_mturkSubmissions < MTURK_CHALLENGE_MAX_SUBMISSIONS) {

            var confirmationDialog = "You achieved a score of " + currentScore + "%. " +
                "Are you sure you want to continue? \nYou have " + (MTURK_CHALLENGE_MAX_SUBMISSIONS - G_mturkSubmissions) +
                " submission attempts left until your labels are automatically submitted.";

            if (!confirm(confirmationDialog)) {
                return;
            }
        }
    }

    // Submit user labels
    var data = genericLogObject();
    data.source = MODE_MTURK;
    data.labels = G_labelsLocal;
    data.score = currentScore;
	data.daysofdata = (G_config.length / G_config.sample_rate) / 86400;
	data.istutorial = MTURK_TUTORIAL_DATASETS.indexOf(G_dataset) >= 0;

    sendLog('mturk-submit', {});
    requestToServer('mturksubmit', data, 3, mturkOnSubmitSuccess, mturkOnSubmitError);

    document.getElementById('mturknext').disabled = true;
}

function mturkOnSubmitError() {
    alert("Error contacting server. Please reconnect to the internet or wait and then try again.");
    document.getElementById('mturknext').disabled = false;
}

function mturkOnSubmitSuccess(response) {
    var data = JSON.parse(response);

    document.getElementById('mturknext').disabled = false;
    document.getElementById('mturknext').innerHTML = mturkNextMessage();
    G_mturkState = MTURK_TUTORIAL_DATASETS.indexOf(G_dataset) >= 0 ? 'TUTORIAL' : 'ADVANCE';

    if (G_mturkState === 'TUTORIAL') {
        document.getElementById('mturkhelpclosebutton').style.display = "none";
        mturkContinueTutorial();
    } else if (MTURK_CHALLENGE_DATASETS.indexOf(G_dataset) >= 0) {
        alert("See how your labels compared to the truth labels");
    }

    mturkUpdateCode(data.amount, data.code);
}

// update mturk code
function mturkUpdateCode(amount, code) {
    document.getElementById('mturkamount').innerHTML = amount;
    document.getElementById('mturkcode').innerHTML = code;
}

// Open mTurk instructions modal
function mturkOpenHelp(page=null) {
    sendLog('mturk-help-open', {});

    G_mturkHelpModalVisitCount += 1;
    document.getElementById('modal-visit-count').innerText = G_mturkHelpModalVisitCount;

    var iframe = document.getElementById("instructions-iframe");

    if (page) {
        iframe.src = page;
    } else {
        iframe.src = G_modeConfig[MC_HIDE_REMOTE_ALGO_LABELS] ? "mturk_instructions_intro.html" : "mturk_instructions_algo_intro.html";
    }

    var modal = document.getElementById("mturkhelpmodal");
    modal.style.display = "block";

}

// Close mTurk instructions modal
function mturkCloseHelp() {
    sendLog('mturk-help-close', {});
    var modal = document.getElementById("mturkhelpmodal");
    modal.style.display = "none";
    window.focus();
}



function getZoomAtMouse() {
    return document.getElementById("mousezoomlock").checked;
}

// Handle the the ui buttons that zoom and pan
function handleZoomUI() {
    if (G_mouseAction === MOUSE_CREATE_LABEL) {
        if (G_mousePos.x <= 0.02) {
            G_zoomUI = "pleft";
        } else if (G_mousePos.x >= 0.98) {
            G_zoomUI = "pright";
        } else {
            G_zoomUI = null;
        }
    }

    if (G_zoomWheel === "zin") {
        zinHandler(getZoomAtMouse());
        G_zoomWheel = null;
    } else if (G_zoomWheel === "zout") {
        zoutHandler(getZoomAtMouse());
        G_zoomWheel = null;
    } else if (G_zoomUI === "pright" || G_prightDown) {
        prightHandler();
    } else if (G_zoomUI === "pleft" || G_pleftDown) {
        pleftHandler();
    } else if (G_zoomUI === "zin" || G_zinDown) {
        zinHandler(false);
    } else if (G_zoomUI === "zout" || G_zoutDown) {
        zoutHandler(false);
    }
}

// Get the dataset configuration from the server
function fetchConfig() {
    if (G_fetchingConfig) {
        return;
    }

    G_fetchingConfig = true;

    requestToServer("fetchdataset?dataset=" + G_dataset + "&type=config", null, 0, onConfigSuccess, onConfigError);
}

let G_urlBaseParam;

// Callback when the config file is loaded from the server
function onConfigError() {
    // TODO: handle error
    showText("message", "Error fetching config.");
    G_config = null;
}

function onConfigSuccess(response) {
    try {
        G_config = JSON.parse(response);

        let requiredFields = ["title", "tile_size", "tile_subsample", "zoom_max", "length", "start_time_ms", "sample_rate", "start_day_idx", "magnitude", "signals", "labels"];
        let missingFields = "";
        for (var ii = 0; ii < requiredFields.length; ++ ii) {
            if (G_config[requiredFields[ii]] === undefined) {
                missingFields += (" " + requiredFields[ii]);
            }
        }
        if (missingFields !== "") {
            debugLogMessage("Config missing fields:" + missingFields);
            showText("message", "Error in config data.");
            G_config = null;
            return;
        }
        if (!Number.isInteger(G_config.magnitude) || G_config.magnitude <= 0) {
            debugLogMessage("Config magnitude error.");
            showText("message", "Error in config data.");
            G_config = null;
            return;
        }

        showText("title", G_config.title);
    } catch(e) {
        G_config = null;
    }

    if (!G_config) {
        showText("message", "Error fetching or parsing config.");
        return;
    }

    G_fetchingConfig = false;
    G_urlBaseParam = window.location.search;

    // Set start date and start day index of output to display
    G_startDate = new Date(G_config.start_time_ms);
    G_startDayIdx = G_config.start_day_idx;


    // Set magnitude parameters
    G_magnitude = G_config.magnitude;
    G_magnitudeMin = G_config.magnitude / MAGNITUDE_SCALE_RANGE;
    G_magnitudeMax = G_config.magnitude * MAGNITUDE_SCALE_RANGE;

    // set components
    G_components = 3 * G_config.signals.length;

    // Set the defaults and initialize the signal position
    DEFAULT_ZOOM = G_config.zoom_max;
    DEFAULT_XSCALE = 1.0 / G_config.tile_size / 3;

    G_zoomUI = null;

    var searchParams = new URLSearchParams(G_urlBaseParam);
    var urlZoom = Number.parseInt(searchParams.get("zoom"));
    var urlZoomInter = Number.parseInt(searchParams.get("zoomi"));
    var urlOffset = Number.parseInt(searchParams.get("offset"));
    var playerIndex = Number.parseInt(searchParams.get("iplayer"));
    var algoIndex = Number.parseInt(searchParams.get("ialgo"));

    G_labelsRemoteStartIndexPlayer = !isNaN(playerIndex) ? Math.max(0, playerIndex) : 0;
    G_labelsRemoteStartIndexAlgo = !isNaN(algoIndex) ? Math.max(0, algoIndex) : 0;
    G_zoomLevel = !isNaN(urlZoom) ? clamp(urlZoom, 0, G_config.zoom_max) : DEFAULT_ZOOM;
    G_zoomLevelIntermediate = !isNaN(urlZoomInter) ? clamp(urlZoomInter, 0, ZOOM_INT_MAX_LEVEL) : ZOOM_INT_MAX_LEVEL;
    G_xScale = getXScale();
    setAndClampXOffset(!isNaN(urlOffset) ? urlOffset : 0);

    G_labelColors = [];
    for (var ii = 0; ii < G_config.labels.length; ++ ii) {
        const label = G_config.labels[ii];
        G_labelColors[label.label] = label.color;
    }

    createLabelInputs();
    createSignalInputs();

    // Get the labels and create the timeline
    fetchLabels(true);
}

function clamp(x, min, max) {
    return Math.min(max, Math.max(min, x));
}

function createInput(labelname, color, name, type,  checked) {
    var id = name + labelname;

    var newDiv = document.createElement("div");
    newDiv.style.backgroundColor = getColorString(color);
    newDiv.style.textAlign = "left";
    newDiv.style.height = "19px";
    newDiv.style.whiteSpace = "nowrap";

    var newLabel = document.createElement("label");
    newLabel.setAttribute("for", id);
    newLabel.innerHTML = labelname;

    var newInput = document.createElement("input");
    newInput.setAttribute("type", type);
    newInput.setAttribute("id", id);
    newInput.setAttribute("name", name);
    if (checked) {
        newInput.setAttribute("checked", true);
    }

    newDiv.appendChild(newInput);
    newDiv.appendChild(newLabel);

    newDiv.onclick=(evt)=>{
        if (evt.target === newDiv) {
            newInput.click();
        }
    };

    return newDiv;
}

function createSignalInputs() {
    if (G_config.signals.length > 1) {
        var showSignalDiv = document.getElementById('showsignaldiv');
        for (var ii = 0; ii < G_config.signals.length; ++ ii) {
            showSignalDiv.appendChild(createInput(G_config.signals[ii], COLOR_LABEL_X, "showsignal", "checkbox", true));
        }
    }
}

function createLabelInputs() {
    var addLabelDiv = document.getElementById('addlabeldiv');
    var showLabelDiv = document.getElementById('showlabeldiv');

    for (var ii = 0; ii < G_config.labels.length; ++ ii) {
        const label = G_config.labels[ii];
        addLabelDiv.appendChild(createInput(label.label, label.color, "addlabel", "radio", ii == 0));
        showLabelDiv.appendChild(createInput(label.label, label.color, "showlabel", "checkbox", true));
    }
    addLabelDiv.appendChild(createInput("ERASE", COLOR_LABEL_X, "addlabel", "radio", false));
    showLabelDiv.appendChild(createInput("OTHER", COLOR_LABEL_X, "showlabel", "checkbox", true));

    var allButton = document.createElement("button");
    allButton.innerHTML = "ALL";
    allButton.addEventListener('click', showAllLabels);
    showLabelDiv.appendChild(allButton);

    var noneButton = document.createElement("button");
    noneButton.innerHTML = "NONE";
    noneButton.addEventListener('click', hideAllLabels);
    showLabelDiv.appendChild(noneButton);
}

// Get all of the labels from the server
function fetchLabels(fetchLocal) {
    if (G_fetchingLabels) {
        return;
    }

    G_fetchingLabels = true;
    G_fetchingLabelsLocal = fetchLocal;

    requestToServer("fetchlabels?dataset=" + G_dataset, null, 0, onLabelsSuccess, onLabelsError);
}

// Callback for when labels are received
function onLabelsError() {
    // TODO: handle error
}

function onLabelsSuccess(response) {
    var updateLocal = G_fetchingLabelsLocal;
    G_fetchingLabels = false;
    G_fetchingLabelsLocal = false;

    G_labelsRemoteYours = null;
    G_labelsRemoteNotes = [];
    G_labelsRemoteOtherPlayer = [];
    G_labelsRemoteOtherAlgo = [];
    G_labelsRemoteGroundTruth = null;

    G_groundTruthScore = null;

    var useLocalLabels = G_labelsLocal;
    if (response.length > 0) {
        // Set remote labels to what was received
        var labelsResponse = JSON.parse(response);
        var initFrom = null;
        for (var ll = 0; ll < labelsResponse.length; ++ ll) {
            var lr = labelsResponse[ll];
            sortLabels(lr.labels);
            if (updateLocal) {
                if (lr.session === G_sessLabelId) {
                    useLocalLabels = lr.labels.slice();
                }
                if (G_config.initfrom && lr.session === G_config.initfrom) {
                    initFrom = lr.labels.slice();
                }
            }

            if (lr.session === G_sessLabelId) {
                G_labelsRemoteYours = lr;
                G_sessions.push(lr.session)
            } else if (lr.source === SOURCE_ALGO) {
                G_labelsRemoteOtherAlgo.push(lr);
            }
            else if (lr.source === SOURCE_NOTES) {
                G_labelsRemoteNotes.push(lr);
            }
            else if(lr.source === SOURCE_EXPERT && !G_modeConfig[MC_HIDE_REMOTE_EXPERT]) {
                G_labelsRemoteOtherPlayer.push(lr);
            }
            else if(lr.source === SOURCE_MTURK && !G_modeConfig[MC_HIDE_REMOTE_MTURK]) {
                G_labelsRemoteOtherPlayer.push(lr);
            }
            else if (lr.source === SOURCE_TRUTH) {
                if (G_labelsRemoteGroundTruth === null) {
                    G_labelsRemoteGroundTruth = lr;
                } else {
                    G_labelsRemoteGroundTruth = 'ERROR';
                    debugLogMessage('Multiple sessions with source Truth');
                }
            } else if (!G_modeConfig[MC_HIDE_REMOTE_PLAYER_LABELS]) {
                G_labelsRemoteOtherPlayer.push(lr);
                G_sessions.push(lr.session)
            }
        }

        // Initialize local labels
        if (updateLocal && initFrom && useLocalLabels.length === 0 && G_labelsLocal.length === 0) {
            useLocalLabels = initFrom;
        }
    }

    updateLabelsLocal(false, useLocalLabels);

    updateSessionsListDropdown(G_sessions);

    G_labelsRemoteStartIndexAlgo = G_labelsRemoteOtherAlgo.length ? ((G_labelsRemoteStartIndexAlgo) % G_labelsRemoteOtherAlgo.length) : 0;
    G_labelsRemoteStartIndexPlayer = G_labelsRemoteOtherPlayer.length ? ((G_labelsRemoteStartIndexPlayer) % G_labelsRemoteOtherPlayer.length) : 0;
}

// Figure out if a tile should be in the data set
function shouldTileBeInData(zoom, tile) {
    var zoomScale = Math.pow(G_config.tile_subsample, zoom);
    var tileLo = (tile + 0) * G_config.tile_size * zoomScale;
    var tileHi = (tile + 1) * G_config.tile_size * zoomScale;
    return tileHi > 0 && tileLo < G_config.length;
}

// Get the given tile from the server if it's not already present
function fetchTileIfNeeded(zoom, tile) {
    if (!shouldTileBeInData(zoom, tile)) {
        return;
    }

    var tileId = getTileId(zoom, tile);
    var tileData = G_tileData.get(tileId);

    var needsFetch = false;
    if (tileData === undefined) {
        needsFetch = true;
    } else if (tileData.status === TILE_STATUS_ERROR && Date.now() > tileData.errortime) {
        needsFetch = true;
    }

    if (needsFetch) {
        // Adds timestamp and clears cache if it has exceeded.
        G_tileData.set(tileId, { status: TILE_STATUS_PENDING });
        updateAccess(tileId);

        requestToServer("fetchdataset?dataset=" + G_dataset + "&type=tile&id=" + tileId, null, 0,
                        function(response) { onTileSuccess(zoom, tile, response); },
                        function() { onTileError(zoom, tile); });
    }
}

// wait a few seconds before retrying tile fetch
function getTileErrorTime() {
    return Date.now() + 2000 + 3000 * Math.random();
}

// Callback function to execute when the server returns a tile
function onTileError(zoom, tile) {
    var tileId = getTileId(zoom, tile);

    // Adds timestamp and clears cache if it has exceeded.
    G_tileData.set(tileId, { status: TILE_STATUS_ERROR, errortime: getTileErrorTime() });
    updateAccess(tileId);
}

function onTileSuccess(zoom, tile, response) {
    var tileId = getTileId(zoom, tile);

    var tileConfig = undefined;
    try {
        tileConfig = JSON.parse(response);
    } catch(e) {
        tileConfig = undefined;
    }

    if (tileConfig === undefined) {
        G_tileData.set(tileId, { status: TILE_STATUS_ERROR, errortime: getTileErrorTime() });
        return;
    }

    G_tileData.set(tileId, { status: TILE_STATUS_RESPONDED });

    allocateTile(zoom, tile, tileConfig);
}

// Converts the newly downloaded tile into a usuable data structure
function allocateTile(zoom, tile, tileConfig) {
    var signal = tileConfig.data;

    // Initialize a 2D array to store data in
    var signaldata = [];
    for (var aa = 0; aa < G_components; aa ++) {
        signaldata.push([]);
    }

    // Put the data received into the 2D array
    for (var ii = 0; ii < signal.length; ii ++) {
        for (var aa = 0; aa < G_components; aa ++) {
            var lo = signal[ii][aa][0];
            var hi = signal[ii][aa][1];
            signaldata[aa].push(ii);
            signaldata[aa].push(lo);
            signaldata[aa].push(ii);
            signaldata[aa].push(hi);
        }
    }

    // Create the buffers for the data
    var signalbuffers = [];
    for (var aa = 0; aa < G_components; aa ++) {
        const new_buffer = G_glCtx.createBuffer();
        G_glCtx.bindBuffer(G_glCtx.ARRAY_BUFFER, new_buffer);
        G_glCtx.bufferData(G_glCtx.ARRAY_BUFFER, new Float32Array(signaldata[aa]), G_glCtx.STATIC_DRAW);
        signalbuffers.push(new_buffer);
    }

    tileData = {
        status: TILE_STATUS_READY,
        buffers: signalbuffers,
        data: signal
    };

    let tileId = getTileId(zoom, tile);
    G_tileData.set(tileId, tileData);

    // Adds timestamp and clears cache if it has exceeded.
    updateAccess(tileId);
}

// Initialize the shader
function initShaderProgram() {
    const vertexShader = loadShader(G_glCtx.VERTEX_SHADER, VS_SOURCE);
    const fragmentShader = loadShader(G_glCtx.FRAGMENT_SHADER, FS_SOURCE);

    // Create the shader program
    const shaderProgram = G_glCtx.createProgram();
    G_glCtx.attachShader(shaderProgram, vertexShader);
    G_glCtx.attachShader(shaderProgram, fragmentShader);
    G_glCtx.linkProgram(shaderProgram);

    // If creating the shader program failed, alert
    if (!G_glCtx.getProgramParameter(shaderProgram, G_glCtx.LINK_STATUS)) {
        alert('Unable to initialize the shader program: ' + G_glCtx.getProgramInfoLog(shaderProgram));
        return null;
    }

    return shaderProgram;
}

// Compile, load, then return the given shader
function loadShader(type, source) {
    const shader = G_glCtx.createShader(type);
    G_glCtx.shaderSource(shader, source);
    G_glCtx.compileShader(shader);

    if (!G_glCtx.getShaderParameter(shader, G_glCtx.COMPILE_STATUS)) {
        alert('An error occurred compiling the shaders: ' + G_glCtx.getShaderInfoLog(shader));
        G_glCtx.deleteShader(shader);
        return null;
    }

    return shader;
}

// Initialize the quad buffers
function initQuadBuffer() {
    const new_buffer = G_glCtx.createBuffer();
    G_glCtx.bindBuffer(G_glCtx.ARRAY_BUFFER, new_buffer);
    G_glCtx.bufferData(G_glCtx.ARRAY_BUFFER, new Float32Array(getQuadBufferData()), G_glCtx.STATIC_DRAW);
    G_quadBuffer = new_buffer;
}

function measureTextWidth(text, fontSize) {
    G_textCtxOffscreen.font = fontSize.toString() + "px Arial, Helvetica, sans-serif";
    return G_textCtxOffscreen.measureText(text).width / G_canvasWidth;
}

function drawText(text, tx, ty, halign, valign, maxwidth, color, fontSize, outline) {
    // on Firefox, the text seems a little higher than on other browsers
    var yoffset = 0;
    if (IS_FIREFOX) {
        if (valign === "middle") {
            yoffset = Math.floor(fontSize / 8);
        }
    }

    G_textCtxOffscreen.font = fontSize.toString() + "px Arial, Helvetica, sans-serif";
    G_textCtxOffscreen.textAlign = halign;
    G_textCtxOffscreen.textBaseline = valign;

    var xp = Math.floor(tx * G_canvasWidth);
    var yp = Math.floor((1.0 - ty) * G_canvasHeight + yoffset);
    var mw = (maxwidth ? maxwidth * G_canvasWidth : undefined);

    if (outline) {
        G_textCtxOffscreen.fillStyle = "#444444";
        for (var dx = -1; dx <= 1; ++ dx) {
            for (var dy = -1; dy <= 1; ++ dy) {
                G_textCtxOffscreen.fillText(text, xp + dx, yp + dy, mw);
            }
        }
    }
    G_textCtxOffscreen.fillStyle = color;
    G_textCtxOffscreen.fillText(text, xp, yp, mw);
}

// Set the color of the webgl renderer
function setColor(clr, scale, alpha) {
    if (scale === undefined) {
        scale = 1.0;
    }
    if (alpha === undefined) {
        alpha = 1.0;
    }
    G_glCtx.uniform4fv(G_uGlobalColor, [scale * clr[0], scale * clr[1], scale * clr[2], alpha]);
}

// Set the uniform of the offset and scale
function setXform(xx, yy, ww, hh) {
    G_glCtx.uniform2fv(G_uOffset, [xx, yy]);
    G_glCtx.uniform2fv(G_uScale, [ww, hh]);
}

// Draw the given buffer
function drawBuffer(buffer, prim, start, size, stride=0, offset=0) {
    G_glCtx.bindBuffer(G_glCtx.ARRAY_BUFFER, buffer);
    G_glCtx.vertexAttribPointer(G_programInfo.attribLocations.vertexPosition, 2, G_glCtx.FLOAT, false, stride, offset);
    G_glCtx.enableVertexAttribArray(G_programInfo.attribLocations.vertexPosition);
    G_glCtx.drawArrays(prim, start, size);
}

// Draw a filled or "hollow" quad at the given x and y with the given width and height
function drawQuad(filled, xl, yc, ww, hh) {
    setXform(xl, yc, ww, hh);
    drawBuffer(G_quadBuffer, filled ? G_glCtx.TRIANGLE_FAN : G_glCtx.LINE_LOOP, 0, 4);
}

// Draw a tile of data
function drawTile(zoom, tile, inactive) {
    if (!G_config) {
        return;
    }

    if (!shouldTileBeInData(zoom, tile)) {
        return;
    }

    var tileId = getTileId(zoom, tile);
    var tileData = G_tileData.get(tileId);
    // Adds timestamp and clears cache if it has exceeded.
    updateAccess(tileId);

    if (tileData) {
        if (isTileDebugging()) {
            setColor([0.3, 0.3, 0.3]);
            drawQuad(false,
                     G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_signalY[0],
                     G_xScale * (G_config.tile_size), G_signalHeight / 2);
        }

        if (tileData.status === TILE_STATUS_READY) {
            setXform(G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_signalY[0],
                     G_xScale, G_signalHeight / 2 / G_magnitude);

            var tileBuffers = tileData.buffers;

            var tileSamples = Math.min(G_config.tile_size, (G_config.length - 1) / Math.pow(G_config.tile_subsample, zoom) - tile * G_config.tile_size);

            var scale = 1.0;
            if (inactive) {
                scale = 0.2;
            }

            for (var aa = G_components - 1; aa >= 0; -- aa) {
                if (!isComponentVisible(aa)) {
                    continue;
                }

                var axisIndex = aa % 3;
                var signalIndex = Math.floor(aa / 3) % COLOR_SIGNAL_COUNT;

                if (axisIndex === 0) {
                    var color = COLOR_SIGNAL_X[signalIndex];
                } else if (axisIndex === 1) {
                    var color = COLOR_SIGNAL_Y[signalIndex];
                } else {
                    var color = COLOR_SIGNAL_Z[signalIndex];
                }

                setColor(color, scale);

                // Fill in area
                drawBuffer(tileBuffers[aa], G_glCtx.TRIANGLE_STRIP, 0, tileSamples * 2 + 2);

                // Draw outlines
                drawBuffer(tileBuffers[aa], G_glCtx.LINE_STRIP, 0, tileSamples + 1, 16);
                drawBuffer(tileBuffers[aa], G_glCtx.LINE_STRIP, 0, tileSamples + 1, 16, 8);
            }
        } else {
            setColor([0.1, 0.1, 0.1]);
            drawQuad(true,
                     G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_signalY[0],
                     G_xScale * (G_config.tile_size), G_signalHeight / 16);

            if (tileData.status === TILE_STATUS_ERROR) {
                var tileText = "Error loading.";
            } else {
                var tileText = "Loading...";
            }
            drawText(tileText, G_xScale * ((G_xOffset + X_OFFSET) + (tile + 0.5) * G_config.tile_size), G_signalY[0], "center", "middle", undefined, COLORH_TIMELINE_TEXT, 14);
        }
    } else {
        if (isTileDebugging()) {
            setColor([0.05, 0.0, 0.0]);
            drawQuad(true,
                     G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_signalY[0],
                     G_xScale * (G_config.tile_size), G_signalHeight / 2);
            setColor([0.5, 0.0, 0.0]);
            drawQuad(false,
                     G_xScale * (G_xOffset + tile * G_config.tile_size) + X_OFFSET, G_signalY[0],
                     G_xScale * (G_config.tile_size), G_signalHeight / 2);
        }
    }
}

// Add column label to indicate creator of the set of labels
function drawLabelName(sessionName, ymid, backing) {
    var mouseOverPlayerLabelName = G_mousePos && NAME_OFFSET <= G_mousePos.x && G_mousePos.x <= NAME_OFFSET + NAME_WIDTH
        && ymid - (LABEL_HEIGHT / 2) <= G_mousePos.y && G_mousePos.y <= ymid + (LABEL_HEIGHT / 2);

    if (backing) {
        setColor(COLOR_TIMELINE);
        drawQuad(true,
                 NAME_OFFSET, ymid,
                 NAME_WIDTH, LABEL_HEIGHT / 2 * 0.9);
    }
    drawText(sessionName, NAME_OFFSET + NAME_WIDTH - TEXT_INSET, ymid, "right", "middle", NAME_WIDTH - 2 * TEXT_INSET, mouseOverPlayerLabelName ? "#ffff88" : "#ffffff", 14);

    return mouseOverPlayerLabelName;
}

function formatXYZ(val) {
    return val.toFixed(3);
}

function checkXYZTooltip() {
    if (!readyForTooltip(TT_DELAY_XYZ)) {
        return;
    }

    var mpos = G_mousePos;

    if (mpos !== null &&  G_signalY[0] - G_signalHeight / 2 < mpos.y && mpos.y < G_signalY[0] + G_signalHeight / 2) {
        var smpx = Math.round((mpos.x - X_OFFSET) / G_xScale - G_xOffset);

        var tileIndex = Math.floor(smpx / G_config.tile_size);
        var tileId = getTileId(G_zoomLevel, tileIndex);
        var currentTile = G_tileData.get(tileId);

        if (currentTile) {
            var tileSampleIndex = smpx - tileIndex * G_config.tile_size;
            var currentSample = currentTile.data[tileSampleIndex];
            if (currentSample) {
                var text = [];

                for (var ss = 0; ss < G_config.signals.length; ++ ss) {
                    if (!isSignalVisible(ss)) {
                        continue;
                    }

                    if (G_config.signals.length !== 1) {
                        text.push(G_config.signals[ss]);
                    }

                    const AXES = ['X', 'Y', 'Z'];
                    for (var aa = 0; aa < AXES.length; ++ aa) {
                        var component = 3 * ss + aa;

                        if (!isComponentVisible(component)) {
                            continue;
                        }

                        var axis = AXES[aa];
                        var lo = currentSample[component][0];
                        var hi = currentSample[component][1];

                        var axisText = '';
                        if (G_config.signals.length !== 1) {
                            axisText += '  ';
                        }
                        axisText += axis;
                        axisText += ': ';
                        if (Math.abs(lo - hi) < 0.002) {
                            axisText += formatXYZ(0.5 * (lo + hi));
                        } else {
                            axisText += formatXYZ(lo);
                            axisText += ' to ';
                            axisText += formatXYZ(hi);
                        }

                        text.push(axisText);
                    }
                }

                if (text.length > 0) {
                    updateToolTip({ text: text });
                }
            }
        }
    }
}

function resetTooltipTimer(evt) {
    G_tooltipDelayFromTime = Date.now();
}

function readyForTooltip(delay) {
    return !G_tooltipInfo && (delay === 0 || Date.now() - G_tooltipDelayFromTime >= delay);
}

function updateToolTip(info) {
    G_tooltipInfo = info;
}

// Draw tooltip near mouse
function drawTooltip(info) {
    if (info === null) {
        return;
    }

    var text = info.text;

    if (!Array.isArray(text)) {
        text = [text];
    }

    const FONT_SIZE = 14;

    var tooltipHeight = (FONT_SIZE * text.length + 6) / G_canvasHeight;
    var tooltipWidth = 0;
    for (var ii = 0; ii < text.length; ++ ii) {
        tooltipWidth = Math.max(tooltipWidth, measureTextWidth(text[ii], FONT_SIZE));
    }
    tooltipWidth += 2 * TEXT_INSET;

    var tooltipX = clamp(G_mousePos.x, 0, 1.0 - tooltipWidth);
    var tooltipY = 0.01 + G_mousePos.y + tooltipHeight * 0.5;

    G_textCtxOffscreen.fillStyle = COLOR_TOOLTIP;
    G_textCtxOffscreen.fillRect(tooltipX * G_canvasWidth, (1.0 - (tooltipY + 0.5 * tooltipHeight)) * G_canvasHeight, tooltipWidth * G_canvasWidth, tooltipHeight * G_canvasHeight);

    for (var ii = 0; ii < text.length; ++ ii) {
        drawText(text[ii], tooltipX + TEXT_INSET, tooltipY - ((ii - text.length / 2) * FONT_SIZE + 2) / G_canvasHeight, "left", "top", tooltipWidth, "#ffffff", FONT_SIZE);
    }
}

// Draw all of the given labels at the starting y
function drawLabels(sessionName, ymid, labels, highlightRange) {
    if (!G_config) {
        return;
    }

    // Used to convert the label's raw data points to data points at the current zoom level
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    // Variables for displaying indication of small labels and gaps
    var lastSmallLoX = null;
    var lastSmallHiX = null;
    var lastSmallHasGap = false;
    var lastSmallColors = [];

    var mouseOnLabel = null; // information on the label the mouse is over, if any
    var textXCutoff = 0.0; // point before which we should not draw label text

    // Construct a list of the label types that should not be displayed
    var visibleLabelsLookup = getVisibleLabels();

    // find the labels to show
    var visibleLabels = [];
    var anyOverlap = false;
    for (var ll = 0; ll < labels.length; ++ ll) {
        var label = labels[ll];

        var lookupName = label.label;
        if (G_labelColors[lookupName] == undefined) {
            lookupName = "OTHER";
        }

        if (visibleLabelsLookup[lookupName] !== undefined) {
            visibleLabels.push(label);
        }

        if (ll + 1 < labels.length && label.hi > labels[ll + 1].lo) {
            anyOverlap = true;
        }
    }

    if (anyOverlap) {
        var errorlabel = {
            lo: 0,
            hi: G_config.length,
            label: "[overlapping labels]"
        };
        visibleLabels = [errorlabel];
    }

    // Go through all labels and gaps to be drawn
    for (var ll = 0; ll < visibleLabels.length * 2 - 1; ++ ll) {
        // even: label, odd: gap
        var slo;
        var shi;
        var name;
        var detail;
        var color;
        var isgap;
        var isempty;
        if (ll % 2 === 0) {
            var label = visibleLabels[ll / 2];
            slo = label.lo;
            shi = label.hi;
            name = label.label;
            detail = label.detail;
            color = getLabelColor(label.label);
            isgap = false;
            isempty = false;
        } else {
            var labelLo = visibleLabels[(ll - 1) / 2];
            var labelHi = visibleLabels[(ll - 1) / 2 + 1];
            slo = labelLo.hi;
            shi = labelHi.lo;
            name = 'NONE';
            detail = null;
            color = COLOR_CANVAS_BACKGROUND;
            isgap = true;
            isempty = (shi <= slo);
        }

        if (isgap && isempty) {
            continue;
        }

        // Determine label coordinates
        var lo = slo / zoom;
        var hi = shi / zoom;

        var left = G_xScale * (G_xOffset + lo) + X_OFFSET;
        var width = G_xScale * (hi - lo);

        var xlo = left;
        var xhi = left + width;

        // Draw label if needed
        const BIGSIZE = 5;
        var isBig = (G_xScale * (hi - lo) * G_canvasWidth) >= BIGSIZE;

        if (isBig) {
            // Draw small label summary, if needed
            if (lastSmallLoX != null) {
                var sleft = lastSmallLoX;
                var swidth = lastSmallHiX - lastSmallLoX;
                if (sleft + swidth >= -0.01 && 1.01 > sleft) {

                    var gapX0 = sleft - LABEL_INDICATOR_OVERHANG;
                    var gapWidth= swidth + 2 * LABEL_INDICATOR_OVERHANG;
                    var gapY0 = ymid + LABEL_HEIGHT / 2 + LABEL_INDICATOR / 2;
                    var gapHeight = LABEL_INDICATOR / 2;

                    setColor(lastSmallHasGap ? COLOR_SMALL_GAP : COLOR_SMALL_LABEL);
                    drawQuad(true, gapX0, gapY0, gapWidth, gapHeight);
                    setColor(averageColor(lastSmallColors));
                    drawQuad(true,
                             sleft, ymid,
                             swidth, LABEL_HEIGHT / 2);

                    // Draw tooltip if mouse is hovering over small gap indicator
                    var mouseOverGapIndicator = G_mousePos && gapX0 <= G_mousePos.x && G_mousePos.x <= gapX0 + gapWidth
                        && gapY0 - (gapHeight * 2) <= G_mousePos.y && G_mousePos.y <= gapY0;

                    if (mouseOverGapIndicator && readyForTooltip(TT_DELAY_SUMMARY)) {
                        updateToolTip({ text: lastSmallHasGap ? TT_SUMMARY_WITH_GAP : TT_SUMMARY_WITHOUT_GAP });
                    }
                }
            }
            lastSmallLoX = null;
            lastSmallHiX = null;
            lastSmallHasGap = false;
            lastSmallColors = [];

            // Draw label itself
            if (left + width >= -0.01 && 1.01 > left) {
                if (!isgap) {
                    setColor(color);
                    drawQuad(true,
                             left, ymid,
                             width, LABEL_HEIGHT / 2);

                    setColor(color, 1.2);
                    drawQuad(true,
                             left, ymid,
                             TINY_SIZE, LABEL_HEIGHT / 2);
                }
            }
        } else {
            // Remember small labels not drawn
            if (lastSmallLoX != null) {
                lastSmallLoX = Math.min(lastSmallLoX, xlo);
                lastSmallHiX = Math.max(lastSmallHiX, xhi);
            } else {
                lastSmallLoX = xlo;
                lastSmallHiX = xhi;
            }
            lastSmallHasGap = lastSmallHasGap || isgap;
            addLabel(lastSmallColors, name, Math.max(1, shi - slo) * (isgap ? 0.25 : 1.0));
        }

        // Handle the text component of this label
        if (!isgap) {
            if (left + width >= -0.01 && 1.01 > left) {
                var text = name;
                var textx = Math.max(NAME_OFFSET + NAME_WIDTH, left) + TEXT_INSET;
                var textxmax = (left + width) - TEXT_INSET;
                var texty = ymid;
                var maxTextWidth = textxmax - textx;
                const TEXT_WIDTH_TO_SHOW = 0.02;

                var mouseOverLabel = G_mousePos && left <= G_mousePos.x && G_mousePos.x <= left + width &&
                    ymid - LABEL_HEIGHT / 2 <= G_mousePos.y && G_mousePos.y <= ymid + LABEL_HEIGHT / 2 &&
                    G_mousePos.x > NAME_OFFSET + NAME_WIDTH + TEXT_INSET;

                if (mouseOverLabel && G_mouseAction === MOUSE_COPY_LABEL) {
                    setCurrentLabel(name);
                    G_mouseAction = MOUSE_COPY_LABEL_COMPLETE;
                }

                if (detail !== null && detail !== undefined) {
                    if (mouseOverLabel && readyForTooltip(TT_DELAY_SUMMARY)) {
                        updateToolTip({ text: detail });
                    }
                }

                var canShowText = false;
                var textWidth = undefined;
                if (maxTextWidth >= TEXT_WIDTH_TO_SHOW) {
                    textWidth = measureTextWidth(text, 18);
                    if (textWidth < maxTextWidth * 1.25) {
                        canShowText = true;
                    }
                }

                if (!mouseOnLabel && mouseOverLabel && (G_mouseAction === MOUSE_COPY_LABEL || G_mouseAction === MOUSE_COPY_LABEL_COMPLETE || G_mouseAction === null)) {
                    var usemaxtextwidth = maxTextWidth;
                    if (!canShowText) {
                        usemaxtextwidth = undefined;
                    }
                    if (G_mouseDown && G_mouseAction === null) {
                        text += ": ";
                        text += dateStringFromSample(slo, true, false, false);
                        text += " - ";
                        text += dateStringFromSample(shi, true, false, false);
                        usemaxtextwidth = undefined;
                        textWidth = measureTextWidth(text, 18);
                        highlightRange.lo = slo;
                        highlightRange.hi = shi;
                    }

                    if (textWidth === undefined) {
                        textWidth = measureTextWidth(text, 18);
                    }
                    textXCutoff = textx + textWidth + TEXT_INSET;
                    mouseOnLabel = { text: text, textx: textx, texty: texty, maxtextwidth: usemaxtextwidth, lo: slo, hi: shi };
                } else {
                    if (canShowText && textx > textXCutoff) {
                        drawText(text, textx, texty, "left", "middle", maxTextWidth, "#ffffff", 18, true);
                    }
                }
            }
        }
    }

    // Draw final small label summary, if needed
    if (lastSmallLoX != null) {

        var sleft = lastSmallLoX;
        var swidth = lastSmallHiX - lastSmallLoX;
        if (sleft + swidth >= -0.01 && 1.01 > sleft) {

            var gapX0 = sleft - LABEL_INDICATOR_OVERHANG;
            var gapWidth= swidth + 2 * LABEL_INDICATOR_OVERHANG;
            var gapY0 = ymid + LABEL_HEIGHT / 2 + LABEL_INDICATOR / 2;
            var gapHeight = LABEL_INDICATOR / 2;

            setColor(lastSmallHasGap ? COLOR_SMALL_GAP : COLOR_SMALL_LABEL);
            drawQuad(true, gapX0, gapY0, gapWidth, gapHeight);

            setColor(averageColor(lastSmallColors));
            drawQuad(true,
                     sleft, ymid,
                     swidth, LABEL_HEIGHT / 2);

            // Draw tooltip if mouse is hovering over small gap indicator
            var mouseOverGapIndicator = G_mousePos && gapX0 <= G_mousePos.x && G_mousePos.x <= gapX0 + gapWidth
                && gapY0 - gapHeight <= G_mousePos.y && G_mousePos.y <= gapY0;

            if (mouseOverGapIndicator && readyForTooltip(TT_DELAY_SUMMARY)) {
                updateToolTip({ text: lastSmallHasGap ? TT_SUMMARY_WITH_GAP : TT_SUMMARY_WITHOUT_GAP });
            }
        }
    }
    lastSmallLoX = null;
    lastSmallHiX = null;

    // Turn the label text yellow if the user is hovering over the label
    if (mouseOnLabel) {
        drawText(mouseOnLabel.text, mouseOnLabel.textx, mouseOnLabel.texty, "left", "middle", mouseOnLabel.maxtextwidth, "#ffff88", 18, true);
    }

    var clickedOnLabelName = drawLabelName(sessionName, ymid, true);
    if (clickedOnLabelName && G_mouseAction === MOUSE_COPY_LABEL) {
        updateLabelsLocal(true, labels);
        G_mouseAction = MOUSE_COPY_LABEL_COMPLETE;
    }
}

function drawTime(sample, elsc, elms, includesample, zoom, ymid, yheight, mouseHover, showDayCount = false) {
    var displayString = dateStringFromSample(sample, includesample, elsc, elms);

    // Get day count for the given sample
    if (showDayCount) {
        var sampleDate = new Date(G_config.start_time_ms + (1000 * (sample / G_config.sample_rate)));
        var dayCount = G_startDayIdx + datediff(G_startDate, sampleDate);
        displayString = "Day " + dayCount + ": " + displayString;
    }

    var smpx = G_xScale * (G_xOffset + (sample / zoom)) + X_OFFSET;

    if (mouseHover) {
        drawQuad(true,
                 smpx - REALLY_TINY_SIZE / 2, G_signalY[0],
                 REALLY_TINY_SIZE, G_signalHeight/2);
    }

    drawQuad(true,
             smpx - TINY_SIZE / 2, ymid,
             TINY_SIZE, yheight);
    drawText(displayString, smpx + TEXT_INSET, ymid, "left", "middle", undefined, COLORH_TIMELINE_TEXT, 14);
}

function checkMouseOnLabelEdge() {
    G_mouseAdjust = null;

    const DELTA = 0.003;

    let y_mid = (G_signalY[0] - G_signalHeight / 2 - LABEL_GAP - LABEL_INDICATOR - LABEL_HEIGHT / 2 - TIMELINE_HEIGHT);
    if (!G_mousePos || G_mousePos.y < y_mid - LABEL_HEIGHT / 2 || G_mousePos.y > y_mid + LABEL_HEIGHT / 2) {
        G_glCanvas.style.cursor = "default";
        return;
    }

    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    var closest = null;
    var closestLeft = null;
    var closestRight = null;
    for (var ll = 0; ll < G_labelsLocal.length; ++ ll) {
        const label = G_labelsLocal[ll];

        var lo = G_xScale * (G_xOffset + (label.lo / zoom)) + X_OFFSET;
        var dlo = Math.abs(G_mousePos.x - lo);
        if (dlo <= DELTA && (closest === null || dlo < closest)) {
            closest = dlo;
            closestLeft = null;
            closestRight = ll;
            if (ll - 1 >= 0 && G_labelsLocal[ll - 1].hi === label.lo) {
                closestLeft = ll - 1;
            }
        }

        var hi = G_xScale * (G_xOffset + (label.hi / zoom)) + X_OFFSET;
        var dhi = Math.abs(G_mousePos.x - hi);
        if (dhi <= DELTA && (closest === null || dhi < closest)) {
            closest = dhi;
            closestLeft = ll;
            closestRight = null;
            if (ll + 1 < G_labelsLocal.length && G_labelsLocal[ll + 1].lo == label.hi) {
                closestRight = ll + 1;
            }
        }
    }

    if (closest === null) {
        G_glCanvas.style.cursor = "default";
    } else {
        G_mouseAdjust = { left: null, right: null};
        if (closestLeft !== null) {
            G_mouseAdjust.left = {
                lo: G_labelsLocal[closestLeft].lo,
                hi: G_labelsLocal[closestLeft].hi,
                label: G_labelsLocal[closestLeft].label,
                detail: G_labelsLocal[closestLeft].detail,
                index: closestLeft
            }
        }
        if (closestRight !== null) {
            G_mouseAdjust.right = {
                lo: G_labelsLocal[closestRight].lo,
                hi: G_labelsLocal[closestRight].hi,
                label: G_labelsLocal[closestRight].label,
                detail: G_labelsLocal[closestRight].detail,
                index: closestRight
            }
        }
        G_glCanvas.style.cursor = "ew-resize";
    }
}

// Draw the axes on the canvas for the signal image
function drawAxes(left, right) {
    setColor(G_modeColorMap.yaxis);

    // Draw the y-axis
    drawQuad(false,
             Y_AXIS_POS, G_signalY[0],
             REALLY_TINY_SIZE, G_signalHeight/2);
    drawYAxisMarkers();

    setColor(G_modeColorMap.xaxis);

    // Draw the x-axis
    drawQuad(false,
             left, G_signalY[0],
             right - left, REALLY_TINY_SIZE);
}

// Draw the indicator bar. Pass parameters of the left and right end point of the highlight.
function drawIndicatorBar(zoom) {
    const YMID = 0.025;
    const HEIGHT = 0.05;
    const MIN_SIZE = 0.005;

    setColor(COLOR_TIMELINE, 0.5);
    drawQuad(true,
             0.0, YMID,
             1.0, HEIGHT / 2);

    var smplo = Math.round((0.0 - X_OFFSET) / G_xScale - G_xOffset);
    var smphi = Math.round((1.0 - X_OFFSET) / G_xScale - G_xOffset);
    var barlo = clamp(smplo / (G_config.length / zoom), 0.0, 1.0);
    var barhi = clamp(smphi / (G_config.length / zoom), 0.0, 1.0);
    if (barhi - barlo < MIN_SIZE) {
        barlo = 0.5 * (barhi + barlo) - MIN_SIZE / 2.0;
        barhi = barlo + MIN_SIZE;
    }
    setColor(COLOR_TIMELINE, 1.5);
    drawQuad(true,
             barlo, YMID,
             barhi - barlo, HEIGHT / 2);

    if (G_zoomInHistory) {
        var hbarlo = clamp(G_zoomInHistory.smplo / G_config.length, 0.0, 1.0);
        var hbarhi = clamp(G_zoomInHistory.smphi / G_config.length, 0.0, 1.0);
        if (hbarhi - hbarlo < MIN_SIZE) {
            hbarlo = 0.5 * (hbarhi + hbarlo) - MIN_SIZE / 2.0;
            hbarhi = hbarlo + MIN_SIZE;
        }

        setColor(COLOR_TIMELINE);
        drawQuad(true,
                 hbarlo, YMID - HEIGHT * 1 / 3,
                 hbarhi - hbarlo, HEIGHT / 6);
    }
}

// This draws the Y axis markers and its labels.
function drawYAxisMarkers() {
    var nMarkers = G_magnitude;
    var markerDistance = (G_signalHeight / 2) / nMarkers;

    for(var ii = 0; ii <= nMarkers; ++ ii){
        // Draws positive markers
        drawQuad(false,
                 Y_AXIS_POS - Y_AXIS_TICK, G_signalY[0] + (markerDistance * ii),
                 Y_AXIS_TICK, REALLY_TINY_SIZE);
        // Draws negative markers
        drawQuad(false,
                 Y_AXIS_POS - Y_AXIS_TICK, G_signalY[0] - (markerDistance * ii),
                 Y_AXIS_TICK, REALLY_TINY_SIZE);
    }

    drawText("+" + G_magnitude + "g", Y_AXIS_POS - Y_AXIS_TICK, G_signalY[0] + G_signalHeight / 2, "right", "top", undefined, G_modeColorMap.yaxisText, 14);
    drawText("-" + G_magnitude + "g", Y_AXIS_POS - Y_AXIS_TICK, G_signalY[0] - G_signalHeight / 2, "right", "bottom", undefined, G_modeColorMap.yaxisText, 14);
}


// Draw the horizontal timeline
function drawTimeline(left, right, ymid, yheight, mylo, myhi) {
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    setColor(COLOR_TIMELINE, 0.5);
    drawQuad(true,
             0.0, ymid,
             1.0, yheight);

    setColor(COLOR_TIMELINE);
    drawQuad(true,
             left, ymid,
             right - left, yheight);

    var considerMouseOverTimeline = ((G_mousePos && mylo <= G_mousePos.y && G_mousePos.y <= myhi) || G_mouseAction === MOUSE_PAN || G_mouseAction === MOUSE_CREATE_LABEL);

    if (G_config.start_time_ms) { // maybe unneeded check
        var SCALES = getScales(G_config.sample_rate);

        var scale = SCALES[0];
        for (var ii = 1; ii < SCALES.length; ++ ii) {
            if (G_xScale * (scale[2] / zoom) > 0.20) {
                break;
            }
            scale = SCALES[ii];
        }

        var elsc = scale[0];
        var elms = scale[1];
        var scalesmp = scale[2];

        var startSample = (G_config.start_time_ms + (1000 * 60 * 60 * 19)) * G_config.sample_rate / 1000; // TODO: offset?
        var startOffset = scalesmp - (startSample % scalesmp);

        var losmp = (((0.0 - X_OFFSET) / G_xScale) - G_xOffset) * zoom;
        losmp = Math.max(0, losmp);
        losmp = Math.floor(losmp / scalesmp) * scalesmp + startOffset;
        if (losmp >= scalesmp) {
            losmp -= scalesmp;
        }
        var hismp = losmp + (6 * scalesmp);
        hismp = Math.min(hismp, G_config.length - scalesmp / 4);

        setColor(COLOR_TIMELINE_TEXT);
        for (var smp = losmp; smp < hismp; smp += scalesmp) {
            var skip = false;
            var smpx = G_xScale * (G_xOffset + (smp / zoom)) + X_OFFSET;
            if (G_mousePos && smpx - 0.20 <= G_mousePos.x && G_mousePos.x <= smpx + 0.12 && left <= G_mousePos.x && G_mousePos.x <= right && considerMouseOverTimeline) {
                skip = true;
            }

            if (!skip) {
                drawTime(smp, elsc, elms, false, zoom, ymid, yheight, false, true);
            }
        }
    }

    if (G_mousePos && left <= G_mousePos.x && G_mousePos.x <= right && considerMouseOverTimeline) {
        var sample = Math.round(((G_mousePos.x - X_OFFSET) / G_xScale) - G_xOffset) * zoom;
        if (sample >= 0 && sample < G_config.length) {
            setColor(G_modeColorMap.yaxis);
            drawTime(sample, false, false, true, zoom, ymid, yheight, true, true);
        }
    }
}

function drawScene() {
    window.requestAnimationFrame(doDrawScene);

    // Restore focus to the document body, unless specified otherwise
    if (document.activeElement !== document.getElementById('importdatadropdown')
        && document.activeElement !== document.getElementById('sessionsdropdown')
        && document.activeElement !== document.getElementById('newlabelset')) {
        document.activeElement.blur();
    }

}

// Render the page
function doDrawScene() {
    var red = COLOR_CANVAS_BACKGROUND[0];
    var green = COLOR_CANVAS_BACKGROUND[1];
    var blue = COLOR_CANVAS_BACKGROUND[2];

    G_glCtx.clearColor(red, green, blue, 1.0);
    G_glCtx.clear(G_glCtx.COLOR_BUFFER_BIT);

    G_textCtxOffscreen.clearRect(0, 0, G_canvasWidth, G_canvasHeight);

    if (!G_config) {
        G_textCtx.clearRect(0, 0, G_canvasWidth, G_canvasHeight);
        return;
    }

    G_tooltipInfo = null;

    // Draw the border of the main image
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);

    var left  = Math.max(0.0, G_xScale * (G_xOffset + 0) + X_OFFSET);
    var right = Math.min(1.0, G_xScale * (G_xOffset + ((G_config.length - 1) / zoom)) + X_OFFSET);

    setColor(G_modeColorMap.border);
    drawQuad(true,
             0.0, G_signalY[0],
             1.0, G_signalHeight / 2);

    setColor(G_modeColorMap.background);
    drawQuad(true,
             left, G_signalY[0],
             right - left, G_signalHeight / 2);

    // Draw the X and Y axis to show magnitude.
    drawAxes(left, right);

    // Draw the indicator bar with highlight suggesting where in the data set you are.
    drawIndicatorBar(zoom);

    // Draw the timestamps (behind the signal)
    drawTimeline(left, right, G_signalY[0] - G_signalHeight / 2 - TIMELINE_HEIGHT / 2, TIMELINE_HEIGHT / 2, G_signalY[0] - G_signalHeight / 2 - TIMELINE_HEIGHT, G_signalY[0] + G_signalHeight / 2);

    // Scissor box to clip the signal
    G_glCtx.enable(G_glCtx.SCISSOR_TEST);
    G_glCtx.scissor(0, G_canvasHeight * (G_signalY[0] - G_signalHeight / 2),
                 G_canvasWidth, G_canvasHeight * G_signalHeight);

    // Load the tiles to be drawn if necessary
    var tileIndex = -Math.floor((G_xOffset + X_OFFSET / G_xScale) / G_config.tile_size);
    for (var tt = -1; tt <= 3; ++ tt) {
        if (G_zoomLevel > 0) {
            for (var ff = 0; ff < G_config.tile_subsample; ++ ff) {
                fetchTileIfNeeded(G_zoomLevel - 1, Math.floor((tileIndex + tt) * G_config.tile_subsample + ff));
            }
        }
        if (G_zoomLevel < G_config.zoom_max) {
            for (var ff = -1; ff <= 1; ++ ff) {
                fetchTileIfNeeded(G_zoomLevel + 1, Math.floor((tileIndex + tt) / G_config.tile_subsample + ff));
            }
        }

        fetchTileIfNeeded(G_zoomLevel, tileIndex + tt);
        drawTile(G_zoomLevel, tileIndex + tt, G_fetchingLabelsLocal);
    }

    G_glCtx.disable(G_glCtx.SCISSOR_TEST);

    var displayedlabels = 0;
    var anyNotDisplayed = false;
    var highlightRange = {};

    var labelY = G_signalY[0] - G_signalHeight / 2 - LABEL_GAP - LABEL_INDICATOR - LABEL_HEIGHT / 2 - TIMELINE_HEIGHT;
    const LABEL_ADVANCE = -(LABEL_GAP + LABEL_INDICATOR + LABEL_HEIGHT);

    // Draw your local labels
    drawLabels("Yours (" + G_session + ")", labelY, G_labelsLocal, highlightRange);
    labelY += LABEL_ADVANCE;

    // Draw your remote labels
    if (G_labelsRemoteYours) {
        var labels = G_labelsRemoteYours;
        var sessionName = "Yours (last saved)";

        if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
            drawLabels(sessionName, labelY, labels.labels, highlightRange);
            labelY += LABEL_ADVANCE;
            ++ displayedlabels;
        } else {
            anyNotDisplayed = true;
        }
    }

    for (var ll = 0; ll < G_labelsRemoteNotes.length; ++ ll) {
        var index = ll;
        var labels = G_labelsRemoteNotes[index];

        var sessionName = labels.session.substring(0, 5);
        if (labels.source) {
            sessionName = labels.source.substring(0, 6) + " " + sessionName;
        }

        if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
            drawLabels(sessionName, labelY, labels.labels, highlightRange);
            labelY += LABEL_ADVANCE;
            ++ displayedlabels;
        } else {
            anyNotDisplayed = true;
        }
    }

    // Display ground truth score and draw ground truth labels
    if (G_labelsRemoteGroundTruth !== null) {
        if (G_groundTruthScore === null) {
            var scoreText = 'Score: ERROR';
        } else {
            if (G_mturkState === 'ADVANCE' || G_mturkState === 'TUTORIAL' ||
                G_dataset === mturkGetFirstDataset() || (G_mturkState === 'SUBMIT' &&
                    MTURK_TUTORIAL_DATASETS.indexOf(G_dataset) >= 0 && G_modeConfig[MC_MODE] === MODE_MTURK)) {
                var scoreText = 'Score: ' + Math.round(G_groundTruthScore)  + '%';
            }
        }
        if (scoreText !== undefined) {
            drawText(scoreText, 0.5, 0.9875, "center", "top", undefined, COLORH_TIMELINE_TEXT, 32);
        }

        if (!G_modeConfig[MC_HIDE_GROUND_TRUTH_LABELS] || MTURK_TUTORIAL_DATASETS.indexOf(G_dataset) >= 0 || G_mturkState === 'ADVANCE') {
            if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
                drawLabels("Truth", labelY, G_labelsRemoteGroundTruth.labels, highlightRange);
                labelY += LABEL_ADVANCE;
                ++ displayedlabels;
            } else {
                anyNotDisplayed = true;
            }
        }
    }

    // Draw algorithm labels
    if (!G_modeConfig[MC_HIDE_REMOTE_ALGO_LABELS]) {
        for (var ll = 0; ll < G_labelsRemoteOtherAlgo.length; ++ll) {
            if (!G_modeConfig[MC_HIDE_REMOTE_PLAYER_LABELS] && ll > 0) {
                anyNotDisplayed = true;
                break;
            }

            var index = (ll + G_labelsRemoteStartIndexAlgo) % G_labelsRemoteOtherAlgo.length;
            var labels = G_labelsRemoteOtherAlgo[index];

            var sessionName = labels.session.substring(0, 5);
            if (labels.source) {
                sessionName = labels.source.substring(0, 6) + " " + sessionName;
            }

            if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
                drawLabels(sessionName, labelY, labels.labels, highlightRange);
                labelY += LABEL_ADVANCE;
                ++displayedlabels;
            } else {
                anyNotDisplayed = true;
            }
        }
    }

    // Draw remote player labels
    if (!G_modeConfig[MC_HIDE_REMOTE_PLAYER_LABELS]) {
        for (var ll = 0; ll < G_labelsRemoteOtherPlayer.length; ++ ll) {
            var index = (ll + G_labelsRemoteStartIndexPlayer) % G_labelsRemoteOtherPlayer.length;
            var labels = G_labelsRemoteOtherPlayer[index];

            var sessionName = labels.session.substring(0, 5);
            if (labels.source) {
                sessionName = labels.source.substring(0, 6) + " " + sessionName;
            }

            if (displayedlabels < MAX_REMOTE_LABEL_DISPLAY) {
                drawLabels(sessionName, labelY, labels.labels, highlightRange);
                labelY += LABEL_ADVANCE;
                ++ displayedlabels;
            } else {
                anyNotDisplayed = true;
            }
        }
    }

    // Draw more labels indicator
    if (anyNotDisplayed) {
        drawLabelName("(more...)", labelY + LABEL_INDICATOR, false);
    }

    if (highlightRange.lo !== undefined && highlightRange.hi !== undefined) {
        setColor(G_modeColorMap.yaxis);
        drawQuad(false,
                 G_xScale * (G_xOffset + highlightRange.lo / zoom) + X_OFFSET, G_signalY[0],
                 G_xScale * (highlightRange.hi - highlightRange.lo) / zoom, G_signalHeight / 2);
    }


    // Draw the box the user is selecting
    var pendingLabels = getPendingLabels();

    for (var ll = 0; ll < pendingLabels.length; ++ ll) {
        const lbl = pendingLabels[ll];

        var color = getLabelColor(lbl.label);
        setColor(color, 1.2);
        drawQuad(false,
                 G_xScale * (G_xOffset + lbl.lo / zoom) + X_OFFSET, G_signalY[0],
                 G_xScale * (lbl.hi - lbl.lo) / zoom, G_signalHeight / 2);
        drawQuad(true,
                 G_xScale * (G_xOffset + lbl.lo / zoom) + X_OFFSET, G_signalY[0] - G_signalHeight / 2 - TIMELINE_HEIGHT - LABEL_GAP - LABEL_INDICATOR - LABEL_HEIGHT / 2,
                 G_xScale * (lbl.hi - lbl.lo) / zoom, LABEL_HEIGHT / 2);
    }

    if (G_mouseAction === MOUSE_COPY_LABEL) {
        G_mouseAction = MOUSE_COPY_LABEL_COMPLETE;
    }

    checkXYZTooltip();

    // Draw tooltip if needed
    drawTooltip(G_tooltipInfo);

    // draw offscreen text
    G_textCtx.clearRect(0, 0, G_canvasWidth, G_canvasHeight);
    G_textCtx.drawImage(G_textCanvasOffscreen, 0, 0);

}

function updateGroundTruthScore() {
    if (G_labelsRemoteGroundTruth !== null && G_labelsRemoteGroundTruth !== 'ERROR') {
        G_groundTruthScore = calculateGroundTruthScore(G_labelsLocal, G_labelsRemoteGroundTruth.labels);
    } else {
        G_groundTruthScore = null;
    }
}

// Calculate Ground Truth Score
function calculateGroundTruthScore(labelsLocal, labelsGroundTruth) {

    let totalSamples = G_config.length;
    let incorrectSamples = 0;
    let configLabels = [];
    let expectedTruthLabels = [];

    // Get config labels available to user
    for (var i = 0; i < G_config.labels.length; i++) {
        configLabels.push(G_config.labels[i].label);
    }

    // Get ground truth labels that the user should have labeled
    for (var tl = 0; tl < labelsGroundTruth.length; ++tl) {
        if (configLabels.indexOf(labelsGroundTruth[tl].label) >= 0) {
            expectedTruthLabels.push(labelsGroundTruth[tl]);
        }
    }

    // Penalize mislabeled sections
    for (var tl = 0; tl < labelsGroundTruth.length; ++tl){
        let truthStart = labelsGroundTruth[tl].lo;
        let truthEnd = labelsGroundTruth[tl].hi;
        for (var ll = 0; ll < labelsLocal.length; ll++){
            let localStart = labelsLocal[ll].lo;
            let localEnd = labelsLocal[ll].hi;

            if (localStart > truthEnd || truthStart > localEnd) {
                continue;
            } else if (labelsLocal[ll].label !== labelsGroundTruth[tl].label) {
                let lo = Math.max(localStart, truthStart);
                let hi = Math.min(localEnd, truthEnd);
                incorrectSamples += (hi - lo);
            }
        }
    }

    // Penalize sections where there are gaps when there should be labels
    for (var tl = 0; tl < expectedTruthLabels.length; ++tl) {
        let truthStart = expectedTruthLabels[tl].lo;
        let truthEnd = expectedTruthLabels[tl].hi;
        let missedSamples = truthEnd - truthStart;

        for (var ll = 0; ll < labelsLocal.length; ++ll) {

            let localStart = labelsLocal[ll].lo;
            let localEnd = labelsLocal[ll].hi;

            if (localStart > truthEnd || truthStart > localEnd) {
                continue;
            } else {
                let lo = Math.max(localStart, truthStart);
                let hi = Math.min(localEnd, truthEnd);
                missedSamples -= (hi - lo);
            }
        }

        incorrectSamples += missedSamples;
    }

    let correctSamples = totalSamples - incorrectSamples;
    return (correctSamples / totalSamples) * 100;
}

// Generate a random id
function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
                                                (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16));
}

// Generate a random id
function makeId() {
    var possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';

    var text = '';
    for (var ii = 0; ii < 9; ++ii) {
        var rnd = crypto.getRandomValues(new Uint8Array(1))[0] / 255.0;
        text += possible.charAt(clamp(Math.floor(rnd * possible.length), 0, possible.length - 1));
    }

    var check = 0;
    for (var ii = 0; ii < text.length; ++ii) {
        check += text.charCodeAt(ii);
    }
    text += (check % 16).toString(16).toUpperCase();

    return text;
}

function loadDataset(session, dataset) {
    window.location.href = 'signaligner.html?session=' + session + '&dataset=' + dataset;
}

function loadPage(page) {
    window.location.href = page;
}

// Return the first dataset
function getDefaultDataset() {
    return 'test_sin30min';
}

// Get the id of the given tile at the given zoom level
function getTileId(zoom, tile) {
    return "z" + zoom.toString().padStart(2, '0') + "t" + tile.toString().padStart(6, '0');
}

function getZoomLevel() {
    return (G_zoomLevel != null && G_zoomLevelIntermediate != null) ? this.G_zoomLevel.toString() + ':' + this.G_zoomLevelIntermediate.toString().padStart(2, '0') : ''
}

function getAmountOfTimeVisibleString() {
    var zoom = Math.pow(G_config.tile_subsample, G_zoomLevel);
    var smplo = zoom * Math.round((0.0 - X_OFFSET) / G_xScale - G_xOffset);
    var smphi = zoom * Math.round((1.0 - X_OFFSET) / G_xScale - G_xOffset);
    var smploc = clamp(smplo, 0, G_config.length);
    var smphic = clamp(smphi, 0, G_config.length);

    var smpSeconds = (smphi - smplo) / G_config.sample_rate;
    var visibleSeconds = (smphic - smploc) / G_config.sample_rate;
    if (smpSeconds >= 60 * 60 * 24) {
        return (visibleSeconds / (60 * 60 * 24)).toFixed(1) + ' days';
    } else if (smpSeconds >= 60 * 60) {
        return (visibleSeconds / (60 * 60)).toFixed(1) + ' hours';
    } else if (smpSeconds >= 60) {
        return (visibleSeconds / (60)).toFixed(1) + ' minutes';
    } else {
        return (visibleSeconds).toFixed(1) + ' seconds';
    }
}

function updateMessageDisplay() {
    var message = getAmountOfTimeVisibleString();
    showText("message", message);
}

function genericLogObject() {
    return {
        time: Date.now(),
        dataset: G_dataset,
        session: G_session,
        run: G_run,
        token: makeId()
    };
}

// Send the given data to the server
function sendLabels() {
    var data = genericLogObject();
    data.source = G_modeConfig[MC_MODE] === MODE_MTURK ? SOURCE_MTURK : G_modeConfig[MC_MODE] === MODE_EXPERT ? SOURCE_EXPERT : SOURCE_PLAYER;
    data.labels = G_labelsLocal;

    requestToServer('reportlabels', data, 3, onSendLabelsSuccess, onSendLabelsError);
}

function onSendLabelsError() {
    alert("Error contacting server. Please reconnect to the internet and then Save and update.");
}

function onSendLabelsSuccess(response) {
    G_labelsRemoteYours = JSON.parse(response);
}

// Send the given data to the server
function sendLog(type, info) {
    var data = genericLogObject();
    data.type = type;
    data.info = info;

    requestToServer('log', data, 0, null, null, null);
}

// Return the average color from the map of label weights
function averageColor(labels) {
    var rr = 0.0;
    var gg = 0.0;
    var bb = 0.0;
    var total = 0.0;

    for (var lbl in labels) {
        var weight = labels[lbl];
        var clr;
        if (lbl === 'NONE') {
            clr = [0.0, 0.0, 0.0];
        } else {
            clr = getLabelColor(lbl);
        }
        rr += weight * clr[0];
        gg += weight * clr[1];
        bb += weight * clr[2];
        total += weight;
    }

    if (total < 0.001) {
        return [0.0, 0.0, 0.0];
    } else {
        return [rr / total, gg / total, bb / total];
    }
}

function addLabel(labels, label, weight) {
    if (labels[label] === undefined) {
        labels[label] = 0.0;
    }
    labels[label] += weight;
}

function pad(number) {
    if (number < 10) {
        return '0' + number;
    }
    return number;
}

// Returns the number of days between the given start and end Date objects
function datediff(start, end) {
    var startDate = new Date(start.getUTCFullYear(), start.getUTCMonth(), start.getUTCDate());
    var endDate = new Date(end.getUTCFullYear(), end.getUTCMonth(), end.getUTCDate());
    var diffInMilliseconds = endDate - startDate;
    return Math.round(diffInMilliseconds / (1000 * 60 * 60 * 24));
}

function dateStringFromSample(sample, includesample, elsc, elms) {

    var ret = null;

    if (G_config.start_time_ms) { // maybe unneeded check
        var dt = new Date(G_config.start_time_ms + (1000 * (sample / G_config.sample_rate)));
        var dy = dt.getUTCDay();
        var hr = dt.getUTCHours() > 12 ? dt.getUTCHours() - 12 : dt.getUTCHours();
        hr = hr === 0 ? 12 : hr;
        var ampm = dt.getUTCHours() > 11 ? "PM" : "AM";
        var mn = dt.getUTCMinutes();
        var sc = dt.getUTCSeconds();
        var ms = dt.getUTCMilliseconds();

        ret = "";

        ret += WEEKDAY[dy] + " ";
        ret += pad(hr) + ":" + pad(mn);
        if (!elsc || sc !== 0) {
            ret += ":" + pad(sc);
        }
        if (!elms || ms !== 0) {
            ret += "." + (ms / 1000).toFixed(3).slice(2, 5);
        }
        ret += " " + ampm;

        if (ret.indexOf("NaN") !== -1) {
            ret = null;
        }
    }

    if (ret == null) {
        ret = "" + sample;
    } else if (includesample) {
        ret = ret + " (" + sample + ")";
    }

    return ret;
}

// Get scales
function getScales(sampleRate) {
    return [[0, 0, sampleRate],
            [0, 1, sampleRate * 2],
            [0, 1, sampleRate * 5],
            [0, 1, sampleRate * 10],
            [0, 1, sampleRate * 30],

            [0, 1, sampleRate * 60],
            [1, 1, sampleRate * 60 * 2],
            [1, 1, sampleRate * 60 * 5],
            [1, 1, sampleRate * 60 * 10],
            [1, 1, sampleRate * 60 * 30],

            [1, 1, sampleRate * 60 * 60],
            [1, 1, sampleRate * 60 * 60 * 2],
            [1, 1, sampleRate * 60 * 60 * 5],
            [1, 1, sampleRate * 60 * 60 * 10],

            [1, 1, sampleRate * 60 * 60 * 24],
            [1, 1, sampleRate * 60 * 60 * 24 * 2],
            [1, 1, sampleRate * 60 * 60 * 24 * 5]
           ];
}

// Return the color associated with the given label
function getLabelColor(label) {
    var color = G_labelColors[label];
    if (color == undefined) {
        color = COLOR_LABEL_X;
    }
    return color;
}

// Return a string of the rgb value of the given color
function getColorString(color) {
    var rr = Math.round(Math.min(255, color[0] * 255));
    var gg = Math.round(Math.min(255, color[1] * 255));
    var bb = Math.round(Math.min(255, color[2] * 255));
    var colorString = '#' + rr.toString(16).padStart(2, '0') + gg.toString(16).padStart(2, '0') + bb.toString(16).padStart(2, '0');
    return colorString;
}

// Display the given text on the page in the textarea
function showText(id, text) {
    document.getElementById(id).innerHTML = text;
}

// Return data array to init quad buffer
function getQuadBufferData() {
    return [0.0,  1.0,
            0.0, -1.0,
            1.0, -1.0,
            1.0, 1.0];
}

function logTick() {
    data = {
        tilesLoaded: noOfTilesLoaded(),
        zoom: [G_zoomLevel, G_zoomLevelIntermediate]
    };

    sendLog('tick', data);
}

// Returns the no of tiles loaded till now.
function noOfTilesLoaded() {
    return G_tileData.size;
}

function getWorldMousePos(evt, g_glCanvas) {
    var rect = g_glCanvas.getBoundingClientRect();

    var x = (evt.clientX - rect.left) / g_glCanvas.width;
    var y = 1.0 - (evt.clientY - rect.top) / g_glCanvas.height;
    x = clamp(x, 0.0, 1.0);
    y = clamp(y, 0.0, 1.0);

    return { x: x, y: y };
}

function debugLogMessage(msg) {
    console.debug(msg);
}

// Updates the access time log in map objects and clears cache if exceeded.
function updateAccess(tileId) {
    let currentTimeStamp = new Date();
    let tileData = G_tileData.get(tileId);
    tileData["timestamp"] = currentTimeStamp;
    G_tileData.set(tileId, tileData);

    // Checks if cache needs to be cleared.
    if (G_tileData.size > G_cacheMax) {
        clearCache();
    }
}

// Clears the oldest cache.
function clearCache() {
    let oldestTimeStamp = new Date();
    let tileIdToBeDeleted;
    let tileBuffers;
    for (let [key, value] of G_tileData) {
        let tileId = key;
        let tileData = value;
        if (tileData.timestamp < oldestTimeStamp) {
            tileIdToBeDeleted = tileId;
            oldestTimeStamp = tileData.timestamp;
        }
    }
    // Deletes the buffers if the tile to be deleted had buffers.
    tileBuffers = G_tileData.get(tileIdToBeDeleted).buffers;
    if (typeof tileBuffers != 'undefined'){
        for (let i = 0; i < tileBuffers.length; i++){
            if (G_glCtx.isBuffer(tileBuffers[i])){
                G_glCtx.deleteBuffer(tileBuffers[i]);
            }
        }
    }

    G_tileData.delete(tileIdToBeDeleted);
}

// let timeAfterWhichCacheIsCleared = (delay) => {return new Date(new Date().getTime() - delay*60000)};

// // Clears the cache size to G_cacheMax/2.
// function clearCache() {
//     let localDelay = G_cacheDelay;
//     while (G_tileData.size > (G_cacheMax/2)) {
//         removeTilesFromCache(timeAfterWhichCacheIsCleared(localDelay));
//         localDelay /= 2;
//     }
// }

// // Removes all the tiles with access time before the delay.
// function removeTilesFromCache(timeDelay) {
//     let entries = G_tileData.entries();
//     for (let [key, value] of G_tileData){
//         let tileId = key;
//         let tileData = value;
//         if (tileData.timestamp < timeDelay) {
//             G_tileData.delete(tileId);
//         }
//     }
// }
