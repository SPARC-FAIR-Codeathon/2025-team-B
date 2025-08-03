(function() {


    const extensionWhitelist = [
        "mat", /* 	MathWorks MATLAB file*/
        "smr", /* 	CED Spike2 binary recording*/
        "csv", /* 	Comma-separated values text (generic)*/
        "adicht", /* 	ADInstruments LabChart binary trace*/
        "hdf5", /* 	Hierarchical Data Format v5 container*/
        "h5", /* 	Same as .hdf5*/
        "ets", /* 	TDT electrophysiology time-series block*/
        "abf", /* 	Molecular Devices Axon Binary File (pClamp)*/
        "rhd", /* 	Intan RHD2000 amplifier data*/
        "nev", /* 	Blackrock NeuroPort event file*/
        "ns5", /* 	Blackrock continuous 30 kHz signal*/
        "ns2", /* 	Blackrock 1 kHz LFP signal*/
        "ns1", /* 	Blackrock low-rate summary signal*/
        "smrx", /* 	CED Spike2 v9+ extended recording*/
        "wav", /* 	Waveform audio (PCM)*/
        "acq", /* 	AxoScope raw acquisition*/
        "tbk", /* 	TDT DataTank “block” metadata*/
        "tdx", /* 	TDT DataTank index (time-stamp)*/
        "tev", /* 	TDT event / continuous data stream*/
        "tin", /* 	TDT Synapse experiment info (zip)*/
        "tnt", /* 	TDT block annotations*/
        "tsq", /* 	TDT global time-stamp table*/
        "eeg", /* 	BrainVision binary signal data*/
        "vmrk", /* 	BrainVision marker/events*/
        "vhdr", /* 	BrainVision header*/
        "sev", /* 	TDT RS4 single-channel stream*/
        "sam", /* 	Sequence Alignment/Map (SAM) or NREL SAM simulation file*/
        "pss", /* 	PicoScope oscilloscope settings snapshot*/
        "psmethod", /* 	PalmSens electrochemistry method definition*/
    ]

    const imageExtensionWhitelist = [
        "tif",
        "tiff",
        "czi",
        "nd2",
        "lsm",
        "jpx",
        "svs",
        "ims",
        "png",
        "jpg",
        "jpeg",
        "bmp",
        "vsi",
        "jp2",
        "roi",
        "dm3",
        "pxp",
        "ipf",
        "lif",
        "ima",
        "mrxs",
        "obj",
        "avi",
        "exf",
        "cxd",
    ]

    const cssString = `

    #global-dropdown-file {
        position: absolute;
        background: white;
        border: 1px solid #ccc;
        z-index: 9999;
        min-width: 150px;
        display: none;
    }

    /* Dropdown Button */
    .dropbtn {
    /*background-color: #3498DB;
    color: white;
    font-size: 16px;*/
    /*background-image: url( '${chrome.runtime.getURL("icons/download.png")}' );
    background-size: 24px 24px;*/
    border: none;
    cursor: pointer;
    }

    .dropbtn-single-file {
        padding: 0;
    }

    .dropbtn img {
        height: 24px;  
        width: 24px;
    }

    .dropdown-dataset img {
        margin-right: 8px;
    }

    /* Dropdown button on hover & focus */
    .dropbtn:hover, .dropbtn:focus {
    /*background-color: #2980B9;*/
    }

    /* The container <div> - needed to position the dropdown content */
    .dropdown {
    position: relative;
    display: inline-block;
    }
    .dropdown-dataset {
    position: relative;
    display: block;
    margin-bottom: 10px;
    }

    /* Dropdown Content (Hidden by Default) */
    .dropdown-content {
    display: none;
    position: absolute;
    background-color: #f1f1f1;
    min-width: 160px;
    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
    z-index: 1000;
    }

    /* Links inside the dropdown */
    .dropdown-content a {
    color: black;
    padding: 12px 16px;
    text-decoration: none;
    display: block;
    }

    /* Change color of dropdown links on hover */
    .dropdown-content a:hover {background-color: #ddd;}

    /* Show the dropdown menu (use JS to add this class to the .dropdown-content container when the user clicks on the dropdown button) */
    .show {display:block;} 

    .hide {display:none;} 

    .toast-row {
        display: flex;
        justify-content: center;
        margin: 1em 0;
        padding: 1rem;
        flex-wrap: wrap;
    }

    .toast {
        position: fixed;
        top: 25px;
        right: 25px;
        max-width: 300px;
        background: #fff;
        padding: 0.5rem;
        border-radius: 4px;
        box-shadow: -1px 1px 10px
            rgba(0, 0, 0, 0.3);
        z-index: 1023;
        animation: slideInRight 0.3s
                ease-in-out forwards,
            fadeOut 0.5s ease-in-out
                forwards 3s;
        transform: translateX(110%);
    }

    .toast.closing {
        animation: slideOutRight 0.5s
            ease-in-out forwards;
    }

    .toast-progress {
        position: absolute;
        display: block;
        bottom: 0;
        left: 0;
        height: 4px;
        width: 100%;
        background: #b7b7b7;
        animation: toastProgress 3s
            ease-in-out forwards;
    }

    .toast-content-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .toast-icon {
        padding: 0.35rem 0.5rem;
        font-size: 1.5rem;
    }

    .toast-message {
        flex: 1;
        font-size: 0.9rem;
        color: #000000;
        padding: 0.5rem;
    }

    .toast.toast-success {
        background: #95eab8;
    }

    .toast.toast-success .toast-progress {
        background-color: #2ecc71;
    }

    .toast.toast-danger {
        background: #efaca5;
    }

    .toast.toast-danger .toast-progress {
        background-color: #e74c3c;
    }

    .toast.toast-info {
        background: #bddaed;
    }

    .toast.toast-info .toast-progress {
        background-color: #3498db;
    }

    .toast.toast-warning {
        background: #ead994;
    }

    .toast.toast-warning .toast-progress {
        background-color: #f1c40f;
    }

    @keyframes slideInRight {
        0% {
            transform: translateX(110%);
        }

        75% {
            transform: translateX(-10%);
        }

        100% {
            transform: translateX(0%);
        }
    }

    @keyframes slideOutRight {
        0% {
            transform: translateX(0%);
        }

        25% {
            transform: translateX(-10%);
        }

        100% {
            transform: translateX(110%);
        }
    }

    @keyframes fadeOut {
        0% {
            opacity: 1;
        }

        100% {
            opacity: 0;
        }
    }

    @keyframes toastProgress {
        0% {
            width: 100%;
        }

        100% {
            width: 0%;
        }
    }
    `; 

    const style = document.createElement("style")
    style.innerHTML = cssString;
    document.head.appendChild(style);


    

    


    function createDropdownSingleFile(href) {
        const dropdown_id = "downloadDropDown-"+href;
        console.log(dropdown_id);
        const dropdownString = `
            <button onclick="dropdownToggleFunction2(event)" class="dropbtn dropbtn-single-file"><img class="dropdown-img" src="${chrome.runtime.getURL('icons/download.png')}" alt=""></button>
            <div id="${dropdown_id}" class="dropdown-content">
                <a href="#zarr" class="dropdown-download-link">ZARR</a>
                <a href="#mat" class="dropdown-download-link">MAT</a>
                <a href="#npz" class="dropdown-download-link">NPZ</a>
            </div>
        `
        const dropdown = document.createElement("div");
        dropdown.id = href;
        dropdown.classList.add("dropdown");
        dropdown.classList.add("sparc-fuse-download");
        dropdown.classList.add("circle");
        dropdown.setAttribute("data-v-c799c5c2", "");
        dropdown.innerHTML = dropdownString;
        

        

        return dropdown;

    }

    

    function downloadConvertedOutput(data) {
        console.log('Success:', data);
        fetch('http://localhost:5000/download', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file: data })  // Replace with real filename
        })
        .then(response => {
            if (!response.ok) {
            throw new Error("Failed to download file");
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data;  // Match the name you want
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }


    function downloadAndConvertEntireDataset(dataset_id, dst_format) {
        // Send POST request to local server
        showToast("The server is now downloading and converting the requested dataset.\nOnce complete, your browser will automatically start the download of the converted file.\nThis may take some time.","info",8000);
        fetch('http://localhost:5000/download_and_convert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ dataset_id: dataset_id, dst_format: dst_format })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('File path:', data.file);
                downloadConvertedOutput(data.file);
                // You can now use this path or show it to the user
            } else {
                console.error('Error:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function downloadAndConvertSingleFile(href, dst_format) {
        console.log("CREATE POST REQUEST");
        const href_match = href.match(/\/datasets\/file\/(\d+)\/(\d+)\?path=files\/(.*)/);
        
        if (href_match) {
            dataset_id = href_match[1];
            version_id = href_match[2];
            path = href_match[3];
        } else {
            console.error("url does not contain any path");
            return;
        }
        showToast("The server is now downloading and converting the requested file.\nOnce complete, your browser will automatically start the download of the converted file.\nThis may take some time.","info",6000);
        // Send POST request to local server
        fetch('http://localhost:5000/download_and_convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ dataset_id: dataset_id, path: path, dst_format: dst_format })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('File path:', data.file);
                downloadConvertedOutput(data.file);
                // You can now use this path or show it to the user
            } else {
                console.error('Error:', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
// --- UI Manipulation Functions ---

    function createDropdownSingleFile(href) {
        const dropdown = document.createElement("div");
        dropdown.id = href;
        dropdown.classList.add("dropdown", "sparc-fuse-download", "circle");
        dropdown.setAttribute("data-v-c799c5c2", "");
        dropdown.innerHTML = `<button class="dropbtn dropbtn-single-file"><img class="dropdown-img" src="${chrome.runtime.getURL('icons/download.png')}" alt=""></button>`;
        
        // NEW: Simplified event listener attached directly on creation
        dropdown.querySelector('.dropbtn').addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            
            const dropdownMenu = document.getElementById("global-dropdown-file");
            const rect = event.currentTarget.getBoundingClientRect();
            
            document.querySelectorAll(".sparc-fuse-download.active").forEach(el => el.classList.remove("active"));
            dropdown.classList.add("active");

            dropdownMenu.style.left = rect.left + window.scrollX + "px";
            dropdownMenu.style.top = rect.bottom + window.scrollY + "px";
            dropdownMenu.style.display = "block";
        });

        return dropdown;
    }

    // Renamed for clarity
    function addDownloadButtonForDataset() {
        const targetSpan = Array.from(document.querySelectorAll('span')).find(span => span.textContent.trim() === 'Download Full Dataset');
        if (!targetSpan) return;

        const id_match = window.location.href.match(/datasets\/(\d+)/);
        if (!id_match) return;
        const datasetId = id_match[1];
        
        const container_div = targetSpan.closest("div");

        const dropdown = document.createElement("div");
        dropdown.classList.add("dropdown", "dropdown-dataset", "sparc-fuse-download");
        dropdown.innerHTML = `
            <button class="dropbtn el-button secondary">
                <img src="${chrome.runtime.getURL('icons/button.png')}" alt="">
                Download & Convert Dataset
            </button>
            <div class="dropdown-content">
                <a href="#zarr" class="dropdown-download-link">ZARR</a>
                <a href="#mat" class="dropdown-download-link">MAT</a>
                <a href="#npz" class="dropdown-download-link">NPZ</a>
            </div>
        `;

        container_div.appendChild(dropdown);

        dropdown.querySelector('.dropbtn').addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.querySelector('.dropdown-content').classList.toggle('show');
        });

        dropdown.querySelectorAll('a.dropdown-download-link').forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                const dst_format = event.target.href.split("#")[1];
                downloadAndConvertEntireDataset(datasetId, dst_format);
            });
        });
    }

    // Renamed for clarity
    function addDownloadButtonsForFiles() {
        document.querySelectorAll('a[href^="/datasets"]').forEach(link => {
            const row = link.closest('tr');
            if (!row) return;

            const isValidExtension = extensionWhitelist.some(ext => link.href.endsWith(ext)) || imageExtensionWhitelist.some(ext => link.href.endsWith(ext));
            if (!isValidExtension) return;

            const cellDiv = row.querySelector('td:last-child div.cell');
            if (cellDiv) {
                const dropdown = createDropdownSingleFile(link.href);
                cellDiv.appendChild(dropdown);
            }
        });
    }
    
    function addGlobalDropdown() {
        if (document.getElementById("global-dropdown-file")) return;
        
        const dropdown = document.createElement("div");
        dropdown.id = "global-dropdown-file";
        dropdown.innerHTML = `
            <a href="#zarr" class="dropdown-download-link">ZARR</a>
            <a href="#mat" class="dropdown-download-link">MAT</a>
            <a href="#npz" class="dropdown-download-link">NPZ</a>
        `;
        document.body.appendChild(dropdown);

        // NEW: Listener logic moved here from the complex toggle function
        dropdown.querySelectorAll('.dropdown-download-link').forEach(dl => {
            dl.addEventListener('click', (link_event) => {
                link_event.preventDefault();
                const dst_format = link_event.target.getAttribute('href').substring(1);
                const activeDownloadElement = document.querySelector(".sparc-fuse-download.active");
                if (activeDownloadElement) {
                    const href = activeDownloadElement.id;
                    downloadAndConvertSingleFile(href, dst_format);
                }
            });
        });
    }

    /*
    // OLD: Complex and bug-prone toggle functions were here
    function dropdownToggleFunction(button) { ... }
    function dropdownToggleFunction2(event) { ... }
    function downloadAndConvertSingleFileListener(link_event) { ... }
    */

    /*
    // OLD: Functions were injected globally, which is not best practice
    injectFunction(downloadAndConvertSingleFile);
    injectFunction(downloadAndConvertEntireDataset);
    injectFunction(downloadAndConvertSingleFileListener);
    injectFunction(downloadConvertedOutput);
    injectFunction(dropdownToggleFunction);
    injectFunction(dropdownToggleFunction2);
    */

    // --- NEW: Central UI update function to fix the bug ---
    // This function will reset the UI state on every navigation change
    function updateUI() {
        // Step 1: Remove all previously injected buttons to avoid duplicates and ghost buttons
        document.querySelectorAll('.sparc-fuse-download').forEach(el => el.remove());

        // Step 2: Re-add buttons based on the current page content
        addDownloadButtonForDataset();
        addDownloadButtonsForFiles();
    }

    // --- Initialization and Event Listeners ---
    addGlobalDropdown();

    document.addEventListener("click", function(event) {
        const isDropdownButton = event.target.closest('.dropbtn');
        if (!isDropdownButton) {
            // Close all dropdowns if click is outside
            document.querySelectorAll(".dropdown-content").forEach(d => d.classList.remove('show'));
            document.getElementById("global-dropdown-file").style.display = "none";
            document.querySelectorAll(".sparc-fuse-download.active").forEach(el => el.classList.remove("active"));
        }
    });

    // NEW: Debounce function for performance
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /*
    // OLD: Multiple observers adding UI elements without removing them
    const observer = new MutationObserver(addDownloadButtons);
    observer.observe(document.body, { childList: true, subtree: true });
    const observer2 = new MutationObserver(addDownloadButtonEntireDataset);
    observer2.observe(document.body, { childList: true, subtree: true });
    */

    // NEW: Single, debounced observer calling the central update function
    const observer = new MutationObserver(debounce(updateUI, 200));
    observer.observe(document.body, { childList: true, subtree: true });

    // Initial run
    updateUI();

    // The toast container creation and showToast function remain the same
    let toast_container = document.createElement("div");
    toast_container.classList.add("toast-overlay");
    toast_container.id = "toast-overlay";
    document.body.appendChild(toast_container);
    
    // Inject showToast as it might be used by other parts of the page or for debugging
    function injectFunction(fn) {
        const script = document.createElement('script');
        script.textContent = fn.toString();
        document.documentElement.appendChild(script);
    }
    injectFunction(showToast);

})();