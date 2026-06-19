interface SubmissionDialogProps {
  open: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function SubmissionDialog({ open, onConfirm, onCancel }: SubmissionDialogProps) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-sm w-full mx-4 shadow-2xl space-y-4">
        <div className="text-center space-y-2">
          <p className="text-4xl">📮</p>
          <h3 className="text-lg font-bold text-white">هل تريد تسليم إجاباتك؟</h3>
          <p className="text-sm text-slate-400">
            لن تستطيع تعديلها بعد التسليم.
          </p>
        </div>

        <div className="flex gap-3 pt-2">
          <button
            onClick={onCancel}
            className="flex-1 py-2.5 bg-slate-800 text-slate-300 border border-slate-700 rounded-xl text-sm font-semibold hover:bg-slate-700 transition"
          >
            العودة للامتحان
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 py-2.5 bg-red-500 text-white rounded-xl text-sm font-bold hover:bg-red-600 transition shadow-lg shadow-red-500/20"
          >
            تأكيد التسليم
          </button>
        </div>
      </div>
    </div>
  )
}
