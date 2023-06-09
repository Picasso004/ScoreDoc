// JavaScript code

//Global variables
let keywords = [];
let clearButton;
let keywordInput;
let keyword;
let dropZone;
let uploadBtn;
let fileInput;
let keyWordInput;
let keyWordUpldBtn;
let addKeywordBtn;
let fileList;
let ul;
let d = new DataTransfer();



/* Function to add keyword to the list
 This function takes a keyword as a parameter and checks if it is not an empty string.
 If not, it adds the keyword to the global keywords array and updates the keyword list in the UI.*/
function addKeyword(keyword) {
  const keywordInput = document.getElementById('keywords');
  if (keyword !== '') {
    keywords.push(keyword);
    keywordInput.value = '';
    updateKeywordList();
  }
}

/* Function to update keyword list in the UI
 This function updates the DOM to display the current list of keywords.
 If there are no keywords, it hides the "clear" button and displays a message saying there are no keywords.
 If there are keywords, it creates a new div for each keyword and appends it to the keyword list in the DOM.*/
function updateKeywordList() {
  const keywordList = document.getElementById('keywordList');
  if(keywords.length === 0){
    clearButton.style.display = 'none';
    keywordList.innerHTML = 'No keywords';
  }
  else{
    clearButton.style.display = 'block';

    keywordList.innerHTML = '';
    for (let i = 0; i < keywords.length; i++) {
      const keywordItem = document.createElement('div');
      keywordItem.className = 'keyword-list-item';
      keywordItem.innerHTML = `
        <span>${keywords[i]}</span>
        <button onclick="removeKeyword(${i})">&#x2716;</button>
      `;
      keywordList.appendChild(keywordItem);
    }
  }


}

/* Function to remove keyword from the list
 This function takes an index as a parameter and removes the keyword at that index from the keywords array.
 It then updates the keyword list in the UI.*/
function removeKeyword(index) {
  keywords.splice(index, 1);
  updateKeywordList();
}

// This function clears the keyword list by setting the keywords array to an empty array and updating the keyword list in the UI.
function clear(){
  keywords = [];
  updateKeywordList();
}


/* Function to search keywords
   This function sends a POST request to the server with the keywords as data.
   The server responds with data that is used to update the results zone in the UI.
   If there are no keywords or files, it displays an error message in the results zone.*/
async function searchKeywords() {
  const searchButton = document.getElementsByClassName('search-button')[0];
  const resultsZone = document.getElementById('resultsZone');
  if (keywords.length > 0 && document.getElementById('fileInput').files.length > 0) { // Check if keywords and file are available
    // Show searching and loading message
    searchButton.innerHTML = 'Searching...';
    searchButton.disabled = true;
    searchButton.classList.add('loading');
    resultsZone.textContent = "Loading...";

    //Sending files
    const formData = new FormData();
    //const files = document.getElementById('fileInput').files;
    for(let i=0; i<d.files.length;i++){
        formData.append(`file${i}`, d.files[i]);
    }
    await fetch('http://localhost:6969/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log(response);
    })
    .catch(error => console.error(error));

    // Prepare data to send to server
    const data = { keywords: keywords};
    const jsonData = JSON.stringify(data);

     // Send keywords data to server
     fetch('http://localhost:6969/api/data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: jsonData
    })
      .then(response => response.json())
      .then(result => {
        // Hide loading spinner
        searchButton.innerHTML = 'Search';
        searchButton.disabled = false;
        searchButton.classList.remove('loading');
        // Update results zone with data from server
        resultsZone.innerHTML = `
        <div class="result_container">
          <h2>Result: </h2>
          <p class="most_relevant"> ${result[0].file} </p>
        </div>`;
        for(let i = 0;i<result.length;i++){
            resultsZone.innerHTML += `
            <h3>${result[i].file}</h3>
            <ul>
                ${result[i].data.map(item => `<li>${item.word}: ${item.score}</li>`).join('')}
            </ul>
        `;
        }
        reorganizeFiles(result);
      })
      .catch(error => {
        console.error('Error sending data to server:', error);
        resultsZone.textContent = 'Error loading data';
      });

  }
  else{
    resultsZone.textContent = "It seems that keywords or files are missing:(";
  }
}

/* Function to handle key press event on keywords input
   This function checks if the key pressed was the Enter key.
   If so, it gets the value of the keyword input, trims it, and adds it to the keyword list.*/
function checkKeyPress(event) {
  if (event.keyCode === 13) {
    event.preventDefault();
    const keywordInput = document.getElementById('keywords');
    const keyword = keywordInput.value.trim();
    addKeyword(keyword);
  }
}

