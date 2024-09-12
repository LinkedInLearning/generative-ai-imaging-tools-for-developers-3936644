// Load initial images
window.addEventListener('load', async function (e) {
  await loadImages();
});
const galleryDiv = document.getElementById('imageGallery');
async function loadImages() {
  showSpinner('gallerySpinner');
  try {
    const response = await fetch('/api/list/');
    const images = await response.json();
    galleryDiv.innerHTML = ''; // Clear existing content
    const imageBoxes = images.map(image => createPhotoBox(image.url, image.prompt))

    galleryDiv.append(...imageBoxes);
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
      const imageBox = createPhotoBox(data.url, prompt);
      galleryDiv.prepend(imageBox);
    } else {
      resultDiv.innerHTML = `<p>Error generating image.</p>`;
    }
  } catch (error) {
    console.error('Error generating image:', error);
    document.getElementById('result').innerHTML = `<p>Error generating image.</p>`;
  } finally {
    hideSpinner('generateSpinner');
  }
});

function createPhotoBox(imageUrl, caption) {
  const imageEl = document.createElement('img');
  imageEl.src = imageUrl;
  const photoBox = document.createElement('div');
  photoBox.className = 'pure-u-1 pure-u-md-1-2 pure-u-lg-1-3';
  photoBox.appendChild(imageEl);
  return photoBox
}

function showSpinner(id) {
  document.getElementById(id).style.display = 'block';
}

function hideSpinner(id) {
  document.getElementById(id).style.display = 'none';
}