import React, { useState } from "react";
import UploadForm from "./UploadForm";
import ReceiptStatus from "./ReceiptStatus";

function App() {
  const [lastReceiptId, setLastReceiptId] = useState(null);

  return (
    <div style={{ maxWidth: 500, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>Invoice/Receipt Analyzer</h1>
      <UploadForm onUploadSuccess={setLastReceiptId} />
      <hr style={{ margin: "2em 0" }} />
      <ReceiptStatus defaultId={lastReceiptId} />
    </div>
  );
}

export default App;