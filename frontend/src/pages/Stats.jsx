import { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { getStats, getAccuracyStats } from '../api'

const COLORS = ['#3b82f6', '#ef4444', '#f59e0b', '#8b5cf6', '#10b981', '#6b7280', '#ec4899']

export default function Stats() {
  const [stats, setStats] = useState(null)
  const [accuracy, setAccuracy] = useState(null)

  useEffect(() => {
    getStats().then(({ data }) => setStats(data))
    getAccuracyStats().then(({ data }) => setAccuracy(data)).catch(() => {})
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
        <div className="space-y-6">
          {/* Accuracy section */}
          {accuracy && accuracy.total_corrected > 0 && (
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h2 className="text-lg font-semibold mb-4">Accuratezza Classificazione</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-green-50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-green-600">{Math.round(accuracy.accuracy * 100)}%</p>
                  <p className="text-sm text-green-700 mt-1">Accuratezza</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-blue-600">{accuracy.total_corrected}</p>
                  <p className="text-sm text-blue-700 mt-1">Email corrette manualmente</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4 text-center">
                  <p className="text-3xl font-bold text-purple-600">{accuracy.correct_predictions}</p>
                  <p className="text-sm text-purple-700 mt-1">Predizioni corrette</p>
                </div>
              </div>
              {accuracy.by_category && Object.keys(accuracy.by_category).length > 0 && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-600 mb-2">Per Categoria</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {Object.entries(accuracy.by_category).map(([cat, data]) => (
                      <div key={cat} className="bg-gray-50 rounded-lg p-3">
                        <p className="text-sm font-medium text-gray-700">{cat.replace('_', ' ')}</p>
                        <p className="text-lg font-bold text-gray-800">{Math.round(data.accuracy * 100)}%</p>
                        <p className="text-xs text-gray-500">{data.correct}/{data.total}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

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
        </div>
      )}
    </div>
  )
}
