import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"

type Expense = {
  id: number
  desc: string
  category: string
  amount: number
  date: string
  user: string
}

async function getExpenses(): Promise<Expense[]> {
  try {
    // Determine the API URL based on environment (development vs production)
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8015/api"
    const res = await fetch(`${apiUrl}/expenses`, { cache: "no-store" })
    if (!res.ok) return []
    return res.json()
  } catch (e) {
    console.error("Error fetching expenses:", e)
    return []
  }
}

type DashboardData = {
  categories: { name: string, value: number }[]
  future: { month: string, amount: number }[]
}

async function getDashboardData(): Promise<DashboardData> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8015/api"
    const res = await fetch(`${apiUrl}/dashboard`, { cache: "no-store" })
    if (!res.ok) return { categories: [], future: [] }
    return res.json()
  } catch (e) {
    console.error("Error fetching dashboard data:", e)
    return { categories: [], future: [] }
  }
}

export default async function Dashboard() {
  const expenses = await getExpenses();
  const dashboardData = await getDashboardData();
  
  const maxCategoryAmount = Math.max(...dashboardData.categories.map(c => c.value), 1);
  const maxFutureAmount = Math.max(...dashboardData.future.map(f => f.amount), 1);
  
  // Calculate total dynamically based on fetched expenses
  const totalAmount = expenses.reduce((acc, exp) => acc + exp.amount, 0);
  
  const voceAmount = expenses
    .filter(exp => exp.user === "Você")
    .reduce((acc, exp) => acc + exp.amount, 0);

  const parceiroAmount = expenses
    .filter(exp => exp.user === "Parceiro")
    .reduce((acc, exp) => acc + exp.amount, 0);

  return (
    <div className="flex min-h-screen w-full flex-col bg-black text-zinc-50 selection:bg-emerald-500/30 font-sans">
      {/* Background Gradients */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-emerald-600/10 blur-[120px]" />
        <div className="absolute top-[60%] -right-[10%] w-[40%] h-[60%] rounded-full bg-teal-600/5 blur-[100px]" />
      </div>

      <div className="relative z-10 flex flex-col sm:gap-6 sm:py-6 sm:pl-14 max-w-7xl mx-auto w-full">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-white/5 bg-black/50 backdrop-blur-md px-4 sm:static sm:h-auto sm:border-0 sm:bg-transparent sm:px-6">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/10">
              <span className="font-bold text-black tracking-tighter">M</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-zinc-400">MeuSaldo</h1>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <Button size="sm" variant="outline" className="border-white/5 bg-white/5 hover:bg-white/10 text-zinc-300 transition-all duration-300">
              Convidar Parceiro
            </Button>
            <a href="http://meusaldo.linkwise.digital:3000/dashboard" target="_blank" rel="noopener noreferrer">
              <Button size="sm" className="bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-500/20 transition-all duration-300 hover:scale-105">
                Conectar WhatsApp
              </Button>
            </a>
          </div>
        </header>

        <main className="grid flex-1 items-start gap-6 p-4 sm:px-6 sm:py-0 md:gap-8 lg:grid-cols-3 xl:grid-cols-3 animate-in fade-in duration-1000">
          <div className="grid auto-rows-max items-start gap-6 md:gap-8 lg:col-span-2">
            <div className="grid gap-6 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-2 xl:grid-cols-4">
              <Card className="sm:col-span-2 bg-zinc-950/40 border-white/5 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.4)] transition-all duration-500 ease-out hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(16,185,129,0.1)] hover:border-emerald-500/20 hover:bg-white/[0.04] animate-in fade-in slide-in-from-bottom-8 duration-700 delay-100 fill-mode-both">
                <CardHeader className="pb-3">
                  <CardTitle className="text-zinc-300 font-medium tracking-wide text-sm uppercase">Gastos da Semana</CardTitle>
                  <CardDescription className="max-w-lg text-zinc-500 text-xs">
                    Resumo financeiro atualizado em tempo real via WhatsApp.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-5xl font-extrabold tracking-tighter text-white">
                    <span className="text-2xl text-zinc-500 font-normal mr-1">R$</span>
                    {totalAmount.toFixed(2).replace('.', ',')}
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-zinc-950/40 border-white/5 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.4)] transition-all duration-500 ease-out hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(16,185,129,0.1)] hover:border-emerald-500/20 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200 fill-mode-both">
                <CardHeader className="pb-2">
                  <CardDescription className="text-zinc-500">Você</CardDescription>
                  <CardTitle className="text-2xl font-bold text-white">R$ {voceAmount.toFixed(2).replace('.', ',')}</CardTitle>
                </CardHeader>
              </Card>
              <Card className="bg-zinc-950/40 border-white/5 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.4)] transition-all duration-500 ease-out hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(16,185,129,0.1)] hover:border-emerald-500/20 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300 fill-mode-both">
                <CardHeader className="pb-2">
                  <CardDescription className="text-zinc-500">Parceiro</CardDescription>
                  <CardTitle className="text-2xl font-bold text-white">R$ {parceiroAmount.toFixed(2).replace('.', ',')}</CardTitle>
                </CardHeader>
              </Card>
            </div>
            
            <Card className="bg-zinc-950/40 border-white/5 backdrop-blur-xl overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.4)] transition-all duration-500 hover:shadow-[0_20px_40px_rgba(0,0,0,0.6)] animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-500 fill-mode-both">
              <CardHeader className="px-7 border-b border-white/5 bg-white/[0.01]">
                <CardTitle className="text-zinc-200">Últimos Gastos</CardTitle>
                <CardDescription className="text-zinc-500">Histórico de despesas sincronizado.</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <Table>
                  <TableHeader className="bg-white/[0.01] hover:bg-transparent">
                    <TableRow className="border-white/5">
                      <TableHead className="text-zinc-500 font-medium">Data</TableHead>
                      <TableHead className="text-zinc-500 font-medium">Descrição</TableHead>
                      <TableHead className="hidden md:table-cell text-zinc-500 font-medium">Categoria</TableHead>
                      <TableHead className="text-right text-zinc-500 font-medium">Valor</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {expenses.length === 0 ? (
                      <TableRow className="border-white/5 hover:bg-white/[0.02]">
                        <TableCell colSpan={4} className="text-center text-zinc-600 py-8">
                          Nenhum gasto registrado ainda. Mande uma mensagem no WhatsApp!
                        </TableCell>
                      </TableRow>
                    ) : (
                      expenses.map((exp) => (
                        <TableRow key={exp.id} className="border-white/5 hover:bg-white/[0.03] transition-colors group cursor-default">
                          <TableCell className="text-zinc-400 group-hover:text-zinc-300 transition-colors">{exp.date}</TableCell>
                          <TableCell className="font-medium text-zinc-300 group-hover:text-white transition-colors">{exp.desc}</TableCell>
                          <TableCell className="hidden md:table-cell text-zinc-500">
                            <span className="inline-flex items-center rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-400 ring-1 ring-inset ring-emerald-500/20">
                              {exp.category || "Outros"}
                            </span>
                          </TableCell>
                          <TableCell className="text-right font-semibold text-rose-500 group-hover:text-rose-400 transition-colors">
                            R$ {exp.amount.toFixed(2).replace('.', ',')}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
          
          <div className="grid gap-6">
            <Card className="bg-zinc-950/40 border-white/5 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.4)] transition-all duration-500 hover:shadow-[0_20px_40px_rgba(0,0,0,0.6)] animate-in fade-in slide-in-from-right-8 duration-1000 delay-500 fill-mode-both">
              <CardHeader className="pb-3 border-b border-white/5 bg-white/[0.01]">
                <CardTitle className="text-zinc-200 text-base">Gastos por Categoria (Mês Atual)</CardTitle>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                {dashboardData.categories.length === 0 ? (
                  <div className="text-sm text-zinc-500 text-center py-4">Nenhum dado</div>
                ) : (
                  dashboardData.categories.map((cat, i) => (
                    <div key={i} className="space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-300 font-medium">{cat.name}</span>
                        <span className="text-zinc-400">R$ {cat.value.toFixed(2).replace('.', ',')}</span>
                      </div>
                      <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-emerald-500/80 rounded-full transition-all duration-1000 ease-out" 
                          style={{ width: `${(cat.value / maxCategoryAmount) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>

            <Card className="bg-zinc-950/40 border-white/5 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.4)] transition-all duration-500 hover:shadow-[0_20px_40px_rgba(0,0,0,0.6)] animate-in fade-in slide-in-from-right-8 duration-1000 delay-600 fill-mode-both">
              <CardHeader className="pb-3 border-b border-white/5 bg-white/[0.01]">
                <CardTitle className="text-zinc-200 text-base">Faturas Futuras (Parcelamentos)</CardTitle>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                {dashboardData.future.length === 0 ? (
                  <div className="text-sm text-zinc-500 text-center py-4">Nenhuma parcela futura</div>
                ) : (
                  dashboardData.future.map((fut, i) => (
                    <div key={i} className="space-y-1.5">
                      <div className="flex justify-between text-xs">
                        <span className="text-zinc-300 font-medium">{fut.month}</span>
                        <span className="text-rose-400 font-semibold">R$ {fut.amount.toFixed(2).replace('.', ',')}</span>
                      </div>
                      <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-rose-500/80 rounded-full transition-all duration-1000 ease-out" 
                          style={{ width: `${(fut.amount / maxFutureAmount) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))
                )}
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-emerald-950/40 to-teal-950/40 border-emerald-500/10 backdrop-blur-xl shadow-[0_8px_32px_rgba(0,0,0,0.4)] relative overflow-hidden group transition-all duration-500 ease-out hover:-translate-y-2 hover:shadow-[0_20px_40px_rgba(16,185,129,0.15)] hover:border-emerald-500/30 animate-in fade-in slide-in-from-right-8 duration-1000 delay-700 fill-mode-both">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <CardHeader className="relative z-10">
                <CardTitle className="text-white flex items-center gap-2">
                  <span className="text-xl">📱</span> WhatsApp API
                </CardTitle>
                <CardDescription className="text-emerald-200/60">
                  Como registrar seus gastos magicamente
                </CardDescription>
              </CardHeader>
              <CardContent className="relative z-10 text-sm">
                <div className="grid gap-4">
                  <div className="space-y-2">
                    <div className="font-medium text-emerald-100/90">Envie uma mensagem natural:</div>
                    <div className="p-3 rounded-lg bg-black/40 border border-emerald-500/10 text-emerald-200/80 font-mono text-xs shadow-inner">
                      "Gastei 50 pila no ifood hj"
                    </div>
                    <div className="p-3 rounded-lg bg-black/40 border border-emerald-500/10 text-emerald-200/80 font-mono text-xs shadow-inner">
                      "Uber 25,90"
                    </div>
                  </div>
                  
                  <div className="pt-2 border-t border-emerald-500/10">
                    <div className="font-medium text-emerald-100/90 mb-2 mt-2">💡 Automação Pro:</div>
                    <p className="text-emerald-200/50 text-xs leading-relaxed">
                      Use o app <strong>MacroDroid</strong> no Android para ler notificações do seu cartão de crédito (Nubank, Itaú, etc) e enviar a mensagem via Waha API sem você encostar no celular!
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
