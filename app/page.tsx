import Link from "next/link"
import { ArrowRight, Languages, LocateFixed, ShieldCheck, TicketCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

const languageLabels = ["English", "हिन्दी", "తెలుగు", "தமிழ்", "ಕನ್ನಡ", "മലയാളം", "मराठी", "বাংলা", "ગુજરાતી", "ਪੰਜਾਬੀ", "اردو"]

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      <header className="border-b border-border/70 bg-background/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-5 py-4 lg:px-8">
          <Link href="/" className="flex items-center gap-3" aria-label="Nagrik Seva home">
            <span className="grid size-10 place-items-center rounded-xl bg-primary text-primary-foreground"><ShieldCheck data-icon="inline-start" /></span>
            <span><span className="block font-semibold tracking-tight">Nagrik Seva</span><span className="block text-xs text-muted-foreground">Public grievance redressal</span></span>
          </Link>
          <nav className="flex items-center gap-2" aria-label="Main navigation">
            <Link href="/track"><Button variant="ghost" size="sm">Track a complaint</Button></Link>
            <Link href="/admin/login"><Button variant="outline" size="sm">Staff sign in</Button></Link>
          </nav>
        </div>
      </header>

      <section className="mx-auto grid max-w-6xl gap-12 px-5 pb-16 pt-16 lg:grid-cols-[1.1fr_.9fr] lg:px-8 lg:pb-24 lg:pt-24">
        <div className="flex flex-col justify-center gap-7">
          <div className="flex w-fit items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1.5 text-sm text-primary"><span className="size-2 rounded-full bg-primary" /> One civic desk for every neighbourhood</div>
          <h1 className="max-w-3xl text-balance text-5xl font-semibold tracking-[-0.04em] text-foreground md:text-6xl">Report what needs fixing. <span className="text-primary">Follow what happens next.</span></h1>
          <p className="max-w-xl text-pretty text-lg leading-8 text-muted-foreground">A simpler way to reach the right local department. Submit in your language, share the location, and keep the tracking code to see every update.</p>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link href="/submit-complaint"><Button size="lg" className="h-12 px-6">Submit a complaint <ArrowRight data-icon="inline-end" /></Button></Link>
            <Link href="/track"><Button size="lg" variant="outline" className="h-12 px-6">I already have a tracking code</Button></Link>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground"><ShieldCheck className="size-4 text-primary" /> No account, Aadhaar, OTP, or unnecessary personal details required.</div>
        </div>

        <Card className="overflow-hidden border-border bg-card shadow-xl shadow-primary/5">
          <CardContent className="flex flex-col gap-6 p-6 sm:p-8">
            <div className="flex items-start justify-between gap-4"><div><p className="text-sm font-medium text-primary">How it works</p><h2 className="mt-2 text-2xl font-semibold tracking-tight">From street to solution</h2></div><div className="grid size-12 place-items-center rounded-2xl bg-primary/10 text-primary"><TicketCheck /></div></div>
            {[{ icon: TicketCheck, title: "Tell us once", body: "Describe the issue in the language you are most comfortable using." }, { icon: LocateFixed, title: "We route it locally", body: "Your ward and department are identified from the location you share." }, { icon: ShieldCheck, title: "You stay informed", body: "Use one private tracking code to follow the resolution timeline." }].map(({ icon: Icon, title, body }) => <div key={title} className="flex gap-4 border-t border-border pt-5"><div className="grid size-10 shrink-0 place-items-center rounded-xl bg-secondary text-primary"><Icon className="size-5" /></div><div><h3 className="font-medium">{title}</h3><p className="mt-1 text-sm leading-6 text-muted-foreground">{body}</p></div></div>)}
            <div className="rounded-xl bg-secondary/60 p-4"><div className="mb-3 flex items-center gap-2 text-sm font-medium"><Languages className="size-4 text-primary" /> Available in 11 languages</div><div className="flex flex-wrap gap-2">{languageLabels.map((language) => <span key={language} className="rounded-md border border-border bg-background px-2 py-1 text-xs text-muted-foreground">{language}</span>)}</div></div>
          </CardContent>
        </Card>
      </section>

      <section className="border-y border-border bg-secondary/40"><div className="mx-auto grid max-w-6xl gap-6 px-5 py-12 md:grid-cols-3 lg:px-8"><div><p className="text-3xl font-semibold tracking-tight">One code</p><p className="mt-1 text-sm text-muted-foreground">to check your complaint without logging in</p></div><div><p className="text-3xl font-semibold tracking-tight">11 languages</p><p className="mt-1 text-sm text-muted-foreground">with right-to-left Urdu support</p></div><div><p className="text-3xl font-semibold tracking-tight">Local routing</p><p className="mt-1 text-sm text-muted-foreground">to your ward and responsible department</p></div></div></section>
      <footer className="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-8 text-sm text-muted-foreground lg:px-8 sm:flex-row sm:items-center sm:justify-between"><p>Nagrik Seva · A transparent public service</p><p>Your location is used only to route your complaint.</p></footer>
    </main>
  )
}
