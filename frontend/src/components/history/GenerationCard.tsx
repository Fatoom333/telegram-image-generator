import type { GenerationResponse } from "../../api/types";
import { StatusBadge } from "../misc/StatusBadge";
import { formatDate } from "../../misc/format_date";
import { AuthImage } from "./AuthImage";

type Props = {
    generation: GenerationResponse;
    onImageClick: (imageUrl: string) => void;
};

export function GenerationCard({ generation, onImageClick }: Props) {
    const outputImages = generation.images?.filter((img) => img.role !== "input") ?? [];
    const previewImage = outputImages.find((img) => img.file_url) ?? outputImages[0];
    const previewUrl = previewImage?.file_url;
    return (
        <article className="generation-card">
            <div className="generation-info">
                <div>
                    <h3>{generation.prompt}</h3>
                    <p>
                        {generation.provider ?? "provider"} / {generation.model_name ?? "model"} ·{" "}
                        {formatDate(generation.created_at)}
                    </p>
                </div>
                <StatusBadge status={generation.status} />
            </div>
            {generation.error_message && (
                <p className="generation-error">{generation.error_message}</p>
            )}
            {outputImages.length > 0 && previewUrl ? (
                <div
                    className="image-grid"
                    onClick={() => onImageClick(previewUrl)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") onImageClick(previewUrl);
                    }}
                >
                    <AuthImage alt={generation.prompt} src={previewUrl} />
                </div>
            ) : (
                <p className="generation-wait">Результат появится здесь после обработки...</p>
            )}
        </article>
    );
}
