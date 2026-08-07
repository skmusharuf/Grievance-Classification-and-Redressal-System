import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ComplaintComposer } from "@/components/complaint-composer"

export default function SubmitComplaintPage() {
  return <main className="min-h-screen bg-background"><header className="border-b border-border/70"><div className="mx-auto flex max-w-5xl items-center px-5 py-4 lg:px-8"><Link href="/"><Button variant="ghost" size="sm"><ArrowLeft data-icon="inline-start" />Back</Button></Link></div></header><section className="mx-auto max-w-3xl px-5 py-10 lg:px-8 lg:py-16"><div className="mb-8"><p className="text-sm font-medium text-primary">New complaint</p><h1 className="mt-2 text-4xl font-semibold tracking-tight text-balance">Reach the right local team in one go.</h1><p className="mt-3 max-w-2xl text-lg leading-7 text-muted-foreground">Share the issue, tell us where it is, and we will route it to the correct ward and department.</p></div><ComplaintComposer /></section></main>
}
