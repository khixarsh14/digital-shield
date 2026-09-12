import { LockKeyhole } from "lucide-react"

export default function PrivacyNotice() {
  return (
    <aside className="privacy-notice">
      <LockKeyhole size={18} aria-hidden="true" />
      <div><strong>Private by design</strong><p id="privacy-description">Only the content you submit is analyzed. We do not access your chats, contacts, or unrelated data.</p></div>
    </aside>
  )
}
