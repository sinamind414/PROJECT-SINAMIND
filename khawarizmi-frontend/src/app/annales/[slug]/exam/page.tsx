"use client"

import { useParams } from "next/navigation"
import { PageShell } from "@/components/ui/PageShell"
import { BacBlancImmersif } from "@/components/bac_blanc/BacBlancImmersif"

export default function BacBlancExamPage() {
  const params = useParams()
  const slug = params.slug as string

  return (
    <PageShell wide>
      <BacBlancImmersif annaleSlug={slug} />
    </PageShell>
  )
}
