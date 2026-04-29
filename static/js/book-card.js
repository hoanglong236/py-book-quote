document.addEventListener('submit', event => {
  const form = event.target.closest('.delete-book-form');
  if (!form) return;

  const bookTitle = form.dataset.bookTitle?.trim() || 'this book';
  const message = `Are you sure you want to delete ${bookTitle}?`;

  if (!confirm(message)) {
    event.preventDefault();
  }
});
