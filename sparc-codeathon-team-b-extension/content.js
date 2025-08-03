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

    function addDownloadButtonEntireDataset() {
        const spans = document.querySelectorAll('span');
        let targetSpan = null;

        for (const span of spans) {
            if (span.textContent.trim() === 'Download Full Dataset') {
                targetSpan = span;
                break;
            }
        }
        if (!targetSpan) return;

        const fullUrl = window.location.href;

        const id_match = fullUrl.match(/datasets\/(\d+)/);

        // If found, check if the sibling already exists
        const container_div = targetSpan.closest("div")

        if (container_div.querySelector(".sparc-fuse-download") !== null) return;

        
        datasetId = -1;
        if (id_match) {
            datasetId = id_match[1];
            console.log('Dataset ID:', datasetId);  // Output: 224
        } else {
            console.log('Dataset ID not found');
            return;
        }

        

        const dropdownString = `
            <button onclick="dropdownToggleFunction(this)" class="dropbtn el-button secondary">
                <img src="${chrome.runtime.getURL('icons/button.png')}" alt="">
                Download Full Dataset
            </button>
            <div id="datasetId_${datasetId}" class="dropdown-content">
                <a href="#zarr" class="dropdown-download-link download-dataset-link">ZARR</a>
                <a href="#mat" class="dropdown-download-link download-dataset-link">MAT</a>
                <a href="#npz" class="dropdown-download-link download-dataset-link">NPZ</a>
            </div>
        `

        const dropdown = document.createElement("div");
        dropdown.classList.add("dropdown");
        dropdown.classList.add("dropdown-dataset");
        dropdown.classList.add("sparc-fuse-download");
        dropdown.innerHTML = dropdownString;

        container_div.appendChild(dropdown);

        document.querySelectorAll('a.download-dataset-link').forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault();
                dataset_id = event.target.closest("div").id.split("_")[1];
                dst_format = event.target.href.split("#")[1];
                downloadAndConvertEntireDataset(dataset_id, dst_format);
            });
        });
    }

    function addGlobalDropdown() {
        global_dropdown_container = document.body.querySelector("div#global-dropdown-file");
        if (global_dropdown_container) return;
        
        const dropdownString = `
            <a href="#zarr" class="dropdown-download-link">ZARR</a>
            <a href="#mat" class="dropdown-download-link">MAT</a>
            <a href="#npz" class="dropdown-download-link">NPZ</a>
        `
        const dropdown = document.createElement("div");
        dropdown.id = "global-dropdown-file";
        dropdown.classList.add("dropdown-content");
        //dropdown.classList.add("hide");
        dropdown.innerHTML = dropdownString;
        document.body.appendChild(dropdown);
    }


    function addDownloadButtons() {
        // Find all matching links
        //const links = document.querySelectorAll('a[href^="/datasets"][href$=".hdf5"]');
        const links = document.querySelectorAll('a[href^="/datasets"]');

        links.forEach(link => {
            const row = link.closest('tr');
            if (row === null) return; // not a single file link
            if (row.querySelector(".sparc-fuse-download") !== null) return;
            if ((extensionWhitelist.some(ext => link.href.endsWith(ext)) == false) &&
                (imageExtensionWhitelist.some(ext => link.href.endsWith(ext)) == false)
            ) return;


            const cellDiv = row.querySelector('td:last-child').querySelector('div.cell');
            
            dropdown = createDropdownSingleFile(link.href);

            cellDiv.appendChild(dropdown);

            const dropdown_links = dropdown.querySelectorAll('.dropdown-download-link');

            dropdown_links.forEach(dl => {
                dl.addEventListener('click', function(event) {
                    event.preventDefault();
                    const dst_format = this.getAttribute('href').substring(1);
                    const href = this.parentNode.id.replace('downloadDropDown-', '');
                    
                    downloadAndConvertSingleFile(href, dst_format);
                });
            });
        });
    }

    



    function dropdownToggleFunction(button) {
        console.log(button);
        const dropdownContent = button.parentNode.querySelector('div.dropdown-content');
        
        dropdownContent.classList.toggle("show");
    }

    function dropdownToggleFunction2(event) {
        event.preventDefault();
        const dropdown = document.getElementById("global-dropdown-file");
        const rect = event.target.closest(".sparc-fuse-download").getBoundingClientRect();
        
        dropdown.style.left = rect.left + window.scrollX + "px";
        dropdown.style.top = rect.bottom + window.scrollY + "px";
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
        //dropdown.classList.toggle("show");
        //dropdown.classList.toggle("hide");

        const dropdown_links = dropdown.querySelectorAll('.dropdown-download-link');
        //const href = event.target.closest(".sparc-fuse-download").id;


        event.target.closest(".sparc-fuse-download").classList.toggle("active")
        

        dropdown_links.forEach(dl => {
            dl.removeEventListener('click', downloadAndConvertSingleFileListener);
            dl.addEventListener('click', downloadAndConvertSingleFileListener);
        });
    }

    function downloadAndConvertSingleFileListener(link_event) {
        link_event.preventDefault();
        const dst_format = link_event.target.getAttribute('href').substring(1);

        const href = document.querySelectorAll(".sparc-fuse-download.active")[0].id;

        downloadAndConvertSingleFile(href, dst_format);

    }

    
    function injectFunction(fn) {
        const script = document.createElement('script');

        // Convert function and arguments to a string
        const fnSource = fn.toString();

        script.textContent = fnSource;
        document.documentElement.appendChild(script);
    }


    injectFunction(downloadAndConvertSingleFile);
    injectFunction(downloadAndConvertEntireDataset);
    injectFunction(downloadAndConvertSingleFileListener);
    injectFunction(downloadConvertedOutput);
    injectFunction(dropdownToggleFunction);
    injectFunction(dropdownToggleFunction2);



    const script = document.createElement("script");
    const scriptString = `
        /*document.addEventListener("click", function(event) {
            if (event.target.matches('#global-dropdown-file')) return;
            const dropdown = document.getElementById("global-dropdown-file");
            if (!dropdown.classList.contains("show")) return;
            dropdown.classList.remove("show");
            dropdown.classList.add("hide");
        });*/

        // Close the dropdown if the user clicks outside of it
        document.addEventListener("click", function(event) {
            console.log(event.target);
            if (event.target.matches('.dropbtn')) return;
            if (event.target.matches('.dropdown')) return;
            if (event.target.matches('.dropdown-img')) return;

            dropdowns = document.querySelectorAll(".dropdown-content")
            for (const element of dropdowns) {
                element.classList.remove("show");
            }
            for (const element of document.querySelectorAll(".sparc-fuse-download.active")) {
                element.classList.remove("active");
            }
            document.getElementById("global-dropdown-file").style.display = "none";
        });



    `;
    script.innerHTML = scriptString;
    document.body.appendChild(script);


    
    const observer = new MutationObserver(addDownloadButtons);
    observer.observe(document.body, { childList: true, subtree: true });
    const observer2 = new MutationObserver(addDownloadButtonEntireDataset);
    observer2.observe(document.body, { childList: true, subtree: true });

    addGlobalDropdown();
    addDownloadButtonEntireDataset();
    addDownloadButtons();
    

    document.addEventListener('DOMContentLoaded', function() {
        
    }, false);


    toast_container = document.createElement("div");
    toast_container.classList.add("toast-overlay");
    toast_container.id = "toast-overlay";
    document.body.appendChild(toast_container);

    
    function showToast(message = "Sample Message", toastType = "info", duration = 8000) {
        let icon = {
            success:
            '<span class="material-symbols-outlined">task_alt</span>',
            danger:
            '<span class="material-symbols-outlined">error</span>',
            warning:
            '<span class="material-symbols-outlined">warning</span>',
            info:
            '<span class="material-symbols-outlined">info</span>',
        };
        if (!Object.keys(icon).includes(toastType))
            toastType = "info";

        let box = document.createElement("div");
        box.classList.add("toast", `toast-${toastType}`);
        box.innerHTML = ` <div class="toast-content-wrapper">
                        <div class="toast-icon">
                        ${icon[toastType]}
                        </div>
                        <div class="toast-message">${message}</div>
                        <div class="toast-progress"></div>
                        </div>`;
        duration = duration || 5000;
        box.querySelector(".toast-progress").style.animationDuration =
                `${duration / 1000}s`;

        let toastAlready = document.body.querySelector(".toast");
        if (toastAlready) {
            toastAlready.remove();
        }

        document.body.appendChild(box)
    }

    injectFunction(showToast);

    
})();


