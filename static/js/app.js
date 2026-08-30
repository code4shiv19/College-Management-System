document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.auto-dismiss').forEach(el => setTimeout(() => el.remove(), 4500));

  // Client-side list search
  document.querySelectorAll('[data-search-target]').forEach(input => {
    input.addEventListener('input', () => {
      const query = input.value.toLowerCase().trim();
      document.querySelectorAll(input.dataset.searchTarget).forEach(item => {
        item.style.display = item.textContent.toLowerCase().includes(query) ? '' : 'none';
      });
    });
  });

  // Any broken uploaded image gets a clean avatar instead of a broken-image icon.
  document.querySelectorAll('img[data-fallback]').forEach(img => {
    img.addEventListener('error', () => {
      img.style.display = 'none';
      const fallback = document.getElementById(img.dataset.fallback);
      if (fallback) fallback.classList.remove('d-none');
    });
  });

  function previewFile(input, image, fallback) {
    const file = input?.files?.[0];
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = e => {
      if (image) {
        image.src = e.target.result;
        image.classList.remove('d-none');
      }
      if (fallback) fallback.classList.add('d-none');
    };
    reader.readAsDataURL(file);
  }

  // Profile upload preview + drag/drop
  const profileInput = document.querySelector('#id_photo');
  const profilePreview = document.querySelector('#photoPreview');
  const profileFallback = document.querySelector('#photoPreviewFallback');
  const profileZone = document.querySelector('#uploadZone');
  if (profileInput) {
    profileInput.addEventListener('change', () => previewFile(profileInput, profilePreview, profileFallback));
    ['dragenter','dragover'].forEach(evt => profileZone?.addEventListener(evt, e => { e.preventDefault(); profileZone.classList.add('dragover'); }));
    ['dragleave','drop'].forEach(evt => profileZone?.addEventListener(evt, e => { e.preventDefault(); profileZone.classList.remove('dragover'); }));
    profileZone?.addEventListener('drop', e => {
      if (e.dataTransfer.files.length) {
        profileInput.files = e.dataTransfer.files;
        profileInput.dispatchEvent(new Event('change'));
      }
    });
  }

  // Management forms: photo and course-cover preview + drag/drop
  document.querySelectorAll('.upload-zone').forEach(zone => {
    const input = zone.querySelector('input[type=file]');
    if (!input) return;
    const image = zone.querySelector('img[id^="manage"]');
    input.addEventListener('change', () => {
      const file = input.files?.[0];
      if (!file || !file.type.startsWith('image/')) return;
      const reader = new FileReader();
      reader.onload = e => {
        if (image) image.src = e.target.result;
        else {
          const holder = zone.querySelector('[id$="Wrap"]');
          if (holder) {
            const isCover = input.name === 'cover_image';
            holder.innerHTML = `<img src="${e.target.result}" class="${isCover ? 'course-cover' : 'profile-img-lg'} mx-auto mb-3" alt="Preview">`;
          }
        }
      };
      reader.readAsDataURL(file);
    });
    ['dragenter','dragover'].forEach(evt => zone.addEventListener(evt, e => { e.preventDefault(); zone.classList.add('dragover'); }));
    ['dragleave','drop'].forEach(evt => zone.addEventListener(evt, e => { e.preventDefault(); zone.classList.remove('dragover'); }));
    zone.addEventListener('drop', e => {
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        input.dispatchEvent(new Event('change'));
      }
    });
  });
});
