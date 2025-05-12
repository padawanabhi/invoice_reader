import React, { useState } from "react";

function UploadForm({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [receiptId, setReceiptId] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError("");
    setReceiptId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file.");
      return;
    }
    setUploading(true);
    setError("");
    setReceiptId(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/receipts/upload", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      setReceiptId(data.id);
      onUploadSuccess && onUploadSuccess(data.id);
    } catch (err) {
      setError("Upload failed. " + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 24 }}>
      <h2>Upload Receipt</h2>
      <input
        type="file"
        accept="image/*,.pdf"
        onChange={handleFileChange}
        disabled={uploading}
      />
      <button type="submit" disabled={uploading} style={{ marginLeft: 8 }}>
        {uploading ? "Uploading..." : "Upload"}
      </button>
      {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
      {receiptId && (
        <div style={{ color: "green", marginTop: 8 }}>
          Uploaded! Your receipt ID is <b>{receiptId}</b>
        </div>
      )}
    </form>
  );
}

export default UploadForm;