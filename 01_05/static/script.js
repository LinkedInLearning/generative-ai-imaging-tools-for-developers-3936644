// Load initial images
window.addEventListener('load', async function () {
  await loadImages();
});

const galleryDiv = document.getElementById('imageGallery');

async function loadImages() {
  showSpinner('gallerySpinner');
  try {
    const response = await fetch('/api/list/');
    const images = await response.json();
    galleryDiv.innerHTML = ''; // Clear existing content
    const imageCards = images.map(image => createImageCard(image.url, image.prompt));
    galleryDiv.append(...imageCards);
  } catch (error) {
    console.error('Error loading images:', error);
  } finally {
    hideSpinner('gallerySpinner');
  }
}

document.getElementById('promptForm').addEventListener('submit', async function (event) {
  event.preventDefault();
  const prompt = document.getElementById('prompt').value;
  showSpinner('generateSpinner');
  try {
    const response = await fetch('/api/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt: prompt })
    });
    const data = await response.json();
    const resultDiv = document.getElementById('result');
    if (data.url) {
      const imageCard = createImageCard(data.url, prompt);
      galleryDiv.prepend(imageCard); // Add the new image at the top
      resultDiv.innerHTML = `<div class="alert alert-success" role="alert">Image generated successfully!</div>`;
    } else {
      resultDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error generating image.</div>`;
    }
  } catch (error) {
    console.error('Error generating image:', error);
    document.getElementById('result').innerHTML = `<div class="alert alert-danger" role="alert">Error generating image.</div>`;
  } finally {
    hideSpinner('generateSpinner');
  }
});

function createImageCard(imageUrl, caption) {
  const colDiv = document.createElement('div');
  colDiv.className = 'col';

  const cardDiv = document.createElement('div');
  cardDiv.className = 'card h-100';

  const imgEl = document.createElement('img');
  imgEl.src = imageUrl;
  imgEl.className = 'card-img-top';
  imgEl.alt = caption;

  const cardBody = document.createElement('div');
  cardBody.className = 'card-body d-flex flex-column';

  const cardText = document.createElement('p');
  cardText.className = 'card-text flex-grow-1';
  cardText.textContent = caption;

  const downloadButton = document.createElement('a');
  downloadButton.className = 'btn btn-primary mt-2';
  downloadButton.href = imageUrl;
  downloadButton.download = '';
  downloadButton.textContent = 'Download Image';

  cardBody.appendChild(cardText);
  cardBody.appendChild(downloadButton);

  cardDiv.appendChild(imgEl);
  cardDiv.appendChild(cardBody);
  colDiv.appendChild(cardDiv);

  return colDiv;
}

function showSpinner(id) {
  document.getElementById(id).classList.remove('invisible');
  document.getElementById(id).classList.add('visible');
}

function hideSpinner(id) {
  document.getElementById(id).classList.remove('visible');
  document.getElementById(id).classList.add('invisible');
}
