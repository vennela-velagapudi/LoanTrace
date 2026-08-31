async function run() {
    try {
        const tokenRes = await fetch("http://127.0.0.1:8000/api/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: "username=reviewer&password=demo123"
        });
        const tokenData = await tokenRes.json();
        const token = tokenData.access_token;
        
        console.log("Testing POST /api/ai/batch-summary with Origin: http://127.0.0.1:3000");
        const res = await fetch("http://127.0.0.1:8000/api/ai/batch-summary", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Origin": "http://127.0.0.1:3000",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({ exception_ids: [3] })
        });
        console.log(res.status, res.headers.get("access-control-allow-origin"));
    } catch (e) {
        console.error(e);
    }
}
run();
