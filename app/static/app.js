async function uploadFile() {
  const fileInput = document.getElementById('file');
  const file = fileInput.files[0];
  if (!file) {
    alert('Select a file first');
    return;
  }
  const fd = new FormData();
  fd.append('file', file);
  document.getElementById('uploadStatus').innerText = 'Uploading...';
  try {
    const res = await fetch('/upload-news', { method: 'POST', body: fd });
    const j = await res.json();
    document.getElementById('uploadStatus').innerText = `Uploaded: ${j.status}, ${j.count || 0} items`;
  } catch (e) {
    document.getElementById('uploadStatus').innerText = 'Upload failed';
    console.error(e);
  }
}

async function runPipeline() {
  document.getElementById('output').innerText = 'Running pipeline...';
  try {
    const res = await fetch('/run-pipeline', { method: 'POST' });
    const j = await res.json();
    document.getElementById('output').innerText = JSON.stringify(j, null, 2);
  } catch (e) {
    document.getElementById('output').innerText = 'Pipeline failed';
    console.error(e);
  }
}

document.getElementById('uploadBtn').addEventListener('click', uploadFile);
document.getElementById('runBtn').addEventListener('click', runPipeline);