// This function handles uploaded files. It creates a new list item for each file and appends it to the file list in the DOM.
function handleFiles(files) {
      let fileFound = false;
      for (const file of files) {
        for(const f of d.files){
          if(file.name === f.name){
            fileFound = true;
            break;
          }
        }
        if(fileFound) continue;
        const div = document.createElement('div');
        const li = document.createElement('li');
        div.textContent = file.name;
        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = 'X';
        deleteBtn.classList.add('remove-btn');
        deleteBtn.addEventListener('click', (e) => {
        e.preventDefault();
        li.remove(); // Remove the file from the file list
        removeFileFromFileList(div.textContent.slice(0,-3));
        });

        const viewBtn = document.createElement('button');
        viewBtn.textContent = String.fromCodePoint(0x1F441);
        viewBtn.classList.add('eye-btn');
        viewBtn.addEventListener('click', () => {
          var pdfViewer = document.getElementById(file.name);
          pdfViewer.style.display = (pdfViewer.style.display === "block") ? "none" : "block";
        });
        div.appendChild(viewBtn);
        div.appendChild(deleteBtn);

        li.append(div);

        const pdfViewer = document.createElement('div');
        pdfViewer.classList.add("pdf-viewer");
        pdfViewer.id = file.name;

        const embedElement = document.createElement('embed');
        embedElement.src = URL.createObjectURL(file);
        embedElement.width = '660';
        embedElement.height = '400';


        pdfViewer.append(embedElement);
        li.append(pdfViewer);
        ul.append(li);

        //Save in files list variable
        d.items.add(file);
      }
      fileInput.files = d.files;

}

// This function removes a file from the file list based on its filename.
function removeFileFromFileList(filename) {
  const dt = new DataTransfer();
  //const input = document.getElementById('fileInput')
  const files = d.files;

  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    if (file.name !== filename){
      dt.items.add(file) // here you exclude the file. thus removing it.
    }
  }
  d = dt // Update the list
  fileInput.files = d.files;

}

// This function reorganizes the files based on the results from the server.
function reorganizeFiles(files){
  var items = Array.from(ul.getElementsByTagName("li"));

  while (ul.firstChild) {
    ul.removeChild(ul.firstChild);
  }

  for(let i =0;i<files.length;i++){
    for (var j = 0; j < items.length; j++) {
      if(files[i].file === items[j].firstChild.textContent.slice(0,-3)){
        ul.appendChild(items[j]);
      }
    }
  }
}

// This function loads keywords from a file. It reads the file, parses the data, and adds each keyword to the keyword list.
function loadKeywords(file){
  const reader = new FileReader();

  reader.onload = function(e) {
    const data = e.target.result;
    let parsedData =null;

    /* Parse data based on file type */
    if (file.name.endsWith('.csv')) {
      // For CSV files
      const workbook = XLSX.read(data, { type: 'binary', cellDates: true });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      parsedData = XLSX.utils.sheet_to_json(sheet, { header: 1 });
    } else {
      // For Excel files
      const workbook = XLSX.read(data, { type: 'binary', cellDates: true });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      parsedData = XLSX.utils.sheet_to_json(sheet, { header: 1 });
    }

    for(let i=0;i<parsedData.length;i++){
      addKeyword(parsedData[i][0]);
    }
  };

  reader.readAsBinaryString(file);
}

// This function runs when the DOM is fully loaded. It adds event listeners to various elements in the DOM.
document.addEventListener("DOMContentLoaded", function(){
  clearButton = document.getElementById('clear-button');
  dropZone = document.getElementById('dropZone');
  uploadBtn = document.getElementById('upload-button');
  fileInput = document.getElementById('fileInput');
  keyWordInput = document.getElementById('keyWordFileInput');
  keyWordUpldBtn = document.getElementById('keyword-upload-button');
  addKeywordBtn = document.getElementById('add-key-word-btn');

  fileList = document.getElementById('fileList');
  ul = fileList.querySelector('ul');

    // Handle upload button click event
    addKeywordBtn.addEventListener('click', () => {
      keywordInput = document.getElementById('keywords');
      keyword = keywordInput.value.trim();
      addKeyword(keyword);
    });

    // Prevent default behavior for drag-and-drop events
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('drag-over'); // Add CSS class to change background color
    });

    // Handle drag leave event
    dropZone.addEventListener('dragleave', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over'); // Remove CSS class to reset background color
    });

    // Handle file drop event
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over'); // Remove CSS class to reset background color
      const files = e.dataTransfer.files;
      document.getElementById('fileInput').files = files;
      handleFiles(files);
    });

    // Handle file input change event
    fileInput.addEventListener('change', (e) => {
      const files = e.target.files;
      handleFiles(files);
    });

    // Handle upload button click event
    uploadBtn.addEventListener('click', () => {
      fileInput.click();
    });

    // Handle add from file button click event
    keyWordUpldBtn.addEventListener('click', () => {
      keyWordInput.click();

    });

    keyWordInput.addEventListener('change', (e) => {
      loadKeywords(e.target.files[0]);
    });

   clearButton.addEventListener('click', () => {
      clear();

    });
});





