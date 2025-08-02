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

    const cssString = `
    /* Dropdown Button */
    .dropbtn {
    /*background-color: #3498DB;
    color: white;
    font-size: 16px;*/
    background-image: url( '${chrome.runtime.getURL("icons/button.png")}' );
    background-size: 24px 24px;
    height: 24px;  
    width: 24px;
    border: none;
    cursor: pointer;
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

    /* Dropdown Content (Hidden by Default) */
    .dropdown-content {
    display: none;
    /*position: absolute;*/
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
    `; 

    const style = document.createElement("style")
    style.innerHTML = cssString;
    document.head.appendChild(style);


    

    const script = document.createElement("script");
    const scriptString = `
        /* When the user clicks on the button, 
        toggle between hiding and showing the dropdown content */
        function dropdownToggleFunction(button) {
            console.log(button);
            const dropdownContent = button.parentNode.querySelector('div.dropdown-content');
            
            dropdownContent.classList.toggle("show");
        }

        // Close the dropdown if the user clicks outside of it
        window.onclick = function(event) {
            if (!event.target.matches('.dropbtn')) {
                var dropdowns = document.getElementsByClassName("dropdown-content");
                var i;
                for (i = 0; i < dropdowns.length; i++) {
                    var openDropdown = dropdowns[i];
                    if (openDropdown.classList.contains('show')) {
                        openDropdown.classList.remove('show');
                    }
                }
            }
        }


    `;
    script.innerHTML = scriptString;
    document.body.appendChild(script);


    function createDropdownSingleFile(href) {
        const dropdown_id = "downloadDropDown-"+href;
        console.log(dropdown_id);
        const dropdownString = `
            <button onclick="dropdownToggleFunction(this)" class="dropbtn"></button>
            <div id="${dropdown_id}" class="dropdown-content">
                <a href="#zarr" class="dropdown-download-link">ZARR</a>
                <a href="#mat" class="dropdown-download-link">MAT</a>
                <a href="#npz" class="dropdown-download-link">NPZ</a>
            </div>
        `
        const dropdown = document.createElement("div");
        dropdown.classList.add("dropdown");
        dropdown.classList.add("sparc-fuse-download");
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
            <button onclick="dropdownToggleFunction(this)" class="dropbtn"></button>
            <div id="datasetId_${datasetId}" class="dropdown-content">
                <a href="#zarr" class="dropdown-download-link download-dataset-link">ZARR</a>
                <a href="#mat" class="dropdown-download-link download-dataset-link">MAT</a>
                <a href="#npz" class="dropdown-download-link download-dataset-link">NPZ</a>
            </div>
        `

        const dropdown = document.createElement("div");
        dropdown.classList.add("dropdown");
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


    function addDownloadButtons() {
        // Find all matching links
        //const links = document.querySelectorAll('a[href^="/datasets"][href$=".hdf5"]');
        const links = document.querySelectorAll('a[href^="/datasets"]');
        

        links.forEach(link => {
            const row = link.closest('tr');
            if (row === null) return; // not a single file link
            if (row.querySelector(".sparc-fuse-download") !== null) return;
            if (extensionWhitelist.some(ext => link.href.endsWith(ext)) == false) return;


            const cellDiv = row.querySelector('td:last-child').querySelector('div.cell');
            
            dropdown = createDropdownSingleFile(link.href)

            cellDiv.appendChild(dropdown);

            console.log(link);

            const dropdown_links = dropdown.querySelectorAll('.dropdown-download-link');

            dropdown_links.forEach(dl => {
                dl.addEventListener('click', function(event) {
                    event.preventDefault();
                    const dst_format = this.getAttribute('href').substring(1);
                    console.log(this);
                    const href = this.parentNode.id.replace('downloadDropDown-', '');
                    console.log(href);

                    downloadAndConvertSingleFile(href, dst_format);
                });
            });
        });
    }

    // Run on load and on future DOM changes
    //addBootstrap();
    
    addDownloadButtonEntireDataset();
    addDownloadButtons();
    const observer = new MutationObserver(addDownloadButtons);
    observer.observe(document.body, { childList: true, subtree: true });

    
    const observer2 = new MutationObserver(addDownloadButtonEntireDataset);
    observer2.observe(document.body, { childList: true, subtree: true });
})();


