import { useMemo } from 'react'

export default function App() {
  const year = useMemo(() => new Date().getFullYear(), [])

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-4xl flex-col px-6 py-10">
        <header className="flex items-start justify-between gap-6">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">ModeShift</h1>
            <p className="mt-2 max-w-prose text-sm text-slate-600">
              Frontend is running. If you expected specific pages/components, wire them here.
            </p>
          </div>
          <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-800">
            OK
          </span>
        </header>

        <main className="mt-10 flex-1">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="text-sm font-medium text-slate-900">Next steps</div>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-700">
              <li>Keep this as a health-check page, or replace with your real router/layout.</li>
              <li>Backend pages can still be served by Django templates in parallel.</li>
            </ul>
          </div>
        </main>

        <footer className="mt-10 text-xs text-slate-500">
          © {year} ModeShift
        </footer>
      </div>
    </div>
  )
}
