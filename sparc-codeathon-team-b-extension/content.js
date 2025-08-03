(function() {
    const extensionWhitelist = [
        "mat", "smr", "csv", "adicht", "hdf5", "h5", "ets", "abf", "rhd", "nev",
        "ns5", "ns2", "ns1", "smrx", "wav", "acq", "tbk", "tdx", "tev", "tin",
        "tnt", "tsq", "eeg", "vmrk", "vhdr", "sev", "sam", "pss", "psmethod",
    ];

    const imageExtensionWhitelist = [
        "tif", "tiff", "czi", "nd2", "lsm", "jpx", "svs", "ims", "png", "jpg",
        "jpeg", "bmp", "vsi", "jp2", "roi", "dm3", "pxp", "ipf", "lif", "ima",
        "mrxs", "obj", "avi", "exf", "cxd",
    ];

    const cssString = `
        #global-dropdown-file { position: absolute; background: white; border: 1px solid #ccc; z-index: 9999; min-width: 150px; display: none; }
        .dropbtn { border: none; cursor: pointer; }
        .dropbtn-single-file { padding: 0; }
        .dropbtn img { height: 24px;  width: 24px; }
        .dropdown-dataset img { margin-right: 8px; }
        .dropdown { position: relative; display: inline-block; }
        .dropdown-dataset { position: relative; display: block; margin-bottom: 10px; }
        .dropdown-content { display: none; position: absolute; background-color: #f1f1f1; min-width: 160px; box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2); z-index: 1000; }
        .dropdown-content a { color: black; padding: 12px 16px; text-decoration: none; display: block; }
        .dropdown-content a:hover { background-color: #ddd; }
        .show { display:block; }
        .toast { position: fixed; top: 25px; right: 25px; max-width: 300px; background: #fff; padding: 0.5rem; border-radius: 4px; box-shadow: -1px 1px 10px rgba(0, 0, 0, 0.3); z-index: 1023; transform: translateX(110%); }
        .toast.closing { animation: slideOutRight 0.5s ease-in-out forwards; }
        .toast-progress { position: absolute; display: block; bottom: 0; left: 0; height: 4px; width: 100%; background: #b7b7b7; }
        .toast-content-wrapper { display: flex; justify-content: space-between; align-items: center; }
        .toast-icon { padding: 0.35rem 0.5rem; font-size: 1.5rem; }
        .toast-message { flex: 1; font-size: 0.9rem; color: #000000; padding: 0.5rem; }
        .toast.toast-success { background: #95eab8; }
        .toast.toast-success .toast-progress { background-color: #2ecc71; }
        .toast.toast-danger { background: #efaca5; }
        .toast.toast-danger .toast-progress { background-color: #e74c3c; }
        .toast.toast-info { background: #bddaed; }
        .toast.toast-info .toast-progress { background-color: #3498db; }
        .toast.toast-warning { background: #ead994; }
        .toast.toast-warning .toast-progress { background-color: #f1c40f; }
        @keyframes slideInRight { 0% { transform: translateX(110%); } 75% { transform: translateX(-10%); } 100% { transform: translateX(0%); } }
        @keyframes slideOutRight { 0% { transform: translateX(0%); } 25% { transform: translateX(-10%); } 100% { transform: translateX(110%); } }
        @keyframes fadeOut { 0% { opacity: 1; } 100% { opacity: 0; } }
        @keyframes toastProgress { 0% { width: 100%; } 100% { width: 0%; } }
    `;

    const style = document.createElement("style");
    style.innerHTML = cssString;
    document.head.appendChild(style);

    function showToast(message = "Sample Message", toastType = "info", duration = 5000) {
        let icon = {
            success: '<span class="material-symbols-outlined">task_alt</span>',
            danger: '<span class="material-symbols-outlined">error</span>',
            warning: '<span class="material-symbols-outlined">warning</span>',
            info: '<span class="material-symbols-outlined">info</span>',
        };
        if (!Object.keys(icon).includes(toastType)) toastType = "info";

        let box = document.createElement("div");
        box.classList.add("toast", `toast-${toastType}`);
        box.innerHTML = ` <div class="toast-content-wrapper">
                        <div class="toast-icon">${icon[toastType]}</div>
                        <div class="toast-message">${message}</div>
                        <div class="toast-progress"></div>
                        </div>`;

        if (duration > 0) {
            box.style.animation = `slideInRight 0.3s ease-in-out forwards, fadeOut 0.5s ease-in-out forwards ${duration / 1000}s`;
            box.querySelector(".toast-progress").style.animation = `toastProgress ${duration / 1000}s ease-in-out forwards`;
        } else {
            box.style.animation = `slideInRight 0.3s ease-in-out forwards`;
            box.querySelector(".toast-progress").style.display = 'none';
        }

        let toastAlready = document.body.querySelector(".toast");
        if (toastAlready) {
            toastAlready.remove();
        }
        document.body.appendChild(box);
    }

    function downloadConvertedOutput(data) {
        fetch('http://localhost:5000/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ file: data })
        })
        .then(response => {
            if (!response.ok) { throw new Error("Failed to download file"); }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
a.href = url;
            a.download = data;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('Error:', error);
            showToast("Failed to initiate file download from server.", "danger", 8000);
        });
    }

    function downloadAndConvertEntireDataset(dataset_id, dst_format) {
        showToast("Starting download and conversion of the dataset...", "info", 0);
        fetch('http://localhost:5000/download_and_convert', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ dataset_id: dataset_id, dst_format: dst_format })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast("Conversion successful! Download will start shortly.", "success", 5000);
                downloadConvertedOutput(data.file);
            } else {
                showToast(`Error: ${data.message}`, "danger", 8000);
                console.error('Error:', data.message);
            }
        })
        .catch(error => {
            showToast("Network error: Could not connect to the local server.", "danger", 8000);
            console.error('Error:', error);
        });
    }

    function downloadAndConvertSingleFile(href, dst_format) {
        const href_match = href.match(/\/datasets\/file\/(\d+)\/(\d+)\?path=files\/(.*)/);
        if (!href_match) {
            console.error("URL does not contain any path");
            return;
        }
        const [_, dataset_id, version_id, path] = href_match;
        showToast("Starting download and conversion of the file...", "info", 0);
        fetch('http://localhost:5000/download_and_convert', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ dataset_id: dataset_id, path: path, dst_format: dst_format })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast("Conversion successful! Download will start shortly.", "success", 5000);
                downloadConvertedOutput(data.file);
            } else {
                showToast(`Error: ${data.message}`, "danger", 8000);
                console.error('Error:', data.message);
            }
        })
        .catch(error => {
            showToast("Network error: Could not connect to the local server.", "danger", 8000);
            console.error('Error:', error);
        });
    }

    function createDropdownSingleFile(href) {
        const dropdownContainer = document.createElement("div");
        dropdownContainer.id = href;
        dropdownContainer.classList.add("dropdown", "sparc-fuse-download", "circle");
        dropdownContainer.setAttribute("data-v-c799c5c2", "");
        
        const button = document.createElement('button');
        button.className = 'dropbtn dropbtn-single-file';
        button.innerHTML = `<img class="dropdown-img" src="${chrome.runtime.getURL('icons/download.png')}" alt="">`;

        button.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();

            const globalDropdown = document.getElementById("global-dropdown-file");
            const rect = button.getBoundingClientRect();
            
            const isAlreadyOpen = globalDropdown.style.display === 'block' && globalDropdown.getAttribute('data-active-href') === href;

            if (isAlreadyOpen) {
                globalDropdown.style.display = 'none';
                globalDropdown.removeAttribute('data-active-href');
            } else {
                globalDropdown.setAttribute('data-active-href', href);
                globalDropdown.style.left = rect.left + window.scrollX + "px";
                globalDropdown.style.top = rect.bottom + window.scrollY + "px";
                globalDropdown.style.display = 'block';
            }
        });

        dropdownContainer.appendChild(button);
        return dropdownContainer;
    }

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
        dropdown.innerHTML = `<a href="#zarr" class="dropdown-download-link">ZARR</a><a href="#mat" class="dropdown-download-link">MAT</a><a href="#npz" class="dropdown-download-link">NPZ</a>`;
        document.body.appendChild(dropdown);

        dropdown.querySelectorAll('.dropdown-download-link').forEach(dl => {
            dl.addEventListener('click', (link_event) => {
                link_event.preventDefault();
                const dst_format = link_event.target.getAttribute('href').substring(1);
                const activeHref = dropdown.getAttribute('data-active-href');
                if (activeHref) {
                    downloadAndConvertSingleFile(activeHref, dst_format);
                }
            });
        });
    }

    function updateUI() {
        document.querySelectorAll('.sparc-fuse-download').forEach(el => el.remove());
        addDownloadButtonForDataset();
        addDownloadButtonsForFiles();
    }
    
    addGlobalDropdown();

    document.addEventListener("click", function(event) {
        if (event.target.closest('.sparc-fuse-download, #global-dropdown-file')) {
            return;
        }

        document.querySelectorAll(".dropdown-dataset .dropdown-content").forEach(d => d.classList.remove('show'));
        const globalDropdown = document.getElementById("global-dropdown-file");
        globalDropdown.style.display = 'none';
        globalDropdown.removeAttribute('data-active-href');
    });

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

    const observer = new MutationObserver(debounce(updateUI, 200));
    observer.observe(document.body, { childList: true, subtree: true });

    updateUI();
    
    function injectFunction(fn) {
        const script = document.createElement('script');
        script.textContent = fn.toString();
        document.documentElement.appendChild(script);
    }
    injectFunction(showToast);

})();