import re

file_path = 'frontend/src/app/reviewer/page.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add filterStatus state
content = content.replace(
    'const [exceptions, setExceptions] = useState<any[]>([]);',
    'const [exceptions, setExceptions] = useState<any[]>([]);\n  const [filterStatus, setFilterStatus] = useState<string>("ALL");'
)

# Update the boxes
old_boxes = """      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Total Exceptions</h3>
            <p className="text-3xl font-bold">{summary.total_validation_failures}</p>
          </div>
          <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Open</h3>
            <p className="text-3xl font-bold text-orange-600">
  		{summary.open_exceptions}
	    </p>
          </div>
          <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">In Review</h3>
            <p className="text-3xl font-bold text-blue-600">
              {exceptions.filter(e => e.status === "IN_REVIEW").length}
            </p>
          </div>
          <div className="bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 shadow-sm">
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Resolved</h3>
            <p className="text-3xl font-bold text-green-600">
  		{summary.resolved_exceptions}
	    </p>
          </div>
        </div>
      )}"""

new_boxes = """      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div 
            onClick={() => setFilterStatus("ALL")}
            className={`bg-[var(--card)] border rounded-xl p-4 shadow-sm cursor-pointer transition-all ${filterStatus === 'ALL' ? 'ring-2 ring-slate-400 border-transparent' : 'border-[var(--border)] hover:border-slate-400'}`}
          >
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Total Exceptions</h3>
            <p className="text-3xl font-bold">{summary.total_validation_failures}</p>
          </div>
          <div 
            onClick={() => setFilterStatus("OPEN")}
            className={`bg-[var(--card)] border rounded-xl p-4 shadow-sm cursor-pointer transition-all ${filterStatus === 'OPEN' ? 'ring-2 ring-orange-500 border-transparent' : 'border-[var(--border)] hover:border-orange-300'}`}
          >
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Open</h3>
            <p className="text-3xl font-bold text-orange-600">
  		{summary.open_exceptions}
	    </p>
          </div>
          <div 
            onClick={() => setFilterStatus("IN_REVIEW")}
            className={`bg-[var(--card)] border rounded-xl p-4 shadow-sm cursor-pointer transition-all ${filterStatus === 'IN_REVIEW' ? 'ring-2 ring-blue-500 border-transparent' : 'border-[var(--border)] hover:border-blue-300'}`}
          >
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">In Review</h3>
            <p className="text-3xl font-bold text-blue-600">
              {exceptions.filter(e => e.status === "IN_REVIEW").length}
            </p>
          </div>
          <div 
            onClick={() => setFilterStatus("RESOLVED")}
            className={`bg-[var(--card)] border rounded-xl p-4 shadow-sm cursor-pointer transition-all ${filterStatus === 'RESOLVED' ? 'ring-2 ring-green-500 border-transparent' : 'border-[var(--border)] hover:border-green-300'}`}
          >
            <h3 className="text-sm font-medium text-[var(--muted-foreground)] mb-1">Resolved</h3>
            <p className="text-3xl font-bold text-green-600">
  		{summary.resolved_exceptions}
	    </p>
          </div>
        </div>
      )}"""

content = content.replace(old_boxes, new_boxes)

# Apply the filter logic
content = content.replace(
    '<tbody>\n              {exceptions.map(exc => (',
    '<tbody>\n              {exceptions.filter(e => filterStatus === "ALL" || e.status === filterStatus).map(exc => ('
)
content = content.replace(
    '{exceptions.length === 0 && (',
    '{exceptions.filter(e => filterStatus === "ALL" || e.status === filterStatus).length === 0 && ('
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
