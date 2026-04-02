import { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { getStats } from '../api'

const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#8b5cf6', '#10b981', '#6b7280', '#ec4899']

export default function Stats() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    getStats().then(({ data }) => setStats(data))
  }, [])

  if (!stats) return <div className="text-center py-12 text-gray-400">Caricamento...</div>

  const categoryData = Object.entries(stats.by_category).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value,
  }))

  const statusData = Object.entries(stats.by_status).map(([name, value]) => ({
    name: name === 'new' ? 'Nuove' : name === 'classified' ? 'Classificate' : name === 'replied' ? 'Risposte' : name,
    value,
  }))

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-8">Statistiche</h1>

      {stats.total === 0 ? (
        <div className="text-center py-12 text-gray-400">
          Nessun dato. Recupera e classifica le email per vedere le statistiche.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-lg font-semibold mb-4">Per Categoria</h2>
            {categoryData.length === 0 ? (
              <p className="text-gray-400 text-center py-8">Nessuna email classificata</p>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={categoryData} cx="50%" cy="50%" outerRadius={100} dataKey="value" label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}>
                    {categoryData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-lg font-semibold mb-4">Per Stato</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={statusData}>
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
