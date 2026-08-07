"use client"

import { useState } from "react"
import { Check, LocateFixed, MapPin, Send, ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"

const languages = [{ code: "en", label: "English" }, { code: "hi", label: "हिन्दी" }, { code: "te", label: "తెలుగు" }, { code: "ta", label: "தமிழ்" }, { code: "kn", label: "ಕನ್ನಡ" }, { code: "ml", label: "മലയാളം" }, { code: "mr", label: "मराठी" }, { code: "bn", label: "বাংলা" }, { code: "gu", label: "ગુજરાતી" }, { code: "pa", label: "ਪੰਜਾਬੀ" }, { code: "ur", label: "اردو" }]

export function ComplaintComposer() {
  const [language, setLanguage] = useState("en")
  const [description, setDescription] = useState("")
  const [address, setAddress] = useState("")
  const [contact, setContact] = useState("")
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null)
  const [status, setStatus] = useState<"idle" | "locating" | "submitting" | "done" | "error">("idle")
  const [result, setResult] = useState<{ complaint_id: string; tracking_code: string; ward: string; department: string } | null>(null)
  const [error, setError] = useState("")

  const locate = () => {
    if (!navigator.geolocation) { setError("Location is not available in this browser. You can enter your area below."); return }
    setStatus("locating")
    navigator.geolocation.getCurrentPosition((position) => { setLocation({ latitude: position.coords.latitude, longitude: position.coords.longitude }); setStatus("idle") }, () => { setStatus("idle"); setError("We could not access your location. You can still submit with an address or landmark.") }, { enableHighAccuracy: true, timeout: 8000 })
  }

  const submit = async () => {
    if (description.trim().length < 12 || (!address.trim() && !location)) { setError("Add a little more detail and either share your location or enter an address."); return }
    setStatus("submitting"); setError("")
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/complaints`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ description, language, address: address || null, contact: contact || null, latitude: location?.latitude ?? null, longitude: location?.longitude ?? null }) })
      if (!response.ok) throw new Error("Unable to submit")
      setResult(await response.json()); setStatus("done")
    } catch { setStatus("error"); setError("The service is temporarily unavailable. Please try again, or use the tracking page if you already submitted.") }
  }

  if (status === "done" && result) return <Card className="border-primary/30 shadow-lg shadow-primary/5"><CardHeader><div className="mb-2 grid size-12 place-items-center rounded-2xl bg-primary/10 text-primary"><Check /></div><CardTitle className="text-2xl">Your complaint is registered</CardTitle><CardDescription>Save these details. You can track progress without creating an account.</CardDescription></CardHeader><CardContent className="flex flex-col gap-5"><div className="grid gap-3 rounded-xl bg-secondary p-5 sm:grid-cols-2"><div><p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Complaint ID</p><p className="mt-1 font-mono text-lg font-semibold">{result.complaint_id}</p></div><div><p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Private tracking code</p><p className="mt-1 font-mono text-lg font-semibold text-primary">{result.tracking_code}</p></div><div><p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Routed to</p><p className="mt-1 font-medium">{result.department}</p></div><div><p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Area queue</p><p className="mt-1 font-medium">{result.ward}</p></div></div><Alert><ShieldCheck className="size-4" /><AlertDescription>We store only the location precision needed to route this complaint. Exact coordinates are not shown on the public tracking page.</AlertDescription></Alert><Button onClick={() => window.location.href = `/track?code=${result.tracking_code}`}>Track this complaint</Button></CardContent></Card>

  return <Card className="border-border shadow-lg shadow-primary/5"><CardHeader><div className="flex items-start justify-between gap-4"><div><CardTitle className="text-2xl">Tell us what happened</CardTitle><CardDescription className="mt-2">No account or OTP. Your tracking code is created after submission.</CardDescription></div><div className="hidden size-11 place-items-center rounded-xl bg-primary/10 text-primary sm:grid"><Send /></div></div></CardHeader><CardContent className="flex flex-col gap-6"><div><Label htmlFor="language">Language</Label><select id="language" value={language} onChange={(event) => setLanguage(event.target.value)} className="mt-2 flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm outline-none focus:ring-2 focus:ring-ring" dir={language === "ur" ? "rtl" : "ltr"}>{languages.map((item) => <option key={item.code} value={item.code}>{item.label}</option>)}</select></div><div><Label htmlFor="description">Describe the issue <span className="text-muted-foreground">(required)</span></Label><Textarea id="description" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="For example: The streetlight outside the community clinic has not worked for three nights." className="mt-2 min-h-36 resize-y" maxLength={2000} /><p className="mt-2 text-xs text-muted-foreground">{description.length}/2000 · Include a landmark, what is affected, and how long it has been happening.</p></div><div className="rounded-xl border border-border bg-secondary/40 p-4"><div className="mb-3 flex items-center gap-2"><MapPin className="size-4 text-primary" /><div><p className="text-sm font-medium">Where is it?</p><p className="text-xs text-muted-foreground">Used to route your complaint to the right local queue.</p></div></div><Button type="button" variant="outline" onClick={locate} disabled={status === "locating"} className="w-full sm:w-auto"><LocateFixed data-icon="inline-start" />{status === "locating" ? "Finding your location…" : location ? "Location captured" : "Use my current location"}</Button><div className="mt-3"><Label htmlFor="address" className="text-xs">Or enter an address / landmark</Label><Input id="address" value={address} onChange={(event) => setAddress(event.target.value)} placeholder="Street, landmark, locality, pincode" className="mt-2" /></div>{location && <p className="mt-3 text-xs text-primary">Location captured privately for routing.</p>}</div><div><Label htmlFor="contact">Phone or email <span className="text-muted-foreground">(optional)</span></Label><Input id="contact" value={contact} onChange={(event) => setContact(event.target.value)} placeholder="Only if you want updates from the department" className="mt-2" /></div>{error && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}<Button onClick={submit} disabled={status === "submitting"} size="lg" className="h-12">{status === "submitting" ? "Registering complaint…" : "Submit complaint"}<Send data-icon="inline-end" /></Button><p className="text-center text-xs text-muted-foreground">By submitting, you agree that this information may be shared with the responsible public department.</p></CardContent></Card>
}
