const inputText = document.querySelector('#input-text');
const addButton = document.querySelector('#add-button');
const labelList = document.querySelector('#label-list');
const searchButton = document.querySelector('#search-button');
const resultsContainer = document.querySelector('#results-container');
const resultsList = document.querySelector('#results-list');
const dropZone = document.querySelector('#drop-zone');
const fileInput = document.querySelector('#file-input');
const pdfViewer = document.querySelector('#pdf-viewer');

let labels = [];

addButton.addEventListener('click', () => {
    const labelText = inputText.value.trim();
    
    if (labelText) {
        labels.push(labelText);
        updateLabelList();
        inputText.value = '';
        updateSearchButton();
    }
});

function updateLabelList() {
    labelList.innerHTML = '';
    
    labels.forEach((label, index) => {
        const labelItem = document.createElement('li');
        labelItem.classList.add('label-item');
        
        const labelSpan = document.createElement('span');
        labelSpan.textContent = label;
        
        const removeButton = document.createElement('button');
        removeButton.textContent = '→';
        removeButton.addEventListener('click', () => {
            labels.splice(index, 1);
            updateLabelList();
            updateSearchButton();
        });
        
        labelItem.appendChild(labelSpan);
        labelItem.appendChild(removeButton);
        
        labelList.appendChild(labelItem);
    });
}

searchButton.addEventListener('click', async () => {
    searchButton.disabled = true;
    searchButton.textContent = 'Loading...';
    
    const response = await fetch('result.json');
    const resultData = await response.json();
    
    resultsList.innerHTML = '';
    
    resultData.forEach(result => {
        const resultItem = document.createElement('li');
        
        const wordSpan = document.createElement('span');
        wordSpan.textContent = result.word;
        
        const scoreSpan = document.createElement('span');
        scoreSpan.textContent = result.score;
        
        resultItem.appendChild(wordSpan);
        resultItem.appendChild(scoreSpan);
        
        resultsList.appendChild(resultItem);
    });
    
    searchButton.disabled = false;
    searchButton.textContent = 'Search';
});

dropZone.addEventListener('dragover', event => {
    event.preventDefault();
});

dropZone.addEventListener('drop', event => {
    event.preventDefault();
    
    if (event.dataTransfer.files.length > 0) {
        handleFile(event.dataTransfer.files[0]);
    }
});

dropZone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0]);
    }
});

function handleFile(file) {
    if (file.type === 'application/pdf') {
        pdfViewer.src = URL.createObjectURL(file);
        updateSearchButton();
    }
}

function updateSearchButton() {
    if (labels.length > 0 && pdfViewer.src) {
        searchButton.disabled = false;
    } else {
        searchButton.disabled = true;
    }
}

updateSearchButton();
