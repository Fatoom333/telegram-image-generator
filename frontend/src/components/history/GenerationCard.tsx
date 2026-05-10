import type { GenerationResponse, GenerationAssetResponse } from "../../api/types";
import { StatusBadge } from "../misc/StatusBadge";
import { formatDate } from "../../misc/format_date";
import { AuthAsset } from "./AuthAsset";
import DownloadBtnIcon from "../../assets/download_btn_icon.svg?react";
import { useState } from "react";

type Props = {
    generation: GenerationResponse;
    onImageClick: (url: string) => void;
    onVideoClick: (url: string) => void;
};

export function GenerationCard({ generation, onImageClick, onVideoClick }: Props) {
    const outputAssets: GenerationAssetResponse[] = 
        generation.assets?.filter((img) => img.role !== "input") ?? [];
    const [loadedBlobUrl, setLoadedBlobUrl] = useState<string | null>(null);
    const firstAsset = outputAssets[0] ?? null;
    const handleDownload = () => {
        if (!loadedBlobUrl || !firstAsset) return;
        const ext = firstAsset.asset_type === "video" ? "mp4" : "png";
        const link = document.createElement("a");
        link.href = loadedBlobUrl;
        link.download = `${generation.prompt.slice(0, 30)}.${ext}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };
    const handleAssetClick = () => {
        if (!loadedBlobUrl || !firstAsset) return;
        if (firstAsset.asset_type === "video") { onVideoClick(loadedBlobUrl); }
        else { onImageClick(loadedBlobUrl); }
    };
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
            {firstAsset ? (
                <div
                    className="image-grid"
                    onClick={handleAssetClick}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") handleAssetClick();
                    }}
                >
                    <AuthAsset 
                        alt={generation.prompt} 
                        src={firstAsset.file_url!}
                        asset_type={firstAsset.asset_type as "image" | "video"} 
                        onLoad={setLoadedBlobUrl}
                    />
                    <button
                        className="download-btn"
                        onClick={(e) => {
                            e.stopPropagation();
                            handleDownload();
                        }}
                        title="Скачать"
                    >
                        <DownloadBtnIcon/>
                    </button>
                </div>
            ) : (
                <p className="generation-wait">Результат появится здесь после обработки...</p>
            )}
        </article>
    );
}
