"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function SettingsCard({ initialPersonality, initialGoals }: { initialPersonality: string, initialGoals: any[] }) {
  const [personality, setPersonality] = useState(initialPersonality)
  const [newCat, setNewCat] = useState("")
  const [newAmount, setNewAmount] = useState("")

  const personalities = [
    "Sarcástico e Engraçado",
    "Sério e Profissional",
    "Fofo e Motivador",
    "Agressivo e Cobrador"
  ]

  const updatePersonality = async (val: string) => {
    setPersonality(val)
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8015/api"
    await fetch(`${apiUrl}/settings/personality`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ personality: val })
    })
  }

  const addGoal = async () => {
    if (!newCat || !newAmount) return
    const amount = parseFloat(newAmount)
    if (isNaN(amount)) return

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8015/api"
    await fetch(`${apiUrl}/settings/goals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category: newCat, amount })
    })
    
    // Simplification for MVP: just reload the page to refresh server data
    window.location.reload()
  }

  const deleteGoal = async (id: number) => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8015/api"
    await fetch(`${apiUrl}/settings/goals/${id}`, {
      method: 'DELETE'
    })
    window.location.reload()
  }

  return (
    <Card className="bg-zinc-950/40 border-white/5 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.4)] transition-all duration-500 hover:shadow-[0_20px_40px_rgba(0,0,0,0.6)] animate-in fade-in slide-in-from-right-8 duration-1000 delay-800 fill-mode-both">
      <CardHeader className="pb-3 border-b border-white/5 bg-white/[0.01]">
        <CardTitle className="text-zinc-200 text-base flex items-center gap-2">
          <span>🤖</span> Configuração da IA
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4 space-y-6">
        <div className="space-y-2">
          <label className="text-sm text-zinc-400 font-medium">Personalidade do Assistente</label>
          <select 
            className="w-full bg-black/40 border border-white/10 rounded-md p-2 text-sm text-white focus:outline-none focus:border-emerald-500/50 transition-colors"
            value={personality}
            onChange={(e) => updatePersonality(e.target.value)}
          >
            {personalities.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>

        <div className="space-y-4">
          <div className="text-sm text-zinc-400 font-medium border-b border-white/5 pb-2 flex items-center gap-2">
            <span>🎯</span> Metas Semanais (Alertas)
          </div>
          
          <div className="space-y-3">
            {initialGoals.length === 0 ? (
              <div className="text-xs text-zinc-500 text-center italic py-2">Nenhuma meta configurada.</div>
            ) : (
              initialGoals.map((g: any, i: number) => {
                const percent = Math.min((g.spent / g.amount) * 100, 100);
                const isWarning = percent >= 90;
                return (
                  <div key={i} className="space-y-1.5 group relative">
                    <div className="flex justify-between text-xs">
                      <span className="text-zinc-300 font-medium">{g.category}</span>
                      <span className={isWarning ? "text-rose-400 font-bold" : "text-zinc-400"}>
                        R$ {g.spent.toFixed(2).replace('.', ',')} / R$ {g.amount.toFixed(2).replace('.', ',')}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="h-2 flex-1 bg-white/5 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-1000 ease-out ${isWarning ? 'bg-rose-500' : 'bg-emerald-500'}`}
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                      <button onClick={() => deleteGoal(g.id)} className="text-xs text-zinc-600 hover:text-rose-400 transition-colors px-1" title="Remover meta">×</button>
                    </div>
                  </div>
                )
              })
            )}
          </div>

          <div className="flex gap-2 pt-2">
            <input 
              type="text" 
              placeholder="Ex: Alimentação" 
              className="flex-1 bg-black/40 border border-white/10 rounded-md p-2 text-xs text-white focus:outline-none focus:border-emerald-500/50"
              value={newCat}
              onChange={e => setNewCat(e.target.value)}
            />
            <input 
              type="number" 
              placeholder="R$ 500" 
              className="w-20 bg-black/40 border border-white/10 rounded-md p-2 text-xs text-white focus:outline-none focus:border-emerald-500/50"
              value={newAmount}
              onChange={e => setNewAmount(e.target.value)}
            />
            <Button size="sm" onClick={addGoal} className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-3">Add</Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
