fetch("http://localhost:8000/api/ai/batch-summary", {
  method: "POST",
  headers: { 
    "Content-Type": "application/json",
    "Origin": "http://localhost:3000"
  },
  body: JSON.stringify({ exception_ids: [3] })
}).then(res => {
  console.log(res.status, res.headers);
  return res.json();
}).then(console.log).catch(console.error);
