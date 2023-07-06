const SCOPES = 'https://www.googleapis.com/auth/drive.readonly';
// TODO(developer): Set to client ID and API key from the Developer Console
const CLIENT_ID = '55814944391-gms412pfcf5lvu31u4i6fvj1easegut1.apps.googleusercontent.com';
const API_KEY = 'AIzaSyCXEn9yP_9kHOeu2izOAe-1_wXDqAaupig';

// TODO(developer): Replace with your own project number from console.developers.google.com.
const APP_ID = '8wPfa1zLbGzoLXP2ISUwGA2a2zSPPztT';

let tokenClient;
let accessToken = null;
let pickerInited = false;
let gisInited = false;


document.getElementById('authorize_button').style.visibility = 'hidden';
document.getElementById('signout_button').style.visibility = 'hidden';
document.getElementById("authorize_button").onclick(()=>{handleAuthClick()});
/**
 * Callback after api.js is loaded.
 */
function gapiLoaded() {
    gapi.load('client:picker', initializePicker);
}

/**
 * Callback after the API client is loaded. Loads the
 * discovery doc to initialize the API.
 */
async function initializePicker() {
    await gapi.client.load('https://www.googleapis.com/discovery/v1/apis/drive/v3/rest');
    pickerInited = true;
    maybeEnableButtons();
}

/**
 * Callback after Google Identity Services are loaded.
 */
function gisLoaded() {
    tokenClient = google.accounts.oauth2.initTokenClient({
        client_id: CLIENT_ID,
        scope: SCOPES,
        callback: '', // defined later
    });
    gisInited = true;
    maybeEnableButtons();
}

/**
 * Enables user interaction after all libraries are loaded.
 */
function maybeEnableButtons() {
    if (pickerInited && gisInited) {
        document.getElementById('authorize_button').style.visibility = 'visible';
    }
}

/**
 *  Sign in the user upon button click.
 */
function handleAuthClick() {
    tokenClient.callback = async (response) => {
        if (response.error !== undefined) {
            throw (response);
        }
        sessionStorage.setItem('access_token', response.access_token)
        // document.getElementById('signout_button').style.visibility = 'visible';
        // document.getElementById('authorize_button').innerText = 'Refresh';
        await createPicker();
    };
    console.log(sessionStorage.getItem('access_token'))
    if (!sessionStorage.getItem('access_token')) {
        // Prompt the user to select a Google Account and ask for consent to share their data
        // when establishing a new session.
        tokenClient.requestAccessToken({ prompt: 'consent' });
    } else {
        // Skip display of account chooser and consent dialog for an existing session.
        tokenClient.requestAccessToken({ prompt: '' });
    }
}

/**
 *  Sign out the user upon button click.
 */
function handleSignoutClick() {
    if (sessionStorage.getItem('access_token')) {
        google.accounts.oauth2.revoke(sessionStorage.getItem('access_token'));
        // document.getElementById('content').innerText = '';
        document.getElementById('authorize_button').innerText = 'Authorize';
        document.getElementById('signout_button').style.visibility = 'hidden';
        sessionStorage.clear();
        window.location.reload()
    }
}

/**
 *  Create and render a Picker object for searching images.
 */
function createPicker() {
    const view = new google.picker.View(google.picker.ViewId.DOCS);
    // view.setMimeTypes('text/plain,application/pdf');
    const picker = new google.picker.PickerBuilder()
        .enableFeature(google.picker.Feature.NAV_HIDDEN)
        .enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
        .setDeveloperKey(API_KEY)
        .setAppId(APP_ID)
        .setOAuthToken(sessionStorage.getItem('access_token'))
        .addView(view)
        .addView(new google.picker.DocsUploadView())
        .setCallback(pickerCallback)
        .build();
    picker.setVisible(true);
}

/**
 * Displays the file details of the user's selection.
 * @param {object} data - Containers the user selection from the picker
 */
async function pickerCallback(data) {
    if (data.action === google.picker.Action.PICKED) {
        let text = `Picker response: \n${JSON.stringify(data, null, 2)}\n`;
        const document = data[google.picker.Response.DOCUMENTS][0];
        const fileId = document[google.picker.Document.ID];
        console.log(fileId);
        await fetch(`http://localhost:3000/get_access?docs_id=${fileId}`).then((response)=>response.json()).
        then((data)=>console.log(data)).
        catch((error)=>console.log(error));
        const res = await gapi.client.drive.files.get({
            'fileId': fileId,
            'fields': '*',
        });
        text += `Drive API response for first document: \n${JSON.stringify(res.result, null, 2)}\n`;
        window.document.getElementById('content').innerText = text;
    }
}