



(function() {
    const cssString = `
    /* Dropdown Button */
    .dropbtn {
    background-color: #3498DB;
    color: white;
    font-size: 16px;
    border: none;
    cursor: pointer;
    }

    /* Dropdown button on hover & focus */
    .dropbtn:hover, .dropbtn:focus {
    background-color: #2980B9;
    }

    /* The container <div> - needed to position the dropdown content */
    .dropdown {
    position: relative;
    display: inline-block;
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
    `; 

    const style = document.createElement("style")
    style.innerHTML = cssString;
    document.head.appendChild(style);


    
    /*button.addEventListener("click", async () => {
        const matUrl = prompt("Enter the URL of the .mat file:");
        if (!matUrl) return;

        try {
            const response = await fetch(matUrl);
            const blob = await response.blob();
            const formData = new FormData();
            formData.append("file", blob, "data.mat");

            const csvResponse = await fetch("http://localhost:5000/convert", {
                method: "POST",
                body: formData
            });

            const csvBlob = await csvResponse.blob();
            const url = URL.createObjectURL(csvBlob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "converted.csv";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        } catch (error) {
            alert("Conversion failed: " + error.message);
            console.error(error);
        }
    });*/

    const script = document.createElement("script");
    const scriptString = `
        /* When the user clicks on the button, 
        toggle between hiding and showing the dropdown content */
        function myFunction(button) {
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
            <button onclick="myFunction(this)" class="dropbtn">Download</button>
            <div id="${dropdown_id}" class="dropdown-content">
                <a href="#zarr" class="dropdown-download-link">ZARR</a>
                <a href="#mat" class="dropdown-download-link">MAT</a>
                <a href="#npz" class="dropdown-download-link">NPZ</a>
            </div>
        `
        const dropdown = document.createElement("div");
        dropdown.classList.add("dropdown");
        dropdown.innerHTML = dropdownString;
        

        

        return dropdown;

        // // Create outer div
        // const dropdown = document.createElement('div');
        // dropdown.className = 'dropdown';

        // // Create button
        // const button = document.createElement('button');
        // button.className = 'btn btn-secondary dropdown-toggle';
        // button.type = 'button';
        // button.id = 'dropdownMenuButton1';
        // button.setAttribute('data-bs-toggle', 'dropdown');
        // button.setAttribute('aria-expanded', 'false');

        // // Create span and img
        // const span = document.createElement('span');
        // const img = document.createElement('img');
        // img.src = chrome.runtime.getURL('icons/download.png');
        // img.alt = 'icon';
        // img.width = 24;
        // img.height = 24;

        // span.appendChild(img);
        // button.appendChild(span);
        // dropdown.appendChild(button);

        // // Create dropdown menu (ul)
        // const ul = document.createElement('ul');
        // ul.className = 'dropdown-menu';
        // ul.setAttribute('aria-labelledby', 'dropdownMenuButton1');

        // // List of file types
        // const fileTypes = ['.zarr', '.mat', '.npz'];
        // fileTypes.forEach(type => {
        //     const li = document.createElement('li');
        //     const a = document.createElement('a');
        //     a.className = 'dropdown-item';
        //     a.href = '#';
        //     a.textContent = type;
        //     li.appendChild(a);
        //     ul.appendChild(li);
        // });

        // dropdown.appendChild(ul);

        // return dropdown;

        // Append to body or any target container
        //document.body.appendChild(dropdown);  // You can replace this with a specific container
    }

    // function addBootstrap() {
    //     const link = document.createElement("link");
    //     link.href = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
    //     link.rel = "stylesheet";
    //     //link.integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC";
    //     link.crossorigin="anonymous";
    //     document.head.appendChild(link);

    //     const script = document.createElement("script");
    //     script.src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js";
    //     //script.integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM";
    //     script.crossorigin="anonymous";
    //     script.defer = true;
    //     document.body.appendChild(script);
    // }



    function addDownloadButtons() {
        // Find all matching links
        //const links = document.querySelectorAll('a[href^="/datasets"][href$=".hdf5"]');
        const links = document.querySelectorAll('a[href^="/datasets"]');

        links.forEach(link => {
            // Prevent adding multiple buttons
            if (link.dataset.hdf5ButtonAdded) return;

            const row = link.closest('tr');

            const lastTd = row ? row.querySelector('td:last-child') : null;

            if (lastTd !== null) {
                const cellDiv = lastTd.querySelector('div.cell');
                
                dropdown = createDropdownSingleFile(link.href)

                cellDiv.appendChild(dropdown);

                // Mark as processed
                link.dataset.hdf5ButtonAdded = "true";
                console.error(link);

                const dropdown_links = dropdown.querySelectorAll('.dropdown-download-link');

                dropdown_links.forEach(dl => {
                    dl.addEventListener('click', function(event) {
                        event.preventDefault();
        
                        // Extract the type from the href (remove the #)
                        const type = this.getAttribute('href').substring(1);

                        console.log("CREATE POST REQUEST");
        
                        // Send POST request to local server
                        fetch('http://localhost:5000/convert', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ href: link.href, type: type })
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Success:', data);

                            fetch('http://localhost:5000/download', {
                                method: 'POST',
                                headers: {
                                'Content-Type': 'application/json'
                                },
                                body: JSON.stringify(data)  // Replace with real filename
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
                                a.download = data.filename;  // Match the name you want
                                document.body.appendChild(a);
                                a.click();
                                a.remove();
                                window.URL.revokeObjectURL(url);
                            })
                            .catch(error => {
                                console.error('Error:', error);
                            });
                        })
                        .catch(error => {
                        console.error('Error:', error);
                        });
                    });
                });
            }


            return;

            // Create the button
            const export_elem = document.createElement("div");
            export_elem.class = "circle";
            export_elem.setAttribute("class", "circle");

            export_elem.setAttribute("data-v-c799c5c2", "");

            const span = document.createElement('span');
            const img = document.createElement('img');
            img.src = chrome.runtime.getURL('icons/matlab.svg'); // Make sure this path is correct
            img.alt = 'icon';
            img.width = 24;
            img.height = 24;

            span.appendChild(img);
            export_elem.appendChild(span);


            
            // Attach click handler
            export_elem.addEventListener("click", async (e) => {
                e.preventDefault();

                const href = link.getAttribute("href");
                const fullUrl = new URL(href, window.location.origin).href;
                console.log(fullUrl);

                /*try {
                    //const response = await fetch(fullUrl);
                    //const blob = await response.blob();

                    const formData = new FormData();
                    const targetFormat = "mat";
                    //formData.append("file", blob, "data.hdf5");
                    formData.append("file", fullUrl, "fullUrl");
                    formData.append("file", "sourceFormat", "hdf5");
                    formData.append("file", "targetFormat", "mat");

                    const response = await fetch("http://localhost:5000/convert", {
                        method: "POST",
                        body: formData
                    });

                    if (!response.ok) throw new Error("Conversion server failed");

                    const responseBlob = await response.blob();
                    const responseUrl = URL.createObjectURL(responseBlob);

                    const a = document.createElement("a");
                    a.href = csvUrl;
                    a.download = "converted."+targetFormat;
                    a.click();
                } catch (err) {
                    alert("Failed to convert HDF5 file: " + err.message);
                    console.error(err);
                }*/
            });

            // Insert the button after the link
            
        });
    }

    // Run on load and on future DOM changes
    //addBootstrap();
    
    addDownloadButtons();
    const observer = new MutationObserver(addDownloadButtons);
    observer.observe(document.body, { childList: true, subtree: true });

    
    
})();


