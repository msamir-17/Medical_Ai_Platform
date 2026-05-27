import { UploadZone } from '@/components/upload/UploadZone';

export default function UploadPage() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-[--color-text-primary]">Upload Medical Report</h1>
        <p className="text-[--color-text-secondary]">Add a new PDF or image to your health history.</p>
      </header>

      <UploadZone />
    </div>
  );
}