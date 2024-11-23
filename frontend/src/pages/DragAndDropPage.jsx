import React from 'react';

function DragAndDropPage() {
  return (
    <div className="container text-center py-5">
      <h1 className="mb-4">Drag and Drop Page</h1>
      <div
        className="border p-5 my-3"
        style={{ borderRadius: '10px', borderStyle: 'dashed', borderColor: '#ccc' }}
      >
        <p className="text-muted">Drag and drop a PDF document here or click to upload.</p>
      </div>
    </div>
  );
}

export default DragAndDropPage;
