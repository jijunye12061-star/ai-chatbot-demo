export async function fetchModels() {
  const res = await fetch('/api/models')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
