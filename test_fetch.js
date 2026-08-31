fetch("http://localhost:8000/api/ai/batch-summary", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ exception_ids: [3] })
}).then(res => res.json()).then(console.log).catch(console.error);
