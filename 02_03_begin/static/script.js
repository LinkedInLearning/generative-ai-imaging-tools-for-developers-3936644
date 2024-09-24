window.addEventListener('load', async function () {
  // DOM is fully loaded
  const galleryDiv = document.getElementById('imageGallery');
  const resultDiv = document.getElementById('result');
  const generateSpinner = document.getElementById('generateSpinner');
  const gallerySpinner = document.getElementById('gallerySpinner');

  // Load initial images
  await loadImages();

  // Event listener for prompt form submission
  document.getElementById('promptForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    const prompt = document.getElementById('prompt').value.trim();
    if (!prompt) return;
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
      if (data.url) {
        const imageCard = createImageCard(data.url, prompt);
        galleryDiv.prepend(imageCard); // Add the new image at the top
        resultDiv.innerHTML = `<div class="alert alert-success" role="alert">Image generated successfully!</div>`;
      } else {
        resultDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error generating image: ${data.error || 'Unknown error'}</div>`;
      }
    } catch (error) {
      console.error('Error generating image:', error);
      resultDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error generating image.</div>`;
    } finally {
      hideSpinner('generateSpinner');
    }
  });

  // Function to load images
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
      resultDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error loading images.</div>`;
    } finally {
      hideSpinner('gallerySpinner');
    }
  }

  // Function to create an image card
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

    // Add the Variations button
    const variationsButton = document.createElement('button');
    variationsButton.className = 'btn btn-secondary mt-2';
    variationsButton.textContent = 'Variations';
    variationsButton.addEventListener('click', function () {
      generateVariations(imageUrl);
    });

    cardBody.appendChild(cardText);
    cardBody.appendChild(downloadButton);
    cardBody.appendChild(variationsButton); // Append the Variations button

    cardDiv.appendChild(imgEl);
    cardDiv.appendChild(cardBody);
    colDiv.appendChild(cardDiv);

    return colDiv;
  }

  // Function to generate variations of an image
  async function generateVariations(imageUrl) {
    const imageFilename = imageUrl.split('/').pop(); // Extract the image filename from the URL
    showSpinner('generateSpinner');
    try {
      const response = await fetch('/api/variations/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageFilename })
      });
      const data = await response.json();
      if (data.success) {
        resultDiv.innerHTML = `<div class="alert alert-success" role="alert">Variations generated successfully!</div>`;
        // Add the variation images to the gallery
        data.images.forEach(variationUrl => {
          const variationCard = createImageCard(variationUrl, 'Variation of ' + imageFilename);
          galleryDiv.prepend(variationCard); // Add the new images at the top
        });
      } else {
        resultDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error generating variations: ${data.error || 'Unknown error'}</div>`;
      }
    } catch (error) {
      console.error('Error generating variations:', error);
      resultDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error generating variations.</div>`;
    } finally {
      hideSpinner('generateSpinner');
    }
  }

  // Function to show a spinner
  function showSpinner(id) {
    document.getElementById(id).classList.remove('invisible');
    document.getElementById(id).classList.add('visible');
  }

  // Function to hide a spinner
  function hideSpinner(id) {
    document.getElementById(id).classList.remove('visible');
    document.getElementById(id).classList.add('invisible');
  }
});
