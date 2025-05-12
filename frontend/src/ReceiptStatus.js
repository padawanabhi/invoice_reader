import React, { useState } from "react";

function ReceiptStatus({ defaultId }) {
  const [receiptId, setReceiptId] = useState(defaultId || "");
  const [loading, setLoading] = useState(false);
  const [receipt, setReceipt] = useState(null);
  const [error, setError] = useState("");

  const fetchStatus = async (e) => {
    e.preventDefault();
    if (!receiptId) return;
    setLoading(true);
    setError("");
    setReceipt(null);
    try {
      const res = await fetch(`http://localhost:8000/receipts/${receiptId}`);
      if (!res.ok) throw new Error("Not found");
      const data = await res.json();
      setReceipt(data);
    } catch (err) {
      setError("Could not fetch receipt. " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Check Receipt Status</h2>
      <form onSubmit={fetchStatus} style={{ marginBottom: 16 }}>
        <input
          type="number"
          placeholder="Enter receipt ID"
          value={receiptId}
          onChange={(e) => setReceiptId(e.target.value)}
          style={{ width: 120 }}
        />
        <button type="submit" disabled={loading || !receiptId} style={{ marginLeft: 8 }}>
          {loading ? "Checking..." : "Check"}
        </button>
      </form>
      {error && <div style={{ color: "red" }}>{error}</div>}
      {receipt && (
        <div style={{ background: "#f6f6f6", padding: 16, borderRadius: 8 }}>
          <div><b>Status:</b> {receipt.status}</div>
          <div><b>Filename:</b> {receipt.filename}</div>
          <div><b>Merchant:</b> {receipt.merchant || <i>Not found</i>}</div>
          <div><b>Date:</b> {receipt.date || <i>Not found</i>}</div>
          <div><b>Total:</b> {receipt.total || <i>Not found</i>}</div>
          <div><b>Group ID:</b> {receipt.group_id || <i>Not assigned</i>}</div>
        </div>
      )}
    </div>
  );
}

export default ReceiptStatus;